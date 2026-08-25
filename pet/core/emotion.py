"""表情判定：根据助手回复的文本，启发式地选出一个表情。

可选表情：happy / thinking / surprised / sad / love / neutral
"""

# 关键词 -> 表情（按优先级从高到低）
_RULES = [
    ("love", ["喜欢", "爱你", "想你", "亲亲", "抱抱", "宝贝", "么么"]),
    ("sad", ["难过", "伤心", "哭", "呜呜", "好难", "失望", "不开心", "委屈", "唉"]),
    ("surprised", ["哇", "天哪", "震惊", "惊讶", "不会吧", "真的吗", "?!", "？？"]),
    ("happy", ["哈哈", "好耶", "开心", "高兴", "太好了", "嘿嘿", "好棒", "棒棒", "喜欢", "谢谢"]),
    ("thinking", ["嗯", "让我想想", "思考", "也许", "可能", "大概", "吧"]),
]


def detect_emotion(text: str, default: str = "neutral") -> str:
    """返回最匹配的表情名。"""
    if not text:
        return default
    lowered = text.lower()
    for emotion, keywords in _RULES:
        for kw in keywords:
            if kw in lowered:
                return emotion
    return default
