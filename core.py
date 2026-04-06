import time
import os
import re
import json
import base64
import html as html_module  # 【修复 12】重命名避免与局部变量冲突，用于 HTML 注入防护
import keyboard
import pyperclip
import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import asyncio
import sqlite3
import httpx
# 【修复 19】移除从未被引用的 deque 导入
import cv2
import mss
import subprocess
import logging   # 【新增】持久化错误日志
import csv       # 【新增】CSV 导出功能
import queue     # 【修复 II】主线程 tkinter 任务投递队列
import shutil
from datetime import datetime  # 【修复 Ia】timedelta 全文无引用，移除无效导入
import google.generativeai as genai
from openai import OpenAI
import anthropic
from PIL import ImageGrab, Image  # 【新增】Image 用于区域截图保存与预览
import ctypes
import pyautogui
import glob
from config import *
genai.configure(api_key=API_KEYS["google"])
_NATIVE_AUDIO_PROVIDERS = {"openai"}  # grok 不支持 input_audio base64 格式，仅 openai 支持原生音频

# 【新增】tkinter 用于截图预览与区域选择，不可用时优雅降级
try:
    import tkinter as tk
    from PIL import ImageTk
    _tk_available = True
except ImportError:
    _tk_available = False

# ================= 🚑 紧急修复与底层系统补丁 =================
if hasattr(np, 'frombuffer'):
    np.fromstring = np.frombuffer

# 【修复 1】修正语法错误：原代码将 try/except 写在同一行，Python 不允许此语法
# 强制 DPI 感知，完美支持多屏与缩放
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # Windows 8.1+
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ================= 🔒 线程安全锁 =================
# 【修复 5】ACTIVE_TEMPLATE 由热键线程写、异步线程读，需加锁防止竞态条件
_template_lock = threading.Lock()

