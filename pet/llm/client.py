"""Ollama 对话客户端（基于 QThread，避免阻塞 UI）。"""
import requests
from PySide6.QtCore import QThread, Signal

from .. import config


class ChatWorker(QThread):
    """在后台线程中调用 Ollama /api/chat 的 worker。"""

    # 成功返回完整回复文本；失败返回错误信息
    finished_ok = Signal(str)
    finished_err = Signal(str)

    def __init__(self, messages: list, parent=None):
        super().__init__(parent)
        self._messages = messages

    def run(self):
        url = f"{config.OLLAMA_BASE}/api/chat"
        payload = {
            "model": config.MODEL,
            "messages": self._messages,
            "stream": False,
            "options": {
                "temperature": config.TEMPERATURE,
                "num_predict": config.MAX_TOKENS,
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=config.TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            text = (data.get("message") or {}).get("content", "").strip()
            if not text:
                self.finished_err.emit("模型返回了空回复")
            else:
                self.finished_ok.emit(text)
        except requests.RequestException as e:
            self.finished_err.emit(f"无法连接本地模型：{e}")
        except Exception as e:  # noqa: BLE001
            self.finished_err.emit(f"出错了：{e}")


class SummarizeWorker(QThread):
    """在后台线程中把一段对话历史压缩成摘要（用于长对话记忆）。"""
    finished_ok = Signal(str)
    finished_err = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个对话压缩助手。请把下面给出的对话记录压缩成一段简短、连贯、有条理的中文摘要，"
                    "保留对后续对话重要的信息：用户的偏好、提到过的事实、约定、正在进行的任务、双方的名字。"
                    "只输出摘要本身，不要解释，不要提问，尽量控制在200字以内。"
                ),
            },
            {"role": "user", "content": self.text},
        ]
        payload = {
            "model": config.MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 300},
        }
        try:
            resp = requests.post(f"{config.OLLAMA_BASE}/api/chat",
                                 json=payload, timeout=config.TIMEOUT)
            resp.raise_for_status()
            text = (resp.json().get("message") or {}).get("content", "").strip()
            if text:
                self.finished_ok.emit(text)
            else:
                self.finished_err.emit("摘要为空")
        except Exception as e:  # noqa: BLE001
            self.finished_err.emit(str(e))
