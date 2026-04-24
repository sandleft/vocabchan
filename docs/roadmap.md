# VocabChan Roadmap

VocabChan is being developed as a **local-first desktop hub for immersive language learning**.

This roadmap describes the intended public direction of the project. It is not a promise that every item is already implemented in the current public snapshot. Instead, it shows the release path from validated prototype to publishable desktop product.

## Product Direction

VocabChan is designed around one workflow:

**capture -> preprocess -> analyze -> store -> export/sync -> review later**

The project focuses on turning real-world language input into long-term study assets.

## Guiding Principles

- **Local-first:** user data should live locally by default.
- **Desktop-native:** the primary experience is a desktop workflow, not a browser plugin.
- **Real input first:** capture from real media matters more than artificial drill content.
- **Integrate, do not replace:** VocabChan should work well with tools like Anki and Obsidian instead of trying to replace them.
- **Productization over feature sprawl:** the goal is a usable release-ready application, not an endless prototype.

## Release Stages

## Stage 0: Validated Prototype

This stage established the core feasibility of the project.

Focus areas:

- clipboard-based capture
- screenshot and region capture
- audio capture
- OBS-related capture workflows
- AI provider integration
- local OCR / ASR options
- SQLite persistence
- Markdown export and basic integration flows

Outcome:

- the core learning workflow was proven workable
- the project moved beyond a throwaway experiment

## Stage 1: Release-Ready Foundation

This is the main current productization stage.

Goals:

- stabilize the desktop shell and navigation
- move from script-like structure to clearer module boundaries
- improve settings, profiles, diagnostics, and runtime reliability
- strengthen task orchestration, retry handling, and state flow
- make packaging and regression checks part of the normal release path

Key deliverables:

- desktop shell with task-oriented navigation
- capture, analysis, library, integrations, settings, and workshop surfaces
- better configuration and profile handling
- logs, retry queue, diagnostics, and release checks
- improved test coverage across desktop flows

## Stage 2: P0 Release Scope

This stage targets the first public release boundary.

### Capture

- hotkey screenshot capture
- clipboard text and image analysis
- audio capture analysis
- OBS replay / hold-to-record flows
- region capture
- subtitle file import
- image file import
- audio file import

### Analysis

- multi-provider AI analysis
- prompt templates
- context-length control
- cache and API cost tracking
- furigana
- dictionary support
- TTS playback
- frequency labeling
- glossary terms
- learner-level-aware analysis

### Storage and Integrations

- SQLite persistence
- Markdown / Obsidian export
- AnkiConnect integration
- CSV import / export
- searchable history and editing
- retry queue
- logs center

### UX and Workflow

- rebuilt main desktop interface
- system tray support
- silent mode
- hotkey conflict detection
- multiple profiles
- production-oriented theming
- floating micro window or persistent result panel
- dashboard summary view

Success criteria for this stage:

- users can complete complete end-to-end capture and study workflows
- the app is stable enough to package and distribute
- the public repository clearly reflects a serious desktop product effort

## Stage 3: Short-Term Post-Release Expansion

These items are important, but not required to define the first release boundary.

Planned areas:

- clipboard monitor mode
- PDF import
- Kindle highlight import
- YouTube subtitle import
- session logs
- media difficulty estimation
- batch request optimization
- Notion integration
- lightweight hover lookup mode
- detached live capture/history panel

## Stage 4: Mid-Term Product Expansion

These are meaningful enhancements once the release foundation is stable.

Planned areas:

- similar sentence retrieval
- confusion pair detection
- language comparison mode
- output practice generation
- cloze generation
- error analysis
- frequency gap analysis
- language journaling
- webhook export
- local REST API mode

## Stage 5: Long-Term Research and Platform Direction

These ideas remain interesting, but they are intentionally not part of the immediate release target.

Examples:

- personalized difficulty models
- pitch accent support
- shadowing mode
- pronunciation feedback
- passive learning mode
- mobile companion workflows
- macOS release target
- editor / launcher plugins

## What Will Not Be Prioritized

The project is intentionally not focused on:

- browser DOM inline translation systems
- galgame hook infrastructure
- replacing Anki with a full custom SRS
- cloud-first community features or accounts
- turning into a heavy backend platform

## Public Repo Expectations

The public repository may show a mix of:

- currently working desktop foundations
- ongoing productization work
- planned release scope documented ahead of full implementation

That is intentional. VocabChan is being built in public as an evolving desktop product, not frozen at the prototype stage.

## Near-Term Public Repository Goals

To make the repository more useful to contributors, users, and program reviewers, the next public-facing improvements should include:

- updated screenshots
- clearer README messaging
- architecture notes for the desktop stack
- a simplified public roadmap
- better public visibility into release scope and status
