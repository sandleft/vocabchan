import os

# ================= 🔧 终极神级配置区域 (Izumi Omni-Arsenal V5.0 绝对领域版) =================
API_KEYS = {
    "google": "", "openai": "", "claude": "", "deepseek": "", "grok": "",
    "qwen": "", "kimi": "", "doubao": "", "minimax": "", "openrouter": ""
}

BASE_URLS = {
    "openai": "https://api.openai.com/v1", "deepseek": "https://api.deepseek.com",
    "grok": "https://api.x.ai/v1", "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "kimi": "https://api.moonshot.cn/v1", "doubao": "https://ark.cn-beijing.volces.com/api/v3",
    "minimax": "https://api.minimax.chat/v1", "openrouter": "https://openrouter.ai/api/v1"
}

# --- 🎯 核心路径与代理配置 (修复 7) ---
_BASE_DIR = os.path.join(os.path.expanduser("~"), "VocabChan")
ASSETS_PATH  = os.path.join(_BASE_DIR, "Assets")
VOCAB_FOLDER = os.path.join(_BASE_DIR, "Vocabulary")
DB_PATH      = os.path.join(_BASE_DIR, "VocabChan.db")
LOG_PATH     = os.path.join(_BASE_DIR, "VocabChan.log")
VN_OUTPUT_DIR = os.path.join(_BASE_DIR, "VN_Output")  # Galgame 剧本输出目录
VN_OUTPUT_DIR = os.path.join(_BASE_DIR, "VN_Output")  # Galgame 剧本输出目录
# 【修复 4】使用统一 PROXY_URL 变量：原代码先将 http_proxy 赋为""，再读取它赋给 https_proxy，
#           导致 https_proxy 永远为空，破坏系统代理配置
PROXY_URL = ""  # e.g. "http://127.0.0.1:7890"
if PROXY_URL:
    os.environ['http_proxy']  = PROXY_URL
    os.environ['https_proxy'] = PROXY_URL

ANKI_BYPASS_PROXY = True

ANKI_DECK_NAME           = "VocabChan"  # Anki 牌组名称
ANKI_CONNECT_PORT        = 8765                      # AnkiConnect 监听端口，默认8765
ANKI_SHOW_ORIGINAL_ON_BACK = True                    # 答案页顶部是否显示原文

OBS_AUTO_START_REPLAY_BUFFER = True   # 回溯缓冲未启动时是否自动启动
OBS_POLL_TIMEOUT             = 15     # OBS 文件轮询超时秒数（慢速磁盘可调高）
OBS_KEEP_SOURCE_FILE         = True   # 视频复制到 Assets 后是否保留 OBS 原始文件

RAG_RECENT_WORD_COUNT = 3    # 系统提示注入的历史词条数量
RETRY_MAX_ATTEMPTS    = 3    # 失败任务自动重试最大次数
DEBUG_MODE            = False # True 时打印 [DEBUG] 调试信息

# --- 🎬 录制与 OBS 破壁配置 (修复 8) ---
CIRCUIT_BREAKER_LIMIT = 60  # 【修复 14】硬性断路器：最长录制60秒，防破产
VIDEO_FPS = 21              # 【修复 2】补充缺失定义：原代码第 484 行使用 VIDEO_FPS 但从未定义，导致 NameError
OBS_WS_HOST = "127.0.0.1"
OBS_WS_PORT = 4455
OBS_WS_PASSWORD = "your_password"  # ⚠️ 请修改为实际密码，启动检查会提示
OBS_WATCH_DIR = r"C:/your/obs/recording/path" # 必须与 OBS 实际保存录像的路径完全一致！