# ================= 📝 持久化错误日志初始化 (新增) =================
# 【修复 II】在 logging.basicConfig 打开日志文件之前先确保目录存在，
# 否则目录不存在时 basicConfig 静默失败，全文所有 logging.error 调用均无效
_log_dir = os.path.dirname(LOG_PATH)
if _log_dir:
    os.makedirs(_log_dir, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

# ================= 🌟 OSD 视觉反馈 (修复 16) =================
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except Exception:
    toaster = None

def show_toast(title, msg, duration=3):
    # 【修复 18】移除 kwargs 中的 threaded=True：原代码已将 show_toast 包装在新线程中，
    #            再传 threaded=True 会导致双重线程化，引发 Windows 通知 API 竞态崩溃
    if toaster:
        threading.Thread(
            target=toaster.show_toast,
            args=(title, msg),
            kwargs={"duration": duration},
            daemon=True
        ).start()
    else:
        print(f"[{title}] {msg}")

# ================= 🧠 本地 ML 模型初始化 (OCR & Whisper) =================
local_ocr_engine = None
if ENABLE_LOCAL_OCR:
    try:
        from paddleocr import PaddleOCR
        print("⚙️ 加载本地 PaddleOCR 引擎中...")
        local_ocr_engine = PaddleOCR(use_angle_cls=True, lang='japan', show_log=False)
    except Exception as e:
        print(f"⚠️ PaddleOCR 加载失败: {e}")

local_whisper_engine = None
if ENABLE_LOCAL_WHISPER or ENABLE_AUTONOMOUS_LISTENER:
    try:
        from faster_whisper import WhisperModel
        print("⚙️ 加载本地 Faster-Whisper 引擎中...")
        local_whisper_engine = WhisperModel("base", device="cpu", compute_type="int8")
    except Exception as e:
        print(f"⚠️ Whisper 加载失败 (检查CUDA环境): {e}")

# ================= 🗄️ 数据库初始化 (修复 6, 11, 12, 17) =================

def get_db_conn():
    """
    【修复 6】统一数据库连接入口。
    - 启用 WAL 模式：允许多线程并发读写，防止 "database is locked" 错误
    - 设置 timeout=10：高并发时排队等待而非立即报错
    """
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db_conn()
    c = conn.cursor()
    # 词汇记忆表 (RAG使用)
    c.execute('''CREATE TABLE IF NOT EXISTS vocab_memory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  core_word TEXT, original_text TEXT, analysis TEXT,
                  lang TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    # 【新增】词频统计表：独立追踪每个词的捕获次数，用于去重检测与学习统计
    c.execute('''CREATE TABLE IF NOT EXISTS word_stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  core_word TEXT, lang TEXT,
                  first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                  last_seen  DATETIME DEFAULT CURRENT_TIMESTAMP,
                  capture_count INTEGER DEFAULT 1,
                  UNIQUE(core_word, lang))''')
    # 任务重试队列表
    c.execute('''CREATE TABLE IF NOT EXISTS retry_queue
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider TEXT, model TEXT, payload_json TEXT,
                  retry_count INTEGER DEFAULT 0)''')
    conn.commit()
    c.close()
    conn.close()

init_db()

# 【新增】区域选择状态，由 toggle_region_select() 写入，handle_sync_capture() 读取
_selected_region = None  # (left, top, width, height) 或 None
_selected_region_lock = threading.Lock()  # 【修复 I.2】保护 _selected_region 的跨线程读写
_main_thread_ui_queue = queue.SimpleQueue()  # 【修复 II】主线程 tkinter 任务队列；非主线程将 UI 调用投递至此，由主循环统一执行

# 【新增】间隔复习提醒：记录最近一次触发日期，防止同一天重复弹出
_last_reminder_date = {"date": None}

event_loop = None  # 【修复 X】前向声明，正式赋值在启动区，消除 batch_import_from_clipboard 等函数的前向引用隐患

def set_active_template(lang_key):
    global ACTIVE_TEMPLATE
    if lang_key in LANGUAGE_TEMPLATES:
        with _template_lock:  # 【修复 5】加锁保护写操作
            ACTIVE_TEMPLATE = lang_key
        show_toast("模板切换", f"已切换至: {LANGUAGE_TEMPLATES[lang_key]['name']}")

# ======================= 🔑 启动验证 (新增) =======================

def validate_paths():
    """【新增】启动时自动创建所有必要目录，避免因目录不存在导致的静默失败"""
    for name, path in [("ASSETS_PATH", ASSETS_PATH), ("VOCAB_FOLDER", VOCAB_FOLDER), ("VN_OUTPUT_DIR", VN_OUTPUT_DIR)]:
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(f"✅  已自动创建目录 [{name}]: {path}")
            except Exception as e:
                print(f"❌  无法创建目录 [{name}]: {e}")
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception as e:
            print(f"❌  无法创建数据库目录: {e}")

def validate_api_keys():
    """【新增】启动时检查 API 密钥配置，对未配置的 provider 立即给出明确提示"""
    missing    = [p for p, k in API_KEYS.items() if not k]
    configured = [p for p, k in API_KEYS.items() if k]
    if missing:
        print(f"⚠️  未配置密钥的 provider: {', '.join(missing)}")
        print("    对应槽位触发时将立即失败，请在配置区填写密钥。")
    if configured:
        print(f"✅  已配置密钥的 provider: {', '.join(configured)}")
    # 【修复 21】OBS 占位符密码检测
    if OBS_WS_PASSWORD == "your_password":
        print("⚠️  OBS_WS_PASSWORD 仍为默认占位符，OBS 连接将失败，请及时修改")

# ======================= 🛠️ 底层工具库与数据清洗 =======================

def mask_pii(text):
    """
    【修复 13】本地隐私脱敏：
    - 修正正则书写错误：[A-Z|a-z] → [A-Za-z]（原写法中 | 是字面量竖线，非逻辑或）
    - 扩展覆盖范围：新增身份证号、银行卡号
    """
    if not text: return text
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL_HIDDEN]', text)
    text = re.sub(r'\b1[3-9]\d{9}\b',    '[PHONE_HIDDEN]', text)   # 中国大陆手机号
    text = re.sub(r'\b\d{17}[\dXx]\b',   '[ID_HIDDEN]',    text)   # 身份证号（18位）
    text = re.sub(r'\b\d{16,19}\b',       '[CARD_HIDDEN]',  text)   # 银行卡号（16-19位）
    return text

def sanitize_filename(name): return re.sub(r'[\\/*?:"<>|]', "", name).strip()

# 【修复 9】encode_image / encode_audio 改用上下文管理器，防止文件描述符泄漏
def encode_image(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def encode_audio(aud_path):
    with open(aud_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def upload_to_teldrive(file_path):
    """
    【接口】将本地媒体文件复制到 Teldrive 挂载的 Z 盘目录。
    ENABLE_TELDRIVE_UPLOAD=True 且 Z 盘已正常挂载时生效；否则静默跳过。
    """
    if not ENABLE_TELDRIVE_UPLOAD or not file_path or not os.path.exists(file_path):
        return
    try:
        os.makedirs(TELDRIVE_MOUNT_PATH, exist_ok=True)
        dest = os.path.join(TELDRIVE_MOUNT_PATH, os.path.basename(file_path))
        shutil.copy2(file_path, dest)
    except Exception as e:
        logging.error(f"Teldrive 上传失败 [{file_path}]: {e}")
        show_toast("⚠️ Teldrive 上传失败", str(e))

def sync_to_anki(core_word, original_text, analysis, lang_tag=None, img_name=None, audio_name=None, anki_card=None):
    """Anki 同步：urllib 直连绕过 TUN 代理，两步写入支持完整内容"""
    import urllib.request, urllib.error
    _ANKI_URL = f"http://127.0.0.1:{ANKI_CONNECT_PORT}"

    def _anki_post(payload, timeout=15):
        """直连 AnkiConnect，ANKI_BYPASS_PROXY=True 时绕过系统代理（含 TUN 模式）"""
        if ANKI_BYPASS_PROXY:
            _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        else:
            _opener = urllib.request.build_opener()
        _req = urllib.request.Request(
            _ANKI_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with _opener.open(_req, timeout=timeout) as _resp:
            return json.loads(_resp.read().decode("utf-8"))

    # 连通性检测
    try:
        _anki_post({"action": "deckNames", "version": 6}, timeout=3)
    except Exception:
        show_toast("⚠️ Anki 未运行", "AnkiConnect 未响应，跳过同步（不影响 Obsidian 写入）")
        logging.warning(f"Anki 同步跳过 [{core_word}]: AnkiConnect 不可达")
        return

    # 媒体文件上传
    def _store_anki_media(filename):
        if not ENABLE_ANKI_MEDIA or not filename: return
        file_path = os.path.join(ASSETS_PATH, filename)
        if not os.path.exists(file_path): return
        try:
            with open(file_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logging.error(f"Anki 媒体读取失败 [{filename}]: {e}"); return
        for _attempt in range(2):
            try:
                result = _anki_post({"action": "storeMediaFile", "version": 6,
                                     "params": {"filename": filename, "data": data}}, timeout=15)
                if result.get("error"):
                    logging.error(f"Anki 媒体上传错误 [{filename}]: {result['error']}")
                return
            except Exception as e:
                if _attempt == 0: time.sleep(1)
                else: logging.error(f"Anki 媒体上传失败 [{filename}]: {e}")

    _store_anki_media(img_name)
    _store_anki_media(audio_name)

    img_html  = f'<img src="{img_name}"><br>' if (img_name   and ENABLE_ANKI_MEDIA) else ""
    sound_tag = f'[sound:{audio_name}]'        if (audio_name and ENABLE_ANKI_MEDIA) else ""
    def _md_to_html(md: str) -> str:
        """
        Markdown → Anki HTML，全语言通用版
        支持：日/中/韩/阿拉伯/希伯来/西/法/德/葡/意/英
        - RTL 语言（阿拉伯/希伯来）自动加 dir=rtl
        - 列表逐行处理，不会破坏周围结构
        - 所有字符均为 Unicode，无编码问题
        """
        RTL_RANGES = (
            '\u0600-\u06FF',   # 阿拉伯语
            '\u0590-\u05FF',   # 希伯来语
            '\u0700-\u074F',   # 叙利亚语
            '\u0750-\u077F',   # 阿拉伯补充
        )
        _rtl_pattern = re.compile(f'[{"".join(RTL_RANGES)}]')

        def _is_rtl(text):
            return bool(_rtl_pattern.search(text))

        lines = md.split('\n')
        html_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # 标题
            m = re.match(r'^(#{1,3})\s+(.+)$', line)
            if m:
                level = len(m.group(1))
                content = m.group(2)
                # 粗体、斜体处理（先处理 ** 再处理 *）
                content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
                content = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', content)
                dir_attr = ' dir="rtl"' if _is_rtl(content) else ''
                html_lines.append(f'<h{level}{dir_attr}>{content}</h{level}>')
                i += 1
                continue

            # 无序列表（- 或 * 开头，* 必须后跟空格避免误匹配斜体）
            m = re.match(r'^\s*(?:-|\*(?=\s))\s+(.+)$', line)
            if m:
                # 收集连续列表项
                items = []
                while i < len(lines):
                    lm = re.match(r'^\s*(?:-|\*(?=\s))\s+(.+)$', lines[i])
                    if lm:
                        item = lm.group(1)
                        item = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', item)
                        item = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', item)
                        dir_attr = ' dir="rtl"' if _is_rtl(item) else ''
                        items.append(f'<li{dir_attr}>{item}</li>')
                        i += 1
                    else:
                        break
                html_lines.append('<ul>' + ''.join(items) + '</ul>')
                continue

            # 有序列表（数字. 开头）
            m = re.match(r'^\s*(\d+)\.\s+(.+)$', line)
            if m:
                items = []
                while i < len(lines):
                    lm = re.match(r'^\s*\d+\.\s+(.+)$', lines[i])
                    if lm:
                        item = lm.group(1)
                        item = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', item)
                        item = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', item)
                        dir_attr = ' dir="rtl"' if _is_rtl(item) else ''
                        items.append(f'<li{dir_attr}>{item}</li>')
                        i += 1
                    else:
                        break
                html_lines.append('<ol>' + ''.join(items) + '</ol>')
                continue

            # 空行
            if line.strip() == '':
                html_lines.append('<br>')
                i += 1
                continue

            # 普通段落
            text = line
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
            dir_attr = ' dir="rtl"' if _is_rtl(text) else ''
            html_lines.append(f'<p{dir_attr}>{text}</p>')
            i += 1

        return '\n'.join(html_lines)

    # 正面内容由 ANKI_FRONT_CONTENT 控制
    if ANKI_FRONT_CONTENT == "core_word":
        _front_text = f"{core_word}"
    elif ANKI_FRONT_CONTENT == "original_text":
        _front_text = f"{original_text}"
    else:  # "both"
        _front_text = f"{core_word}<br>{original_text}"

    # 语音位置由 ANKI_AUDIO_SIDE 控制
    if ANKI_AUDIO_SIDE == "front":
        _front_html = f"{img_html}{sound_tag}{_front_text}"
        _back_sound = ""
    else:
        _front_html = f"{img_html}{_front_text}"
        _back_sound = sound_tag

    _back_md      = f"{anki_card}" if anki_card else analysis
    _original_html = f"<p><b>{original_text}</b></p><hr>" if ANKI_SHOW_ORIGINAL_ON_BACK else ""
    _back_content  = f"{_back_sound}{_original_html}{_md_to_html(_back_md)}"

    # 自动探测模板名和字段名
    _model_name = "Basic"
    _front_field = "Front"
    _back_field  = "Back"
    try:
        _models = _anki_post({"action": "modelNames", "version": 6}, timeout=5).get("result", [])
        for _c in ["基础", "Basic"]:
            if _c in _models: _model_name = _c; break
        else:
            if _models: _model_name = _models[0]
        _fields = _anki_post({"action": "modelFieldNames", "version": 6,
                               "params": {"modelName": _model_name}}, timeout=5).get("result", [])
        if len(_fields) >= 2: _front_field, _back_field = _fields[0], _fields[1]
    except Exception as e:
        logging.warning(f"Anki 模板探测失败，使用默认值: {e}")

    # 确保牌组存在
    try:
        _anki_post({"action": "createDeck", "version": 6,
                    "params": {"deck": ANKI_DECK_NAME}}, timeout=5)
    except Exception: pass

    # 第一步：建空卡拿 NoteID
    _payload = {"action": "addNote", "version": 6, "params": {"note": {
        "deckName": ANKI_DECK_NAME, "modelName": _model_name,
        "fields": {_front_field: _front_html, _back_field: ""},
        "options": {"allowDuplicate": True},
        "tags": ["Omni-Arsenal", lang_tag if lang_tag else ACTIVE_TEMPLATE]
    }}}
    try:
        _result = _anki_post(_payload, timeout=15)
        if _result.get("error"):
            show_toast("⚠️ Anki 建卡失败", f"{_result['error']}")
            logging.error(f"Anki 建卡错误 [{core_word}]: {_result['error']}"); return
        _note_id = _result.get("result")
        logging.info(f"Anki 建卡成功 [{core_word}] NoteID={_note_id}")
    except Exception as e:
        show_toast("⚠️ Anki 建卡失败", str(e))
        logging.error(f"Anki 建卡失败 [{core_word}]: {e}"); return

    # 第二步：写入完整 Back 内容
    try:
        _upd = _anki_post({"action": "updateNoteFields", "version": 6,
                           "params": {"note": {"id": _note_id,
                                               "fields": {_back_field: _back_content}}}}, timeout=30)
        if _upd.get("error"):
            show_toast("⚠️ Anki 内容写入失败", f"{_upd['error']}")
            logging.error(f"Anki 内容写入错误 [{core_word}]: {_upd['error']}")
        else:
            logging.info(f"Anki 完整写入成功 [{core_word}] NoteID={_note_id}")
    except Exception as e:
        show_toast("⚠️ Anki 内容写入超时", str(e))
        logging.error(f"Anki 内容写入失败 [{core_word}]: {e}")

def save_atomic_note(json_data, img_name=None, audio_name=None, source="Unknown", model_used="Unknown", video_name=None):
    """
    【修复 7, 21】原子性写入：先写文件后写库。
    - 文件写入失败则直接返回，不写数据库，保证两侧一致性
    - 新增重复词条检测与词频追踪（word_stats 表）
    """
    with _template_lock:  # 【修复 5】快照当前模板，防止写入期间被其他线程切换
        snapshot_template = ACTIVE_TEMPLATE

    core_word    = json_data.get("core_word", "Unknown")
    original_text = json_data.get("original_text", "")
    full_analysis = json_data.get("analysis", "")

    clean_name = sanitize_filename(core_word) or f"Note_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    file_path  = os.path.join(VOCAB_FOLDER, f"{clean_name}.md")
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M")

    media_refs  = "".join([f"![[{m}]]\n" for m in [img_name, audio_name, video_name] if m])
    # 【修复 16】过滤已知章节标题黑名单，防止 analysis 中的标题误生成 Obsidian 双链
    graph_links = "\n".join([
        f"[[{word}]]" for word in set(re.findall(r'【(.*?)】', full_analysis))
        if len(word) < 10 and word not in ANALYSIS_SECTION_HEADERS
    ])

    card_content = f"""
#card
{media_refs}
?
**【原文】**\n{original_text}\n\n---\n**【深度解析】**\n{full_analysis}\n
**【知识图谱链接】**\n{graph_links}\n
*Capture: {timestamp} | Source: {source} ({model_used}) | Template: {snapshot_template.upper()}*
---
"""
    # ── Step 1: 写入 Obsidian 文件（失败则终止，不继续写库）──
    try:
        mode = "a" if os.path.exists(file_path) else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"---\ntags:\n  - flashcard\n  - {snapshot_template}\ncreated: {timestamp}\n---\n# {core_word}\n\n")
            f.write(f"\n{card_content}")
    except Exception as e:
        logging.error(f"写入 Obsidian 文件失败 [{core_word}]: {e}")
        print(f"❌ 写入文件失败: {e}")
        return  # 文件失败则不继续，保证两侧一致

    # ── Step 2: 文件成功后再写数据库 ──
    conn = get_db_conn()
    try:
        conn.execute(
            "INSERT INTO vocab_memory (core_word, original_text, analysis, lang) VALUES (?, ?, ?, ?)",
            (core_word, original_text, full_analysis, snapshot_template)
        )
        # 【新增】词频追踪：UPSERT 到 word_stats
        existing = conn.execute(
            "SELECT capture_count FROM word_stats WHERE core_word=? AND lang=?",
            (core_word, snapshot_template)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE word_stats SET capture_count=capture_count+1, last_seen=CURRENT_TIMESTAMP WHERE core_word=? AND lang=?",
                (core_word, snapshot_template)
            )
            show_toast("处理完成 ⚠️ 重复词条", f"[{core_word}] 已是第 {existing[0]+1} 次捕获，笔记已追加")
        else:
            conn.execute("INSERT INTO word_stats (core_word, lang) VALUES (?, ?)", (core_word, snapshot_template))
            show_toast("处理完成", f"[{core_word}] 笔记已存入 Obsidian！")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"数据库写入失败 [{core_word}]: {e}")
        print(f"❌ 数据库写入失败: {e}")
        return  # DB 写入失败则不继续，防止 Anki 同步与媒体清理造成双重不一致
    finally:
        conn.close()

    anki_card = json_data.get("anki_card", None)
    sync_to_anki(core_word, original_text, full_analysis, lang_tag=snapshot_template, img_name=img_name, audio_name=audio_name, anki_card=anki_card)
    # 【修复 I.1】传入已加锁快照，不再让 sync_to_anki 直接读全局变量

    # 媒体文件保留在本地 ASSETS_PATH，供 Obsidian 正常引用；不再删除
    # 【新增】如已配置 Teldrive，将图片、音频、视频同步复制到 Z 盘备份
    for media in [img_name, audio_name, video_name]:
        if media:
            upload_to_teldrive(os.path.join(ASSETS_PATH, media))

def get_system_prompt():
    """【修复 11, 17】注入 RAG 记忆流与双语输出指令"""
    with _template_lock:  # 【修复 5】加锁保护读操作
        snapshot_template = ACTIVE_TEMPLATE

    lang_info = LANGUAGE_TEMPLATES.get(snapshot_template, LANGUAGE_TEMPLATES["japanese"])

    conn = get_db_conn()
    try:
        recent = conn.execute(
            f"SELECT core_word, original_text FROM vocab_memory WHERE lang=? ORDER BY timestamp DESC LIMIT {RAG_RECENT_WORD_COUNT}",
            (snapshot_template,)
        ).fetchall()
    finally:
        conn.close()
    recent_memory = "\n".join([f"- {row[0]}: {row[1]}" for row in recent])

    return f"""
    你是一位严谨的语言学教授。
    ⚠️ 全局指令：
    - 源语言：【{lang_info['name']}】
    - 所有解析必须包含：【{TARGET_LANGUAGE}的信达雅翻译】 + 【源语言的直译逻辑】
    - 历史记忆上下文 (如有关联请指出)：\n{recent_memory}
    
    返回严格 JSON 结构：
    {{"core_word": "最核心生词原型", "original_text": "准确的原文", "analysis": "Markdown 详细报告"}}

    analysis 必须包含：
    1. **【翻译】**：{TARGET_LANGUAGE}翻译及双向直译解析。
    2. **【单词详解】**：词性及释义。
    3. **【语法与核心难点】**：{lang_info['focus']}
    4. **【实战语感】**：适用场合、正式程度等。
    """

# ======================= 📊 词汇管理与学习统计 (新增) =======================

def search_vocab(query=None):
    """【新增】在数据库中搜索已保存词条，结果打印到控制台并发送 Toast 摘要"""
    conn = get_db_conn()
    try:
        if query and query.strip():
            rows = conn.execute(
                "SELECT vm.core_word, vm.original_text, vm.lang, vm.timestamp, COALESCE(ws.capture_count,1) "
                "FROM vocab_memory vm LEFT JOIN word_stats ws ON vm.core_word=ws.core_word AND vm.lang=ws.lang "
                "WHERE vm.core_word LIKE ? OR vm.original_text LIKE ? ORDER BY vm.timestamp DESC LIMIT 10",
                (f"%{query}%", f"%{query}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT vm.core_word, vm.original_text, vm.lang, vm.timestamp, COALESCE(ws.capture_count,1) "
                "FROM vocab_memory vm LEFT JOIN word_stats ws ON vm.core_word=ws.core_word AND vm.lang=ws.lang "
                "ORDER BY vm.timestamp DESC LIMIT 10"
            ).fetchall()
    finally:
        conn.close()

    if not rows:
        show_toast("搜索结果", f"未找到匹配词条: {query or '(最近词条)'}")
        return
    print(f"\n📚 词汇搜索结果 (查询: {query or '最近10条'}):")
    for r in rows:
        print(f"  [{r[2]}] {r[0]}: {r[1][:40]}  ×{r[4]}次  ({r[3][:10]})")
    show_toast("搜索完成", f"找到 {len(rows)} 条词条，详情见控制台")

def show_learning_stats():
    """【新增】显示学习统计信息（总量、今日、本周、语言分布、高频词）"""
    conn = get_db_conn()
    try:
        total    = conn.execute("SELECT COUNT(*) FROM word_stats").fetchone()[0]
        today    = conn.execute("SELECT COUNT(*) FROM word_stats WHERE date(first_seen,'localtime')=date('now','localtime')").fetchone()[0]
        week     = conn.execute("SELECT COUNT(*) FROM word_stats WHERE date(first_seen,'localtime')>=date('now','localtime','-7 days')").fetchone()[0]
        by_lang  = conn.execute("SELECT lang, COUNT(*) FROM word_stats GROUP BY lang ORDER BY COUNT(*) DESC").fetchall()
        top5     = conn.execute("SELECT core_word, capture_count FROM word_stats ORDER BY capture_count DESC LIMIT 5").fetchall()
    finally:
        conn.close()

    print("\n" + "="*60)
    print(f"📊 学习统计报告 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"  总词汇量: {total} 词 | 今日新增: {today} 词 | 本周新增: {week} 词")
    if by_lang:
        print("  语言分布: " + " | ".join([f"{r[0]}: {r[1]}词" for r in by_lang]))
    if top5:
        print("  高频词汇: " + " | ".join([f"{r[0]}(×{r[1]})" for r in top5]))
    print("="*60)
    show_toast("学习统计", f"总词汇: {total} | 今日: {today} | 本周: {week}")

def export_vocab_csv():
    """【新增】将全部词汇导出为 UTF-8 BOM CSV 文件（Excel 直接可读）"""
    os.makedirs(VOCAB_FOLDER, exist_ok=True)
    export_path = os.path.join(VOCAB_FOLDER, f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
    conn = get_db_conn()
    try:
        rows = conn.execute(
            "SELECT vm.core_word, vm.original_text, vm.analysis, vm.lang, vm.timestamp, COALESCE(ws.capture_count,1) "
            "FROM vocab_memory vm LEFT JOIN word_stats ws ON vm.core_word=ws.core_word AND vm.lang=ws.lang "
            "ORDER BY vm.timestamp DESC"
        ).fetchall()
    finally:
        conn.close()
    try:
        with open(export_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["核心词", "原文", "解析", "语言", "时间戳", "捕获次数"])
            writer.writerows(rows)
        show_toast("导出完成", f"CSV 已保存: {os.path.basename(export_path)}")
        print(f"✅ CSV 导出完成: {export_path}")
    except Exception as e:
        logging.error(f"CSV 导出失败: {e}")
        show_toast("❌ 导出失败", str(e))

def export_vocab_txt():
    """【新增】将全部词汇导出为纯文本词表（按语言分组）"""
    os.makedirs(VOCAB_FOLDER, exist_ok=True)
    export_path = os.path.join(VOCAB_FOLDER, f"wordlist_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
    conn = get_db_conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT vm.core_word, vm.original_text, vm.lang "
            "FROM vocab_memory vm ORDER BY vm.lang, vm.core_word"
        ).fetchall()
    finally:
        conn.close()
    try:
        with open(export_path, "w", encoding="utf-8") as f:
            current_lang = None
            for row in rows:
                if row[2] != current_lang:
                    current_lang = row[2]
                    f.write(f"\n=== {current_lang.upper()} ===\n")
                f.write(f"{row[0]}: {row[1]}\n")
        show_toast("导出完成", f"词表已保存: {os.path.basename(export_path)}")
        print(f"✅ TXT 词表导出完成: {export_path}")
    except Exception as e:
        logging.error(f"TXT 导出失败: {e}")
        show_toast("❌ 导出失败", str(e))

def batch_import_from_clipboard():
    """【新增】从剪贴板读取多行文本，逐行批量投喂 AI 进行分析（每行一个词条）"""
    text_block = pyperclip.paste()
    if not text_block or not text_block.strip():
        show_toast("批量导入", "剪贴板内容为空")
        return
    lines = [l.strip() for l in text_block.strip().split('\n') if l.strip()]
    if not lines:
        show_toast("批量导入", "剪贴板无有效行")
        return
    show_toast("批量导入", f"开始处理 {len(lines)} 条词条...")
    provider_slot = SLOTS_CONFIG.get("clipboard", [{}])
    if not provider_slot:
        show_toast("批量导入失败", "clipboard 槽位未配置，请在设置中添加")
        return
    provider_slot = provider_slot[0]  # 使用 clipboard 槽位的首个 provider
    # 【修复 III.2】将循环及 sleep 移入 daemon 线程，防止热键回调线程被阻塞 N×0.3 秒
    def _do_batch():
        for line in lines:
            asyncio.run_coroutine_threadsafe(
                async_universal_api_call(provider_slot["provider"], provider_slot["model"], "clipboard", line, None, None, None),
                event_loop
            )
            time.sleep(0.3)  # 避免请求过于密集
    threading.Thread(target=_do_batch, daemon=True).start()
    show_toast("批量导入", f"已提交 {len(lines)} 条，正在后台处理...")

# ======================= 🖼️ 截图预览与区域选择 (新增) =======================

def show_capture_preview(img_path):
    """
    【新增】弹出截图预览窗口，用户可确认发送或取消。
    返回 True=确认，False=取消。30 秒无操作自动确认。
    仅在 ENABLE_CAPTURE_PREVIEW=True 且 tkinter 可用时调用。
    """
    if not _tk_available:
        return True  # tkinter 不可用则静默跳过预览直接发送
    cancelled = threading.Event()

    def _run_ui():
        try:
            root = tk.Tk()
            root.title("📸 截图预览 — 确认发送？")
            root.attributes('-topmost', True)
            try:
                img = Image.open(img_path)
                img.thumbnail((800, 500))
                photo = ImageTk.PhotoImage(img)
                tk.Label(root, image=photo).pack(padx=10, pady=10)
            except Exception:
                tk.Label(root, text="[图片加载失败]").pack(padx=10, pady=10)
            btn_frame = tk.Frame(root)
            btn_frame.pack(pady=10)
            def on_confirm():
                root.destroy()
            def on_cancel():
                cancelled.set()
                root.destroy()
            tk.Button(btn_frame, text="✅ 确认发送", command=on_confirm, bg="#4CAF50", fg="white", padx=15).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="❌ 取消",     command=on_cancel,  bg="#f44336", fg="white", padx=15).pack(side=tk.LEFT, padx=10)
            root.after(30000, on_confirm)  # 30秒无操作自动确认
            root.mainloop()
        except Exception as e:
            logging.error(f"截图预览窗口异常: {e}")

    # 【修复 II】tkinter 的 mainloop() 必须在主线程调用。
    # 本函数由 _dispatch daemon 线程调用，属于非主线程，直接调用 mainloop() 在 macOS 上
    # 必然崩溃，在 Windows 上也属未定义行为。
    # 修复：若检测到当前不在主线程，将本次调用打包投递到 _main_thread_ui_queue，
    # 主循环（while True）会取出并执行；调用方通过 threading.Event 同步等待结果。
    if threading.current_thread() is not threading.main_thread():
        _result_box = [True]
        _done = threading.Event()
        def _ui_task():
            _result_box[0] = show_capture_preview(img_path)
            _done.set()
        _main_thread_ui_queue.put(_ui_task)
        _done.wait(timeout=CIRCUIT_BREAKER_LIMIT + 5)
        return _result_box[0]
    _run_ui()
    return not cancelled.is_set()

def select_screen_region():
    """
    【新增】弹出全屏半透明蒙版，用户拖拽框选截图区域。
    返回 (left, top, width, height) 或 None（取消/超时）。
    """
    if not _tk_available:
        show_toast("⚠️ 区域选择不可用", "tkinter 未安装，无法使用区域选择功能")
        return None
    result = [None]

    def _run_ui():
        try:
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            root.attributes('-alpha', 0.35)
            root.attributes('-topmost', True)
            root.configure(bg='#000000')
            canvas = tk.Canvas(root, cursor="cross", bg='#000000', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            state = {"sx": 0, "sy": 0, "rect": None}

            def on_press(e):
                state["sx"], state["sy"] = e.x, e.y
                state["rect"] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline='#FF0000', width=2)
            def on_drag(e):
                if state["rect"]:
                    canvas.coords(state["rect"], state["sx"], state["sy"], e.x, e.y)
            def on_release(e):
                x1 = min(state["sx"], e.x); y1 = min(state["sy"], e.y)
                x2 = max(state["sx"], e.x); y2 = max(state["sy"], e.y)
                if x2 - x1 > 10 and y2 - y1 > 10:
                    result[0] = (x1, y1, x2 - x1, y2 - y1)
                root.destroy()

            canvas.bind('<ButtonPress-1>',   on_press)
            canvas.bind('<B1-Motion>',        on_drag)
            canvas.bind('<ButtonRelease-1>', on_release)
            root.bind('<Escape>', lambda e: root.destroy())
            root.after(30000, root.destroy)  # 30秒无操作自动关闭，与 show_capture_preview 行为一致，防止主线程永久阻塞
            root.mainloop()
        except Exception as e:
            logging.error(f"区域选择窗口异常: {e}")

    # 【修复 II】同 show_capture_preview，tkinter 须在主线程执行。
    # toggle_region_select 由 alt+r 热键回调触发，运行于键盘库内部线程，非主线程。
    # 将调用投递到 _main_thread_ui_queue，主循环执行后通过 threading.Event 返回结果。
    if threading.current_thread() is not threading.main_thread():
        _result_box = [None]
        _done = threading.Event()
        def _ui_task():
            _result_box[0] = select_screen_region()
            _done.set()
        _main_thread_ui_queue.put(_ui_task)
        _done.wait(timeout=30)
        return _result_box[0]
    _run_ui()
    return result[0]

def toggle_region_select():
    """【新增】触发区域选择并存入 _selected_region；再次触发则清除选区恢复全屏模式"""
    global _selected_region
    # 【修复 I.2】加锁读取，避免与 handle_sync_capture 的并发读产生竞态
    with _selected_region_lock:
        current = _selected_region
    if current is not None:
        with _selected_region_lock:
            _selected_region = None
        show_toast("区域选择", "已清除选区，恢复全屏截图模式")
        return
    region = select_screen_region()
    with _selected_region_lock:
        _selected_region = region
    if region:
        show_toast("区域选择", f"已锁定区域: {region[2]}×{region[3]} @ ({region[0]},{region[1]})")
    else:
        show_toast("区域选择", "未选择区域，保持全屏截图模式")

# ======================= 🎥 核心黑科技：OBS 破壁与硬件编码 (修复 8, 9, 真正轮询) =======================

class OBSDashcam:
    def __init__(self):
        self.enabled = False
        try:
            import obsws_python as obs
            self.cl = obs.ReqClient(host=OBS_WS_HOST, port=OBS_WS_PORT, password=OBS_WS_PASSWORD)
            self.enabled = True
            print("🎥 【妃爱后台系统】OBS WebSocket 挂载成功！")
        except Exception: print("⚠️ OBS 未连接，视频回溯将失效。")

    def save_and_poll_replay(self, timeout=None):
        """回溯缓冲保存，自动启动缓冲，只轮询 mp4"""
        timeout = timeout or OBS_POLL_TIMEOUT
        if not self.enabled: return None
        # 检查并自动启动回溯缓冲
        try:
            status = self.cl.get_replay_buffer_status()
            if not status.output_active:
                if OBS_AUTO_START_REPLAY_BUFFER:
                    self.cl.start_replay_buffer()
                    time.sleep(1.0)
                else:
                    show_toast("⚠️ 回溯缓冲未启动", "请在 OBS 中手动启动回溯缓冲")
                    return None
        except Exception as _rb_e:
            logging.error(f"回溯缓冲状态检查失败: {_rb_e}")
            show_toast("⚠️ 回溯缓冲未就绪", "请在 OBS 中手动启动回溯缓冲")
            return None
                
        # 记录触发前的文件快照，再保存
        before_files = set(glob.glob(os.path.join(OBS_WATCH_DIR, "*.mp4")))
        try:
            self.cl.save_replay_buffer()
            show_toast("OBS 录制", "触发硬件级回溯，等待文件写入...")
            start_t = time.time()
            while time.time() - start_t < timeout:
                current_files = set(glob.glob(os.path.join(OBS_WATCH_DIR, "*.mp4")))
                new_files = current_files - before_files
                if new_files:
                    latest_file = max(new_files, key=os.path.getctime)
                    time.sleep(1.0)
                    return latest_file
                time.sleep(0.5)
            print("❌ OBS 文件轮询超时！")
        except Exception as e:
            logging.error(f"OBS 抓取异常: {e}")
            print(f"OBS 抓取异常: {e}")
        return None

    def record_while_held(self, hotkey):
        """【新增】按住热键期间 OBS 录制未来内容，松开后停止，返回录制文件路径"""
        if not self.enabled:
            show_toast("⚠️ OBS未连接", "video_hold 需要 OBS WebSocket 连接")
            return None
        try:
            before_files = set(glob.glob(os.path.join(OBS_WATCH_DIR, "*.mp4")))
            self.cl.start_record()
            show_toast("🔴 OBS录制中", f"松开 [{hotkey}] 结束录制...")

            start_t = time.time()
            while keyboard.is_pressed(hotkey):
                if time.time() - start_t > CIRCUIT_BREAKER_LIMIT:
                    show_toast("⚠️ 触发断路器", f"达到{CIRCUIT_BREAKER_LIMIT}秒录制上限，强制停止！")
                    break
                time.sleep(0.05)

            self.cl.stop_record()
            show_toast("⏹ 停止录制", "等待文件写入...")

            poll_start = time.time()
            while time.time() - poll_start < OBS_POLL_TIMEOUT * 2:
                current_files = set(glob.glob(os.path.join(OBS_WATCH_DIR, "*.mp4")))
                new_files = current_files - before_files
                if new_files:
                    latest_file = max(new_files, key=os.path.getctime)
                    time.sleep(1.5)
                    return latest_file
                time.sleep(0.5)

            print("❌ OBS video_hold 文件轮询超时")
            return None
        except Exception as e:
            logging.error(f"OBS video_hold 录制异常: {e}")
            print(f"OBS video_hold 录制异常: {e}")
            return None
                
obs_dashcam = OBSDashcam()

# 【新增】预初始化 pyaudiowpatch，消除录音时的初始化延迟
# 延迟发生在按键按下瞬间，导致 is_pressed 检测到按键已松，录音循环立即退出
_pa_instance = None
_loopback_dev_cache = None
try:
    import pyaudiowpatch as _paw
    _pa_instance = _paw.PyAudio()
    _wasapi_info = _pa_instance.get_host_api_info_by_type(_paw.paWASAPI)
    _default_spk = _pa_instance.get_device_info_by_index(_wasapi_info["defaultOutputDevice"])
    for _ci in range(_pa_instance.get_device_count()):
        _cd = _pa_instance.get_device_info_by_index(_ci)
        if _cd.get("isLoopbackDevice") and _default_spk["name"] in _cd["name"]:
            _loopback_dev_cache = _cd
            break
    if _loopback_dev_cache:
        print(f"✅ 录音设备预初始化成功: {_loopback_dev_cache['name']} @ {int(_loopback_dev_cache['defaultSampleRate'])}Hz")
    else:
        print("⚠️ 未找到 loopback 设备，录音功能将不可用")
except Exception as _e:
    print(f"⚠️ pyaudiowpatch 预初始化失败: {_e}")

def convert_to_h264(input_path):
    """
    【修复 9, 15】调用 FFmpeg 强制压制为 Obsidian 兼容的 H.264+AAC 格式。
    - 修正路径替换逻辑：使用 os.path.splitext 替代 str.replace，
      防止路径中含 .avi/.mkv 字样的目录名被误替换
    """
    if not input_path or not os.path.exists(input_path): return input_path
    base, ext = os.path.splitext(input_path)
    output_path = (base + "_h264.mp4") if ext.lower() == ".mp4" else (base + ".mp4")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", output_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return output_path
    except Exception as e:
        logging.error(f"FFmpeg 转码失败 [{input_path}]: {e}")  # 【修复 Vc】原为裸 except 静默丢弃，无法追查
        return input_path  # FFmpeg 不存在或转码失败则直接返回原文件

# ======================= 🚀 异步万能全API路由引擎与队列处理 (修复 1, 12) =======================

async def async_universal_api_call(provider, model_name, action_type, text_content=None, img_path=None, audio_path=None, video_path=None):
    show_toast("AI 解析中", f"正在使用 {model_name} 分析...")

    text_content = mask_pii(text_content)
    prompt = get_system_prompt()

    # 【修复 10】本地 OCR 防幻觉注入
    if ENABLE_LOCAL_OCR and local_ocr_engine and img_path:
        try:
            res = local_ocr_engine.ocr(img_path, cls=True)
            ocr_text = "\n".join([line[1][0] for line in res[0]]) if res and res[0] else ""
            if ocr_text: text_content = (text_content or "") + f"\n\n[本地OCR防幻觉预提取文本]:\n{mask_pii(ocr_text)}"
        except Exception as e: logging.error(f"本地 OCR 调用异常: {e}")  # 【修复 Vd】原为裸 except: pass，静默丢弃，无日志可查
    if ENABLE_LOCAL_WHISPER and local_whisper_engine and audio_path \
        and provider != "google" and action_type in ["audio_only", "av_fast", "av_deep"]:
        try:
            segments, _ = local_whisper_engine.transcribe(audio_path, beam_size=5)
            whisper_text = " ".join([segment.text for segment in segments])
            if whisper_text: text_content = (text_content or "") + f"\n\n[本地Whisper精确转录]:\n{mask_pii(whisper_text)}"
        except Exception as e: logging.error(f"本地 Whisper 转录异常: {e}")  # 【修复 Ve】原为裸 except: pass，静默丢弃，无日志可查
    # minimax 等 provider 既不支持原生音频，Whisper 也未启用时，请求将是空壳，中止并警告
    # 仅支持 input_audio 格式的原生音频 provider
    if action_type == "audio_only" and audio_path and provider not in _NATIVE_AUDIO_PROVIDERS and provider != "google":
        has_whisper_fallback = ENABLE_LOCAL_WHISPER and local_whisper_engine
        if not has_whisper_fallback:
            msg = f"[{provider}] 不支持原生音频输入，且本地 Whisper 未启用，audio_only 槽位无内容可发送，已跳过"
            show_toast("⚠️ 音频槽位配置错误", msg)
            logging.error(msg)  # 【修复 VI】原为 logging.warning；统一使用 error 级别，与其他失败路径保持一致
            return True  # 【修复 IX】永久性配置错误，非瞬态网络失败；返回 True 使重试回调将其从队列删除而非反复重试

    # 【修复 14】使用 get_running_loop() 替代已废弃的 get_event_loop()
    loop = asyncio.get_running_loop()

    def _call_api():
        """
        【修复 11】返回 (True, content) 或 (False, error_str) 二元组，
        不再用字符串前缀 "ERROR:" 判断成败，防止内容本身含 ERROR: 时误判
        """
        try:
            if provider == "google":
                model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
                inputs = [prompt]
                if text_content: inputs.append(f"\n\n【文本】:\n{text_content}")
                if img_path:   inputs.append(genai.upload_file(img_path))
                if audio_path: inputs.append(genai.upload_file(audio_path))
                if video_path:
                    print("上传视频至 Google...")
                    v_file = genai.upload_file(video_path)
                    _v_upload_t = time.time()  # 【修复 VIII】记录上传起始时刻，用于超时守卫
                    while v_file.state.name == "PROCESSING":
                        # 【修复 VIII】原为无超时的裸 while 循环；Google 端卡住时线程池线程被永久占用，
                        # 线程耗尽后所有后续 API 调用全部阻塞，程序进入实质性死锁。
                        # 加入 300 秒硬性超时，超时后抛出异常由外层 _call_api 的 except 捕获并入重试队列。
                        if time.time() - _v_upload_t > 300:
                            raise TimeoutError("Google 视频处理超时（超过300秒），已中止")
                        time.sleep(2)
                        v_file = genai.get_file(v_file.name)
                    inputs.append(v_file)
                return (True, model.generate_content(inputs).text)
            else:
                if provider == "claude":
                    client = anthropic.Anthropic(api_key=API_KEYS["claude"])
                elif provider == "openrouter":
                    client = OpenAI(
                        api_key=API_KEYS.get("openrouter", ""),
                        base_url=BASE_URLS.get("openrouter"),
                        default_headers={
                            "HTTP-Referer": "https://github.com/sandleft/vocabchan",
                            "X-Title": "VocabChan"
                        }
                    )
                else:
                    client = OpenAI(api_key=API_KEYS.get(provider, ""), base_url=BASE_URLS.get(provider))
                content_payload = []

                if video_path:
                    # 【修复 9】VideoCapture 使用 try/finally 确保句柄在任何情况下都被释放
                    cap = cv2.VideoCapture(video_path)                    
                    try:
                        frames_to_extract = 4
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        for i in range(1, frames_to_extract + 1):
                            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, (i * total_frames // (frames_to_extract + 1))))
                            ret, frame = cap.read()
                            if ret:
                                _enc_ok, _enc_buf = cv2.imencode('.jpg', frame)
                                if not _enc_ok:
                                    logging.error(f"cv2.imencode 帧编码失败，跳过该帧")
                                    continue
                                b64_img = base64.b64encode(_enc_buf).decode('utf-8')
                                if provider == "claude":
                                    content_payload.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_img}})
                                else:
                                    content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}})
                    finally:
                        cap.release()

                if img_path:
                    if provider == "claude": content_payload.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encode_image(img_path)}})
                    else: content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(img_path)}"}})  # 【修复 III】截图均保存为 PNG，MIME 类型应为 image/png 而非 image/jpeg
                content_payload.append({"type": "text", "text": prompt})
                if text_content: content_payload.append({"type": "text", "text": f"\n\n【文本】:\n{text_content}"})
# grok 不支持 input_audio 格式，openai/openrouter 支持；其余排除
                _audio_excluded = {"deepseek", "qwen", "kimi", "doubao", "minimax", "grok"}
                if audio_path and provider not in _audio_excluded:
                    content_payload.append({"type": "input_audio", "input_audio": {"data": encode_audio(audio_path), "format": "wav"}})
                if provider == "claude":
                    return (True, client.messages.create(model=model_name, max_tokens=2048, messages=[{"role": "user", "content": content_payload}]).content[0].text)
                elif provider == "openai" and "audio" in model_name:
                    # gpt-4o-audio-preview 等音频模型需要指定 modalities，且响应结构不同
                    resp = client.chat.completions.create(
                        model=model_name,
                        modalities=["text"],
                        messages=[{"role": "user", "content": content_payload}]
                    )
                    return (True, resp.choices[0].message.content)
                else:
                    return (True, client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": content_payload}]).choices[0].message.content)
        except Exception as e:
            logging.error(f"API 调用失败 [{provider}/{model_name}]: {e}")
            return (False, str(e))

    success, content = await loop.run_in_executor(None, _call_api)

    # 【修复 11】通过布尔标志判断，而非字符串前缀
    if not success:
        print(f"❌ API 调用失败: {content}")
        show_toast("解析失败", "网络错误，任务已存入队列等待自动重试！")
        if action_type != "retry":
            payload = json.dumps({"text": text_content, "img": img_path, "audio": audio_path, "video": video_path})
            conn = get_db_conn()
            try:
                conn.execute("INSERT INTO retry_queue (provider, model, payload_json) VALUES (?, ?, ?)", (provider, model_name, payload))
                conn.commit()
            finally:
                conn.close()
        return False

    try:
        # ── 第一阶段：原始文本清洗 ──────────────────────────────────────
        raw = content.strip()
        # 剥离所有 fence 变体：```json  ```JSON  ``` 等
        raw = re.sub(r'```[A-Za-z]*\s*', '', raw).strip()
        # 提取第一个完整 {} 块，兼容 Claude/GPT 在 JSON 前后附加说明文字
        _outer = re.search(r'\{.*\}', raw, re.DOTALL)
        raw_json = _outer.group() if _outer else raw
        # 兼容 Kimi/OpenRouter 偶发 [{...}] 数组格式
        if raw_json.strip().startswith('['):
            _inner = re.search(r'\{.*\}', raw_json, re.DOTALL)
            raw_json = _inner.group() if _inner else raw_json

        # ── 第二阶段：字符级修复（状态机，一次遍历）────────────────────
        def _sanitize_json_string(s):
            """
            在 JSON 字符串值内部修复所有非法字符，结构层（键名、括号、逗号）不受影响。
            处理顺序（优先级由高到低）：
              1. \\ 合法转义序列 → 原样保留
              2. \ + 换行/空格（AI 续行符）→ 折叠为单个空格
              3. \ + 非法字符（\* \- \( \) 等 Markdown 转义）→ 去掉反斜杠
              4. 裸控制字符（换行/制表符等）→ 转为合法 \n \t 等
              5. 裸双引号（字符串内未转义 "）→ 前瞻判断，非闭合则转为 \"
            """
            _CTRL = {'\n': '\\n', '\r': '\\r', '\t': '\\t',
                     '\b': '\\b', '\f': '\\f'}
            # JSON 标准合法转义字符集
            _LEGAL_ESC = set('"\\/ b f n r t u')
            result = []
            in_string = False
            i = 0
            while i < len(s):
                c = s[i]

                if c == '\\' and in_string:
                    nxt = s[i + 1] if i + 1 < len(s) else ''
                    if nxt == '\n' or (nxt == '\r' and i + 2 < len(s) and s[i + 2] == '\n'):
                        # 规则2：续行符，折叠为空格
                        result.append(' ')
                        i += 2 if nxt == '\n' else 3
                        # 跳过续行后的缩进空格
                        while i < len(s) and s[i] in ' \t':
                            i += 1
                        continue
                    if nxt and nxt not in _LEGAL_ESC:
                        # 规则3：非法转义，去掉反斜杠只保留字符
                        result.append(nxt)
                        i += 2
                        continue
                    # 规则1：合法转义，原样保留两个字符
                    result.append(c)
                    if nxt:
                        result.append(nxt)
                        i += 2
                    else:
                        i += 1
                    continue

                if c == '"':
                    if not in_string:
                        in_string = True
                        result.append(c)
                    else:
                        # 规则5：前瞻判断是否为合法闭合引号
                        j = i + 1
                        while j < len(s) and s[j] in ' \t\r\n':
                            j += 1
                        if j >= len(s) or s[j] in ':,}]':
                            in_string = False
                            result.append(c)
                        else:
                            result.append('\\"')
                    i += 1
                    continue

                if in_string and ord(c) < 0x20:
                    # 规则4：裸控制字符
                    result.append(_CTRL.get(c, f'\\u{ord(c):04x}'))
                    i += 1
                    continue

                result.append(c)
                i += 1

            return ''.join(result)

        raw_json = _sanitize_json_string(raw_json)

        # ── 第三阶段：JSON 解析，带末尾截断兜底 ────────────────────────
        def _try_parse(s):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                pass
            # 尝试补全末尾：统计未闭合引号决定是否补 "
            _q = sum(1 for m in re.finditer(r'(?<!\\)"', s))
            tail = '"' if _q % 2 == 1 else ''
            # 统计未闭合大括号层数
            _depth = s.count('{') - s.count('}')
            tail += '}' * max(_depth, 1)
            try:
                return json.loads(s.rstrip() + tail)
            except json.JSONDecodeError:
                # 最后兜底：强制截断到最后一个完整键值对后补全
                _last = max(s.rfind(','), s.rfind('{'))
                if _last > 0:
                    return json.loads(s[:_last].rstrip().rstrip(',') + '}')
                raise

        data = _try_parse(raw_json)

        # ── 第四阶段：字段类型规范化 ─────────────────────────────────────
        def _flatten_to_md(v, depth=0):
            """将任意嵌套结构展平为 Markdown 字符串"""
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                parts = []
                for item in v:
                    if isinstance(item, dict):
                        parts.append("- " + "　".join(f"**{ik}**：{iv}" for ik, iv in item.items()))
                    else:
                        parts.append(f"- {item}")
                return "\n".join(parts)
            if isinstance(v, dict):
                parts = []
                for k, val in v.items():
                    prefix = "##" if depth == 0 else "###"
                    parts.append(f"{prefix} {k}\n{_flatten_to_md(val, depth + 1)}")
                return "\n\n".join(parts)
            return str(v)

        # analysis 字段：dict/list → Markdown 字符串
        if not isinstance(data.get("analysis"), str):
            data["analysis"] = _flatten_to_md(data.get("analysis", ""))

        # core_word / original_text：非字符串 → 强制转字符串
        for _f in ("core_word", "original_text"):
            if _f in data and not isinstance(data[_f], str):
                data[_f] = str(data[_f])

        # ── 第五阶段：写入 ────────────────────────────────────────────────
        save_atomic_note(data, os.path.basename(img_path) if img_path else None,
                         os.path.basename(audio_path) if audio_path else None,
                         source=provider.upper(), model_used=model_name,
                         video_name=os.path.basename(video_path) if video_path else None)
        return True
    except Exception as e:
        logging.error(f"JSON 解析失败 [{provider}]: {e}\n{content}")
        print(f"❌ JSON 解析失败: {e}\n{content}")
        if action_type != "retry":
            payload = json.dumps({"text": text_content, "img": img_path, "audio": audio_path, "video": video_path})
            conn = get_db_conn()
            try:
                conn.execute("INSERT INTO retry_queue (provider, model, payload_json) VALUES (?, ?, ?)", (provider, model_name, payload))
                conn.commit()
            finally:
                conn.close()
        return False

# ======================= 🎮 同步捕获引擎与长按逻辑修复 (修复 1, 3, 5) =======================

def get_active_monitor_bbox():
    """【修复 5】智能获取鼠标所在屏幕的坐标边界"""
    x, y = pyautogui.position()
    with mss.mss() as sct:
        for monitor in sct.monitors[1:]:
            if monitor["left"] <= x <= monitor["left"] + monitor["width"] and \
               monitor["top"] <= y <= monitor["top"] + monitor["height"]:
                return monitor
        return sct.monitors[1]

def handle_sync_capture(slot_config, action_type):
    """【修复 1, 3】同步阻塞主线程进行完美的物理设备捕获，捕获完毕后释放到异步 API 队列"""
    provider = slot_config.get("provider", "openrouter")
    model    = slot_config.get("model")
    hotkey   = slot_config.get("key")

    img_path = None; audio_path = None; text_content = None; video_path = None
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    if action_type == "clipboard":
        image = ImageGrab.grabclipboard()
        # 【修复 IV】grabclipboard() 返回类型为 Image.Image | list[str] | None；
        # 原代码 if image: 在用户复制文件时返回非空 list，真值判断通过，
        # 随后 list.save() 触发 AttributeError 崩溃热键回调线程。
        # 修正：严格用 isinstance 区分图像对象；save() 加 try/except 防磁盘异常崩溃。
        if isinstance(image, Image.Image):
            img_path = os.path.join(ASSETS_PATH, f"Img_Clip_{timestamp}.png")
            try:
                image.save(img_path, "PNG")
            except Exception as e:
                logging.error(f"剪贴板图片保存失败: {e}")
                return
        else:
            text_content = pyperclip.paste()
            if not text_content or not text_content.strip(): return

    elif action_type == "video_retro":
        video_path = obs_dashcam.save_and_poll_replay()
        if not video_path: return
        try:
            _vr_dest = os.path.join(ASSETS_PATH, os.path.basename(video_path))
            shutil.copy2(video_path, _vr_dest)
            if not OBS_KEEP_SOURCE_FILE:
                try: os.remove(video_path)
                except Exception: pass
            video_path = _vr_dest
        except Exception as e:
            logging.error(f"video_retro 文件复制至 ASSETS_PATH 失败 [{video_path}]: {e}")
            return

    elif action_type in ["av_fast", "av_deep", "audio_only", "video_hold", "vision_only"]:
        is_hold_action = action_type in ["av_fast", "av_deep", "audio_only", "video_hold"]
        if DEBUG_MODE: print(f"[DEBUG] action_type={action_type}, is_hold_action={is_hold_action}")

        with mss.mss() as sct:
            monitor = get_active_monitor_bbox()

            if action_type in ["av_fast", "av_deep", "vision_only"]:
                img_path = os.path.join(ASSETS_PATH, f"Img_{timestamp}.png")
                # 【新增】若用户已用 Alt+R 选定区域，优先截取选定区域
                # 【修复 I.2】加锁快照 _selected_region，防止读取时被 toggle_region_select 并发写入
                with _selected_region_lock:
                    _region_snapshot = _selected_region
                if _region_snapshot and ENABLE_REGION_SELECT:
                    lft, top, wid, hgt = _region_snapshot
                    shot = sct.grab({"left": lft, "top": top, "width": wid, "height": hgt})
                    Image.frombytes("RGB", shot.size, shot.rgb).save(img_path)
                else:
                    # 【修复 VIII】monitor 来自不同 mss() 实例，.index() 在显示器配置
                    # 变化时会抛 ValueError；改用 try/except 回退到第一块显示器
                    try:
                        mon_idx = sct.monitors.index(monitor)
                    except ValueError:
                        mon_idx = 1
                    if mon_idx >= len(sct.monitors): mon_idx = 1
                    sct.shot(mon=mon_idx, output=img_path)

            if is_hold_action:
                if action_type == "video_hold":
                    # 【修复】走 OBS 方案，硬件编码，音视频由 OBS 直接混合
                    _obs_file = obs_dashcam.record_while_held(hotkey)
                    if _obs_file:
                        # Obsidian 只能嵌入 vault 内文件，必须复制到 ASSETS_PATH
                        try:
                            _vh_dest = os.path.join(ASSETS_PATH, os.path.basename(_obs_file))
                            shutil.copy2(_obs_file, _vh_dest)
                            if not OBS_KEEP_SOURCE_FILE:
                                try: os.remove(_obs_file)
                                except Exception: pass
                            video_path = _vh_dest
                        except Exception as e:
                            logging.error(f"video_hold 文件复制至 ASSETS_PATH 失败: {e}")
                            show_toast("⚠️ 复制失败", str(e))

                    else:
                        show_toast("⚠️ 录制失败", "OBS 未返回录制文件，请检查 OBS 连接与音频设置")                        
                else:
                    # av_fast / av_deep / audio_only：纯音频录制
                    show_toast("🔴 正在录制", f"松开 [{hotkey}] 结束录制...", duration=2)
                    try:
                        import pyaudiowpatch as _paw
                        if _loopback_dev_cache is None:
                            raise RuntimeError("录音设备未初始化，请检查启动日志")
                        _loopback_dev = _loopback_dev_cache
                        _pa = _paw.PyAudio()
                        try:
                            _sr  = int(_loopback_dev["defaultSampleRate"])
                            _ch  = int(_loopback_dev["maxInputChannels"])
                            _buf = max(512, int(_sr * 0.01))
                            _frames = []
                            _stream = _pa.open(
                                format=_paw.paFloat32,
                                channels=_ch,
                                rate=_sr,
                                input=True,
                                input_device_index=_loopback_dev["index"],
                                frames_per_buffer=_buf
                            )
                            _record_start = time.time()
                            while True:
                                _frames.append(_stream.read(_buf, exception_on_overflow=False))
                                _elapsed = time.time() - _record_start
                                if _elapsed > CIRCUIT_BREAKER_LIMIT:
                                    show_toast("⚠️ 触发断路器", f"达到{CIRCUIT_BREAKER_LIMIT}秒录制上限，强制停止！")
                                    break
                                if _elapsed > 0.5 and not keyboard.is_pressed(hotkey):
                                    break
                            _stream.stop_stream()
                            _stream.close()
                        finally:
                            _pa.terminate()

                        if _frames:
                            _raw = b"".join(_frames)
                            _audio_np = np.frombuffer(_raw, dtype=np.float32).reshape(-1, _ch)
                            if _audio_np.shape[0] > _sr * 0.3:
                                audio_path = os.path.join(ASSETS_PATH, f"Aud_{timestamp}.wav")
                                sf.write(audio_path, _audio_np, _sr, subtype='PCM_24')
                            else:
                                print("⚠️ 录音数据过短，跳过保存")
                        else:
                            print("⚠️ 未采集到任何音频数据")
                    except Exception as e:
                        import traceback
                        logging.error(f"捕获设备错误: {e}")
                        print(f"捕获设备错误: {e}")
                        print(traceback.format_exc())
                        show_toast("⚠️ 录音失败", str(e))
                                                                            # 【修复 III.1】将预览确认与 API 派发移入 daemon 线程：
    # 原代码直接在调用方线程执行，对长按动作会冻结主轮询循环最多 35 秒，
    # 对单次触发动作会冻结键盘回调线程；移入 daemon 线程后两者均立即返回
    _p, _m, _at = provider, model, action_type
    _tc, _ip, _ap, _vp = text_content, img_path, audio_path, video_path

    # 【修复】audio_only / av_fast / av_deep 模式下没录到音频，拦截空请求
    if _at in {"audio_only", "av_fast", "av_deep"} and _ap is None:
        show_toast("⚠️ 录音为空", "未录到有效音频，请重试")
        return

    def _dispatch():
        if ENABLE_CAPTURE_PREVIEW and _ip and os.path.exists(_ip):
            if not show_capture_preview(_ip):
                try: os.remove(_ip)
                except Exception as e: logging.error(f"预览取消后截图文件清理失败 [{_ip}]: {e}")  # 【修复 IX】
                show_toast("已取消", "用户取消了本次截图发送")
                return
        asyncio.run_coroutine_threadsafe(
            async_universal_api_call(_p, _m, _at, _tc, _ip, _ap, _vp),
            event_loop
        )
    threading.Thread(target=_dispatch, daemon=True).start()

# ================= 🌟 逆向情景生成：全自动 Galgame 引擎 (深渊天花板方案) =================
def generate_visual_novel():
    if not ENABLE_VN_GALGAME_GENERATOR: return
    print("\n🌙 【妃爱の午夜工坊】正在为你生成专属 Galgame 复习剧本...")

    conn = get_db_conn()
    try:
        words = conn.execute("SELECT core_word FROM vocab_memory WHERE date(timestamp,'localtime') = date('now','localtime') LIMIT 20").fetchall()
    finally:
        conn.close()

    if len(words) < 5: return

    vocab_list = ", ".join([w[0] for w in words])
    prompt = f"你是Galgame剧本家。使用生词库：{vocab_list} 写一段2分钟悬疑/恋爱剧本。输出JSON数组:[{{\"char\":\"角色\",\"dia\":\"带生词的源语言台词\",\"trans\":\"中文\"}}]"

    try:
        script_data = json.loads(genai.GenerativeModel("gemini-2.0-flash-exp", generation_config={"response_mime_type": "application/json"}).generate_content(prompt).text)
        if not isinstance(script_data, list):
            raise ValueError(f"AI 返回 JSON 结构不符合预期（非列表）: {type(script_data)}")

        os.makedirs(VN_OUTPUT_DIR, exist_ok=True)        # 【修复 12】将局部变量重命名为 html_content，避免遮蔽顶部 html_module 导入
        html_content  = "<html><head><meta charset='utf-8'><title>妃爱の专属复习剧场</title><style>body{background:#222;color:white;font-family:sans-serif;text-align:center;padding:50px;} .box{border:2px solid pink;padding:20px;border-radius:10px;margin:20px auto;width:80%;font-size:24px;}</style></head><body>"
        html_content += f"<h1>🌙 今日复习剧场 ({datetime.now().strftime('%Y-%m-%d')})</h1>"

        for line in script_data:
            # 【修复 12】使用 html_module.escape 对 AI 返回内容转义，防止 XSS 注入
            char_safe  = html_module.escape(str(line.get('char',  '')))
            dia_safe   = html_module.escape(str(line.get('dia',   '')))
            trans_safe = html_module.escape(str(line.get('trans', '')))
            # SD/VITS 多媒体集成功能尚未实现，如需图片/语音嵌入请在此处添加对应 API 调用
            html_content += f"<div class='box'><b>{char_safe}</b>: {dia_safe}<br><span style='font-size:16px;color:#aaa;'>{trans_safe}</span></div>"

        # 【修复 9】使用 with 语句确保文件在任何情况下都被正确关闭
        output_file = os.path.join(VN_OUTPUT_DIR, f"Review_{datetime.now().strftime('%Y%m%d')}.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content + "</body></html>")
        show_toast("Galgame 炼成", "专属复习剧本已生成！")
    except Exception as e:
        logging.error(f"Galgame 生成失败: {e}")
        print(f"❌ Galgame 生成失败: {e}")

# ======================= 🚀 守护进程与启动控制台 =======================

def cron_jobs():
    """处理重试队列与定时任务"""
    while True:
        # 【修复 20】使用 try/finally 保证连接在任何情况下都被关闭，防止连接泄漏
        conn = get_db_conn()
        try:
            failed_tasks = conn.execute(f"SELECT id, provider, model, payload_json FROM retry_queue WHERE retry_count < {RETRY_MAX_ATTEMPTS}").fetchall()
            for task in failed_tasks:
                try:
                    p = json.loads(task[3])
                    _tid = task[0]
                    future = asyncio.run_coroutine_threadsafe(
                        async_universal_api_call(task[1], task[2], "retry", p.get("text"), p.get("img"), p.get("audio"), p.get("video")),
                        event_loop
                    )
                    # 【修复 IV.1】移除 future.result(timeout=120) 阻塞：原代码每个任务最多等待
                    # 2 分钟，多个任务时 cron 线程长时间卡死，定时任务严重失准。
                    # 改用 add_done_callback，协程完成后回调函数负责更新队列状态。
                    def _on_retry_done(fut, tid=_tid):
                        try:
                            result = fut.result()
                        except Exception:
                            result = False
                        # 【修复 VII】原代码直接在 asyncio 事件循环线程内执行阻塞的 SQLite 操作；
                        # add_done_callback 的回调由事件循环线程触发，SQLite 阻塞期间整个事件循环
                        # 无法调度其他任何协程。改为在独立 daemon 线程中执行 DB 操作。
                        def _db_update():
                            try:
                                _c = get_db_conn()
                                try:
                                    if result:
                                        _c.execute("DELETE FROM retry_queue WHERE id=?", (tid,))
                                    else:
                                        _c.execute("UPDATE retry_queue SET retry_count = retry_count + 1 WHERE id=?", (tid,))
                                    _c.commit()
                                finally:
                                    _c.close()
                            except Exception as ex:
                                logging.error(f"cron_jobs 重试回调异常 [id={tid}]: {ex}")
                        threading.Thread(target=_db_update, daemon=True).start()
                    future.add_done_callback(_on_retry_done)
                except Exception as e:
                    # 【修复 VI】原为裸 except Exception: 无日志，无法判断是 JSON 损坏还是事件循环异常
                    logging.error(f"cron_jobs 任务解析或投递失败 [id={task[0]}]: {e}")
                    conn.execute("UPDATE retry_queue SET retry_count = retry_count + 1 WHERE id=?", (task[0],))
                    conn.commit()  # 立即提交，防止外层异常触发 finally: conn.close() 时此更新被回滚
            conn.execute(f"DELETE FROM retry_queue WHERE retry_count >= {RETRY_MAX_ATTEMPTS}")
            conn.commit()
        except Exception as e:
            logging.error(f"cron_jobs 重试队列处理异常: {e}")
        finally:
            conn.close()

        # 夜间自动生成 Galgame
        if datetime.now().hour == 23 and datetime.now().minute == 50:
            generate_visual_novel()
            time.sleep(60)

        # 【新增】间隔复习提醒：每天 09:00 后触发一次，检查 3/7/14 天前的词条
        today_str = datetime.now().strftime('%Y-%m-%d')
        if _last_reminder_date["date"] != today_str and datetime.now().hour >= 9:
            _last_reminder_date["date"] = today_str
            reminder_conn = get_db_conn()
            try:
                with _template_lock:
                    current_lang = ACTIVE_TEMPLATE
                for interval in [3, 7, 14]:
                    due = reminder_conn.execute(
                        "SELECT core_word FROM word_stats WHERE lang=? AND date(first_seen,'localtime')=date('now','localtime',?) LIMIT 5",  # 【修复 V】应基于 first_seen（初次学习日）而非 last_seen（最近捕获日）
                        (current_lang, f"-{interval} days")
                    ).fetchall()
                    if due:
                        words_str = "、".join([w[0] for w in due])
                        show_toast(f"📅 {interval}天复习提醒", f"建议复习: {words_str[:60]}")
                        time.sleep(2)
            except Exception as e:
                logging.error(f"间隔复习提醒异常: {e}")
            finally:
                reminder_conn.close()

        time.sleep(30)

# ======================= 启动验证与控制台 =======================

validate_paths()
validate_api_keys()

print("=========================================================================")
print(" 🚀 全武装系统 (VocabChan) ")
print("=========================================================================")
print(f"🌐 目标语言: {TARGET_LANGUAGE} | 🎯 默认模板: {LANGUAGE_TEMPLATES[ACTIVE_TEMPLATE]['name']}")
print(f"🛡️ 破产断路器: {CIRCUIT_BREAKER_LIMIT}秒 | 🎥 OBS 0负载回溯: {'【就绪】' if obs_dashcam.enabled else '【离线】'}")
print("=========================================================================")
print("📌 新增热键: Alt+S=搜索词条 | Alt+Q=学习统计 | Alt+E=导出CSV | Alt+W=导出TXT | Alt+B=批量导入 | Alt+R=区域选择")
print("=========================================================================")

# 启动后台异步事件循环与 Cron Daemon
event_loop = asyncio.new_event_loop()
threading.Thread(target=event_loop.run_forever, daemon=True).start()
threading.Thread(target=cron_jobs, daemon=True).start()

# 注册语言切换
for shortcut in TEMPLATE_SWITCH_HOTKEYS:
    keyboard.add_hotkey(shortcut["key"], lambda k=shortcut["lang"]: set_active_template(k))

# 【修复 3】拆分热键注册逻辑：
# 原代码将 OPENROUTER_HOTKEYS 混入同一循环，但其条目不存在于 SLOTS_CONFIG 中，
# 导致列表推导结果为空列表，[0] 取首元素触发 IndexError，程序在启动阶段崩溃
# ── 注册常规单次触发热键 ──
for slot in SLOTS_CONFIG["clipboard"] + SLOTS_CONFIG["vision_only"] + SLOTS_CONFIG["video_retro"]:
    action = [k for k, v in SLOTS_CONFIG.items() if slot in v][0]
    keyboard.add_hotkey(slot["key"], lambda s=slot, a=action: handle_sync_capture(s, a))

# ── 长按动作集合，与 SLOTS_CONFIG 保持一致 ──
_HOLD_ACTIONS = {"av_fast", "av_deep", "audio_only", "video_hold"}

# ── 单独注册 OpenRouter 热键，补全缺失的 provider 字段 ──
_or_hold_slots = []
for or_slot in OPENROUTER_HOTKEYS:
    _s = {"key": or_slot["key"], "provider": "openrouter", "model": or_slot["model"]}
    _a = or_slot.get("action", "vision_only")
    if _a in _HOLD_ACTIONS:
        _or_hold_slots.append((_a, _s))
    else:
        keyboard.add_hotkey(or_slot["key"], lambda s=_s, a=_a: handle_sync_capture(s, a))

# 【新增】功能扩展热键注册
keyboard.add_hotkey("alt+s", lambda: search_vocab(pyperclip.paste() or None))
keyboard.add_hotkey("alt+q", show_learning_stats)
keyboard.add_hotkey("alt+e", export_vocab_csv)
keyboard.add_hotkey("alt+w", export_vocab_txt)
keyboard.add_hotkey("alt+b", batch_import_from_clipboard)
if ENABLE_REGION_SELECT:
    keyboard.add_hotkey("alt+r", toggle_region_select)

# 对于长按动作，不注册 hotkey，而是放入主线程轮询，防止 keyboard 库的长按判定 BUG
hold_slots = []
for action in _HOLD_ACTIONS: hold_slots.extend([ (action, slot) for slot in SLOTS_CONFIG[action] ])
hold_slots.extend(_or_hold_slots)

while True:
    while not _main_thread_ui_queue.empty():
        try:
            _main_thread_ui_queue.get_nowait()()
        except Exception as _e:
            logging.error(f"主线程 UI 任务执行异常: {_e}")
    for action, slot in hold_slots:
        if keyboard.is_pressed(slot["key"]):
            handle_sync_capture(slot, action)
            # 【修复】等待按键完全松开再继续，防止重复触发
            while keyboard.is_pressed(slot["key"]):
                time.sleep(0.01)
            time.sleep(0.2)  # 额外防抖
    time.sleep(0.01)