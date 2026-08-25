"""PySide6 桥接层：在 QML 与 Python 之间传递消息、表情、思考状态。"""
import time

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from . import config
from .core import emotion as emotion_mod, terminal, usage
from .core.memory import ChatMemory
from .core.message_model import MessageModel
from .llm.client import ChatWorker, SummarizeWorker
from .search.client import SearchWorker, format_search_reply, is_casual, is_search_intent


class PetBridge(QObject):
    """暴露给 QML 的上下文对象。"""

    # --- 信号（QML 侧 connect） ---
    userMessage = Signal(str)          # 用户说的内容
    botMessage = Signal(str)           # 助手完整回复
    thinking = Signal(bool)            # 是否正在思考
    emotion = Signal(str)              # 表情变化

    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory = ChatMemory()
        self.messageModel = MessageModel(self)
        self._worker = None
        self._busy = False
        self._summarizing = False
        self._pending_sources = []     # 本次回答附带的结果来源
        self.show_sources = config.SHOW_SOURCES
        self._last_time_report = 0     # 上次报时时间(防刷屏)

        # 久坐提醒 + 整点报时
        self._active_ms = 0
        self._break_idx = 0
        self._last_check = None
        if config.BREAK_REMIND_ENABLED:
            self._break_timer = QTimer(self)
            self._break_timer.setInterval(15000)
            self._break_timer.timeout.connect(self._check_usage)
            self._break_timer.start()
            self._last_check = int(time.time() * 1000)
        self._last_chime_hour = None
        if config.CHIME_ENABLED:
            self._chime_timer = QTimer(self)
            self._chime_timer.setInterval(20000)
            self._chime_timer.timeout.connect(self._check_chime)
            self._chime_timer.start()

    def _auto_say(self, msg: str):
        """发一条自动消息（只显示，不入对话上下文，避免干扰）。"""
        self.messageModel.add("assistant", msg)
        self.botMessage.emit(msg)
        self.emotion.emit("happy")

    def on_schedule_remind(self, msg: str):
        """日程提醒 → 显示到气泡。"""
        self._auto_say(msg)

    def _check_usage(self):
        """累计"正在使用电脑"的时长，到 1/2/3/4/5 小时各提醒一次。"""
        if not config.BREAK_REMIND_ENABLED or self._busy:
            return
        if self._break_idx >= len(config.BREAK_HOURS):
            return  # 已提醒过所有档位
        now = int(time.time() * 1000)
        if self._last_check is None:
            self._last_check = now
            return
        dt = now - self._last_check
        self._last_check = now
        if usage.system_idle_ms() >= config.BREAK_ACTIVE_IDLE_MAX_MS:
            return  # 人不在电脑前，不计入
        self._active_ms += dt
        hour = config.BREAK_HOURS[self._break_idx]
        if self._active_ms >= hour * 3600000:
            self._auto_say(config.BREAK_MESSAGES.get(hour, "起来活动一下吧~"))
            self._break_idx += 1

    @Slot(int)
    def reportTime(self, idle_ms: int):
        """待机一段时间后触碰桌宠时，实时报当前时间（带冷却防刷屏）。"""
        if not config.REPORT_TIME_ENABLED or idle_ms < config.REPORT_TIME_AFTER_IDLE_MS:
            return
        now_ts = time.time()
        if now_ts - self._last_time_report < config.REPORT_TIME_COOLDOWN_SEC:
            return
        self._last_time_report = now_ts
        from datetime import datetime
        now = datetime.now()
        self._auto_say(f"已经{now:%H:%M}了喵，记得注意时间哦")

    def _check_chime(self):
        """整点报时：每个整点(分钟为0)按「已经HH:MM:SS了喵，记得…哦」格式报一次。"""
        if not config.CHIME_ENABLED or self._busy:
            return
        from datetime import datetime
        now = datetime.now()
        if now.minute != 0:
            return
        if self._last_chime_hour == now.hour:
            return  # 这一小时已报过
        self._last_chime_hour = now.hour
        tail = config.CHIME_MESSAGES.get(now.hour, "记得休息一下哦")
        self._auto_say(f"已经{now:%H:%M}了喵，{tail}")

    @Slot(str)
    def sendMessage(self, text: str):
        """QML 输入框回车时调用。"""
        text = text.strip()
        if not text or self._busy:
            return

        # 终端命令模式：/+命令 打开终端执行
        if config.TERMINAL_ENABLED and text.startswith(config.TERMINAL_PREFIX):
            self._handle_terminal(text)
            return

        # 用户消息
        self.memory.add("user", text)
        self.messageModel.add("user", text)
        self.userMessage.emit(text)

        # 开始思考
        self._busy = True
        self.thinking.emit(True)
        self._pending_sources = []

        # 模式一：联网对话。寒暄/闲聊直接聊，真正的问题才搜索并注入上下文
        if config.SEARCH_ENABLED and config.SEARCH_ALWAYS:
            if is_casual(text):
                self._start_chat()
                return
            self._worker = SearchWorker(text)
            self._worker.finished_ok.connect(self._on_search_for_chat)
            self._worker.finished_err.connect(self._on_chat_no_search)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker.start()
            return

        # 模式二：命中搜索关键词，直接展示搜索结果
        if is_search_intent(text):
            self._worker = SearchWorker(text)
            self._worker.finished_ok.connect(self._on_search)
            self._worker.finished_err.connect(self._on_search_error)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker.start()
            return

        # 普通对话
        self._start_chat()

    def _start_chat(self):
        """用当前记忆启动一次普通对话（可选带上搜索上下文）。"""
        messages = self.memory.build_payload_messages()
        ctx = self._search_context
        if ctx:
            messages.append({"role": "system", "content": ctx})
        self._worker = ChatWorker(messages)
        self._worker.finished_ok.connect(self._on_reply)
        self._worker.finished_err.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    @property
    def _search_context(self) -> str:
        """把待展示的来源拼成搜索上下文；无来源返回空串。"""
        if not self._pending_sources:
            return ""
        lines = ["【以下是联网搜索到的信息，请参考它们回答问题，回答要自然】"]
        for i, r in enumerate(self._pending_sources, 1):
            lines.append(f"{i}. {r['title']}：{r['snippet']}")
        lines.append("来源：")
        lines.extend(r["url"] for r in self._pending_sources)
        return "\n".join(lines)

    def _on_search_for_chat(self, query: str, results: list):
        # 把搜索结果作为上下文，交给模型回答
        self._pending_sources = results
        self._start_chat()

    def _on_chat_no_search(self, err: str):
        # 联网失败则退回普通对话
        self._pending_sources = []
        self._start_chat()

    @Slot()
    def clearHistory(self):
        """清空记忆。"""
        self.memory.clear()
        self.messageModel.clear()

    def _handle_terminal(self, text: str):
        """处理 /+命令：打开终端执行。不入对话记忆。"""
        cmd = text[len(config.TERMINAL_PREFIX):].strip()
        self.messageModel.add("user", text)
        self.userMessage.emit(text)
        self._busy = True
        self.thinking.emit(True)
        if cmd:
            ok = terminal.run_in_terminal(cmd)
            reply = f"好嘞，已打开终端执行：{cmd}" if ok else f"呜，打开终端执行「{cmd}」失败啦~"
        else:
            reply = f"想让我执行命令的话，输入 {config.TERMINAL_PREFIX}命令 哦，比如 {config.TERMINAL_PREFIX}dir"
        self.messageModel.add("assistant", reply)
        self.botMessage.emit(reply)
        self.emotion.emit("happy")
        self._busy = False
        self.thinking.emit(False)

    @Slot(bool)
    def setShowSources(self, on: bool):
        """开关：是否在回复末尾附上来源链接。"""
        self.show_sources = bool(on)

    def _on_reply(self, text: str):
        if self.show_sources and self._pending_sources:
            urls = [r["url"] for r in self._pending_sources if r.get("url")]
            if urls:
                text = text.rstrip() + "\n\n来源：\n" + "\n".join(urls)
        self.memory.add("assistant", text)
        self.messageModel.add("assistant", text)
        self._finish()
        self.botMessage.emit(text)
        self.emotion.emit(emotion_mod.detect_emotion(text))
        self._maybe_summarize()

    def _on_error(self, err: str):
        reply = f"呜，出错了：{err}。再试一次吧~"
        self.messageModel.add("assistant", reply)
        self._finish()
        self.botMessage.emit(reply)

    def _on_search(self, query: str, results: list):
        reply = format_search_reply(query, results)
        self.memory.add("assistant", reply)
        self.messageModel.add("assistant", reply)
        self._finish()
        self.botMessage.emit(reply)
        self.emotion.emit("happy")
        self._maybe_summarize()

    def _on_search_error(self, err: str):
        reply = "呜，联网搜索没成功，可能是网络问题~ 我们聊点别的吧？"
        self.messageModel.add("assistant", reply)
        self._finish()
        self.botMessage.emit(reply)

    def _maybe_summarize(self):
        """若历史超长，把最旧的部分交给后台模型压缩成摘要。"""
        if self._summarizing:
            return
        text = self.memory.get_summarize_text()
        if not text:
            return
        self._summarizing = True
        w = SummarizeWorker(text)
        w.finished_ok.connect(self._on_summarized)
        w.finished_err.connect(self._on_summarized)   # 失败也结束状态
        w.finished.connect(w.deleteLater)
        w.start()

    def _on_summarized(self, summary: str):
        self.memory.set_summary(summary)
        self._summarizing = False

    def _finish(self):
        self._busy = False
        self.thinking.emit(False)
