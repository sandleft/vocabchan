# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> 按一个键，AI 解析，自动存进 Anki。就这么简单。

> ⚠️ **Windows EXE 版本目前处于测试阶段，可能存在 bug，建议先用 Python 源码运行。**

---

## 这是什么

VocabChan 是一个专为"边看边学"设计的语言学习工具。

看日剧、刷动漫、玩游戏、看 YouTube，遇到不懂的句子，按一个快捷键，它就会自动截图（或者录音、或者读剪贴板），发给 AI，然后把语法分析、单词解释、发音备注、使用场景全部给你，同时自动生成 Anki 卡片和 Obsidian 笔记。不需要切窗口，不需要复制粘贴，继续看就行。

---

## 能做什么

- **截图分析** — 截取当前屏幕，让 AI 解释画面内容
- **音频捕获** — 录制麦克风或系统音频，自动转录并分析
- **OBS 视频回溯** — 抓取 OBS 最近几秒的录像发给 AI 分析
- **剪贴板模式** — 复制任意文本，一键获取解析
- **批量导入** — 粘贴一整个词表，全部自动处理
- **Anki 同步** — 自动生成包含单词、原句、完整分析的闪卡
- **Obsidian 同步** — 每条记录自动保存为结构化笔记
- **间隔复习提醒** — 自动提醒你复习 3、7、14 天前的词条
- **词汇搜索与统计** — 搜索历史词条，查看学习数据，导出 CSV 或 TXT
- **快捷键切换语言** — 随时切换日语、英语等模板

### 支持的 AI 模型
Google Gemini · OpenAI · Claude · DeepSeek · Grok · 通义千问 · Kimi · 豆包 · MiniMax · OpenRouter

### 支持的语言
日语 · 英语 · 中文 · 西班牙语 · 法语 · 德语 · 韩语 · 意大利语 · 葡萄牙语 · 阿拉伯语 · 以及自定义模板

---

## 怎么用

### 需要准备的东西
- Python 3.10+
- [Anki](https://apps.ankiweb.net/) + [AnkiConnect 插件](https://ankiweb.net/shared/info/2055492159)
- [Obsidian](https://obsidian.md/)
- 至少一个上面列出的 AI 服务的 API Key
- OBS Studio（只有用到视频功能才需要）
- 可选：[Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper) 本地音频转录
- 可选：PaddleOCR 本地文字识别

### 安装

```bash
git clone https://github.com/你的用户名/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### 配置

打开 `config.py`，填写你要用的 API Key 和路径：

```python
# 填入你的 API Key，用哪个填哪个
API_KEYS = {
    "google": "你的key",
    "openai": "你的key",
    # ...
}

# OBS 相关（只用视频功能才需要填）
OBS_WS_HOST     = "127.0.0.1"
OBS_WS_PASSWORD = "你的OBS密码"
OBS_WATCH_DIR   = r"C:/你的OBS录像保存路径"
```

其他选项都有默认值，刚开始不用动。

### 启动

```bash
python main.py
```

配置界面会自动弹出，快捷键监听在后台同时启动。

---

## 快捷键

| 按键 | 功能 |
|------|------|
| F4 | 截图+录音，快速分析 |
| F6 | 截图+录音，深度分析 |
| F2 | 剪贴板文本分析 |
| F7 | 按住录制（OBS 实时录制） |
| F12 | OBS 回溯缓冲（最近N秒） |
| F8 / F9 | 纯截图分析 |
| Alt+Z / X / C | 切换语言模板 |
| Alt+S | 搜索已保存词条 |
| Alt+Q | 查看学习统计 |
| Alt+E | 导出词汇到 CSV |
| Alt+W | 导出词汇到 TXT |
| Alt+B | 从剪贴板批量导入 |
| Alt+R | 选择截图区域 |

所有快捷键都可以在 `config.py` 里改。

---

## 注意事项

- API Key 只保存在你本地的 `config.py` 里，不会被上传或发送到任何地方
- Anki 同步需要 Anki 在后台运行，且 AnkiConnect 插件已启用
- OBS 功能需要在 OBS 设置里开启 WebSocket 服务
- 第一次启用本地 Whisper 或 OCR 时会自动下载模型，需要等一会儿
- 截图和音频文件会保存在你配置的 Assets 文件夹里，不会自动删除

---

## 开源协议

MIT