# --- 🤖 本地 AI 增强模块开关 (修复 2, 10, 19, Abyss) ---
ENABLE_LOCAL_OCR = False         # 开启后使用 PaddleOCR 辅助识别，根绝幻觉
ENABLE_LOCAL_WHISPER = True     # 开启后使用 Faster-Whisper 转录音频
ENABLE_AUTONOMOUS_LISTENER = False # 开启后后台常驻监听，自动触发抓取 (慎用，极耗性能)
ENABLE_VN_GALGAME_GENERATOR = False # 每天晚上23:50自动生成专属Galgame
ENABLE_CAPTURE_PREVIEW = False   # 【新增】截图后弹出预览窗口，确认后再发送 AI（需 tkinter）
ENABLE_REGION_SELECT = False     # 【新增】开启后 Alt+R 进入区域选择，下次截图仅截取选定区域
OBS_WATCH_DIR = r"C:/Users/你的OBS录像保存路径"  # 请修改为你的OBS录像路径
# 【修复 Ic】SD_API_URL / VITS_API_URL 全文仅出现于注释，实际无调用，移除无效占位符

# --- 📁 媒体文件本地保留与外部接口配置 ---
ENABLE_TELDRIVE_UPLOAD = False   # 开启后将媒体文件复制到 Teldrive 挂载的 Z 盘
TELDRIVE_MOUNT_PATH    = r"Z:\Izumi_Media"  # Teldrive 在本机的挂载路径，需提前挂载 Z 盘
ENABLE_ANKI_MEDIA      = True    # 开启后将图片和音频上传至 Anki 媒体库（视频 Anki 不支持，不上传）

# Anki 卡片正面显示内容："core_word" 只显示单词 / "original_text" 只显示原文 / "both" 两者都显示
ANKI_FRONT_CONTENT = "both"
# Anki 语音播放位置："front" 正面翻转前自动播放 / "back" 答案页播放
ANKI_AUDIO_SIDE = "front"

# --- 🧹 分析报告章节标题黑名单 ---
# 【修复 16】系统提示强制要求 AI 输出的章节标题，不应被误识别为 Obsidian 知识图谱链接
ANALYSIS_SECTION_HEADERS = {
    "翻译", "单词详解", "语法与核心难点", "实战语感", "原文", "深度解析", "知识图谱链接"
}

# ================= 🌍 槽位与模板系统 (保持绝对一致) =================
TARGET_LANGUAGE = "简体中文"
ACTIVE_TEMPLATE = "japanese"

SLOTS_CONFIG = {
    "av_fast":     [ {"key": "f4",       "provider": "google",   "model": "gemini-2-flash-exp"},       {"key": "ctrl+f4",  "provider": "openai",   "model": "gpt-4o-mini"} ],
    "av_deep":     [ {"key": "f6",       "provider": "google",   "model": "gemini-1.5-pro-latest"},      {"key": "ctrl+f6",  "provider": "claude",   "model": "claude-3-5-sonnet-20241022"} ],
    "clipboard":   [ {"key": "f2",       "provider": "deepseek", "model": "deepseek-chat"},              {"key": "ctrl+f2",  "provider": "qwen",     "model": "qwen-vl-max"} ],
    "vision_only": [ {"key": "f8",       "provider": "kimi",     "model": "moonshot-v1-auto"},           {"key": "f9",       "provider": "doubao",   "model": "doubao-vision-pro"} ],
    "audio_only":  [ {"key": "f10",      "provider": "openai",   "model": "gpt-4o-audio-preview"},       {"key": "f11",      "provider": "minimax",  "model": "abab6.5s-chat"} ],
    "video_hold":  [ {"key": "f7",       "provider": "google",   "model": "gemini-2.0-flash-exp"},       {"key": "ctrl+f7",  "provider": "claude",   "model": "claude-3-5-sonnet-20241022"} ],
    "video_retro": [ {"key": "f12",      "provider": "google",   "model": "gemini-2.0-flash-exp"},       {"key": "ctrl+f12", "provider": "openai",   "model": "gpt-4o"} ]
}

OPENROUTER_HOTKEYS = [
    {"key": "alt+1", "model": "google/gemini-2.0-flash-lite-001",          "action": "av_fast"},
    {"key": "alt+2", "model": "google/gemini-2.0-flash-lite-001",          "action": "av_deep"},
    {"key": "alt+3", "model": "deepseek/deepseek-v3.2",   "action": "clipboard"},
    {"key": "alt+4", "model": "google/gemini-2.0-flash-lite-001",                       "action": "vision_only"},
    {"key": "alt+5", "model": "google/gemini-2.0-flash-lite-001",          "action": "audio_only"},
    {"key": "alt+6", "model": "google/gemini-2.0-flash-lite-001",          "action": "video_hold"},
    {"key": "alt+7", "model": "google/gemini-2.0-flash-lite-001",          "action": "video_retro"},
]

