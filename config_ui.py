try:
    import customtkinter as ctk
except ImportError:
    raise ImportError("Missing dependency: customtkinter. Install with: pip install customtkinter")

import os
import re
import sys
import sqlite3
import csv
import json
import copy
import logging
import shutil
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
import httpx

from config import (
    API_KEYS, BASE_URLS, ASSETS_PATH, VOCAB_FOLDER, DB_PATH, LOG_PATH,
    PROXY_URL, CIRCUIT_BREAKER_LIMIT, VIDEO_FPS, OBS_WS_HOST, OBS_WS_PORT,
    OBS_WS_PASSWORD, OBS_WATCH_DIR, ENABLE_LOCAL_OCR, ENABLE_LOCAL_WHISPER,
    ENABLE_AUTONOMOUS_LISTENER, ENABLE_VN_GALGAME_GENERATOR,
    ENABLE_CAPTURE_PREVIEW, ENABLE_REGION_SELECT, VN_OUTPUT_DIR,
    ENABLE_TELDRIVE_UPLOAD, TELDRIVE_MOUNT_PATH, ENABLE_ANKI_MEDIA,
    TARGET_LANGUAGE, ACTIVE_TEMPLATE, SLOTS_CONFIG, OPENROUTER_HOTKEYS,
    TEMPLATE_SWITCH_HOTKEYS, LANGUAGE_TEMPLATES, ANALYSIS_SECTION_HEADERS,
    ANKI_BYPASS_PROXY, ANKI_DECK_NAME, ANKI_CONNECT_PORT,
    ANKI_SHOW_ORIGINAL_ON_BACK, ANKI_FRONT_CONTENT, ANKI_AUDIO_SIDE,
    OBS_AUTO_START_REPLAY_BUFFER, OBS_POLL_TIMEOUT, OBS_KEEP_SOURCE_FILE,
    RAG_RECENT_WORD_COUNT, RETRY_MAX_ATTEMPTS, DEBUG_MODE,
)

# ================= UI Translation System =================

_UI_STRINGS = {
    "English": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Control Panel",
        "sec_workflow": "Workflow", "sec_customize": "Customize", "sec_engine": "Engine",
        "nav_console": "▣ Console", "nav_memory": "⌕ Memory", "nav_data": "↕ Data",
        "nav_prompts": "◈ Prompts", "nav_hotkeys": "⌨ Hotkeys", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ Overview", "nav_ai_models": "◆ AI Models",
        "nav_behavior": "◉ Behavior", "nav_paths": "⊞ Paths", "nav_database": "▨ Database",
        "nav_logs": "☰ Logs", "nav_lang": "⟳ Language",
        "title_console": "Dashboard", "title_memory": "Memory Search",
        "title_data": "Data Bridge", "title_prompts": "AI Persona & Focus",
        "title_api": "AI Engine Gateway", "title_behavior": "Behavior & Limits",
        "title_database": "Storage Maintenance", "title_hotkeys": "Hotkeys Hub",
        "title_logs": "Logs & Retry Queue", "title_obs": "OBS Connection",
        "title_anki": "Anki Integration", "title_paths": "Paths & Network",
        "title_overview": "Global Config Snapshot",
        "btn_save": "▣ Save", "btn_delete": "✕ Delete", "btn_refresh": "↺ Refresh",
        "btn_add": "+ Add", "btn_browse": "⊞ Browse", "btn_cancel": "Cancel",
        "btn_confirm": "✓ Confirm", "btn_test": "◌ Test",
        "warn_unsaved": "Warning",
        "warn_unsaved_msg": "Unsaved changes in:\n{tabs}\n\nForce quit?",
        "warn_corrupt_config": "▲ Config File Damaged",
        "warn_corrupt_msg": "Runtime config load failed, reverted to defaults.\n\nError: {err}\n\nPath: {path}\n\nSuggestion: check file integrity or delete and reconfigure.",
        "toast_saved": "✓ Settings saved", "lbl_ui_lang": "UI Language:",
    },
    "简体中文": {
        "app_title": "Izumi Omni-Arsenal V5.0 — 控制面板",
        "sec_workflow": "常用工作流", "sec_customize": "定制", "sec_engine": "底层引擎",
        "nav_console": "▣ 控制台", "nav_memory": "⌕ 记忆", "nav_data": "↕ 数据",
        "nav_prompts": "◈ 提示词", "nav_hotkeys": "⌨ 快捷键", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ 总览", "nav_ai_models": "◆ AI 模型",
        "nav_behavior": "◉ 行为", "nav_paths": "⊞ 路径", "nav_database": "▨ 数据库",
        "nav_logs": "☰ 日志", "nav_lang": "⟳ 语言",
        "title_console": "仪表板", "title_memory": "记忆检索",
        "title_data": "数据桥", "title_prompts": "AI 人设与焦点",
        "title_api": "AI 引擎网关", "title_behavior": "行为与限制",
        "title_database": "存储维护", "title_hotkeys": "快捷键中枢",
        "title_logs": "日志与重试队列", "title_obs": "OBS 连接",
        "title_anki": "Anki 集成", "title_paths": "路径与网络",
        "title_overview": "全局配置快照",
        "btn_save": "▣ 保存", "btn_delete": "✕ 删除", "btn_refresh": "↺ 刷新",
        "btn_add": "+ 新增", "btn_browse": "⊞ 浏览", "btn_cancel": "取消",
        "btn_confirm": "✓ 确认", "btn_test": "◌ 测试",
        "warn_unsaved": "警告",
        "warn_unsaved_msg": "以下模块有未保存的修改：\n{tabs}\n\n确认强行退出？",
        "warn_corrupt_config": "▲ 配置文件损坏",
        "warn_corrupt_msg": "运行时配置读取失败，已回退至全部默认值。\n\n错误：{err}\n\n路径：{path}\n\n建议：检查文件完整性，或删除后重新配置。",
        "toast_saved": "✓ 设置已保存", "lbl_ui_lang": "界面语言：",
    },
    "日本語": {
        "app_title": "Izumi Omni-Arsenal V5.0 — コントロールパネル",
        "sec_workflow": "ワークフロー", "sec_customize": "カスタマイズ", "sec_engine": "エンジン",
        "nav_console": "▣ コンソール", "nav_memory": "⌕ メモリ", "nav_data": "↕ データ",
        "nav_prompts": "◈ プロンプト", "nav_hotkeys": "⌨ ホットキー", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ 概要", "nav_ai_models": "◆ AIモデル",
        "nav_behavior": "◉ 動作設定", "nav_paths": "⊞ パス", "nav_database": "▨ データベース",
        "nav_logs": "☰ ログ", "nav_lang": "⟳ 言語",
        "title_console": "ダッシュボード", "title_memory": "メモリ検索",
        "title_data": "データ移動", "title_prompts": "AIペルソナ・フォーカス",
        "title_api": "AIエンジンゲートウェイ", "title_behavior": "動作・制限",
        "title_database": "ストレージ管理", "title_hotkeys": "ホットキー設定",
        "title_logs": "ログ・リトライ", "title_obs": "OBS接続",
        "title_anki": "Anki連携", "title_paths": "パス・ネットワーク",
        "title_overview": "グローバル設定スナップショット",
        "btn_save": "▣ 保存", "btn_delete": "✕ 削除", "btn_refresh": "↺ 更新",
        "btn_add": "+ 追加", "btn_browse": "⊞ 参照", "btn_cancel": "キャンセル",
        "btn_confirm": "✓ 確認", "btn_test": "◌ テスト",
        "warn_unsaved": "警告",
        "warn_unsaved_msg": "未保存の変更があります：\n{tabs}\n\n強制終了しますか？",
        "warn_corrupt_config": "▲ 設定ファイル破損",
        "warn_corrupt_msg": "実行時設定の読み込みに失敗しました。デフォルト値に戻しました。\n\nエラー：{err}\n\nパス：{path}",
        "toast_saved": "✓ 設定を保存しました", "lbl_ui_lang": "UI言語：",
    },
    "Español": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Panel de Control",
        "sec_workflow": "Flujo de trabajo", "sec_customize": "Personalizar", "sec_engine": "Motor",
        "nav_console": "▣ Consola", "nav_memory": "⌕ Memoria", "nav_data": "↕ Datos",
        "nav_prompts": "◈ Prompts", "nav_hotkeys": "⌨ Atajos", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ General", "nav_ai_models": "◆ Modelos IA",
        "nav_behavior": "◉ Comportamiento", "nav_paths": "⊞ Rutas", "nav_database": "▨ BD",
        "nav_logs": "☰ Registros", "nav_lang": "⟳ Idioma",
        "title_console": "Panel", "title_memory": "Búsqueda", "title_data": "Datos",
        "title_prompts": "Perfil IA", "title_api": "Gateway IA", "title_behavior": "Comportamiento",
        "title_database": "Mantenimiento", "title_hotkeys": "Atajos",
        "title_logs": "Registros", "title_obs": "Conexión OBS",
        "title_anki": "Integración Anki", "title_paths": "Rutas y red",
        "title_overview": "Config Snapshot",
        "btn_save": "▣ Guardar", "btn_delete": "✕ Eliminar", "btn_refresh": "↺ Actualizar",
        "btn_add": "+ Añadir", "btn_browse": "⊞ Examinar", "btn_cancel": "Cancelar",
        "btn_confirm": "✓ Confirmar", "btn_test": "◌ Probar",
        "warn_unsaved": "Advertencia",
        "warn_unsaved_msg": "Cambios sin guardar en:\n{tabs}\n\n¿Forzar salida?",
        "warn_corrupt_config": "▲ Config dañada",
        "warn_corrupt_msg": "Error al cargar config. Valores predeterminados usados.\n\nError: {err}\n\nRuta: {path}",
        "toast_saved": "✓ Config guardada", "lbl_ui_lang": "Idioma UI:",
    },
    "Français": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Panneau de contrôle",
        "sec_workflow": "Flux de travail", "sec_customize": "Personnaliser", "sec_engine": "Moteur",
        "nav_console": "▣ Console", "nav_memory": "⌕ Mémoire", "nav_data": "↕ Données",
        "nav_prompts": "◈ Prompts", "nav_hotkeys": "⌨ Raccourcis", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ Aperçu", "nav_ai_models": "◆ Modèles IA",
        "nav_behavior": "◉ Comportement", "nav_paths": "⊞ Chemins", "nav_database": "▨ BdD",
        "nav_logs": "☰ Journaux", "nav_lang": "⟳ Langue",
        "title_console": "Tableau de bord", "title_memory": "Recherche mémoire",
        "title_data": "Pont de données", "title_prompts": "Persona IA",
        "title_api": "Passerelle IA", "title_behavior": "Comportement",
        "title_database": "Maintenance", "title_hotkeys": "Raccourcis",
        "title_logs": "Journaux", "title_obs": "Connexion OBS",
        "title_anki": "Intégration Anki", "title_paths": "Chemins et réseau",
        "title_overview": "Instantané de config",
        "btn_save": "▣ Enregistrer", "btn_delete": "✕ Supprimer", "btn_refresh": "↺ Actualiser",
        "btn_add": "+ Ajouter", "btn_browse": "⊞ Parcourir", "btn_cancel": "Annuler",
        "btn_confirm": "✓ Confirmer", "btn_test": "◌ Tester",
        "warn_unsaved": "Avertissement",
        "warn_unsaved_msg": "Modifications non enregistrées dans :\n{tabs}\n\nForcer la fermeture?",
        "warn_corrupt_config": "▲ Config endommagée",
        "warn_corrupt_msg": "Échec du chargement de la config.\n\nErreur: {err}\n\nChemin: {path}",
        "toast_saved": "✓ Paramètres enregistrés", "lbl_ui_lang": "Langue UI :",
    },
    "Deutsch": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Steuerfeld",
        "sec_workflow": "Workflow", "sec_customize": "Anpassen", "sec_engine": "Engine",
        "nav_console": "▣ Konsole", "nav_memory": "⌕ Speicher", "nav_data": "↕ Daten",
        "nav_prompts": "◈ Prompts", "nav_hotkeys": "⌨ Tastenkürzel", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ Übersicht", "nav_ai_models": "◆ KI-Modelle",
        "nav_behavior": "◉ Verhalten", "nav_paths": "⊞ Pfade", "nav_database": "▨ Datenbank",
        "nav_logs": "☰ Protokoll", "nav_lang": "⟳ Sprache",
        "title_console": "Dashboard", "title_memory": "Speichersuche",
        "title_data": "Datenbrücke", "title_prompts": "KI-Persona",
        "title_api": "KI-Gateway", "title_behavior": "Verhalten",
        "title_database": "Wartung", "title_hotkeys": "Tastenkürzel",
        "title_logs": "Protokoll", "title_obs": "OBS-Verbindung",
        "title_anki": "Anki-Integration", "title_paths": "Pfade und Netzwerk",
        "title_overview": "Konfigurationsübersicht",
        "btn_save": "▣ Speichern", "btn_delete": "✕ Löschen", "btn_refresh": "↺ Aktualisieren",
        "btn_add": "+ Hinzufügen", "btn_browse": "⊞ Durchsuchen", "btn_cancel": "Abbrechen",
        "btn_confirm": "✓ Bestätigen", "btn_test": "◌ Testen",
        "warn_unsaved": "Warnung",
        "warn_unsaved_msg": "Nicht gespeicherte Änderungen in:\n{tabs}\n\nErzwungen beenden?",
        "warn_corrupt_config": "▲ Konfiguration beschädigt",
        "warn_corrupt_msg": "Konfiguration konnte nicht geladen werden.\n\nFehler: {err}\n\nPfad: {path}",
        "toast_saved": "✓ Einstellungen gespeichert", "lbl_ui_lang": "UI-Sprache:",
    },
    "한국어": {
        "app_title": "Izumi Omni-Arsenal V5.0 — 제어판",
        "sec_workflow": "워크플로우", "sec_customize": "사용자 지정", "sec_engine": "엔진",
        "nav_console": "▣ 콘솔", "nav_memory": "⌕ 메모리", "nav_data": "↕ 데이터",
        "nav_prompts": "◈ 프롬프트", "nav_hotkeys": "⌨ 단축키", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ 개요", "nav_ai_models": "◆ AI 모델",
        "nav_behavior": "◉ 동작", "nav_paths": "⊞ 경로", "nav_database": "▨ DB",
        "nav_logs": "☰ 로그", "nav_lang": "⟳ 언어",
        "title_console": "대시보드", "title_memory": "메모리 검색",
        "title_data": "데이터 브리지", "title_prompts": "AI 페르소나",
        "title_api": "AI 게이트웨이", "title_behavior": "동작 및 제한",
        "title_database": "저장소 관리", "title_hotkeys": "단축키 설정",
        "title_logs": "로그", "title_obs": "OBS 연결",
        "title_anki": "Anki 연동", "title_paths": "경로 및 네트워크",
        "title_overview": "전역 설정 스냅샷",
        "btn_save": "▣ 저장", "btn_delete": "✕ 삭제", "btn_refresh": "↺ 새로고침",
        "btn_add": "+ 추가", "btn_browse": "⊞ 찾아보기", "btn_cancel": "취소",
        "btn_confirm": "✓ 확인", "btn_test": "◌ 테스트",
        "warn_unsaved": "경고",
        "warn_unsaved_msg": "저장되지 않은 변경 사항:\n{tabs}\n\n강제 종료하시겠습니까?",
        "warn_corrupt_config": "▲ 설정 파일 손상",
        "warn_corrupt_msg": "설정 로드 실패.\n\n오류: {err}\n\n경로: {path}",
        "toast_saved": "✓ 설정이 저장되었습니다", "lbl_ui_lang": "UI 언어:",
    },
    "Italiano": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Pannello di controllo",
        "sec_workflow": "Flusso di lavoro", "sec_customize": "Personalizza", "sec_engine": "Motore",
        "nav_console": "▣ Console", "nav_memory": "⌕ Memoria", "nav_data": "↕ Dati",
        "nav_prompts": "◈ Prompt", "nav_hotkeys": "⌨ Scorciatoie", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ Panoramica", "nav_ai_models": "◆ Modelli IA",
        "nav_behavior": "◉ Comportamento", "nav_paths": "⊞ Percorsi", "nav_database": "▨ DB",
        "nav_logs": "☰ Log", "nav_lang": "⟳ Lingua",
        "title_console": "Dashboard", "title_memory": "Ricerca memoria",
        "title_data": "Ponte dati", "title_prompts": "Persona IA",
        "title_api": "Gateway IA", "title_behavior": "Comportamento",
        "title_database": "Manutenzione", "title_hotkeys": "Scorciatoie",
        "title_logs": "Log", "title_obs": "Connessione OBS",
        "title_anki": "Integrazione Anki", "title_paths": "Percorsi e rete",
        "title_overview": "Snapshot configurazione",
        "btn_save": "▣ Salva", "btn_delete": "✕ Elimina", "btn_refresh": "↺ Aggiorna",
        "btn_add": "+ Aggiungi", "btn_browse": "⊞ Sfoglia", "btn_cancel": "Annulla",
        "btn_confirm": "✓ Conferma", "btn_test": "◌ Test",
        "warn_unsaved": "Attenzione",
        "warn_unsaved_msg": "Modifiche non salvate in:\n{tabs}\n\nForzare l'uscita?",
        "warn_corrupt_config": "▲ Config danneggiata",
        "warn_corrupt_msg": "Config non caricata.\n\nErrore: {err}\n\nPercorso: {path}",
        "toast_saved": "✓ Impostazioni salvate", "lbl_ui_lang": "Lingua UI:",
    },
    "Português": {
        "app_title": "Izumi Omni-Arsenal V5.0 — Painel de controle",
        "sec_workflow": "Fluxo de trabalho", "sec_customize": "Personalizar", "sec_engine": "Motor",
        "nav_console": "▣ Console", "nav_memory": "⌕ Memória", "nav_data": "↕ Dados",
        "nav_prompts": "◈ Prompts", "nav_hotkeys": "⌨ Atalhos", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ Visão geral", "nav_ai_models": "◆ Modelos IA",
        "nav_behavior": "◉ Comportamento", "nav_paths": "⊞ Caminhos", "nav_database": "▨ BD",
        "nav_logs": "☰ Logs", "nav_lang": "⟳ Idioma",
        "title_console": "Painel", "title_memory": "Pesquisa de memória",
        "title_data": "Ponte de dados", "title_prompts": "Persona IA",
        "title_api": "Gateway IA", "title_behavior": "Comportamento",
        "title_database": "Manutenção", "title_hotkeys": "Atalhos",
        "title_logs": "Logs", "title_obs": "Conexão OBS",
        "title_anki": "Integração Anki", "title_paths": "Caminhos e rede",
        "title_overview": "Instantâneo de config",
        "btn_save": "▣ Salvar", "btn_delete": "✕ Excluir", "btn_refresh": "↺ Atualizar",
        "btn_add": "+ Adicionar", "btn_browse": "⊞ Procurar", "btn_cancel": "Cancelar",
        "btn_confirm": "✓ Confirmar", "btn_test": "◌ Testar",
        "warn_unsaved": "Aviso",
        "warn_unsaved_msg": "Alterações não salvas em:\n{tabs}\n\nForçar saída?",
        "warn_corrupt_config": "▲ Config danificada",
        "warn_corrupt_msg": "Falha ao carregar config.\n\nErro: {err}\n\nCaminho: {path}",
        "toast_saved": "✓ Configurações salvas", "lbl_ui_lang": "Idioma UI:",
    },
    "العربية": {
        "app_title": "Izumi Omni-Arsenal V5.0 — لوحة التحكم",
        "sec_workflow": "سير العمل", "sec_customize": "تخصيص", "sec_engine": "المحرك",
        "nav_console": "▣ وحدة التحكم", "nav_memory": "⌕ الذاكرة", "nav_data": "↕ البيانات",
        "nav_prompts": "◈ التعليمات", "nav_hotkeys": "⌨ اختصارات", "nav_obs": "▦ OBS",
        "nav_anki": "◇ Anki", "nav_overview": "⚙ نظرة عامة", "nav_ai_models": "◆ نماذج AI",
        "nav_behavior": "◉ السلوك", "nav_paths": "⊞ المسارات", "nav_database": "▨ قاعدة البيانات",
        "nav_logs": "☰ السجلات", "nav_lang": "⟳ اللغة",
        "title_console": "لوحة المعلومات", "title_memory": "بحث الذاكرة",
        "title_data": "جسر البيانات", "title_prompts": "شخصية AI",
        "title_api": "بوابة AI", "title_behavior": "السلوك والحدود",
        "title_database": "صيانة التخزين", "title_hotkeys": "الاختصارات",
        "title_logs": "السجلات", "title_obs": "اتصال OBS",
        "title_anki": "تكامل Anki", "title_paths": "المسارات والشبكة",
        "title_overview": "لقطة الإعدادات",
        "btn_save": "▣ حفظ", "btn_delete": "✕ حذف", "btn_refresh": "↺ تحديث",
        "btn_add": "+ إضافة", "btn_browse": "⊞ تصفح", "btn_cancel": "إلغاء",
        "btn_confirm": "✓ تأكيد", "btn_test": "◌ اختبار",
        "warn_unsaved": "تحذير",
        "warn_unsaved_msg": "تغييرات غير محفوظة في:\n{tabs}\n\nإجبار الخروج?",
        "warn_corrupt_config": "▲ ملف الإعدادات تالف",
        "warn_corrupt_msg": "فشل تحميل الإعدادات.\n\nخطأ: {err}\n\nالمسار: {path}",
        "toast_saved": "✓ تم حفظ الإعدادات", "lbl_ui_lang": "لغة الواجهة:",
    },
}

