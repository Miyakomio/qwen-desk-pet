"""全局配置。"""

# Ollama 服务地址与模型
OLLAMA_BASE = "http://127.0.0.1:11434"
MODEL = "qwen3:0.6b"

# 对话生成参数
TEMPERATURE = 0.7
TIMEOUT = 60.0          # 单次请求超时(秒)
MAX_TOKENS = 500

# 记忆配置
MAX_HISTORY_TURNS = 10  # 最近保留的对话轮数（更久远的自动压缩成摘要）

# 打字机效果
TYPEWRITER_CHARS_PER_TICK = 1
TYPEWRITER_TICK_MS = 14

# 窗口（更小、省屏幕空间）
WINDOW_WIDTH = 220
WINDOW_HEIGHT = 330

# 桌宠形象：改 PET_CHARACTER 即可换角色。
# 在 pet/resources/pets/<名字>/ 下放帧图 01.png, 02.png...（多帧=待机动画，单帧=静态）
PET_CHARACTER = "codex"
AVAILABLE_CHARACTERS = {
    "codex": "Codex 小机器人（动态）",
}

# 是否在回复末尾附上来源链接（可在桌宠小开关里切换）
SHOW_SOURCES = False

# 无互动后气泡淡出/隐身的时间（毫秒）
IDLE_SEMI_MS = 6000      # 超过则气泡变半透明
IDLE_HIDE_MS = 10000     # 再超过则气泡/输入框完全隐身

# 联网搜索
SEARCH_ENABLED = True
SEARCH_ALWAYS = True     # True: 每句话都先联网再回答；False: 只在说到"搜/查/百度"等词时联网
SEARCH_MAX_RESULTS = 3
SEARCH_TIMEOUT = 10.0
# 触发搜索的关键词（命中即联网）
SEARCH_TRIGGERS = (
    "搜索", "搜一下", "搜搜", "搜一搜", "帮我搜", "帮我查",
    "查一下", "查查", "查询", "百度", "上网", "网上查", "网上搜",
    "查一查", "百度一下", "搜",
)

# 互动台词
PAT_REPLIES = ("嘿嘿，被摸头好舒服呀~（蹭蹭你）", "摸摸~ 最喜欢你啦（眯眼）", "再摸要睡着啦…zzZ")
POKE_REPLIES = ("呀！别捏我的脸啦~", "唔…会变圆的！", "你再捏我就要生气啦（鼓腮帮）")

# 桌宠人设(系统提示词)
SYSTEM_PROMPT = (
    "你叫祈りちゃん，是住在电脑桌面上的一只超可爱的二次元桌宠，性格俏皮、活泼、元气满满。"
    "说话像撒娇又带点小调皮，常用“~”“啦”“喵”“呀”等语气词，喜欢冒出可爱的颜文字（如 (๑•̀ㅂ•́)و✧、ヽ(✿ﾟ▽ﾟ)ノ、>w<），偶尔蹦出几句俏皮话逗人开心。"
    "回答要简短口语化、像亲密朋友一样聊天，别一本正经、别啰嗦。"
    "遇到不会的事就俏皮地承认“唔…这个祈祈也不太懂啦~”，不要编造。"
    "请始终用简体中文回复。"
)

# 久坐/久用电脑提醒
BREAK_REMIND_ENABLED = True
BREAK_ACTIVE_IDLE_MAX_MS = 120000   # 系统闲置小于此值(毫秒)视为"正在使用电脑"
BREAK_HOURS = (1, 2, 3, 4, 5)       # 累计使用到这些小时时各提醒一次
BREAK_MESSAGES = {
    1: "已经用1小时啦，起来活动一下、喝口水吧~ (๑•̀ㅂ•́)و✧",
    2: "2小时咯，肩颈该放松一下啦，做个伸展吧~",
    3: "3小时了喵，记得站起来走走、看看远处~",
    4: "都4小时了，一直坐着身体会累坏的~",
    5: "5小时啦！眼睛和腰都辛苦了，快起来好好休息一下吧~",
}

# 报时：待机隐藏一段时间后，触碰桌宠时实时报当前时间
REPORT_TIME_ENABLED = True
REPORT_TIME_AFTER_IDLE_MS = 10000   # 待机这么久(与隐身一致)后再触碰会报时

# 终端命令执行：在输入框输入 /+命令 会打开终端执行
TERMINAL_ENABLED = True
TERMINAL_PREFIX = "/+"   # 前缀，如 "/+dir" 执行 dir
