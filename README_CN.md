# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> 按一个键，AI 解析，自动存进笔记。就这么简单。

> ⚠️ **Windows EXE 版本目前处于测试阶段，可能存在 bug，建议先用 Python 源码运行。**

---

## 这是什么

VocabChan 是一个专为「边看边学」设计的语言学习工具。

看日剧、刷动漫、玩游戏、看 YouTube，遇到不懂的句子，按一个快捷键，它就会自动截图（或者录音、或者读剪贴板），发给 AI，然后把翻译、语法分析、单词解释、发音备注、使用场景全部整理好，同时自动保存到 Obsidian 笔记，还可以同步到 Anki。不需要切窗口，不需要复制粘贴，继续看就行。

---

## 能做什么

**捕获任何内容**
- 截取当前屏幕，让 AI 解释画面中的句子
- 录制麦克风或系统音频，自动转录并分析
- 从 OBS 抓取最近 N 秒的录像发给 AI 分析
- 复制任意文本一键解析
- 粘贴整个词表批量处理
- 选定屏幕区域，只截取你需要的部分
- 可选截图预览窗口，确认后再发给 AI

**AI 分析**
- 发送给你配置的任意 AI 服务商
- 返回内容包括：翻译、单词详解、语法难点、实战语感、发音提示
- 自动把最近学过的词注入提示词（RAG 记忆），让 AI 帮你发现关联
- 重复词检测：同一个词出现第二次、第三次时，会提醒你已经遇到过几次了
- API 请求失败时自动放入重试队列，不会丢失任何记录
- 可选本地 OCR（PaddleOCR），在发给 AI 之前先提取文字，减少幻觉
- 可选本地音频转录（Faster-Whisper），完全离线运行

**保存所有内容**
- 每条记录自动保存到 Obsidian，包含单词、原句、完整分析报告，以及截图、音频、视频
- Obsidian 配合 [Spaced Repetition 插件](https://github.com/st3v3nmw/obsidian-spaced-repetition) 就能直接在 Obsidian 里做间隔复习，不需要额外工具
- 可选同步到 Anki，自动生成带图片和音频的闪卡
- **注意：Anki 不支持视频**，视频内容只会保存在 Obsidian 中
- 可选将媒体文件备份到 Teldrive

**复习与统计**
- 内置间隔复习提醒，自动提示你复习 3、7、14 天前的词条
- 搜索历史词条
- 学习统计：总词汇量、今日新增、本周新增、语言分布、高频词
- 导出词汇到 CSV 或 TXT

**彩蛋**
- 每天 23:50 自动用今天学过的词生成一段 Galgame 风格的复习剧本（可以关闭）
- 隐私保护：发送给 AI 之前自动屏蔽邮箱、手机号、身份证号等敏感信息
- 支持代理，方便需要的地区使用

---

## 支持的 AI 服务商

VocabChan 预设了以下服务商，但**每一个都是可选的、可自由替换的**——用哪个填哪个的 Key，其余留空就行。也可以通过 OpenRouter 一个 Key 打通多个模型：

Google Gemini · OpenAI · Claude · DeepSeek · Grok · 通义千问 · Kimi · 豆包 · MiniMax · OpenRouter

`config.py` 里每个快捷键槽位就是一个服务商名称加模型名，随时可以改。

---

## 支持的语言

日语 · 英语 · 中文 · 西班牙语 · 法语 · 德语 · 韩语 · 意大利语 · 葡萄牙语 · 阿拉伯语 · 自定义模板（可自由添加）

---

## 怎么用

### 需要准备什么

**必须有**
- Python 3.10+
- 至少一个上面列出的 AI 服务商的 API Key

**笔记保存——选一个或两个都用**
- [Obsidian](https://obsidian.md/) — 图片、音频、视频、文字全都可以放在一个笔记里。配合 [Spaced Repetition 插件](https://github.com/st3v3nmw/obsidian-spaced-repetition) 可以直接在里面做间隔复习
- [Anki](https://apps.ankiweb.net/) + [AnkiConnect 插件](https://ankiweb.net/shared/info/2055492159) — 经典闪卡系统，图片和音频都支持，但**不支持视频**

**视频功能**
- OBS Studio，并在设置里开启 WebSocket 服务

**可选**
- [Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper) — 本地音频转录，不消耗 API
- PaddleOCR — 本地文字识别，提升准确度

### 安装

```bash
git clone https://github.com/你的用户名/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### 配置

打开 `config.py`，填写你需要的部分：

```python
# 用哪个服务商就填哪个，其余留空
API_KEYS = {
    "google": "你的key",
    "openai": "你的key",
    "claude": "",       # 不用就留空
    "deepseek": "",
    # ...
}

# OBS 设置（只用视频功能才需要填）
OBS_WS_HOST     = "127.0.0.1"
OBS_WS_PASSWORD = "你的OBS密码"
OBS_WATCH_DIR   = r"C:/你的OBS录像保存路径"

# 代理（需要的话填）
PROXY_URL = ""  # 例如 "http://127.0.0.1:7890"
```

其他选项都有默认值，第一次用不需要动快捷键和模型设置，跑起来再慢慢调整。

### 启动

```bash
python main.py
```

配置界面会自动弹出，快捷键监听在后台同时启动。

---

## 快捷键

**所有快捷键都可以在 `config.py` 里自由修改**，下面是默认设置：

| 按键 | 功能 |
|------|------|
| F4 | 截图+录音，快速分析 |
| F6 | 截图+录音，深度分析 |
| F2 | 剪贴板文本分析 |
| F7 | 按住录制（OBS 实时录制） |
| F12 | OBS 回溯缓冲（最近N秒） |
| F8 / F9 | 纯截图分析 |
| F10 / F11 | 纯音频分析 |
| Alt+1～7 | 通过 OpenRouter 模型执行对应操作 |
| Alt+Z / X / C | 切换语言模板 |
| Alt+S | 搜索已保存词条 |
| Alt+Q | 查看学习统计 |
| Alt+E | 导出词汇到 CSV |
| Alt+W | 导出词汇到 TXT |
| Alt+B | 从剪贴板批量导入 |
| Alt+R | 选择截图区域 |

---

## 注意事项

- API Key 只保存在本地的 `config.py` 里，不会被上传或发送到任何地方
- Anki 同步需要 Anki 在后台运行且 AnkiConnect 插件已启用
- OBS 功能需要在 OBS 设置里开启 WebSocket 服务
- 第一次启用本地 Whisper 或 OCR 时会自动下载模型，需要等几分钟
- 截图和音频文件保存在本地，不会自动删除

---

## 开源协议

MIT
