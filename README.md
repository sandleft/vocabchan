# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> Press a hotkey. AI breaks it down. Saved to your notes automatically. That's it.

> ⚠️ **Windows EXE is currently in beta — bugs expected. Running from Python source is recommended for now.**

---

## What is this?

VocabChan is a hotkey-driven language learning tool for people who learn by watching — anime, dramas, YouTube, games, you name it.

You hit a key, it grabs whatever's on your screen (or your mic, or your clipboard), sends it to an AI, and gets back a full linguistic breakdown — grammar, nuance, pronunciation notes, usage context. The result gets saved to Obsidian and optionally Anki automatically. No copy-pasting, no tab-switching, just keep watching.

---

## What it can do

**Capture anything**
- Screenshot the screen and ask AI to explain what's on it
- Record mic or system audio, auto-transcribe and analyze
- Pull the last N seconds of OBS footage and send it for analysis
- Paste any text from clipboard and get it broken down instantly
- Paste a whole word list and process everything at once (batch import)
- Select a specific region of the screen instead of capturing everything
- Optional preview window — confirm the screenshot before it gets sent to AI

**AI analysis**
- Sends your capture to any AI provider you configure
- Gets back: translation, word breakdown, grammar notes, usage context, pronunciation tips
- Injects your recent vocabulary history into the prompt so the AI can spot connections (RAG memory)
- Flags duplicate words — if you keep running into the same word, it tells you how many times
- Auto-retries failed requests — if the API is flaky, it queues the task and tries again
- Optional local OCR (PaddleOCR) to pre-extract text before sending, reduces hallucinations
- Optional local transcription (Faster-Whisper) for audio, works fully offline

**Save everything**
- Every entry saves to Obsidian as a structured note with the word, original sentence, full analysis, and any captured image / audio / video
- Obsidian with the [Spaced Repetition plugin](https://github.com/st3v3nmw/obsidian-spaced-repetition) gives you full review capability without leaving your vault
- Optionally syncs to Anki as a flashcard with image and audio — note that **Anki does not support video**, so video captures are stored in Obsidian only
- Optionally backs up all media files to Teldrive

**Review and stats**
- Built-in spaced repetition reminders at 3, 7, and 14 days
- Search all your saved vocabulary
- Learning stats: total words, today, this week, by language, most-seen words
- Export full vocabulary to CSV or TXT

**Bonus**
- Auto-generates a short Galgame-style review script from today's vocabulary at 23:50 every night (can be disabled)
- Privacy masking — strips emails, phone numbers, ID numbers from text before sending to AI
- Proxy support for regions with restricted API access

---

## Supported AI providers

VocabChan comes pre-configured for these providers, but **every single one is optional and interchangeable** — use whichever you have API keys for, swap them out freely, or route everything through OpenRouter if you prefer:

Google Gemini · OpenAI · Claude · DeepSeek · Grok · Qwen · Kimi · Doubao · MiniMax · OpenRouter

Each hotkey slot in `config.py` is just a provider name and model string. Change either one to whatever you want.

---

## Supported languages

Japanese · English · Chinese · Spanish · French · German · Korean · Italian · Portuguese · Arabic · Custom templates (add your own)

---

## How to set it up

### What you need

**Required**
- Python 3.10+
- At least one API key from any provider above

**For note-saving — pick one or both**
- [Obsidian](https://obsidian.md/) — supports images, audio, video, and text all in one note. Pair with the [Spaced Repetition plugin](https://github.com/st3v3nmw/obsidian-spaced-repetition) for built-in review
- [Anki](https://apps.ankiweb.net/) + [AnkiConnect plugin](https://ankiweb.net/shared/info/2055492159) — excellent flashcard system, but **Anki does not support video**. Images and audio work fine

**For video features**
- OBS Studio with WebSocket enabled

**Optional**
- [Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper) — local audio transcription, no API needed
- PaddleOCR — local OCR for better text accuracy

### Installation

```bash
git clone https://github.com/yourusername/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### Configuration

Open `config.py` and fill in the parts you need:

```python
# Add keys for whichever providers you want — leave the rest empty
API_KEYS = {
    "google": "your-key-here",
    "openai": "your-key-here",
    "claude": "",        # leave empty if not using
    "deepseek": "",
    # ...
}

# OBS settings — only needed for video replay features
OBS_WS_HOST     = "127.0.0.1"
OBS_WS_PASSWORD = "your-obs-password"
OBS_WATCH_DIR   = r"C:/your/obs/recording/path"

# Optional proxy
PROXY_URL = ""  # e.g. "http://127.0.0.1:7890"
```

Everything else has sensible defaults. You don't need to touch the hotkey assignments or model names to get started — but they're all there when you want to customize.

### Run

```bash
python main.py
```

A config UI will open and the hotkey daemon starts in the background automatically.

---

## Hotkeys

**All hotkeys are fully customizable in `config.py`** — the ones below are just the defaults.

| Key | Action |
|-----|--------|
| F4 | Screenshot + audio, fast analysis |
| F6 | Screenshot + audio, deep analysis |
| F2 | Clipboard text analysis |
| F7 | Hold to record (OBS live recording) |
| F12 | OBS replay buffer (last N seconds) |
| F8 / F9 | Screenshot only |
| F10 / F11 | Audio only |
| Alt+1–7 | Same actions via OpenRouter models |
| Alt+Z / X / C | Switch language template |
| Alt+S | Search saved vocabulary |
| Alt+Q | Show learning stats |
| Alt+E | Export to CSV |
| Alt+W | Export to TXT |
| Alt+B | Batch import from clipboard |
| Alt+R | Select capture region |

---

## Notes

- API keys stay in your local `config.py` only — never sent anywhere else
- Anki must be running with AnkiConnect active for card sync to work
- OBS requires WebSocket service enabled in OBS settings
- First-time Whisper or OCR setup will download models — takes a few minutes
- Media files are saved locally and never auto-deleted

---

## License

MIT
