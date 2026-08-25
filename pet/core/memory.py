"""聊天历史记忆：保留最近若干轮 + 对更早对话自动压缩成摘要，保证长对话上下文连贯。"""
from collections import deque
from .. import config


class ChatMemory:
    """保存 user/assistant 消息。

    策略：
    - 最近 `max_turns` 轮逐字保留（保证即时连贯）。
    - 一旦超出，把最旧的若干轮交给后台压缩成一句摘要保存，
      之后 `build_payload_messages()` 会把摘要以 system 消息形式带上下文。
    """

    def __init__(self, system_prompt: str = None, max_turns: int = None):
        self.system_prompt = system_prompt or config.SYSTEM_PROMPT
        self.max_turns = max_turns or config.MAX_HISTORY_TURNS
        self.summary = ""          # 早于 recent 的压缩摘要
        self._recent: deque = deque()   # 元素 (role, content)

    def add(self, role: str, content: str) -> None:
        """追加一条消息。"""
        self._recent.append((role, content))

    def get_summarize_text(self) -> str or None:
        """当 recent 超过上限时，把最旧的部分取出来用于压缩；否则返回 None。

        返回需要被压缩成摘要的文本；同时这些消息会从 recent 移除。
        """
        if len(self._recent) <= self.max_turns * 2:
            return None
        overflow = len(self._recent) - self.max_turns * 2
        cut = []
        for _ in range(overflow):
            cut.append(self._recent.popleft())
        base = (f"【此前摘要】{self.summary}\n\n" if self.summary else "")
        body = "\n".join(f"{role}: {content}" for role, content in cut)
        return base + body

    def set_summary(self, text: str) -> None:
        """写入压缩后的摘要。"""
        if text:
            self.summary = text.strip()

    def build_payload_messages(self) -> list:
        """构造发送给 /api/chat 的 messages（含 system 与可选摘要）。"""
        msgs = [{"role": "system", "content": self.system_prompt}]
        if self.summary:
            msgs.append({
                "role": "system",
                "content": f"【此前对话摘要（发生在最近对话之前，供你保持连贯）】\n{self.summary}",
            })
        for role, content in self._recent:
            msgs.append({"role": role, "content": content})
        return msgs

    def clear(self) -> None:
        self._recent.clear()
        self.summary = ""

    @property
    def is_empty(self) -> bool:
        return len(self._recent) == 0 and not self.summary
