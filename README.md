# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> Press a hotkey. AI breaks it down. Saved to your notes automatically. That's it.

> ⚠️ **Windows EXE is currently in beta — bugs expected. Running from Python source is recommended for now.**

---

## What is this?

VocabChan is a hotkey-driven language learning tool for people who learn by watching — anime, dramas, YouTube, games, you name it.

You hit a key, it grabs whatever's on your screen (or mic, or clipboard), sends it to an AI with a language-specific analysis prompt, and gets back a full linguistic breakdown tailored to whatever language you're learning. The result saves to Obsidian and optionally Anki automatically. No copy-pasting, no tab-switching, just keep watching.

---

## What it can do

**Capture anything**
- Screenshot the screen and ask AI to explain what's on it
- Record mic or system audio, auto-transcribe and analyze
- Pull the last N seconds of OBS footage and send it for analysis
- Paste any text from clipboard and break it down instantly
- Paste a whole word list and process everything at once (batch import)
- Select a specific region of the screen instead of full capture
- Optional preview window — confirm the screenshot before it gets sent

**AI analysis**
- Sends to any AI provider you configure, with a language-specific prompt (see Language Templates below)
- Returns: translation, word breakdown, grammar deep-dive, usage context, pronunciation notes
- Injects your recent vocabulary into every prompt so the AI can spot connections (RAG memory)
- Duplicate detection — if you keep running into the same word, it tells you how many times
- Auto-retries failed requests — queued and retried automatically if the API is flaky
- Optional local OCR (PaddleOCR) to pre-extract text before sending, reduces hallucinations
- Optional local transcription (Faster-Whisper) for audio, works fully offline
- Optional always-on background listener that auto-triggers without pressing anything *(heavy on CPU, use with caution)*

**Save everything**
- Every entry saves to Obsidian as a structured note: word, original sentence, full analysis, screenshot, audio, video — all in one place
- Obsidian with the [Spaced Repetition plugin](https://github.com/st3v3nmw/obsidian-spaced-repetition) gives you full review capability without leaving your vault
- Vocabulary links automatically become Obsidian knowledge graph nodes — your notes build a web of connected words over time
- Optionally syncs to Anki as a flashcard with image and audio
- **Anki does not support video** — video captures are stored in Obsidian only
- Anki card front content is configurable: show just the word, just the sentence, or both
- Anki audio placement is configurable: play before or after flipping the card
- Optionally backs up all media to Teldrive

**Review and stats**
- Built-in spaced repetition reminders at 3, 7, and 14 days
- Search all saved vocabulary
- Learning stats: total words, today, this week, by language, most-seen words
- Export full vocabulary to CSV or TXT

**Bonus**
- Auto-generates a short Galgame-style review script from today's vocabulary at 23:50 every night (can be disabled)
- Privacy masking — strips emails, phone numbers, ID numbers from text before sending to AI
- Proxy support
- Change most settings at runtime without recompiling the EXE

---

## Language-specific AI templates

This is one of VocabChan's core features. Every language has a tailored analysis prompt that tells the AI exactly what to focus on — not just "translate this," but the specific grammar traps and nuances that actually trip up learners of that language.

**All target languages are freely configurable.** The ones below are built-in presets:

| Language | What the AI focuses on |
|----------|----------------------|
| 🇯🇵 Japanese | Honorific system (尊敬語/謙譲語/丁寧語) — who uses what to whom; kanji on-yomi vs kun-yomi; contexts where the subject is dropped |
| 🇺🇸 English | Pronunciation vs spelling disconnect; phrasal verbs — collocations and how meaning shifts by context |
| 🇪🇸 Spanish | Verb conjugation forms; subjunctive mood — when it triggers and what emotion it carries; noun gender |
| 🇫🇷 French | Noun gender patterns; liaison and elision — when sounds link or disappear; pronunciation vs spelling |
| 🇩🇪 German | Four-case declension (nominative/accusative/dative/genitive) with three genders; verb-final bracket structures in subordinate clauses |
| 🇰🇷 Korean | Speech level system (존댓말) — endings and who they apply to; liaison, final consonant assimilation, and other sound change rules |
| 🇮🇹 Italian | Noun-adjective gender/number agreement; verb conjugation system; cultural context words and gesture-linked expressions |
| 🇨🇳 Chinese | Pinyin with tone markings; character composition logic; measure word collocations |
| 🇵🇹 Portuguese | Nasal sound characteristics; European vs Brazilian Portuguese — grammar and vocabulary differences flagged explicitly |
| 🇸🇦 Arabic | MSA vs dialect (Egyptian, Levantine, etc.) distinction; root-based morphology; letter shape variants by position |
| ✏️ Custom 1/2/3 | Write your own focus instructions for any language |

Switch between templates instantly with a hotkey while watching. The AI immediately adjusts its analysis style.

---

## Supported AI providers

VocabChan comes pre-configured for these providers, but **every single one is optional and interchangeable** — fill in keys for whichever you have, leave the rest empty. Or route everything through OpenRouter if you prefer one key for everything:

Google Gemini · OpenAI · Claude · DeepSeek · Grok · Qwen · Kimi · Doubao · MiniMax · OpenRouter

Each hotkey slot in `config.py` is just a provider name and model string — change either freely.

---

## How to set it up

### What you need

**Required**
- Python 3.10+
- At least one API key from any provider above

**For note-saving — pick one or both**
- [Obsidian](https://obsidian.md/) — images, audio, video, and text all in one note. Add the [Spaced Repetition plugin](https://github.com/st3v3nmw/obsidian-spaced-repetition) for built-in review
- [Anki](https://apps.ankiweb.net/) + [AnkiConnect plugin](https://ankiweb.net/shared/info/2055492159) — great flashcard system, but **Anki does not support video**

**For video features**
- OBS Studio with WebSocket enabled

**Optional**
- [Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper) — local audio transcription, no API needed
- PaddleOCR — local OCR for better accuracy

### Installation

```bash
git clone https://github.com/yourusername/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### Configuration

Open `config.py` and fill in what you need:

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

Everything else has sensible defaults. Hotkey assignments, model names, Anki card style, feature toggles — all configurable, but you don't need to touch any of it to get started.

### Run

```bash
python core.py
```

A config UI will open and the hotkey daemon starts in the background automatically.

---

## Hotkeys

**All hotkeys are fully customizable in `config.py`.** The ones below are just the defaults.

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
- First-time Whisper or OCR setup downloads models — takes a few minutes
- Media files are saved locally and never auto-deleted
- Most settings can be changed at runtime via the config UI without touching `config.py`

---

## License

MIT