TEMPLATE_SWITCH_HOTKEYS = [
    {"key": "alt+z", "lang": "english"},
    {"key": "alt+x", "lang": "japanese"},
    {"key": "alt+c", "lang": "custom_1"}
]

LANGUAGE_TEMPLATES = {
    "english":    {"name": "英语",         "focus": "严格指出发音与拼写的脱节现象。如果出现短语动词（Phrasal verbs），必须详细解释其搭配和语境差异。"},
    "spanish":    {"name": "西班牙语",     "focus": "深度剖析动词变位（Conjugation）的形态，重点解释虚拟式（Subjunctive）的触发条件和主观情绪表达，标注名词阴阳性。"},
    "french":     {"name": "法语",         "focus": "重点分析名词的阴阳性规律，详细标注并解释连音连读（Liaison）和省音现象，注意发音与拼写的差异。"},
    "japanese":   {"name": "日语",         "focus": "严谨分析敬语系统（尊敬语、谦让语、郑重语）的阶级性和使用对象，解释汉字音读/训读，并剖析主语省略的语境。"},
    "german":     {"name": "德语",         "focus": "破解名词及冠词的四格变格（主/宾/与/属格）和三种词性，重点分析从句中\u201c动词后置\u201d等框形结构语法。"},
    "korean":     {"name": "韩语",         "focus": "梳理尊卑语阶（Honorifics）的词尾变化与适用对象，准确标注连读、收音同化等复杂的发音音变规律。"},
    "italian":    {"name": "意大利语",     "focus": "确保名词与形容词的性数严格一致性分析，解释复杂的动词变位体系，如有必要可补充意大利语特有的语气词或手势文化语境。"},
    "chinese":    {"name": "中文 (普通话)","focus": "精准标注拼音及声调（Tones），解释汉字字形构成逻辑，并归纳特定量词（Measure words）的搭配规律。"},
    "portuguese": {"name": "葡萄牙语",     "focus": "指出特有的鼻音发音特征。如果在语法或用词上存在欧洲葡语与巴西葡语的显著差异，请务必详细对比说明。"},
    "arabic":     {"name": "阿拉伯语",     "focus": "区分句子是属于现代标准阿拉伯语（MSA）还是特定方言（如埃及、黎凡特方言）。解释复杂的词根变位及字母在不同位置的书写变化。"},
    "custom_1":   {"name": "自定义语言1",  "focus": "【请自行修改】"},
    "custom_2":   {"name": "自定义语言2",  "focus": "【请自行修改】"},
    "custom_3":   {"name": "自定义语言3",  "focus": "【请自行修改】"}
}

# ===== 🔄 运行时覆盖加载 (由 IzumiConfig.exe 写入，无需重新编译) =====
import json as _json_rt
import sys as _sys_rt
_RT_OVERRIDE_FILE = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'izumi_runtime_settings.json')
if os.path.exists(_RT_OVERRIDE_FILE):
    try:
        with open(_RT_OVERRIDE_FILE, 'r', encoding='utf-8') as _rt_f:
            _rt_overrides = _json_rt.load(_rt_f)
        _rt_mod = _sys_rt.modules[__name__]
        for _rt_k, _rt_v in _rt_overrides.items():
            setattr(_rt_mod, _rt_k, _rt_v)
        # 重新应用代理（覆盖可能改变了 PROXY_URL）
        if getattr(_rt_mod, 'PROXY_URL', ''):
            os.environ['http_proxy']  = _rt_mod.PROXY_URL
            os.environ['https_proxy'] = _rt_mod.PROXY_URL
        del _rt_mod, _rt_overrides
    except Exception:
        pass
del _json_rt, _sys_rt, _RT_OVERRIDE_FILE