_UI_LANG = "English"  # default; updated in IzumiOmniUI.__init__ from runtime settings


def _t(key):
    """Return translated UI string for the current language, falling back to English."""
    d = _UI_STRINGS.get(_UI_LANG, _UI_STRINGS["English"])
    return d.get(key, _UI_STRINGS["English"].get(key, key))


# ================= Persistent Logging & Core Config Path =================
_config_log_path = os.path.splitext(LOG_PATH)[0] + "_config.log"
_log_dir = os.path.dirname(_config_log_path)
if _log_dir: os.makedirs(_log_dir, exist_ok=True)
logging.basicConfig(filename=_config_log_path, level=logging.WARNING, format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')

# Bind to script's absolute path to prevent path drift
SETTINGS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'izumi_runtime_settings.json')

# Runtime settings cache layer (eliminates repeated disk IO)
_settings_cache = None
_cache_lock = threading.Lock()
_settings_load_error = None  # Stores load error at startup for UI warning dialog

def _load_runtime_settings():
    global _settings_cache, _settings_load_error
    with _cache_lock:
        if _settings_cache is None:
            if os.path.exists(SETTINGS_JSON_PATH):
                try:
                    with open(SETTINGS_JSON_PATH, 'r', encoding='utf-8') as f:
                        _settings_cache = json.load(f)
                except Exception as e:
                    logging.error(f"Failed to load runtime settings: {e}")
                    _settings_load_error = str(e)
                    _settings_cache = {}
            else:
                _settings_cache = {}
        return dict(_settings_cache)  # return copy to prevent cache pollution

def _sanitize_for_json(obj):
    """序列化防崩装甲：递归清洗 set 等非法类型"""
    if isinstance(obj, set): return list(obj)
    if isinstance(obj, dict): return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list): return [_sanitize_for_json(i) for i in obj]
    return obj

def _save_runtime_settings(data):
    global _settings_cache
    try:
        clean_data = _sanitize_for_json(data)
        serialized = json.dumps(clean_data, ensure_ascii=False, indent=2)
        json.loads(serialized)  # 二次校验
        # 原子写入：先写临时文件再 os.replace，防断电导致配置文件损坏
        tmp_path = SETTINGS_JSON_PATH + ".tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(serialized)
        os.replace(tmp_path, SETTINGS_JSON_PATH)
        with _cache_lock:
            _settings_cache = clean_data  # 同步更新缓存
        return True
    except Exception as e:
        logging.error(f"Failed to save runtime settings: {e}"); return False

def _get_effective(key, default):
    return _load_runtime_settings().get(key, default)

