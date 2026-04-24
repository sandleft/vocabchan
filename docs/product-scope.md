# VocabChan Product Scope

## Overview

VocabChan is a **desktop-native, local-first language learning workflow hub** built for immersive learners.

It is not just a sentence translator. It is intended to help users capture language from real sources, analyze it, store it locally, export it into existing study tools, and revisit it later.

The core workflow is:

**capture -> preprocess -> analyze -> store -> export/sync -> review later**

## Target Users

Primary users:

- immersive Japanese learners
- multi-language self-learners
- learners who already use tools such as Anki and Obsidian
- users who want a low-friction desktop workflow for collecting and studying real input

Typical study contexts:

- anime and video
- games
- manga and image-based content
- copied text from websites or apps
- subtitles
- audio and podcasts
- PDFs and ebooks

## Problem VocabChan Solves

Many learning tools cover only one layer of the workflow:

- OCR only
- translation only
- flashcards only
- note export only

VocabChan is designed to unify these steps in one desktop workflow so that users can move from capture to long-term retention without rebuilding the pipeline manually each time.

## Product Boundaries

VocabChan should be understood as:

- a local-first desktop application
- a multi-source language capture and analysis hub
- a storage and export layer for long-term accumulation
- a workflow tool that integrates with existing study systems

It should not be understood as:

- a browser DOM translation overlay
- a galgame hooking platform
- a replacement for Anki's full SRS role
- a cloud-first social learning platform

## Capability Areas

VocabChan is organized around six product areas.

## 1. Capture Layer

Responsible for collecting language input from real sources.

Current and planned scope includes:

- clipboard text
- clipboard images
- full-screen screenshots
- region screenshots
- audio capture
- OBS replay / recording-based capture
- subtitle file import
- image file import
- audio file import
- future file-based and workflow-oriented capture extensions

## 2. Preprocess Layer

Responsible for preparing captured material before full analysis.

Scope includes:

- OCR
- ASR / transcription
- text cleanup
- deduplication
- splitting long or batch inputs into manageable units

## 3. Analysis Layer

Responsible for enriching captured content.

Scope includes:

- AI provider routing
- prompt templates
- learner-level-aware analysis
- dictionary-style lookup
- furigana
- TTS
- frequency labeling
- glossary terms
- cache and cost awareness

## 4. Memory and Review Layer

Responsible for making captured input useful over time.

Scope includes:

- searchable history
- editing and inspection
- session-oriented views
- review helpers
- workshop-style generated study material

## 5. Storage and Integration Layer

Responsible for local persistence and downstream workflows.

Scope includes:

- SQLite storage
- local asset files
- Markdown export
- AnkiConnect integration
- Obsidian workflows
- CSV import and export
- future integrations where they support the same local-first workflow

## 6. UX and Workflow Layer

Responsible for the desktop experience itself.

Scope includes:

- desktop shell and navigation
- system tray behavior
- silent mode
- hotkeys
- profiles
- diagnostics
- retry handling
- floating result surfaces
- dashboard and status visibility

## First Release Scope

The first release should establish a complete desktop workflow rather than chasing every future idea.

### Included in the intended first release

- screenshot and clipboard capture
- audio and OBS-related capture flows
- subtitle, image, and audio import
- AI analysis with prompt templates
- dictionary / furigana / TTS / frequency signals
- local persistence and searchable history
- Markdown / Obsidian / Anki / CSV workflows
- logs, retry queue, diagnostics, profiles, tray behavior, and a stronger desktop shell

### Planned after the first release

- clipboard monitor mode
- PDF import
- Kindle import
- YouTube subtitle import
- session logs
- media difficulty estimation
- Notion integration
- additional lightweight lookup workflows

### Longer-term expansion

- confusion detection
- output practice generation
- cloze generation
- similarity search
- webhook / local API modes
- more advanced learning intelligence features

## Current Public Communication Model

The public repository may describe both:

- what already exists in the desktop foundation
- what belongs to the intended release scope

This is deliberate. VocabChan is not being positioned as a finished product today, but as an actively maintained open-source desktop application moving toward a coherent release boundary.

## Success Definition

VocabChan succeeds as a product when users can reliably do at least these three things:

1. capture language quickly from real media
2. analyze and store the result locally in a structured way
3. export, revisit, and reuse the result in a long-term study workflow

If those three loops are strong, the project has a meaningful product core.
