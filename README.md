# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> Press a hotkey. Get a full breakdown. Card saved to Anki. That's it.

> ⚠️ **Windows EXE is currently in beta — bugs expected. Running from Python source is recommended for now.**

---

## What is this?

VocabChan is a hotkey-driven language learning tool for people who learn by watching — anime, dramas, YouTube, games, you name it.

You hit a key, it grabs whatever's on your screen (or your mic, or your clipboard), sends it to an AI, and gets back a proper linguistic breakdown — grammar, nuance, pronunciation notes, usage context — all in your target language. The result gets saved as an Anki card and an Obsidian note automatically. No copy-pasting. No tab-switching. Just keep watching.

---

## What it can do

- **Screenshot analysis** — captures your screen and asks AI to explain what's on it
- **Audio capture** — records from your mic or system audio and transcribes + analyzes it
- **OBS video replay** — pulls the last N seconds of footage from OBS and sends it for analysis
- **Clipboard mode** — paste any text and get it broken down instantly
- **Batch import** — paste a whole word list and process everything at once
- **Anki sync** — auto-creates flashcards with the word, original sentence, and full analysis
- **Obsidian sync** — saves every entry as a structured note in your vault
- **Spaced repetition reminders** — reminds you to review words from 3, 7, and 14 days ago
- **Vocabulary search & stats** — search past entries, see how many words you've captured, export to CSV or TXT
- **Language switching on the fly** — swap between Japanese, English, and other templates with a hotkey

### Supported AI providers
Google Gemini · OpenAI · Claude · DeepSeek · Grok · Qwen · Kimi · Doubao · MiniMax · OpenRouter

### Supported languages
Japanese · English · Chinese · Spanish · French · German · Korean · Italian · Portuguese · Arabic · and more via custom templates

---

## How to set it up

### What you need
- Python 3.10+
- [Anki](https://apps.ankiweb.net/) + [AnkiConnect plugin](https://ankiweb.net/shared/info/2055492159)
- [Obsidian](https://obsidian.md/)
- At least one API key from the providers above
- OBS Studio (only needed for video replay features)
- Optional: [Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper) for local audio transcription
- Optional: PaddleOCR for local OCR

### Installation

```bash
git clone https://github.com/yourusername/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### Configuration

Open `config.py` and fill in:

```python
# Your API keys — fill in whichever providers you want to use
API_KEYS = {
    "google": "your-key-here",
    "openai": "your-key-here",
    # ...
}

# OBS settings (only if you use video features)
OBS_WS_HOST     = "127.0.0.1"
OBS_WS_PASSWORD = "your-obs-password"
OBS_WATCH_DIR   = r"C:/your/obs/recording/path"
```

Everything else has sensible defaults and you can leave it alone to start.

### Run it

```bash
python main.py
```

A config UI will open. The hotkey daemon starts in the background automatically.

---

## Hotkeys

| Key | Action |
|-----|--------|
| F4 | Screenshot + audio, fast analysis |
| F6 | Screenshot + audio, deep analysis |
| F2 | Clipboard text analysis |
| F7 | Record while held (OBS live recording) |
| F12 | OBS replay buffer (last N seconds) |
| F8 / F9 | Screenshot only (vision models) |
| Alt+Z / X / C | Switch language template |
| Alt+S | Search saved vocabulary |
| Alt+Q | Show learning stats |
| Alt+E | Export vocabulary to CSV |
| Alt+W | Export vocabulary to TXT |
| Alt+B | Batch import from clipboard |
| Alt+R | Select screen region for capture |

All hotkeys can be reconfigured in `config.py`.

---

## Notes

- VocabChan does **not** store or send your API keys anywhere — they stay in your local `config.py`
- Anki must be open and running with AnkiConnect active for card sync to work
- The OBS features require OBS WebSocket to be enabled in OBS settings
- If you enable local Whisper or OCR, first-run model download will take a while
- Captured media files are saved locally in your configured `Assets` folder and are never deleted automatically

---

## License

MIT
