"""联网搜索：多后端 + 后台线程。

优先使用 DuckDuckGo（若安装了 ddgs/duckduckgo_search），否则回退到中文 Wikipedia API。
全部使用公开接口，无需 API Key。
"""
import re
import urllib.parse
import urllib.request

from PySide6.QtCore import QThread, Signal

from .. import config

# 用于去掉 Wikipedia 摘要里的 HTML 标签
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text or "").strip()


def _try_ddg(query: str, max_results: int) -> list:
    """DuckDuckGo 搜索（需要已安装 ddgs / duckduckgo_search）。"""
    DDGS = None
    try:
        from ddgs import DDGS  # 新版包名
    except Exception:  # noqa: BLE001
        try:
            from duckduckgo_search import DDGS  # 旧版包名
        except Exception:  # noqa: BLE001
            return []
    try:
        with DDGS() as d:
            raw = list(d.text(query, max_results=max_results))
        results = []
        for r in raw:
            results.append({
                "title": r.get("title", "").strip(),
                "snippet": (r.get("body") or r.get("snippet") or "").strip(),
                "url": (r.get("href") or r.get("url") or "").strip(),
            })
        return [r for r in results if r["title"]]
    except Exception:  # noqa: BLE001
        return []


def _try_wikipedia(query: str, max_results: int) -> list:
    """中文 Wikipedia 搜索（无需 Key，稳定）。"""
    api = ("https://zh.wikipedia.org/w/api.php?action=query&list=search&format=json"
           f"&srsearch={urllib.parse.quote(query)}&srlimit={max_results}")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "qwen-desk-pet/1.0"})
        with urllib.request.urlopen(req, timeout=config.SEARCH_TIMEOUT) as resp:
            data = __import__("json").loads(resp.read().decode("utf-8"))
        results = []
        for it in data.get("query", {}).get("search", []) or []:
            title = it.get("title", "").strip()
            if not title:
                continue
            results.append({
                "title": title,
                "snippet": _strip_html(it.get("snippet", "")),
                "url": f"https://zh.wikipedia.org/wiki/{urllib.parse.quote(title)}",
            })
        return results
    except Exception:  # noqa: BLE001
        return []


def search(query: str, max_results: int = None) -> list:
    """返回 [{title, snippet, url}, ...]。多后端回退。"""
    max_results = max_results or config.SEARCH_MAX_RESULTS
    results = _try_ddg(query, max_results)
    if results:
        return results
    return _try_wikipedia(query, max_results)


def format_search_reply(query: str, results: list) -> str:
    """把搜索结果格式化成祈りちゃん的口吻回复。"""
    if not results:
        return "呜，没搜到相关结果，要不要换个说法试试？(￣▽￣*)"
    lines = [f"这是我在网上搜到的「{query}」的结果：" ]
    for i, r in enumerate(results[:config.SEARCH_MAX_RESULTS], 1):
        snippet = r["snippet"] or "（暂无简介）"
        lines.append(f"{i}. {r['title']}：{snippet}")
    lines.append("")
    lines.append("来源：")
    for r in results[:config.SEARCH_MAX_RESULTS]:
        if r.get("url"):
            lines.append(r["url"])
    return "\n".join(lines)


def is_search_intent(text: str) -> bool:
    """判断这句话是否需要联网搜索（启发式关键词）。"""
    if not config.SEARCH_ENABLED:
        return False
    t = text.strip()
    if len(t) < 2:
        return False
    for kw in config.SEARCH_TRIGGERS:
        if kw in t:
            return True
    return False


# 寒暄/闲聊词：命中这些就不联网，避免无关搜索内容干扰小模型
_CASUAL_WORDS = (
    "你好", "您好", "早上好", "下午好", "晚上好", "晚安", "再见", "拜拜",
    "哈哈", "嘿嘿", "嘻嘻", "呵呵", "谢谢", "感谢", "辛苦", "在吗", "在不在",
    "hello", "hi", "嗯嗯", "嗯", "哦", "行", "好呀", "好的", "么么", "抱抱",
    "摸摸", "爱你", "想你", "开心", "难过", "累",
)


def is_casual(text: str) -> bool:
    """判断是不是寒暄/闲聊（这类不联网，保证对话连贯）。"""
    t = text.strip().lower()
    if not t:
        return True
    for w in _CASUAL_WORDS:
        if w in t:
            return True
    if len(t) <= 3:
        return True
    return False


class SearchWorker(QThread):
    """后台线程中执行搜索。"""
    finished_ok = Signal(str, list)   # query, results
    finished_err = Signal(str)

    def __init__(self, query: str, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        try:
            results = search(self.query)
            self.finished_ok.emit(self.query, results)
        except Exception as e:  # noqa: BLE001
            self.finished_err.emit(str(e))