def get_db_conn():
    current_db = _get_effective("DB_PATH", DB_PATH)
    conn = sqlite3.connect(current_db, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA journal_size_limit=5242880") # WAL size limit 5MB
    return conn

# ================= Database Initialization =================
def init_db():
    conn = get_db_conn()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS vocab_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, core_word TEXT, original_text TEXT, analysis TEXT, lang TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS word_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, core_word TEXT, lang TEXT, first_seen DATETIME DEFAULT CURRENT_TIMESTAMP, last_seen DATETIME DEFAULT CURRENT_TIMESTAMP, capture_count INTEGER DEFAULT 1, UNIQUE(core_word, lang))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS retry_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, provider TEXT, model TEXT, payload_json TEXT, retry_count INTEGER DEFAULT 0)''')
        conn.commit()
    finally:
        conn.close()

init_db()

# ================= Main UI Class =================

class IzumiOmniUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        global _UI_LANG
        _UI_LANG = _get_effective("UI_LANGUAGE", "English")
        if _UI_LANG not in _UI_STRINGS:
            _UI_LANG = "English"
        self.title(_t("app_title"))
        self.geometry("1100x768")

        # Show warning if config file was corrupted on load
        if _settings_load_error:
            self.after(500, lambda: messagebox.showwarning(
                _t("warn_corrupt_config"),
                _t("warn_corrupt_msg").format(err=_settings_load_error, path=SETTINGS_JSON_PATH)
            ))

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Dark theme for ttk Treeview compatibility
        self._style = ttk.Style(self)
        self._style.theme_use("default")
        self._style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        self._style.map("Treeview", background=[('selected', '#1f538d')])
        self._style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat")
        # Force override header background on Windows (native theme ignores configure)
        self._style.layout("Treeview.Heading", [
            ("Treeview.Heading.cell", {"sticky": "nswe"}),
            ("Treeview.Heading.border", {"sticky": "nswe", "children": [
                ("Treeview.Heading.padding", {"sticky": "nswe", "children": [
                    ("Treeview.Heading.image", {"side": "right", "sticky": ""}),
                    ("Treeview.Heading.label", {"sticky": "we"})
                ]})
            ]})
        ])

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._unsaved_tabs = set()
        self.frames = {}
        self.current_frame = None
        self._current_toast = None        # toast dedup reference
        self._stats_lock = threading.Lock()  # prevent concurrent stats refresh
        self._sec_labels = []              # [(label_widget, sec_key), ...] for lang switching
        self._menu_nav_keys = {}           # {stable_key: nav_key} for lang switching

        self._build_sidebar()
        # Lazy load: _select_menu builds frames on first access

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._select_menu("Console")

        # 注册全局极客搜索快捷键 (支持 Win/Mac)
        self.bind("<Control-k>", self._show_cmd_palette)
        self.bind("<Command-k>", self._show_cmd_palette)

    def _on_close(self):
        if self._unsaved_tabs:
            if not messagebox.askyesno(_t("warn_unsaved"), _t("warn_unsaved_msg").format(tabs=', '.join(self._unsaved_tabs))):
                return
        self.destroy()

    def show_toast(self, message, color="#4CAF50"):
        """Floating toast notification (auto-clears previous, prevents stacking)."""
        if self._current_toast is not None:
            try:
                self._current_toast.destroy()
            except Exception:
                pass
        toast = ctk.CTkLabel(self, text=message, fg_color=color, text_color="white", corner_radius=10, padx=20, pady=10, font=("", 14, "bold"))
        toast.place(relx=0.5, rely=0.05, anchor="center")
        self._current_toast = toast
        def _expire():
            try:
                toast.destroy()
            except Exception:
                pass
            if self._current_toast is toast:
                self._current_toast = None
        self.after(3000, _expire)

    def mark_unsaved(self, tab_name):
        self._unsaved_tabs.add(tab_name)

    def mark_saved(self, tab_name):
        self._unsaved_tabs.discard(tab_name)
        self.show_toast(_t("toast_saved"))

    # ── Sidebar Navigation ──
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # (sec_key, stable_key, builder, nav_key)
        # sec_key != None means section label; stable_key is the dict key used everywhere
        menu_defs = [
            ("sec_workflow",  None,          None,                         None),
            (None, "Console",   self._build_stats_frame,    "nav_console"),
            (None, "Memory",    self._build_search_frame,   "nav_memory"),
            (None, "Data",      self._build_export_frame,   "nav_data"),
            ("sec_customize", None,          None,                         None),
            (None, "Prompts",   self._build_templates_frame,"nav_prompts"),
            (None, "Hotkeys",   self._build_hotkeys_frame,  "nav_hotkeys"),
            (None, "OBS",       self._build_obs_frame,      "nav_obs"),
            (None, "Anki",      self._build_anki_frame,     "nav_anki"),
            ("sec_engine",    None,          None,                         None),
            (None, "Overview",  self._build_config_frame,   "nav_overview"),
            (None, "AI Models", self._build_api_frame,      "nav_ai_models"),
            (None, "Behavior",  self._build_features_frame, "nav_behavior"),
            (None, "Paths",     self._build_paths_frame,    "nav_paths"),
            (None, "Database",  self._build_db_frame,       "nav_database"),
            (None, "Logs",      self._build_log_frame,      "nav_logs"),
        ]

        # rows: 0=title, 1..N=menu items, N+1=spacer, N+2=lang label, N+3=lang combobox
        n_rows = len(menu_defs)
        self.sidebar.grid_rowconfigure(n_rows + 1, weight=1)

        ctk.CTkLabel(self.sidebar, text="Omni-Arsenal", font=("", 20, "bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        self.menu_buttons = {}
        self._sec_labels = []
        self._menu_nav_keys = {}
        row = 1
        for sec_key, stable_key, builder, nav_key in menu_defs:
            if sec_key is not None:
                lbl = ctk.CTkLabel(self.sidebar, text=_t(sec_key), font=("", 12, "bold"), text_color="gray")
                lbl.grid(row=row, column=0, padx=20, pady=(15, 5), sticky="w")
                self._sec_labels.append((lbl, sec_key))
            else:
                btn = ctk.CTkButton(self.sidebar, text=_t(nav_key), anchor="w", fg_color="transparent",
                                    text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                    command=lambda k=stable_key: self._select_menu(k))
                btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
                self.menu_buttons[stable_key] = btn
                self.frames[stable_key] = {"builder": builder, "instance": None}
                self._menu_nav_keys[stable_key] = nav_key
            row += 1

        # Language selector at bottom of sidebar
        ctk.CTkLabel(self.sidebar, text=_t("nav_lang"), font=("", 11), text_color="gray").grid(
            row=n_rows + 2, column=0, padx=10, pady=(5, 0), sticky="w")
        self._lang_cb = ctk.CTkComboBox(self.sidebar, values=list(_UI_STRINGS.keys()),
                                         command=self._switch_ui_language, width=170)
        self._lang_cb.set(_UI_LANG)
        self._lang_cb.grid(row=n_rows + 3, column=0, padx=10, pady=(0, 15), sticky="ew")

    def _select_menu(self, title):
        # 优化：先切换按钮状态，再异步加载内容
        for btn in self.menu_buttons.values():
            btn.configure(fg_color="transparent")
        self.menu_buttons[title].configure(fg_color=("gray75", "gray25"))

        if self.current_frame:
            self.current_frame.grid_forget()

        # 立即显示一个简单的加载占位符
        loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        loading_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 延迟加载实际内容，避免卡顿
        self.after(10, lambda: self._lazy_load_frame(title, loading_frame))

    def _lazy_load_frame(self, title, loading_frame):
        """异步加载帧内容"""
        if self.frames[title]["instance"] is None:
            frm = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
            self.frames[title]["builder"](frm)
            self.frames[title]["instance"] = frm

        loading_frame.grid_forget()
        self.current_frame = self.frames[title]["instance"]
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def _switch_ui_language(self, lang):
        """切换UI语言：平滑更新，避免界面卡顿"""
        global _UI_LANG
        _UI_LANG = lang
        curr = _load_runtime_settings()
        curr["UI_LANGUAGE"] = lang
        _save_runtime_settings(curr)

        # 批量更新文本，减少UI刷新次数
        self.title(_t("app_title"))

        # 异步更新侧边栏按钮标签
        def update_sidebar():
            for stable_key, btn in self.menu_buttons.items():
                nav_key = self._menu_nav_keys.get(stable_key)
                if nav_key:
                    btn.configure(text=_t(nav_key))

            for lbl, sec_key in self._sec_labels:
                lbl.configure(text=_t(sec_key))

        self.after(10, update_sidebar)

        # 清空帧缓存，但保留当前帧可见性
        current_key = None
        for k, btn in self.menu_buttons.items():
            try:
                if btn.cget("fg_color") != "transparent":
                    current_key = k
            except Exception:
                pass

        # 延迟重新构建当前页面
        if current_key:
            def rebuild_current():
                self.frames[current_key]["instance"] = None
                self._select_menu(current_key)
            self.after(50, rebuild_current)

    def _show_vocab_detail(self, event):
        """Double-click edit panel for memory entries."""
        sel = self.search_tree.selection()
        if not sel: return
        row_id = self.search_tree.item(sel[0])["values"][0]
        
        try:
            conn = get_db_conn()
            try:
                row = conn.execute("SELECT core_word, lang, timestamp, original_text, analysis FROM vocab_memory WHERE id=?", (row_id,)).fetchone()
            finally:
                conn.close()
            if not row: return
        except Exception as e: self.show_toast(str(e), "red"); return
            
        win = ctk.CTkToplevel(self)
        win.title(f"Edit Entry - ID:{row_id} ({row[0]})")
        win.geometry("850x650")
        win.attributes('-topmost', True)
        win.after(150, win.grab_set)  # Delay grab_set on Windows to prevent grab failure

        info_frm = ctk.CTkFrame(win, corner_radius=10)
        info_frm.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(info_frm, text=f"Word: {row[0]}", font=("", 18, "bold"), text_color="#1976D2").pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(info_frm, text=f"Language: {row[1]}").pack(side="left", padx=15)
        ctk.CTkLabel(info_frm, text=f"Captured: {row[2]}", text_color="gray").pack(side="right", padx=15)

        ctk.CTkLabel(win, text="Original Context:", font=("", 14, "bold")).pack(anchor="w", padx=20)
        orig_txt = ctk.CTkTextbox(win, height=80, font=("Consolas", 14))
        orig_txt.pack(fill="x", padx=20, pady=5)
        orig_txt.insert("1.0", row[3] or "")

        ctk.CTkLabel(win, text="AI Analysis:", font=("", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        ana_txt = ctk.CTkTextbox(win, height=300, font=("Consolas", 14), wrap="word")
        ana_txt.pack(fill="both", expand=True, padx=20, pady=5)
        ana_txt.insert("1.0", row[4] or "")

        def _save():
            new_orig = orig_txt.get("1.0", "end").strip()
            new_ana  = ana_txt.get("1.0", "end").strip()
            try:
                c = get_db_conn()
                try:
                    c.execute("UPDATE vocab_memory SET original_text=?, analysis=? WHERE id=?", (new_orig, new_ana, row_id))
                    c.commit()
                finally:
                    c.close()
                self.show_toast(f"✓ Entry {row[0]} updated")
                self._do_search()
                win.destroy()
            except Exception as ex: messagebox.showerror("Save Error", str(ex))

        btn_frm = ctk.CTkFrame(win, fg_color="transparent")
        btn_frm.pack(pady=20)
        ctk.CTkButton(btn_frm, text="▣ Save to Database", width=150, fg_color="#4CAF50", hover_color="#388E3C", command=_save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frm, text="Discard", width=100, fg_color="gray", command=win.destroy).pack(side="left", padx=10)

    def _show_prompt_sandbox(self):
        """Prompt sandbox with live preview of the engine request structure."""
        win = ctk.CTkToplevel(self)
        win.title("Prompt Sandbox (Live Preview)")
        win.geometry("900x750")
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Engine Request Structure Preview", font=("", 20, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(win, text="Shows the final prompt: system persona + language focus + RAG memory injection.", text_color="gray").pack()
        
        preview_txt = ctk.CTkTextbox(win, font=("Consolas", 14), wrap="word", fg_color="#1E1E1E", text_color="#D4D4D4")
        preview_txt.pack(fill="both", expand=True, padx=20, pady=15)
        
        def _render():
            persona = self.persona_txt.get("1.0", "end").strip()
            lang = self.target_lang_cb.get()
            
            # Use first template for focus demo; placeholder if empty
            tpl_keys = list(self.tpl_data.keys())
            tpl_key = tpl_keys[0] if tpl_keys else None
            tpl_focus = self.tpl_data.get(tpl_key, {}).get("focus", "(no focus defined)") if tpl_key else "(template list is empty)"
            rag_count = _get_effective("RAG_RECENT_WORD_COUNT", RAG_RECENT_WORD_COUNT)
            
            # 模拟假数据注入
            mock_rag = "1. [yesterday] e.g.: これはテストです。 (analysis: This is a test.)\n2. [2 days ago] e.g.: システム起動。 (analysis: System started.)"

            prompt = f"[SYSTEM PROMPT]\n{persona}\n\n"
            prompt += f"====================================\n"
            prompt += f"[Target Language]: {lang}\n"
            prompt += f"[Analysis Focus]:\n{tpl_focus}\n\n"
            prompt += f"====================================\n"
            prompt += f"[RAG Memory Injection (last {rag_count} entries)]:\n{mock_rag}\n\n"
            prompt += f"====================================\n"
            prompt += f"[USER INPUT]:\n<clipboard text or vision model output will be injected here>\n\n"
            prompt += f"Strictly output results according to the predefined JSON Schema..."
            
            preview_txt.configure(state="normal")
            preview_txt.delete("1.0", "end")
            preview_txt.insert("1.0", prompt)
            preview_txt.configure(state="disabled")
            
        _render()
        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=20)

    # ================= 各大模块构建 =================

    # ── 1. Dashboard ──
    def _build_stats_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_console"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        self.stats_text = ctk.CTkTextbox(frm, height=160, font=("Consolas", 14))
        self.stats_text.pack(fill="x", pady=(0, 20))

        btn_frm = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frm.pack(fill="x")
        ctk.CTkButton(btn_frm, text=_t("btn_refresh"), command=self._refresh_stats).pack(side="left")

        ctk.CTkLabel(frm, text="Top 5 Frequent Words", font=("", 16, "bold")).pack(anchor="w", pady=(20, 5))
        self.top5_tree = ttk.Treeview(frm, columns=("Word", "Language", "Count"), show="headings", height=5)
        for c, w in zip(("Word", "Language", "Count"), [200, 100, 100]):
            self.top5_tree.heading(c, text=c); self.top5_tree.column(c, width=w)
        self.top5_tree.pack(fill="x")

        ctk.CTkLabel(frm, text="Language Distribution", font=("", 16, "bold")).pack(anchor="w", pady=(20, 5))
        self.lang_tree = ttk.Treeview(frm, columns=("Language", "Count"), show="headings", height=5)
        self.lang_tree.heading("Language", text="Language"); self.lang_tree.heading("Count", text="Count")
        self.lang_tree.pack(fill="x")
        
        self._refresh_stats()

    def _refresh_stats(self):
        # 防止并发刷新造成 UI 数据竞争
        if not self._stats_lock.acquire(blocking=False):
            return
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", "Loading...\n")
        self.stats_text.configure(state="disabled")
        threading.Thread(target=self._stats_worker, daemon=True).start()

    def _stats_worker(self):
        try:
            conn = get_db_conn()
            try:
                total    = conn.execute("SELECT COUNT(*) FROM word_stats").fetchone()[0]
                today    = conn.execute("SELECT COUNT(*) FROM word_stats WHERE date(first_seen,'localtime')=date('now','localtime')").fetchone()[0]
                week_new = conn.execute("SELECT COUNT(*) FROM word_stats WHERE date(first_seen,'localtime') >= date('now','localtime','-6 days')").fetchone()[0]
                top5     = conn.execute("SELECT core_word, lang, capture_count FROM word_stats ORDER BY capture_count DESC LIMIT 5").fetchall()
                by_lang  = conn.execute("SELECT lang, COUNT(*) FROM word_stats GROUP BY lang ORDER BY COUNT(*) DESC").fetchall()
            finally:
                conn.close()
            self.after(0, lambda: self._update_stats_ui(total, today, week_new, top5, by_lang))
        except Exception as e:
            self.after(0, lambda: self.show_toast(f"Data fetch failed: {e}", "red"))
        finally:
            self._stats_lock.release()

    def _update_stats_ui(self, total, today, week_new, top5, by_lang):
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end",
            f"[{datetime.now().strftime('%H:%M:%S')}] Updated\n\n"
            f"Total entries: {total}    Today: {today}    This week: {week_new}\n"
            f"Status: Running"
        )
        self.stats_text.configure(state="disabled")

        for row in self.top5_tree.get_children(): self.top5_tree.delete(row)
        for r in top5: self.top5_tree.insert("", "end", values=(r[0], r[1], r[2]))

        for row in self.lang_tree.get_children(): self.lang_tree.delete(row)
        for r in by_lang: self.lang_tree.insert("", "end", values=(r[0], r[1]))

    # ── 2. Memory Search ──
    def _build_search_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_memory"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))

        ctrl = ctk.CTkFrame(frm, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0, 10))
        self.search_var = ctk.CTkEntry(ctrl, placeholder_text="Search word or text...", width=300)
        self.search_var.pack(side="left", padx=(0, 10))
        self.search_limit = ctk.CTkComboBox(ctrl, values=["50", "100", "500", "1000"], width=80)
        self.search_limit.set("50")  # Must set explicitly; otherwise get() returns empty string
        self.search_limit.pack(side="left", padx=(0, 10))
        ctk.CTkButton(ctrl, text="⌕ Search", width=100, command=self._do_search).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text=_t("btn_delete") + " Selected", width=140, fg_color="#d32f2f", hover_color="#b71c1c", command=self._delete_selected_vocab).pack(side="right")

        cols = ("ID", "Word", "Text", "Language", "Time")
        self.search_tree = ttk.Treeview(frm, columns=cols, show="headings", height=20)
        for c, w in zip(cols, [50, 150, 400, 100, 150]):
            self.search_tree.heading(c, text=c); self.search_tree.column(c, width=w)
        self.search_tree.pack(fill="both", expand=True)
        self.search_tree.bind("<Double-1>", self._show_vocab_detail)

    def _do_search(self):
        query = self.search_var.get().strip() or None
        try:
            limit = int(self.search_limit.get())
        except (ValueError, TypeError):
            limit = 50
        try:
            conn = get_db_conn()
            try:
                if query:
                    rows = conn.execute("SELECT id, core_word, original_text, lang, timestamp FROM vocab_memory WHERE core_word LIKE ? OR original_text LIKE ? ORDER BY timestamp DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit)).fetchall()
                else:
                    rows = conn.execute("SELECT id, core_word, original_text, lang, timestamp FROM vocab_memory ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            finally:
                conn.close()
            for row in self.search_tree.get_children(): self.search_tree.delete(row)
            for r in rows: self.search_tree.insert("", "end", values=(r[0], r[1], r[2][:60], r[3], r[4][:16]))
        except Exception as e: self.show_toast(str(e), "red")

    def _delete_selected_vocab(self):
        sel = self.search_tree.selection()
        if not sel: return
        row_id, core_word, _, lang, _ = self.search_tree.item(sel[0])["values"]
        if not messagebox.askyesno("Warning", f"Permanently delete ID:{row_id} ({core_word})?\nThis will also update word frequency stats."): return
        try:
            conn = get_db_conn()
            try:
                conn.execute("DELETE FROM vocab_memory WHERE id=?", (row_id,))
                # 删除后重新统计实际剩余条数，避免词频与真实数据不一致
                remaining = conn.execute(
                    "SELECT COUNT(*) FROM vocab_memory WHERE core_word=? AND lang=?", (core_word, lang)
                ).fetchone()[0]
                if remaining > 0:
                    conn.execute("UPDATE word_stats SET capture_count=? WHERE core_word=? AND lang=?", (remaining, core_word, lang))
                else:
                    conn.execute("DELETE FROM word_stats WHERE core_word=? AND lang=?", (core_word, lang))
                conn.commit()
            finally:
                conn.close()
            self.search_tree.delete(sel[0])
            self.show_toast(f"Deleted entry ID:{row_id}")
        except Exception as e: self.show_toast(str(e), "red")

    # ── 3. Data Bridge (Import / Export) ──
    def _build_export_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_data"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # 过滤条件区
        filter_frm = ctk.CTkFrame(frm, fg_color="transparent")
        filter_frm.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(filter_frm, text="Language Filter:").pack(side="left", padx=(0, 5))
        self._export_lang_var = ctk.StringVar(value="All")
        ctk.CTkEntry(filter_frm, textvariable=self._export_lang_var, width=100, placeholder_text="All").pack(side="left", padx=(0, 15))
        ctk.CTkLabel(filter_frm, text="From (YYYY-MM-DD):").pack(side="left", padx=(0, 5))
        self._export_date_from_var = ctk.StringVar()
        ctk.CTkEntry(filter_frm, textvariable=self._export_date_from_var, width=120, placeholder_text="leave blank for all").pack(side="left", padx=(0, 15))
        ctk.CTkLabel(filter_frm, text="To:").pack(side="left", padx=(0, 5))
        self._export_date_to_var = ctk.StringVar()
        ctk.CTkEntry(filter_frm, textvariable=self._export_date_to_var, width=120, placeholder_text="leave blank for all").pack(side="left")

        row1 = ctk.CTkFrame(frm, fg_color="transparent"); row1.pack(fill="x", pady=10)
        ctk.CTkButton(row1, text="↓ Export CSV", command=self._export_csv).pack(side="left", padx=5)
        ctk.CTkButton(row1, text="↑ Import CSV", fg_color="#f57c00", hover_color="#e65100", command=self._import_csv).pack(side="left", padx=5)

        row2 = ctk.CTkFrame(frm, fg_color="transparent"); row2.pack(fill="x", pady=10)
        ctk.CTkButton(row2, text="⊞ Export Obsidian MD", command=self._export_obsidian).pack(side="left", padx=5)
        ctk.CTkButton(row2, text="⊟ Export Anki TSV", command=self._export_anki_tsv).pack(side="left", padx=5)

    def _get_export_rows(self):
        """根据过滤条件查询导出数据，供各导出方法复用"""
        lang  = self._export_lang_var.get().strip()
        d_from = self._export_date_from_var.get().strip()
        d_to   = self._export_date_to_var.get().strip()
        conds, params = [], []
        if lang and lang != "All":
            conds.append("vm.lang=?"); params.append(lang)
        if d_from:
            conds.append("date(vm.timestamp)>=?"); params.append(d_from)
        if d_to:
            conds.append("date(vm.timestamp)<=?"); params.append(d_to)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        sql = (f"SELECT vm.core_word, vm.original_text, vm.analysis, vm.lang, vm.timestamp, "
               f"COALESCE(ws.capture_count,1) FROM vocab_memory vm "
               f"LEFT JOIN word_stats ws ON vm.core_word=ws.core_word AND vm.lang=ws.lang "
               f"{where} ORDER BY vm.timestamp DESC")
        conn = get_db_conn()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def _export_csv(self):
        vocab_folder = _get_effective("VOCAB_FOLDER", VOCAB_FOLDER)
        os.makedirs(vocab_folder, exist_ok=True)
        path = os.path.join(vocab_folder, f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
        try:
            rows = self._get_export_rows()
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["core_word", "original_text", "analysis", "lang", "timestamp", "capture_count"])
                for r in rows: writer.writerow([r[0], r[1], (r[2] or "").replace('\n', '\r\n'), r[3], r[4], r[5]])
            self.show_toast(f"CSV exported: {path}")
        except Exception as e: self.show_toast(str(e), "red")

    def _import_csv(self):
        src = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not src: return
        eff_lang = _get_effective("TARGET_LANGUAGE", TARGET_LANGUAGE)
        try:
            conn = get_db_conn()
            try:
                count = 0
                with open(src, "r", encoding="utf-8-sig") as f:
                    for row in csv.DictReader(f):
                        cw   = row.get("core_word", "")
                        orig = row.get("original_text", "")
                        ana  = row.get("analysis", "").replace('\r\n', '\n')
                        lng  = row.get("lang", eff_lang)
                        if not cw: continue
                        # 防止重复倒吸：原文+语言完全相同的条目跳过
                        if conn.execute("SELECT 1 FROM vocab_memory WHERE core_word=? AND lang=? AND original_text=?", (cw, lng, orig)).fetchone():
                            continue
                        conn.execute("INSERT INTO vocab_memory (core_word, original_text, analysis, lang) VALUES (?,?,?,?)", (cw, orig, ana, lng))
                        if conn.execute("SELECT 1 FROM word_stats WHERE core_word=? AND lang=?", (cw, lng)).fetchone():
                            conn.execute("UPDATE word_stats SET capture_count=capture_count+1 WHERE core_word=? AND lang=?", (cw, lng))
                        else:
                            conn.execute("INSERT INTO word_stats (core_word, lang) VALUES (?, ?)", (cw, lng))
                        count += 1
                conn.commit()
            finally:
                conn.close()
            self.show_toast(f"Import complete: {count} records merged")
        except Exception as e: self.show_toast(str(e), "red")

    def _export_obsidian(self):
        vocab_folder = _get_effective("VOCAB_FOLDER", VOCAB_FOLDER)
        out_dir = os.path.join(vocab_folder, "obsidian")
        os.makedirs(out_dir, exist_ok=True)
        tags = _get_effective("OBSIDIAN_BASE_TAGS", ["flashcard"])
        tag_str = "\n".join([f"  - {t}" for t in (tags if isinstance(tags, list) else [tags])])
        try:
            rows = self._get_export_rows()
            count = 0
            for r in rows:
                core_word, orig, analysis, lang, ts, cap_count = r
                safe_name = re.sub(r'[\\/:*?"<>|]', '_', core_word)
                md_path = os.path.join(out_dir, f"{safe_name}_{lang}.md")
                content = (
                    f"---\ntags:\n{tag_str}\nlang: {lang}\ncapture_count: {cap_count}\n"
                    f"first_captured: {ts}\n---\n\n"
                    f"# {core_word}\n\n"
                    f"## Original Context\n\n{orig or ''}\n\n"
                    f"## Analysis\n\n{analysis or ''}\n"
                )
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content)
                count += 1
            self.show_toast(f"Exported {count} Obsidian MD files → {out_dir}")
        except Exception as e: self.show_toast(str(e), "red")

    def _export_anki_tsv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".tsv",
            filetypes=[("TSV Files", "*.tsv"), ("All Files", "*.*")],
            initialfile=f"anki_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.tsv"
        )
        if not path: return
        try:
            rows = self._get_export_rows()
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                for r in rows:
                    core_word, orig, analysis, lang, ts, _ = r
                    front = core_word
                    back  = f"{orig}\n\n---\n\n{analysis or ''}".strip()
                    writer.writerow([front, back, lang])
            self.show_toast(f"Anki TSV exported: {path}")
        except Exception as e: self.show_toast(str(e), "red")

    # ── 4. Prompts ──
    def _build_templates_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_prompts"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(frm, text="System Persona (SYSTEM_PROMPT_PERSONA):").pack(anchor="w")
        self.persona_txt = ctk.CTkTextbox(frm, height=60, font=("Consolas", 12))
        self.persona_txt.pack(fill="x", pady=5)
        self.persona_txt.insert("1.0", _get_effective("SYSTEM_PROMPT_PERSONA", "You are a rigorous linguistics professor."))

        ctrl = ctk.CTkFrame(frm, fg_color="transparent"); ctrl.pack(fill="x", pady=10)

        ctk.CTkLabel(ctrl, text="TARGET_LANGUAGE:").grid(row=0, column=0, padx=5)
        # ComboBox 选项从 LANGUAGE_TEMPLATES 键中动态获取，与其他模块保持一致
        lang_keys = list(LANGUAGE_TEMPLATES.keys()) if LANGUAGE_TEMPLATES else ["japanese", "english", "chinese"]
        self.target_lang_cb = ctk.CTkComboBox(ctrl, values=lang_keys)
        self.target_lang_cb.set(_get_effective("TARGET_LANGUAGE", TARGET_LANGUAGE))
        self.target_lang_cb.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(ctrl, text="ACTIVE_TEMPLATE:").grid(row=0, column=2, padx=(20, 5))
        self._active_tpl_var = ctk.StringVar(value=_get_effective("ACTIVE_TEMPLATE", ACTIVE_TEMPLATE))
        active_tpl_cb = ctk.CTkComboBox(ctrl, values=lang_keys, variable=self._active_tpl_var, width=160)
        active_tpl_cb.set(self._active_tpl_var.get())
        active_tpl_cb.grid(row=0, column=3, padx=5)
        
        # 可编辑模板列表（Treeview + CRUD）
        self.tpl_data = copy.deepcopy(dict(_get_effective("LANGUAGE_TEMPLATES", LANGUAGE_TEMPLATES)))

        tpl_ctrl = ctk.CTkFrame(frm, fg_color="transparent"); tpl_ctrl.pack(fill="x", pady=(15, 4))
        ctk.CTkLabel(tpl_ctrl, text="Language Templates (double-click to edit):", font=("", 16, "bold")).pack(side="left")
        ctk.CTkButton(tpl_ctrl, text=_t("btn_add"), width=80, command=self._add_template).pack(side="left", padx=10)
        ctk.CTkButton(tpl_ctrl, text=_t("btn_delete"), width=80, fg_color="#d32f2f", hover_color="#b71c1c", command=self._del_template).pack(side="left")

        tpl_cols = ("Key", "Name", "Focus (first 40 chars)")
        self._tpl_tree = ttk.Treeview(frm, columns=tpl_cols, show="headings", height=6)
        for c, w in zip(tpl_cols, [130, 160, 400]):
            self._tpl_tree.heading(c, text=c); self._tpl_tree.column(c, width=w)
        self._tpl_tree.pack(fill="x", padx=5, pady=5)
        self._tpl_tree.bind("<Double-1>", self._edit_template_row)
        self._refresh_tpl_tree()

        ctk.CTkButton(frm, text="◈ Prompt Sandbox Preview", fg_color="#E64A19", hover_color="#D84315", command=self._show_prompt_sandbox).pack(pady=10)
        ctk.CTkButton(frm, text=_t("btn_save") + " Prompts & Templates", command=self._save_templates).pack(pady=20)

    def _refresh_tpl_tree(self):
        for row in self._tpl_tree.get_children(): self._tpl_tree.delete(row)
        for k, v in self.tpl_data.items():
            self._tpl_tree.insert("", "end", values=(k, v.get("name",""), v.get("focus","")[:40]))

    def _add_template(self):
        key = simpledialog.askstring("Add Template", "Enter template key (e.g. french, korean):")
        if not key: return
        if key in self.tpl_data:
            messagebox.showerror("Conflict", f"Key '{key}' already exists!"); return
        self.tpl_data[key] = {"name": key, "focus": "Enter analysis focus instructions here"}
        self._refresh_tpl_tree(); self.mark_unsaved("Prompts")

    def _del_template(self):
        sel = self._tpl_tree.selection()
        if not sel: return
        key = self._tpl_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete template '{key}'?"):
            self.tpl_data.pop(key, None)
            self._refresh_tpl_tree(); self.mark_unsaved("Prompts")

    def _edit_template_row(self, event):
        sel = self._tpl_tree.selection()
        if not sel: return
        key = self._tpl_tree.item(sel[0])["values"][0]
        tpl = self.tpl_data.get(key, {})

        win = ctk.CTkToplevel(self)
        win.title(f"Edit Template - {key}")
        win.geometry("600x400")
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text=f"Key: {key}", font=("", 14, "bold"), text_color="#1976D2").pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(win, text="Display Name:").pack(anchor="w", padx=20)
        name_var = ctk.StringVar(value=tpl.get("name", ""))
        ctk.CTkEntry(win, textvariable=name_var, width=400).pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(win, text="Focus:").pack(anchor="w", padx=20, pady=(10, 0))
        focus_txt = ctk.CTkTextbox(win, height=180, font=("Consolas", 13), wrap="word")
        focus_txt.pack(fill="both", expand=True, padx=20, pady=5)
        focus_txt.insert("1.0", tpl.get("focus", ""))

        def _save():
            self.tpl_data[key] = {"name": name_var.get().strip(), "focus": focus_txt.get("1.0", "end").strip()}
            self._refresh_tpl_tree(); self.mark_unsaved("Prompts"); win.destroy()

        ctk.CTkButton(win, text=_t("btn_save"), command=_save).pack(pady=15)

    def _save_templates(self):
        curr = _load_runtime_settings()
        curr["SYSTEM_PROMPT_PERSONA"] = self.persona_txt.get("1.0", "end").strip()
        curr["TARGET_LANGUAGE"] = self.target_lang_cb.get()
        curr["ACTIVE_TEMPLATE"] = self._active_tpl_var.get()
        curr["LANGUAGE_TEMPLATES"] = self.tpl_data
        if _save_runtime_settings(curr): self.mark_saved("Prompts")

    # ── 7. AI Models ──
    def _build_api_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_api"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.api_vars = {}; self.url_vars = {}
        # 合并 config.py 与运行时中的所有 provider（防止运行时新增的 provider 被覆盖丢失）
        eff_keys = _get_effective("API_KEYS", API_KEYS)
        eff_urls = _get_effective("BASE_URLS", BASE_URLS)
        all_providers = dict(API_KEYS)
        for p in eff_keys:
            if p not in all_providers:
                all_providers[p] = eff_keys[p]
        
        # Local ML resources
        ctk.CTkLabel(frm, text="Local ML Resources (hot reload on change):", font=("", 16, "bold"), text_color="#1976D2").pack(anchor="w", pady=(10, 5))
        ml_frm = ctk.CTkFrame(frm); ml_frm.pack(fill="x", pady=5, padx=5)
        
        self.ocr_lang = ctk.CTkComboBox(ml_frm, values=["japan", "en", "ch", "korean"]); self.ocr_lang.set(_get_effective("OCR_LANGUAGE", "japan"))
        ctk.CTkLabel(ml_frm, text="PaddleOCR Language:").grid(row=0, column=0, padx=5, pady=5); self.ocr_lang.grid(row=0, column=1, padx=5, pady=5)

        self.wh_model = ctk.CTkComboBox(ml_frm, values=["tiny", "base", "small", "large-v3"]); self.wh_model.set(_get_effective("WHISPER_MODEL", "base"))
        ctk.CTkLabel(ml_frm, text="Whisper Model:").grid(row=0, column=2, padx=5, pady=5); self.wh_model.grid(row=0, column=3, padx=5, pady=5)

        self.wh_dev = ctk.CTkComboBox(ml_frm, values=["cpu", "cuda"]); self.wh_dev.set(_get_effective("WHISPER_DEVICE", "cpu"))
        ctk.CTkLabel(ml_frm, text="Whisper Device:").grid(row=0, column=4, padx=5, pady=5); self.wh_dev.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(frm, text="Cloud API Keys & Models:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 5))
        # 添加获取模型按钮
        fetch_btn_frm = ctk.CTkFrame(frm, fg_color="transparent")
        fetch_btn_frm.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(fetch_btn_frm, text="🔍 Fetch Available Models", command=self._fetch_models, width=180).pack(side="left", padx=5)

        # 模型选择器字典
        self.model_combo_boxes = {}

        for p in all_providers.keys():
            row_frm = ctk.CTkFrame(frm, fg_color="transparent"); row_frm.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frm, text=f"{p}:", width=100, anchor="e").pack(side="left", padx=5)
            var = ctk.StringVar(value=eff_keys.get(p, ""))
            self.api_vars[p] = var  # 存储到字典

            # API密钥输入框
            entry = ctk.CTkEntry(row_frm, textvariable=var, width=300)
            entry.pack(side="left", padx=5)

            # 添加模型下拉框
            model_cb = ctk.CTkComboBox(row_frm, values=[], state="readonly", width=200)
            model_cb.pack(side="left", padx=5)
            self.model_combo_boxes[p] = model_cb

            # 绑定API密钥变化事件
            def _on_key_change(*args, provider=p):
                self._on_api_key_change(provider)

            var.trace_add("write", _on_key_change)

        ctk.CTkLabel(frm, text="API Endpoints (Base URLs):", font=("", 16, "bold")).pack(anchor="w", pady=(20, 5))
        all_url_providers = dict(BASE_URLS)
        for p in eff_urls:
            if p not in all_url_providers:
                all_url_providers[p] = eff_urls[p]
        for p in all_url_providers.keys():
            row_frm = ctk.CTkFrame(frm, fg_color="transparent"); row_frm.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frm, text=f"{p} URL:", width=100, anchor="e").pack(side="left", padx=5)
            var = ctk.StringVar(value=eff_urls.get(p, BASE_URLS.get(p, "")))
            self.url_vars[p] = var
            ctk.CTkEntry(row_frm, textvariable=var, width=400, placeholder_text="https://api.example.com/v1").pack(side="left", padx=5)

        ctk.CTkButton(frm, text=_t("btn_save"), command=self._save_api).pack(pady=20)

    def _fetch_models(self):
        """获取所有API提供商可用的模型列表"""
        try:
            # OpenAI模型
            openai_key = self.api_vars.get("openai").get()
            if openai_key:
                client = httpx.Client(timeout=10, proxies={"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None)
                response = client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {openai_key}"})
                if response.status_code == 200:
                    models = [model["id"] for model in response.json()["data"]]
                    # 过滤常用模型
                    openai_models = [m for m in models if "gpt" in m.lower() or "o1" in m.lower() or "o3" in m.lower()]
                    if openai_models:
                        self.model_combo_boxes["openai"].configure(values=openai_models)
                        self.model_combo_boxes["openai"].set(openai_models[0] if openai_models else "")

            # Claude模型
            claude_key = self.api_vars.get("claude").get()
            if claude_key:
                claude_models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
                self.model_combo_boxes["claude"].configure(values=claude_models)
                self.model_combo_boxes["claude"].set(claude_models[0])

            # DeepSeek模型
            deepseek_key = self.api_vars.get("deepseek").get()
            if deepseek_key:
                deepseek_models = ["deepseek-chat", "deepseek-coder", "deepseek-v2"]
                self.model_combo_boxes["deepseek"].configure(values=deepseek_models)
                self.model_combo_boxes["deepseek"].set(deepseek_models[0])

            # Grok模型
            grok_key = self.api_vars.get("grok").get()
            if grok_key:
                grok_models = ["grok-2-1212", "grok-1", "grok-beta"]
                self.model_combo_boxes["grok"].configure(values=grok_models)
                self.model_combo_boxes["grok"].set(grok_models[0])

            # 其他提供商
            for provider in ["qwen", "kimi", "doubao", "minimax"]:
                if self.api_vars.get(provider) and self.api_vars[provider].get():
                    # 为其他提供商提供通用模型列表
                    generic_models = ["default", "chat", "completion"]
                    self.model_combo_boxes[provider].configure(values=generic_models)
                    self.model_combo_boxes[provider].set(generic_models[0])

            messagebox.showinfo("Success", "Model lists fetched successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch models: {e}")

    def _on_api_key_change(self, provider):
        """当API密钥改变时，尝试自动获取模型"""
        key = self.api_vars[provider].get()
        if key and provider in ["openai", "claude", "deepseek", "grok", "qwen", "kimi", "doubao", "minimax"]:
            try:
                # 延迟500ms后执行，避免频繁调用
                self.after(500, lambda: self._fetch_single_provider_models(provider))
            except:
                pass

    def _fetch_single_provider_models(self, provider):
        """获取单个提供商的模型列表"""
        try:
            key = self.api_vars.get(provider).get()
            if not key:
                return

            if provider == "openai":
                client = httpx.Client(timeout=10, proxies={"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None)
                response = client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"})
                if response.status_code == 200:
                    models = [model["id"] for model in response.json()["data"]]
                    openai_models = [m for m in models if "gpt" in m.lower() or "o1" in m.lower() or "o3" in m.lower()]
                    if openai_models:
                        self.model_combo_boxes["openai"].configure(values=openai_models)
                        self.model_combo_boxes["openai"].set(openai_models[0] if openai_models else "")

            elif provider == "claude":
                claude_models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
                self.model_combo_boxes["claude"].configure(values=claude_models)
                self.model_combo_boxes["claude"].set(claude_models[0])

            elif provider == "deepseek":
                deepseek_models = ["deepseek-chat", "deepseek-coder", "deepseek-v2"]
                self.model_combo_boxes["deepseek"].configure(values=deepseek_models)
                self.model_combo_boxes["deepseek"].set(deepseek_models[0])

            elif provider == "grok":
                grok_models = ["grok-2-1212", "grok-1", "grok-beta"]
                self.model_combo_boxes["grok"].configure(values=grok_models)
                self.model_combo_boxes["grok"].set(grok_models[0])

            elif provider in ["qwen", "kimi", "doubao", "minimax"]:
                generic_models = ["default", "chat", "completion"]
                self.model_combo_boxes[provider].configure(values=generic_models)
                self.model_combo_boxes[provider].set(generic_models[0])

        except Exception as e:
            # 静默失败，不显示错误
            pass

    def _save_api(self):
        curr = _load_runtime_settings()
        curr["API_KEYS"] = {k: v.get() for k, v in self.api_vars.items()}
        curr["BASE_URLS"] = {k: v.get() for k, v in self.url_vars.items()}
        curr["OCR_LANGUAGE"] = self.ocr_lang.get()
        curr["WHISPER_MODEL"] = self.wh_model.get()
        curr["WHISPER_DEVICE"] = self.wh_dev.get()
        # 保存选中的模型
        curr["SELECTED_MODELS"] = {k: v.get() for k, v in self.model_combo_boxes.items() if v.get()}
        if _save_runtime_settings(curr): self.mark_saved("AI Models")

    # ── 8. Behavior & Limits ──
    def _build_features_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_behavior"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.feat_vars = {}
        
        def _add_switch(key, label, default):
            var = ctk.BooleanVar(value=_get_effective(key, default))
            self.feat_vars[key] = var
            sw = ctk.CTkSwitch(frm, text=label, variable=var, onvalue=True, offvalue=False)
            sw.pack(anchor="w", pady=5, padx=20)

        ctk.CTkLabel(frm, text="Toggles:", font=("", 16, "bold")).pack(anchor="w", pady=10)
        _add_switch("ENABLE_LOCAL_OCR",              "Local OCR (anti-hallucination)",         ENABLE_LOCAL_OCR)
        _add_switch("ENABLE_LOCAL_WHISPER",          "Local Whisper (offline transcription)",  ENABLE_LOCAL_WHISPER)
        _add_switch("ENABLE_REGION_SELECT",          "Alt+R Region Select Capture",            ENABLE_REGION_SELECT)
        _add_switch("ENABLE_CAPTURE_PREVIEW",        "Screenshot Preview & Confirm",           ENABLE_CAPTURE_PREVIEW)
        _add_switch("ENABLE_TELDRIVE_UPLOAD",        "Teldrive Remote Backup Sync",            ENABLE_TELDRIVE_UPLOAD)
        _add_switch("ENABLE_VN_GALGAME_GENERATOR",   "Galgame Script Generator",               ENABLE_VN_GALGAME_GENERATOR)
        _add_switch("ENABLE_AUTONOMOUS_LISTENER",    "Autonomous Listener (background)",       ENABLE_AUTONOMOUS_LISTENER)
        _add_switch("ENABLE_ANKI_MEDIA",             "Anki Auto Media Injection",              ENABLE_ANKI_MEDIA)
        _add_switch("DEBUG_MODE",                    "Debug Mode (verbose output)",            DEBUG_MODE)

        ctk.CTkLabel(frm, text="Parameters:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 10))
        params = [
            ("CLAUDE_MAX_TOKENS",    "Claude Max Tokens",                2048),
            ("VIDEO_EXTRACT_FRAMES", "Video Frame Count",                4),
            ("CIRCUIT_BREAKER_LIMIT","Circuit Breaker Limit (sec)",      CIRCUIT_BREAKER_LIMIT),
            ("RAG_RECENT_WORD_COUNT","RAG Recent Word Count",            RAG_RECENT_WORD_COUNT),
            ("RETRY_MAX_ATTEMPTS",   "Max Retry Attempts",               RETRY_MAX_ATTEMPTS),
            ("REVIEW_DAYS_ARRAY",    "Review Days Array (comma-separated)", "3,7,14"),
            ("OBSIDIAN_BASE_TAGS",   "Obsidian Base Tags (comma-separated)", "flashcard"),
        ]
        
        self.param_vars = {}
        for k, lbl, dflt in params:
            row_frm = ctk.CTkFrame(frm, fg_color="transparent"); row_frm.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frm, text=f"{lbl}:", width=220, anchor="e").pack(side="left", padx=5)
            val = _get_effective(k, dflt)
            if isinstance(val, list): val = ",".join(map(str, val))
            var = ctk.StringVar(value=str(val))
            self.param_vars[k] = var
            ctk.CTkEntry(row_frm, textvariable=var, width=300).pack(side="left", padx=5)

        ctk.CTkButton(frm, text=_t("btn_save"), command=self._save_features).pack(pady=20)

    def _save_features(self):
        curr = _load_runtime_settings()
        for k, v in self.feat_vars.items(): curr[k] = v.get()
        for k, v in self.param_vars.items():
            val = v.get().strip()
            if "ARRAY" in k or "TAGS" in k:
                curr[k] = [x.strip() for x in val.split(",") if x.strip()]
            else:
                try:
                    curr[k] = int(val)
                except ValueError:
                    messagebox.showerror("Format Error", f"Parameter [{k}] must be an integer, got: '{val}'")
                    return
        if _save_runtime_settings(curr): self.mark_saved("Behavior")

    # ── 11. Database Maintenance ──
    def _build_db_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_database"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))

        row1 = ctk.CTkFrame(frm, fg_color="transparent"); row1.pack(fill="x", pady=10)
        ctk.CTkButton(row1, text="▣ Backup", command=self._backup_db).pack(side="left", padx=5)
        ctk.CTkButton(row1, text="↩ Restore", fg_color="#d32f2f", hover_color="#b71c1c", command=self._restore_db).pack(side="left", padx=5)

        row2 = ctk.CTkFrame(frm, fg_color="transparent"); row2.pack(fill="x", pady=10)
        ctk.CTkButton(row2, text="⊟ VACUUM", fg_color="#1976D2", hover_color="#1565C0", command=self._vacuum_db).pack(side="left", padx=5)
        ctk.CTkButton(row2, text="◌ Orphan GC", fg_color="#E64A19", hover_color="#D84315", command=self._clean_media).pack(side="left", padx=5)

        ctk.CTkLabel(frm, text="Section Header Blacklist (ANALYSIS_SECTION_HEADERS):").pack(anchor="w", pady=(20, 5))
        self.bl_txt = ctk.CTkTextbox(frm, height=100, font=("Consolas", 12))
        self.bl_txt.pack(fill="x")
        self.bl_txt.insert("1.0", "\n".join(_get_effective("ANALYSIS_SECTION_HEADERS", ANALYSIS_SECTION_HEADERS)))
        ctk.CTkButton(frm, text=_t("btn_save"), command=self._save_bl).pack(pady=10)

    def _backup_db(self):
        current_db = os.path.normpath(_get_effective("DB_PATH", DB_PATH))
        backup_path = filedialog.asksaveasfilename(
            title="Save Backup",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        if not backup_path: return
        try:
            src = sqlite3.connect(current_db)
            dst = sqlite3.connect(backup_path)
            try:
                src.backup(dst)
            finally:
                dst.close()
                src.close()
            self.show_toast(f"✓ Backup saved → {backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))

    def _restore_db(self):
        src_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not src_path: return
        current_db = os.path.normpath(_get_effective("DB_PATH", DB_PATH))
        if not messagebox.askyesno("▲ Danger",
            f"A backup of the current database will be created before restore.\n\n"
            f"Current DB: {current_db}\n"
            f"Restore from: {src_path}\n\n"
            f"Confirm? This will overwrite all current data."):
            return
        # 还原前先自动备份
        auto_backup = current_db + f".pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        try:
            shutil.copy2(current_db, auto_backup)
        except Exception as e:
            messagebox.showerror("Auto-Backup Failed", f"Restore aborted, could not create safety backup: {e}")
            return
        try:
            src = sqlite3.connect(src_path)
            dst = sqlite3.connect(current_db)
            try:
                src.backup(dst)
            finally:
                dst.close()
                src.close()
            self.show_toast(f"✓ Database restored. Old data backed up to {auto_backup}")
        except Exception as e:
            messagebox.showerror("Restore Failed", str(e))

    def _vacuum_db(self):
        # 移入后台线程，避免主线程阻塞冻结 UI
        self.show_toast("Running VACUUM, please wait...", "#1976D2")
        def _do():
            try:
                conn = get_db_conn()
                try:
                    conn.execute("VACUUM")
                finally:
                    conn.close()
                self.after(0, lambda: self.show_toast("VACUUM complete, database compacted."))
            except Exception as e:
                self.after(0, lambda: self.show_toast(str(e), "red"))
        threading.Thread(target=_do, daemon=True).start()

    def _clean_media(self):
        if not messagebox.askyesno("Orphan GC", "Scan ASSETS_PATH for all png/wav/mp4 files not referenced in the database and permanently delete them.\nEnsure no capture tasks are running. Confirm?"): return
        try:
            conn = get_db_conn()
            try:
                rows = conn.execute("SELECT analysis, core_word FROM vocab_memory").fetchall()
            finally:
                conn.close()
            used = set()
            for r in rows: used.update(re.findall(r'[\w\-]+\.(?:png|wav|mp4|jpg)', (r[0] or "") + (r[1] or "")))
            
            assets = os.path.normpath(_get_effective("ASSETS_PATH", ASSETS_PATH))
            count = 0; size = 0; errors = []
            for f in os.listdir(assets):
                if f.endswith(('.png', '.wav', '.mp4', '.jpg')) and f not in used:
                    p = os.path.join(assets, f)
                    try:
                        size += os.path.getsize(p)
                        os.remove(p)
                        count += 1
                    except Exception as e:
                        errors.append(f"{f}: {e}")
            msg = f"GC complete! Removed {count} orphaned files, freed {size/1024/1024:.2f} MB."
            if errors:
                msg += f"\n\nFailed to delete (possibly in use):\n" + "\n".join(errors[:5])
            self.show_toast(msg[:80] + "..." if len(msg) > 80 else msg)
            if errors:
                messagebox.showwarning("Some Files Failed to Delete", "\n".join(errors))
        except Exception as e: self.show_toast(str(e), "red")

    def _save_bl(self):
        curr = _load_runtime_settings()
        curr["ANALYSIS_SECTION_HEADERS"] = [x.strip() for x in self.bl_txt.get("1.0", "end").split('\n') if x.strip()]
        if _save_runtime_settings(curr): self.mark_saved("Database")

    def _init_all_frames(self): pass  # placeholder; actual lazy loading done by _select_menu

    # ─────────────────────────────────────────────────────────────
    # ── 5. Hotkeys ──
    # ─────────────────────────────────────────────────────────────
    def _build_hotkeys_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_hotkeys"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self._slots_data  = copy.deepcopy(dict(_get_effective("SLOTS_CONFIG", SLOTS_CONFIG)))
        self._or_data     = copy.deepcopy(list(_get_effective("OPENROUTER_HOTKEYS", OPENROUTER_HOTKEYS)))
        self._tpl_hk_data = copy.deepcopy(list(_get_effective("TEMPLATE_SWITCH_HOTKEYS", TEMPLATE_SWITCH_HOTKEYS)))

        # ── Slot Hotkeys ──
        frm1 = ctk.CTkFrame(frm, fg_color="transparent")
        frm1.pack(fill="x", pady=(10, 4))
        ctk.CTkLabel(frm1, text="Slot Mappings (double-click to edit):", font=("", 16, "bold")).pack(side="left")
        ctk.CTkButton(frm1, text="+ Add Mapping", width=110, command=self._add_slot).pack(side="left", padx=10)
        ctk.CTkButton(frm1, text=_t("btn_delete"), width=90, fg_color="#d32f2f", hover_color="#b71c1c", command=self._del_slot).pack(side="left")

        slot_cols = ("Action", "Hotkey", "Provider", "Model")
        self._slots_tree = ttk.Treeview(frm, columns=slot_cols, show="headings", height=8)
        for c, w in zip(slot_cols, [120, 150, 120, 300]):
            self._slots_tree.heading(c, text=c); self._slots_tree.column(c, width=w)
        self._slots_tree.pack(fill="x", padx=5, pady=5)
        self._slots_tree.bind("<Double-1>", self._edit_slot_row)

        # ── OpenRouter Channels ──
        frm2 = ctk.CTkFrame(frm, fg_color="transparent")
        frm2.pack(fill="x", pady=(20, 4))
        ctk.CTkLabel(frm2, text="OpenRouter Channels (double-click to edit):", font=("", 16, "bold")).pack(side="left")
        ctk.CTkButton(frm2, text="+ Add Channel", width=110, command=self._add_or).pack(side="left", padx=10)
        ctk.CTkButton(frm2, text=_t("btn_delete"), width=90, fg_color="#d32f2f", hover_color="#b71c1c", command=self._del_or).pack(side="left")

        or_cols = ("Hotkey", "Model ID", "Action")
        self._or_tree = ttk.Treeview(frm, columns=or_cols, show="headings", height=4)
        for c, w in zip(or_cols, [150, 350, 150]):
            self._or_tree.heading(c, text=c); self._or_tree.column(c, width=w)
        self._or_tree.pack(fill="x", padx=5, pady=5)
        self._or_tree.bind("<Double-1>", self._edit_or_row)

        # ── Template Switch Hotkeys ──
        frm3 = ctk.CTkFrame(frm, fg_color="transparent")
        frm3.pack(fill="x", pady=(20, 4))
        ctk.CTkLabel(frm3, text="Template Switch Hotkeys (double-click to edit):", font=("", 16, "bold")).pack(side="left")
        ctk.CTkButton(frm3, text=_t("btn_add"), width=80, command=self._add_tpl_hk).pack(side="left", padx=10)
        ctk.CTkButton(frm3, text=_t("btn_delete"), width=90, fg_color="#d32f2f", hover_color="#b71c1c", command=self._del_tpl_hk).pack(side="left")

        tpl_hk_cols = ("Hotkey", "Template Key")
        self._tpl_hk_tree = ttk.Treeview(frm, columns=tpl_hk_cols, show="headings", height=4)
        for c, w in zip(tpl_hk_cols, [180, 300]):
            self._tpl_hk_tree.heading(c, text=c); self._tpl_hk_tree.column(c, width=w)
        self._tpl_hk_tree.pack(fill="x", padx=5, pady=5)
        self._tpl_hk_tree.bind("<Double-1>", self._edit_tpl_hk_row)

        ctk.CTkButton(frm, text=_t("btn_save") + " Hotkeys", command=self._save_hotkeys).pack(pady=20)
        self._refresh_all_hk_trees()

    def _refresh_all_hk_trees(self):
        for row in self._slots_tree.get_children(): self._slots_tree.delete(row)
        for act, slots in self._slots_data.items():
            for s in slots: self._slots_tree.insert("", "end", values=(act, s.get("key",""), s.get("provider",""), s.get("model","")))
        
        for row in self._or_tree.get_children(): self._or_tree.delete(row)
        for item in self._or_data: self._or_tree.insert("", "end", values=(item.get("key",""), item.get("model",""), item.get("action","")))

        for row in self._tpl_hk_tree.get_children(): self._tpl_hk_tree.delete(row)
        for item in self._tpl_hk_data: self._tpl_hk_tree.insert("", "end", values=(item.get("key",""), item.get("lang","")))

    def _add_slot(self):
        act = simpledialog.askstring("Add Slot", "Enter action name (e.g. av_fast, clipboard):")
        if act:
            if act not in self._slots_data: self._slots_data[act] = []
            self._slots_data[act].append({"key": "f1", "provider": "openai", "model": "gpt-4o-mini"})
            self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _del_slot(self):
        sel = self._slots_tree.selection()
        if sel:
            vals = self._slots_tree.item(sel[0])["values"]
            for s in self._slots_data[vals[0]]:
                if s["key"] == vals[1]: self._slots_data[vals[0]].remove(s); break
            self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _add_or(self):
        self._or_data.append({"key": "alt+x", "model": "google/gemini-2.0-flash-lite-001", "action": "vision_only"})
        self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _del_or(self):
        sel = self._or_tree.selection()
        if sel: self._or_data.pop(self._or_tree.index(sel[0])); self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _add_tpl_hk(self):
        self._tpl_hk_data.append({"key": "ctrl+alt+1", "lang": "japanese"})
        self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _del_tpl_hk(self):
        sel = self._tpl_hk_tree.selection()
        if sel: self._tpl_hk_data.pop(self._tpl_hk_tree.index(sel[0])); self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys")

    def _edit_tpl_hk_row(self, event):
        sel = self._tpl_hk_tree.selection()
        if not sel: return
        idx = self._tpl_hk_tree.index(sel[0])
        item = self._tpl_hk_data[idx]

        win = ctk.CTkToplevel(self)
        win.title("Edit Template Switch Hotkey")
        win.geometry("420x220")
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Hotkey:").grid(row=0, column=0, padx=10, pady=10)
        key_var = ctk.StringVar(value=item.get("key",""))
        ctk.CTkEntry(win, textvariable=key_var, width=150, state="readonly").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(win, text="◎ Record", width=80, command=lambda: self._capture_hotkey_dialog(key_var.get(), key_var.set)).grid(row=0, column=2)

        ctk.CTkLabel(win, text="Template Key:").grid(row=1, column=0, padx=10, pady=10)
        tpl_var = ctk.StringVar(value=item.get("lang",""))
        lang_keys = list(LANGUAGE_TEMPLATES.keys()) if LANGUAGE_TEMPLATES else []
        tpl_cb = ctk.CTkComboBox(win, values=lang_keys, variable=tpl_var, width=200)
        tpl_cb.set(tpl_var.get()); tpl_cb.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=10)

        def _save():
            self._tpl_hk_data[idx] = {"key": key_var.get(), "lang": tpl_cb.get()}
            self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys"); win.destroy()

        ctk.CTkButton(win, text="▣ Save", command=_save).grid(row=2, column=0, columnspan=3, pady=20)

    def _capture_hotkey_dialog(self, current_key, callback):
        """Record hotkey: captures keyboard events and sets the binding."""
        win = ctk.CTkToplevel(self)
        win.title("Record Hotkey")
        win.geometry("400x200")
        win.attributes('-topmost', True)
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Press the key combination you want to bind\n(e.g. Ctrl + Shift + X)", font=("", 14)).pack(pady=20)
        lbl = ctk.CTkLabel(win, text=current_key.upper(), font=("Consolas", 24, "bold"), text_color="#2196F3")
        lbl.pack(pady=10)
        
        captured = [current_key]
        def on_key(e):
            mods = []
            if e.state & 0x0004: mods.append("ctrl")
            if e.state & 0x0001: mods.append("shift")
            # Windows: Alt=0x0008；屏蔽 AltGr 的 Ctrl 误触（AltGr 同时置 Ctrl+Alt 位）
            is_alt = bool(e.state & 0x0008)
            is_ctrl_from_altgr = bool(e.state & 0x0004) and bool(e.state & 0x0008)
            if is_alt and not is_ctrl_from_altgr:
                mods = [m for m in mods if m != "ctrl"]  # AltGr 时移除误置的 ctrl
                mods.append("alt")
            elif is_alt:
                mods.append("alt")

            k = e.keysym.lower()
            if k not in ("control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r",
                         "caps_lock", "num_lock", "scroll_lock"):
                full_key = "+".join(mods + [k])
                lbl.configure(text=full_key.upper())
                captured[0] = full_key

        win.bind("<KeyPress>", on_key)
        
        btn_frm = ctk.CTkFrame(win, fg_color="transparent")
        btn_frm.pack(pady=10)
        ctk.CTkButton(btn_frm, text="✓ Confirm", command=lambda: [callback(captured[0]), win.destroy()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frm, text="Cancel", fg_color="gray", command=win.destroy).pack(side="left")

    def _edit_slot_row(self, event):
        sel = self._slots_tree.selection()
        if not sel: return
        vals = self._slots_tree.item(sel[0])["values"]
        act = vals[0]

        # 用树中行的物理顺序（当前 act 内的第几条）精确定位数据，避免 key+provider 重复时错位
        slot_index = 0
        for iid in self._slots_tree.get_children():
            if iid == sel[0]:
                break
            if self._slots_tree.item(iid)["values"][0] == act:
                slot_index += 1
        slot = self._slots_data[act][slot_index]
        key, prv, mod = slot.get("key",""), slot.get("provider",""), slot.get("model","")
        
        win = ctk.CTkToplevel(self)
        win.title(f"Edit Slot - {act}")
        win.geometry("450x300")
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Hotkey:").grid(row=0, column=0, padx=10, pady=10)
        key_var = ctk.StringVar(value=key)
        key_ent = ctk.CTkEntry(win, textvariable=key_var, width=150, state="readonly")
        key_ent.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(win, text="◎ Re-record", width=80, command=lambda: self._capture_hotkey_dialog(key_var.get(), key_var.set)).grid(row=0, column=2)

        ctk.CTkLabel(win, text="Provider:").grid(row=1, column=0, padx=10, pady=10)
        prv_cb = ctk.CTkComboBox(win, values=list(API_KEYS.keys()), width=240)
        prv_cb.set(prv); prv_cb.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(win, text="Model:").grid(row=2, column=0, padx=10, pady=10)
        mod_var = ctk.StringVar(value=mod)
        ctk.CTkEntry(win, textvariable=mod_var, width=240).grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=10)

        def _save():
            # 直接按 index 更新，不再依赖 key+provider 匹配
            self._slots_data[act][slot_index] = {
                "key": key_var.get(), "provider": prv_cb.get(), "model": mod_var.get()
            }
            self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys"); win.destroy()

        ctk.CTkButton(win, text="▣ Save", command=_save).grid(row=3, column=0, columnspan=3, pady=20)

    def _edit_or_row(self, event):
        sel = self._or_tree.selection()
        if not sel: return
        idx = self._or_tree.index(sel[0])
        item = self._or_data[idx]
        
        win = ctk.CTkToplevel(self)
        win.title("Edit OpenRouter Channel")
        win.geometry("450x300")
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Hotkey:").grid(row=0, column=0, padx=10, pady=10)
        key_var = ctk.StringVar(value=item.get("key"))
        ctk.CTkEntry(win, textvariable=key_var, width=150, state="readonly").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(win, text="◎ Record", width=80, command=lambda: self._capture_hotkey_dialog(key_var.get(), key_var.set)).grid(row=0, column=2)

        ctk.CTkLabel(win, text="OpenRouter Model:").grid(row=1, column=0, padx=10, pady=10)
        mod_var = ctk.StringVar(value=item.get("model"))
        ctk.CTkEntry(win, textvariable=mod_var, width=240).grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(win, text="Action:").grid(row=2, column=0, padx=10, pady=10)
        act_cb = ctk.CTkComboBox(win, values=list(SLOTS_CONFIG.keys()), width=240)
        act_cb.set(item.get("action", "vision_only")); act_cb.grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=10)

        def _save():
            self._or_data[idx] = {"key": key_var.get(), "model": mod_var.get(), "action": act_cb.get()}
            self._refresh_all_hk_trees(); self.mark_unsaved("Hotkeys"); win.destroy()

        ctk.CTkButton(win, text="▣ Save", command=_save).grid(row=3, column=0, columnspan=3, pady=20)

    def _save_hotkeys(self):
        # 热键冲突检测：保存前遍历所有热键，发现重复则阻止
        all_keys = []
        for act, slots in self._slots_data.items():
            for s in slots:
                if s.get("key"): all_keys.append((s["key"], f"Slot[{act}]"))
        for item in self._or_data:
            if item.get("key"): all_keys.append((item["key"], f"OpenRouter[{item.get('model','')}]"))
        for item in self._tpl_hk_data:
            if item.get("key"): all_keys.append((item["key"], f"Template[{item.get('lang','')}]"))

        seen = {}
        conflicts = []
        for k, label in all_keys:
            if k in seen:
                conflicts.append(f"  {k}  ←→  {seen[k]}  vs  {label}")
            else:
                seen[k] = label
        if conflicts:
            messagebox.showerror("Hotkey Conflict", "The following hotkeys conflict. Please fix before saving:\n\n" + "\n".join(conflicts))
            return

        curr = _load_runtime_settings()
        curr["SLOTS_CONFIG"] = self._slots_data
        curr["OPENROUTER_HOTKEYS"] = self._or_data
        curr["TEMPLATE_SWITCH_HOTKEYS"] = self._tpl_hk_data
        if _save_runtime_settings(curr): self.mark_saved("Hotkeys")


    # ─────────────────────────────────────────────────────────────
    # ── 13. 深渊日志台 (实装：层级过滤与 Payload 外科手术) ──
    # ─────────────────────────────────────────────────────────────
    def _build_log_frame(self, frm):
        ctk.CTkLabel(frm, text="Logs & Retry Queue", font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- Error Log ---
        ctk.CTkLabel(frm, text="Error Log", font=("", 16, "bold")).pack(anchor="w", pady=5)
        btn_frm1 = ctk.CTkFrame(frm, fg_color="transparent"); btn_frm1.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frm1, text="↺ Refresh", command=self._refresh_log).pack(side="left", padx=5)
        ctk.CTkButton(btn_frm1, text="✕ Clear Log", fg_color="#d32f2f", hover_color="#b71c1c", command=self._clear_log).pack(side="left", padx=5)

        ctk.CTkLabel(btn_frm1, text="Level Filter:").pack(side="left", padx=(20, 5))
        self._log_filter = ctk.CTkComboBox(btn_frm1, values=["All", "WARNING", "ERROR"], command=lambda e: self._refresh_log())
        self._log_filter.set("All"); self._log_filter.pack(side="left")

        self._log_txt = ctk.CTkTextbox(frm, height=200, font=("Consolas", 12))
        self._log_txt.pack(fill="x", pady=5)

        # --- Retry Queue ---
        ctk.CTkLabel(frm, text="API Retry Queue (double-click to edit payload)", font=("", 16, "bold")).pack(anchor="w", pady=(20, 5))
        btn_frm2 = ctk.CTkFrame(frm, fg_color="transparent"); btn_frm2.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frm2, text="↺ Refresh", command=self._refresh_retry_queue).pack(side="left", padx=5)
        ctk.CTkButton(btn_frm2, text="✕ Delete Selected", fg_color="#d32f2f", hover_color="#b71c1c", command=self._delete_retry_row).pack(side="left", padx=5)

        rq_cols = ("ID", "Provider", "Model", "Retries", "Payload Summary")
        self._retry_tree = ttk.Treeview(frm, columns=rq_cols, show="headings", height=8)
        for c, w in zip(rq_cols, [40, 100, 200, 60, 400]):
            self._retry_tree.heading(c, text=c); self._retry_tree.column(c, width=w)
        self._retry_tree.pack(fill="x", padx=5, pady=5)
        self._retry_tree.bind("<Double-1>", self._edit_payload_dialog)

        self._refresh_log()
        self._refresh_retry_queue()

    def _refresh_log(self):
        self._log_txt.configure(state="normal")
        self._log_txt.delete("1.0", "end")

        # 先收集所有行，然后一次性插入
        all_text = []
        for path in [_get_effective("LOG_PATH", LOG_PATH), _config_log_path]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        src = os.path.basename(path).split('_')[0]
                        for line in f:
                            all_text.append(f"[{src}] {line}" if not line.startswith("[") else line)
                except Exception as e:
                    all_text.append(f"[Sys] Read error {path}: {e}\n")

        flt = self._log_filter.get()
        if flt != "All":
            all_text = [l for l in all_text if f"[{flt}]" in l]

        # 限制行数并一次性插入
        if len(all_text) > 1000:
            all_text = [f"... (truncated — showing last 1000 of {len(all_text)} lines) ...\n"] + all_text[-1000:]

        # 禁用Textbox的刷新，一次性插入所有文本
        self._log_txt.configure(state="disabled")
        self._log_txt.configure(state="normal")
        self._log_txt.insert("end", "".join(all_text) if all_text else "No errors logged.")
        self._log_txt.configure(state="disabled")

    def _clear_log(self):
        if not messagebox.askyesno("Clear Log", "Permanently delete all local error logs? This cannot be undone."): return
        for path in [_get_effective("LOG_PATH", LOG_PATH), _config_log_path]:
            norm_path = os.path.normpath(path)
            # 关闭并替换持有该文件的 logging FileHandler，解决 Windows 文件锁问题
            replaced = False
            for h in logging.root.handlers[:]:
                if isinstance(h, logging.FileHandler) and os.path.normpath(h.baseFilename) == norm_path:
                    h.close()
                    logging.root.removeHandler(h)
                    try:
                        new_h = logging.FileHandler(norm_path, mode='w', encoding='utf-8')
                        new_h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
                        logging.root.addHandler(new_h)
                        replaced = True
                    except Exception:
                        pass
                    break
            if not replaced:
                try:
                    open(norm_path, 'w', encoding='utf-8').close()
                except Exception:
                    pass
        self._refresh_log()

    def _refresh_retry_queue(self):
        for row in self._retry_tree.get_children(): self._retry_tree.delete(row)
        try:
            conn = get_db_conn()
            try:
                rows = conn.execute("SELECT id, provider, model, retry_count, payload_json FROM retry_queue ORDER BY id").fetchall()
            finally:
                conn.close()
            for r in rows:
                try:
                    p = json.loads(r[4])
                    sum_txt = f"Txt={str(p.get('text',''))[:20]} Img={'yes' if p.get('img') else 'no'} Aud={'yes' if p.get('audio') else 'no'}"
                except: sum_txt = str(r[4])[:50]
                self._retry_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], sum_txt))
        except Exception as e: self.show_toast(f"Failed to read queue: {e}", "red")

    def _delete_retry_row(self):
        sel = self._retry_tree.selection()
        if not sel: return
        try:
            conn = get_db_conn()
            try:
                conn.execute("DELETE FROM retry_queue WHERE id=?", (self._retry_tree.item(sel[0])["values"][0],))
                conn.commit()
            finally:
                conn.close()
            self._retry_tree.delete(sel[0])
            self.show_toast("Retry task deleted.")
        except Exception as e:
            self.show_toast(f"Delete failed: {e}", "red")

    def _edit_payload_dialog(self, event):
        """JSON payload editor for retry queue tasks."""
        sel = self._retry_tree.selection()
        if not sel: return
        row_id = self._retry_tree.item(sel[0])["values"][0]
        
        try:
            conn = get_db_conn()
            try:
                task = conn.execute("SELECT provider, model, payload_json FROM retry_queue WHERE id=?", (row_id,)).fetchone()
            finally:
                conn.close()
            if not task: return
        except Exception as e: self.show_toast(str(e), "red"); return

        win = ctk.CTkToplevel(self)
        win.title(f"Edit Payload - ID:{row_id} ({task[0]}/{task[1]})")
        win.geometry("700x500")
        win.after(150, win.grab_set)
        
        ctk.CTkLabel(win, text="Warning: only edit the 'text' field — do not break JSON structure!", text_color="orange", font=("", 14, "bold")).pack(pady=10)
        
        txt = ctk.CTkTextbox(win, font=("Consolas", 14), wrap="none")
        txt.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 美化格式化输出
        try:
            pretty_json = json.dumps(json.loads(task[2]), ensure_ascii=False, indent=4)
            txt.insert("1.0", pretty_json)
        except:
            txt.insert("1.0", task[2])

        def _save_and_retry():
            new_payload = txt.get("1.0", "end").strip()
            try:
                json.loads(new_payload) # 语法校验防呆
                conn = get_db_conn()
                try:
                    # 重置重试次数，更新 payload
                    conn.execute("UPDATE retry_queue SET payload_json=?, retry_count=0 WHERE id=?", (new_payload, row_id))
                    conn.commit()
                finally:
                    conn.close()
                self.show_toast("✓ Payload updated. Task reactivated for retry.")
                self._refresh_retry_queue()
                win.destroy()
            except Exception as e:
                messagebox.showerror("JSON Parse Error", f"Invalid JSON — check commas, quotes, and brackets.\nDetails: {e}")

        btn_frm = ctk.CTkFrame(win, fg_color="transparent")
        btn_frm.pack(pady=15)
        ctk.CTkButton(btn_frm, text="↑ Save & Retry", fg_color="#4CAF50", hover_color="#388E3C", command=_save_and_retry).pack(side="left", padx=10)
        ctk.CTkButton(btn_frm, text="Cancel", fg_color="gray", command=win.destroy).pack(side="left")

    # ─────────────────────────────────────────────────────────────
    # ── 💡 究极极客体验：Cmd+K 全局命令面板 (Spotlight) ──
    # ─────────────────────────────────────────────────────────────
    def _show_cmd_palette(self, event=None):
        """Open the Cmd+K command palette (spotlight search)."""
        if hasattr(self, "_cmd_win") and self._cmd_win.winfo_exists():
            self._cmd_win.focus_force(); return

        self._cmd_win = ctk.CTkToplevel(self)
        self._cmd_win.title("")
        self._cmd_win.geometry("500x300")
        # Windows 下 overrideredirect(True) 会导致窗口无法获取焦点，仅在非 Windows 平台启用
        if sys.platform != "win32":
            self._cmd_win.overrideredirect(True)
        self._cmd_win.attributes('-topmost', True)
        
        # 居中屏幕
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 150
        self._cmd_win.geometry(f"+{x}+{y}")

        # 亚克力背景底板
        bg_frm = ctk.CTkFrame(self._cmd_win, corner_radius=15, border_width=1, border_color="gray30")
        bg_frm.pack(fill="both", expand=True)

        search_var = ctk.StringVar()
        entry = ctk.CTkEntry(bg_frm, textvariable=search_var, font=("", 20), placeholder_text="Search settings, features or pages (e.g. obs, proxy)...", corner_radius=10, height=45)
        entry.pack(fill="x", padx=15, pady=15)
        entry.focus_set()

        res_list = tk.Listbox(bg_frm, bg="#2b2b2b", fg="white", font=("", 14), borderwidth=0, highlightthickness=0, selectbackground="#1f538d")
        res_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Global route table
        routes = {
            "OBS": "OBS", "recording": "OBS", "password": "OBS",
            "Anki": "Anki", "deck": "Anki", "sync": "Anki",
            "hotkey": "Hotkeys", "shortcut": "Hotkeys", "OpenRouter": "Hotkeys",
            "proxy": "Paths", "Proxy": "Paths", "path": "Paths", "Teldrive": "Paths",
            "API": "AI Models", "model": "AI Models", "key": "AI Models",
            "template": "Prompts", "prompt": "Prompts", "Prompt": "Prompts",
            "log": "Logs", "error": "Logs", "retry": "Logs",
            "database": "Database", "backup": "Database", "clean": "Database",
            "export": "Data", "CSV": "Data",
            "search": "Memory", "vocab": "Memory",
            "stats": "Console", "overview": "Console"
        }

        def _update_search(*args):
            q = search_var.get().lower()
            res_list.delete(0, tk.END)
            matches = []
            for kw, target in routes.items():
                if q in kw.lower() or q in target.lower():
                    if target not in matches: matches.append(target)
            for m in matches: res_list.insert(tk.END, f"Go -> {m}")
            if not matches: res_list.insert(tk.END, "No results found...")

        def _execute_jump(event=None):
            sel = res_list.curselection()
            if not sel: return
            item_text = res_list.get(sel[0])
            # Skip "No results" placeholder row
            if not item_text.startswith("Go -> "): return
            target = item_text.replace("Go -> ", "")
            if target in self.menu_buttons:
                self._select_menu(target)
                self._cmd_win.destroy()

        def _on_return(e):
            if res_list.size() == 0: return
            # 若用户未在列表中选中任何项，默认跳转第一条
            if not res_list.curselection():
                res_list.selection_set(0)
            _execute_jump()

        search_var.trace_add("write", _update_search)
        res_list.bind("<Double-1>", _execute_jump)
        entry.bind("<Return>", _on_return)
        self._cmd_win.bind("<Escape>", lambda e: self._cmd_win.destroy())
        _update_search()


    # ─────────────────────────────────────────────────────────────
    # ── 9. OBS 物理桥接 (解绑密码可见性与文件对话框) ──
    # ─────────────────────────────────────────────────────────────
    def _build_obs_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_obs"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.obs_vars = {}
        
        # WebSocket connection
        ctk.CTkLabel(frm, text="WebSocket Auth:", font=("", 16, "bold")).pack(anchor="w", pady=10)
        net_frm = ctk.CTkFrame(frm, fg_color="transparent"); net_frm.pack(fill="x")
        
        ctk.CTkLabel(net_frm, text="OBS Host IP:").grid(row=0, column=0, padx=5, pady=5)
        self.obs_vars["OBS_WS_HOST"] = ctk.StringVar(value=_get_effective("OBS_WS_HOST", OBS_WS_HOST))
        ctk.CTkEntry(net_frm, textvariable=self.obs_vars["OBS_WS_HOST"], width=150).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(net_frm, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.obs_vars["OBS_WS_PORT"] = ctk.StringVar(value=str(_get_effective("OBS_WS_PORT", OBS_WS_PORT)))
        ctk.CTkEntry(net_frm, textvariable=self.obs_vars["OBS_WS_PORT"], width=80).grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(net_frm, text="Password:").grid(row=1, column=0, padx=5, pady=10)
        self.obs_vars["OBS_WS_PASSWORD"] = ctk.StringVar(value=_get_effective("OBS_WS_PASSWORD", OBS_WS_PASSWORD))
        pwd_ent = ctk.CTkEntry(net_frm, textvariable=self.obs_vars["OBS_WS_PASSWORD"], width=200, show="*")
        pwd_ent.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=10)
        ctk.CTkButton(net_frm, text="◉", width=40, command=lambda: pwd_ent.configure(show="" if pwd_ent.cget("show") == "*" else "*")).grid(row=1, column=3, sticky="w")

        # Recording path and strategy
        ctk.CTkLabel(frm, text="Recording & Buffer:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 10))
        
        path_frm = ctk.CTkFrame(frm, fg_color="transparent"); path_frm.pack(fill="x")
        ctk.CTkLabel(path_frm, text="Watch Dir (OBS output):").grid(row=0, column=0, padx=5)
        self.obs_vars["OBS_WATCH_DIR"] = ctk.StringVar(value=_get_effective("OBS_WATCH_DIR", OBS_WATCH_DIR))
        ctk.CTkEntry(path_frm, textvariable=self.obs_vars["OBS_WATCH_DIR"], width=350).grid(row=0, column=1, padx=5)
        ctk.CTkButton(path_frm, text="⊡ Browse", width=60, command=lambda: self.obs_vars["OBS_WATCH_DIR"].set(filedialog.askdirectory() or self.obs_vars["OBS_WATCH_DIR"].get())).grid(row=0, column=2)

        self.obs_vars["OBS_AUTO_START_REPLAY_BUFFER"] = ctk.BooleanVar(value=_get_effective("OBS_AUTO_START_REPLAY_BUFFER", OBS_AUTO_START_REPLAY_BUFFER))
        ctk.CTkSwitch(frm, text="Auto-start OBS replay buffer", variable=self.obs_vars["OBS_AUTO_START_REPLAY_BUFFER"]).pack(anchor="w", padx=10, pady=10)

        self.obs_vars["OBS_KEEP_SOURCE_FILE"] = ctk.BooleanVar(value=_get_effective("OBS_KEEP_SOURCE_FILE", OBS_KEEP_SOURCE_FILE))
        ctk.CTkSwitch(frm, text="Keep original OBS video after processing", variable=self.obs_vars["OBS_KEEP_SOURCE_FILE"]).pack(anchor="w", padx=10, pady=5)

        to_frm = ctk.CTkFrame(frm, fg_color="transparent"); to_frm.pack(fill="x", pady=5)
        ctk.CTkLabel(to_frm, text="Replay poll timeout (sec):").pack(side="left", padx=5)
        self.obs_vars["OBS_POLL_TIMEOUT"] = ctk.StringVar(value=str(_get_effective("OBS_POLL_TIMEOUT", OBS_POLL_TIMEOUT)))
        ctk.CTkEntry(to_frm, textvariable=self.obs_vars["OBS_POLL_TIMEOUT"], width=80).pack(side="left")

        # Controls
        ctrl_frm = ctk.CTkFrame(frm, fg_color="transparent"); ctrl_frm.pack(fill="x", pady=20)
        ctk.CTkButton(ctrl_frm, text="◌ Test Connection", fg_color="#1976D2", hover_color="#1565C0", command=self._test_obs).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frm, text="▣ Save OBS", command=self._save_obs).pack(side="left", padx=15)
        self.obs_status_lbl = ctk.CTkLabel(ctrl_frm, text="", text_color="green")
        self.obs_status_lbl.pack(side="left")

    def _test_obs(self):
        # 移入后台线程，避免 self.update() 引发 tkinter 重入崩溃
        self.obs_status_lbl.configure(text="Connecting...", text_color="orange")
        host = self.obs_vars["OBS_WS_HOST"].get()
        port = self.obs_vars["OBS_WS_PORT"].get()
        pwd  = self.obs_vars["OBS_WS_PASSWORD"].get()
        def _do():
            try:
                import obsws_python as obs
                cl = obs.ReqClient(host=host, port=int(port), password=pwd)
                ver = cl.get_version()
                self.after(0, lambda: self.obs_status_lbl.configure(text=f"✓ Connected! OBS {ver.obs_version}", text_color="#4CAF50"))
            except Exception as e:
                self.after(0, lambda: self.obs_status_lbl.configure(text=f"✕ Connection failed: {e}", text_color="#F44336"))
        threading.Thread(target=_do, daemon=True).start()

    def _save_obs(self):
        curr = _load_runtime_settings()
        for k, v in self.obs_vars.items():
            val = v.get()
            if k in ["OBS_WS_PORT", "OBS_POLL_TIMEOUT"]:
                try: val = int(val)
                except: return messagebox.showerror("Format Error", f"{k} must be an integer.")
            curr[k] = val
        if _save_runtime_settings(curr): self.mark_saved("OBS")


    # ─────────────────────────────────────────────────────────────
    # ── 10. Anki 突触 (解绑私有化标签与字段) ──
    # ─────────────────────────────────────────────────────────────
    def _build_anki_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_anki"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.anki_vars = {}
        
        # 连通性设置
        conn_frm = ctk.CTkFrame(frm, fg_color="transparent"); conn_frm.pack(fill="x", pady=5)
        ctk.CTkLabel(conn_frm, text="AnkiConnect IP:").grid(row=0, column=0, padx=5)
        self.anki_vars["ANKI_CONNECT_IP"] = ctk.StringVar(value=_get_effective("ANKI_CONNECT_IP", "127.0.0.1"))
        ctk.CTkEntry(conn_frm, textvariable=self.anki_vars["ANKI_CONNECT_IP"], width=120).grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(conn_frm, text="Port:").grid(row=0, column=2, padx=5)
        self.anki_vars["ANKI_CONNECT_PORT"] = ctk.StringVar(value=str(_get_effective("ANKI_CONNECT_PORT", ANKI_CONNECT_PORT)))
        ctk.CTkEntry(conn_frm, textvariable=self.anki_vars["ANKI_CONNECT_PORT"], width=80).grid(row=0, column=3, padx=5)
        
        self.anki_vars["ANKI_BYPASS_PROXY"] = ctk.BooleanVar(value=_get_effective("ANKI_BYPASS_PROXY", ANKI_BYPASS_PROXY))
        ctk.CTkSwitch(conn_frm, text="Bypass system proxy", variable=self.anki_vars["ANKI_BYPASS_PROXY"]).grid(row=0, column=4, padx=15)

        # Deck & field mapping
        ctk.CTkLabel(frm, text="Deck & Field Mapping:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 10))
        map_frm = ctk.CTkFrame(frm, fg_color="transparent"); map_frm.pack(fill="x")
        
        ctk.CTkLabel(map_frm, text="Target Deck:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.anki_vars["ANKI_DECK_NAME"] = ctk.StringVar(value=_get_effective("ANKI_DECK_NAME", ANKI_DECK_NAME))
        self.anki_deck_cb = ctk.CTkComboBox(map_frm, variable=self.anki_vars["ANKI_DECK_NAME"], width=200)
        self.anki_deck_cb.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(map_frm, text="↺ Fetch Decks", width=100, fg_color="#1976D2", hover_color="#1565C0", command=self._fetch_anki_decks).grid(row=0, column=2, padx=5)
        
        ctk.CTkLabel(map_frm, text="Front Field:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.anki_vars["ANKI_FRONT_FIELD"] = ctk.StringVar(value=_get_effective("ANKI_FRONT_FIELD", "Front"))
        ctk.CTkEntry(map_frm, textvariable=self.anki_vars["ANKI_FRONT_FIELD"], width=200).grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(map_frm, text="Back Field:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.anki_vars["ANKI_BACK_FIELD"] = ctk.StringVar(value=_get_effective("ANKI_BACK_FIELD", "Back"))
        ctk.CTkEntry(map_frm, textvariable=self.anki_vars["ANKI_BACK_FIELD"], width=200).grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(map_frm, text="Base Tags:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tags = _get_effective("ANKI_BASE_TAGS", ["Omni-Arsenal"])
        self.anki_vars["ANKI_BASE_TAGS"] = ctk.StringVar(value=",".join(tags) if isinstance(tags, list) else tags)
        ctk.CTkEntry(map_frm, textvariable=self.anki_vars["ANKI_BASE_TAGS"], width=200, placeholder_text="comma-separated").grid(row=3, column=1, padx=5, pady=5)

        # Display strategy
        ctk.CTkLabel(frm, text="Display Strategy:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 10))
        strt_frm = ctk.CTkFrame(frm, fg_color="transparent"); strt_frm.pack(fill="x")
        
        ctk.CTkLabel(strt_frm, text="Front Content:").grid(row=0, column=0, padx=5, pady=5)
        self.anki_vars["ANKI_FRONT_CONTENT"] = ctk.StringVar(value=_get_effective("ANKI_FRONT_CONTENT", ANKI_FRONT_CONTENT))
        ctk.CTkComboBox(strt_frm, variable=self.anki_vars["ANKI_FRONT_CONTENT"], values=["both", "core_word", "original_text"], width=150).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(strt_frm, text="Audio Side:").grid(row=0, column=2, padx=(20,5), pady=5)
        self.anki_vars["ANKI_AUDIO_SIDE"] = ctk.StringVar(value=_get_effective("ANKI_AUDIO_SIDE", ANKI_AUDIO_SIDE))
        ctk.CTkComboBox(strt_frm, variable=self.anki_vars["ANKI_AUDIO_SIDE"], values=["front", "back"], width=100).grid(row=0, column=3, padx=5, pady=5)

        self.anki_vars["ANKI_SHOW_ORIGINAL_ON_BACK"] = ctk.BooleanVar(value=_get_effective("ANKI_SHOW_ORIGINAL_ON_BACK", ANKI_SHOW_ORIGINAL_ON_BACK))
        ctk.CTkSwitch(frm, text="Show original text on back side (context anchor)", variable=self.anki_vars["ANKI_SHOW_ORIGINAL_ON_BACK"]).pack(anchor="w", padx=10, pady=10)

        ctk.CTkButton(frm, text="▣ Save Anki", command=self._save_anki).pack(pady=20)

    def _anki_req(self, payload):
        import urllib.request
        ip   = self.anki_vars["ANKI_CONNECT_IP"].get() or "127.0.0.1"
        port_str = self.anki_vars["ANKI_CONNECT_PORT"].get() or "8765"
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"AnkiConnect port must be an integer, got: '{port_str}'")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if self.anki_vars["ANKI_BYPASS_PROXY"].get() else urllib.request.build_opener()
        req = urllib.request.Request(f"http://{ip}:{port}", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with opener.open(req, timeout=3) as r: return json.loads(r.read().decode("utf-8"))

    def _fetch_anki_decks(self):
        # 移入后台线程，避免网络阻塞主线程
        def _do():
            try:
                res = self._anki_req({"action": "deckNames", "version": 6})
                def _update():
                    self.anki_deck_cb.configure(values=res.get("result", []))
                    self.show_toast(f"✓ Fetched {len(res.get('result', []))} decks.")
                self.after(0, _update)
            except Exception as e:
                self.after(0, lambda: self.show_toast(f"Fetch failed: {e}", "red"))
        threading.Thread(target=_do, daemon=True).start()

    def _save_anki(self):
        curr = _load_runtime_settings()
        for k, v in self.anki_vars.items():
            val = v.get()
            if k == "ANKI_CONNECT_PORT":
                try: val = int(val)
                except: return messagebox.showerror("Format Error", "Port must be an integer.")
            elif k == "ANKI_BASE_TAGS":
                val = [x.strip() for x in str(val).split(",") if x.strip()]
            curr[k] = val
        if _save_runtime_settings(curr): self.mark_saved("Anki")


    # ─────────────────────────────────────────────────────────────
    # ── 14. 路径与隧道 (底层 IO 重定向) ──
    # ─────────────────────────────────────────────────────────────
    def _build_paths_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_paths"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.path_vars = {}
        paths = [
            ("ASSETS_PATH", "Assets Dir (images/audio)", ASSETS_PATH, True),
            ("VOCAB_FOLDER", "Vocab Output Dir (Markdown/CSV)", VOCAB_FOLDER, True),
            ("DB_PATH", "Database File (*.db)", DB_PATH, False),
            ("LOG_PATH", "Error Log File (*.log)", LOG_PATH, False),
            ("VN_OUTPUT_DIR", "Galgame Script Output Dir", VN_OUTPUT_DIR, True),
            ("TELDRIVE_MOUNT_PATH", "Teldrive Mount Path", TELDRIVE_MOUNT_PATH, True),
        ]
        
        for k, lbl, dflt, is_dir in paths:
            row_frm = ctk.CTkFrame(frm, fg_color="transparent"); row_frm.pack(fill="x", pady=5)
            ctk.CTkLabel(row_frm, text=f"{lbl}:", width=250, anchor="e").pack(side="left", padx=5)
            
            var = ctk.StringVar(value=_get_effective(k, dflt))
            self.path_vars[k] = var
            ctk.CTkEntry(row_frm, textvariable=var, width=400).pack(side="left", padx=5)
            
            def _browse(v=var, d=is_dir):
                res = filedialog.askdirectory() if d else filedialog.asksaveasfilename(initialfile=os.path.basename(v.get()))
                if res: v.set(res)
            ctk.CTkButton(row_frm, text="⊡ Browse", width=60, command=_browse).pack(side="left")

        ctk.CTkLabel(frm, text="Network Proxy:", font=("", 16, "bold")).pack(anchor="w", pady=(20, 10))
        net_frm = ctk.CTkFrame(frm, fg_color="transparent"); net_frm.pack(fill="x")
        ctk.CTkLabel(net_frm, text="PROXY_URL:").pack(side="left", padx=5)
        self.path_vars["PROXY_URL"] = ctk.StringVar(value=_get_effective("PROXY_URL", PROXY_URL))
        ctk.CTkEntry(net_frm, textvariable=self.path_vars["PROXY_URL"], width=400, placeholder_text="http://127.0.0.1:7890 (leave blank for direct connection)").pack(side="left", padx=5)

        ctk.CTkButton(frm, text="▣ Save Paths", command=self._save_paths).pack(pady=30)

    def _save_paths(self):
        prev_db = os.path.normpath(_get_effective("DB_PATH", DB_PATH))
        curr = _load_runtime_settings()
        for k, v in self.path_vars.items():
            # 统一路径分隔符，防止 Windows 混用 / 和 \ 导致部分 API 解析失败
            curr[k] = os.path.normpath(v.get()) if v.get() else v.get()
        if _save_runtime_settings(curr):
            # DB_PATH 变更时，对新路径执行 init_db()，确保表结构存在
            new_db = os.path.normpath(_get_effective("DB_PATH", DB_PATH))
            if new_db != prev_db:
                try:
                    init_db()
                except Exception as e:
                    messagebox.showwarning("New Database Init", f"DB_PATH changed, but initializing new database failed: {e}\nCheck path permissions.")
            self.mark_saved("Paths")


    # ─────────────────────────────────────────────────────────────
    # ── 15. 引擎总揽 (全局快照只读视图) ──
    # ─────────────────────────────────────────────────────────────
    def _build_config_frame(self, frm):
        ctk.CTkLabel(frm, text=_t("title_overview"), font=("", 24, "bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(frm, text="Merged view of config.py defaults and izumi_runtime_settings.json overrides.", text_color="gray").pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(frm, text="↺ Refresh Snapshot", command=self._refresh_config_snap).pack(anchor="w", pady=5)
        
        self.snap_txt = ctk.CTkTextbox(frm, height=500, font=("Consolas", 13), wrap="none")
        self.snap_txt.pack(fill="both", expand=True, pady=10)
        self._refresh_config_snap()

    def _refresh_config_snap(self):
        rt = _load_runtime_settings()
        def _v(key, default): return rt.get(key, default)

        # 用显式字典替代 eval()，彻底消除 NameError 崩溃风险
        known_defaults = {
            "ENABLE_LOCAL_OCR":           ENABLE_LOCAL_OCR,
            "ENABLE_LOCAL_WHISPER":       ENABLE_LOCAL_WHISPER,
            "ENABLE_AUTONOMOUS_LISTENER": ENABLE_AUTONOMOUS_LISTENER,
            "CLAUDE_MAX_TOKENS":          2048,
            "VIDEO_EXTRACT_FRAMES":       4,
            "CIRCUIT_BREAKER_LIMIT":      CIRCUIT_BREAKER_LIMIT,
        }
        
        lines = [
            "// ====== Izumi Omni-Arsenal V5.0 Runtime State ======",
            f"  TARGET_LANGUAGE          : {_v('TARGET_LANGUAGE', TARGET_LANGUAGE)}",
            f"  ACTIVE_TEMPLATE          : {_v('ACTIVE_TEMPLATE', ACTIVE_TEMPLATE)}",
            f"  DB_PATH                  : {_v('DB_PATH', DB_PATH)}",
            "",
            "// ====== API Keys ======"
        ]
        keys = _v("API_KEYS", API_KEYS)
        for p, k in keys.items(): lines.append(f"  [{p:<10}] : {'configured (len:'+str(len(k))+')' if k else 'not set'}")

        lines.append("\n// ====== Behavior ======")
        for k, default in known_defaults.items():
            lines.append(f"  {k:<30}: {_v(k, default)}")

        lines.append("\n// ====== Integrations ======")
        lines.append(f"  OBS_WS_HOST      : {_v('OBS_WS_HOST', OBS_WS_HOST)}:{_v('OBS_WS_PORT', OBS_WS_PORT)}")
        lines.append(f"  ANKI_CONNECT     : {_v('ANKI_CONNECT_IP', '127.0.0.1')}:{_v('ANKI_CONNECT_PORT', ANKI_CONNECT_PORT)}")
        lines.append(f"  ANKI_DECK        : {_v('ANKI_DECK_NAME', ANKI_DECK_NAME)}")

        self.snap_txt.configure(state="normal")
        self.snap_txt.delete("1.0", "end")
        self.snap_txt.insert("end", "\n".join(lines))
        self.snap_txt.configure(state="disabled")

if __name__ == "__main__":
    app = IzumiOmniUI()
    app.mainloop()
