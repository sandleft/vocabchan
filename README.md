# VocabChan

VocabChan is a local-first desktop hub for immersive language learning.

It is built for learners who collect language from real media, not just textbook examples: games, anime, YouTube, manga, screenshots, copied text, subtitles, and audio. The goal is not only to translate a sentence, but to turn real input into searchable, reusable study material.

VocabChan connects the full workflow:

**capture -> preprocess -> analyze -> store -> export/sync -> review later**

## Status

VocabChan is currently moving from a validated prototype to a release-ready desktop application.

The public repository is intended to show both:

- the working foundation that already exists
- the product direction and feature scope being built toward

This means some parts of the project are already usable, while some roadmap items are documented ahead of full implementation.

## Who It Is For

VocabChan is designed for:

- immersive Japanese learners
- self-learners working across multiple languages
- learners who already use tools like Anki and Obsidian
- users who want a desktop-native, low-friction, local-first workflow

## What Makes It Different

Most tools handle only one part of the workflow: OCR, translation, flashcards, or notes.

VocabChan is designed as a single desktop workspace that can unify:

- capture from clipboard, screenshots, audio, OBS replay, and imported files
- OCR / ASR / text cleanup before analysis
- AI analysis plus dictionary-style support information
- local SQLite storage for long-term accumulation
- export and sync to learning tools such as Anki and Obsidian

## Core Product Direction

VocabChan is being productized around six capability areas:

1. **Capture**  
   Clipboard, screenshots, region capture, audio capture, OBS replay, subtitle/image/audio import.

2. **Preprocess**  
   OCR, ASR, text cleanup, deduplication, media splitting.

3. **Analysis**  
   AI providers, prompt templates, dictionary support, furigana, TTS, frequency labeling, caching, cost tracking.

4. **Memory & Review**  
   Searchable history, session views, review helpers, workshop-style generated learning content.

5. **Storage & Integrations**  
   SQLite, local assets, Markdown export, AnkiConnect, Obsidian, CSV workflows.

6. **UX & Workflow**  
   Tray behavior, silent mode, profiles, diagnostics, retry queue, floating result windows.

## Current Foundation

The project already includes a substantial desktop foundation and productization work in progress, including:

- PySide6 desktop shell with task-oriented navigation
- hotkey-driven capture workflows
- clipboard text and image ingestion
- screenshot and region capture flows
- audio capture and OBS-related workflows
- local SQLite persistence
- history, logs, retry queue, and import/export surfaces
- provider configuration, prompt configuration, glossary and analysis settings
- Anki / Obsidian / CSV integration surfaces
- packaging and release-regression scripts
- unit and integration test coverage for the evolving desktop architecture

## Planned Release Scope

The broader release target includes the following product scope, tracked in the specification and being implemented in stages:

- multi-source capture from clipboard, screenshots, audio, OBS replay, subtitles, images, and audio files
- AI analysis with configurable providers and prompt templates
- dictionary lookup, furigana, TTS, glossary support, and frequency signals
- analysis cache and API cost tracking
- searchable library, editing, logs, retry queue, and session-oriented memory
- Anki and Obsidian export/sync workflows
- multi-profile configuration, tray control, silent mode, diagnostics, and floating result windows

Some roadmap items in the specification are still planned rather than complete. The README reflects the intended product boundary, not only the smallest currently exposed code path.

## Screenshots

### Main Window
![Main Window](docs/images/dashboard.png)

### Capture
![Capture Page](docs/images/capture-page.png)

### Analysis
![Analysis Page](docs/images/analysis-page.png)

### Library
![Library Page](docs/images/library-page.png)

### Integrations
![Integrations Page](docs/images/integrations-page.png)


## Example Workflows

### 1. Instant capture while reading or watching

1. Trigger a hotkey or capture from the clipboard.
2. Send text, image, audio, or replay media through preprocessing.
3. Run AI analysis and supporting enrichment.
4. Save the result locally.
5. Export or sync to Anki / Obsidian if needed.
6. Revisit it later in the library.

### 2. Batch import from study material

1. Import subtitles, images, audio, or other source files.
2. Preview, split, and analyze in batches.
3. Save results into the local database.
4. Export selected outputs into downstream tools.

### 3. Long-term accumulation

1. Keep collecting real-world language input.
2. Build a searchable personal vocabulary and sentence history.
3. Review, organize, and generate follow-up study material.

## Screenshots

Add screenshots under `docs/images/` and embed them here.

Recommended screenshot set:

- main dashboard
- capture page with hotkeys / import entry points
- analysis settings page
- library/history page
- integrations page
- floating micro window
- one batch import preview dialog

## Tech Stack

- **Language:** Python 3.11+
- **Desktop UI:** PySide6
- **Storage:** SQLite + local asset files
- **Packaging:** PyInstaller
- **Architecture direction:** local-first desktop app with modular services, event bus, async host, task engine, and Qt-based UI shell

## Project Layout

```text
src/vocabchan/
  app/
  gui/
  infrastructure/
  storage_adapter/
  task_engine/
  unified_interface/
  shared/

scripts/
tests/
resources/
docs/
Development Setup
pip install -e ".[dev]"
Run
python main.py
or

python -m vocabchan
Test
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
Packaging
python scripts/package_release.py --dry-run
python scripts/release_regression.py --dry-run
Platform Focus
Current productization work is focused on Windows desktop first.

Non-Goals
VocabChan is intentionally not trying to be:

a browser DOM translation overlay
a galgame hook platform
a replacement for Anki
a cloud-first social learning platform
It is meant to be a desktop-native, local-first language input and learning workflow hub.
---

