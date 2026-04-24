#!/usr/bin/env python3
"""VocabChan Project Skeleton Generator - Part 1/3: Core files"""
from pathlib import Path
import os

ROOT = Path(__file__).parent
FILES = {}

FILES["pyproject.toml"] = '''[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "vocabchan"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "PySide6>=6.6.0",
    "PySide6-WebEngine>=6.6.0",
    "httpx>=0.27.0",
    "aiohttp>=3.9.0",
    "websockets>=12.0",
    "pyaudio>=0.2.14",
    "Pillow>=10.0.0",
    "keyboard>=0.13.5",
    "pywin32>=306; sys_platform == \\'win32\\'",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "platformdirs>=4.0.0",
    "typing-extensions>=4.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-qt>=4.3.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.3.0",
]
package = ["pyinstaller>=6.3.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
qt_api = "pyside6"

[tool.ruff]
line-length = 100
target-version = "py311"
'''

FILES["main.py"] = '''"""VocabChan entry point."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from vocabchan.app.bootstrap import main
if __name__ == "__main__":
    sys.exit(main())
'''

FILES[".gitignore"] = '''__pycache__/
*.py[cod]
.env
.venv/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
*.db
*.db-wal
*.db-shm
/logs/
/assets/
/backups/
config.json
'''

FILES["README.md"] = '''# VocabChan
Multi-source immersive language learning desktop hub.

## Setup
```bash
pip install -e ".[dev]"
```

## Run
```bash
python main.py
```

## Test
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```
'''

FILES["src/vocabchan/__init__.py"] = '"""VocabChan."""\n__version__ = "0.1.0"\n'

FILES["src/vocabchan/shared/__init__.py"] = ""

FILES["src/vocabchan/shared/enums.py"] = '''"""All domain enumerations."""
from __future__ import annotations
from enum import Enum


class SourceType(str, Enum):
    CLIPBOARD_TEXT = "clipboard_text"
    CLIPBOARD_IMAGE = "clipboard_image"
    SCREENSHOT = "screenshot"
    REGION_SCREENSHOT = "region_screenshot"
    AUDIO_RECORD = "audio_record"
    VIDEO_RETRO = "video_retro"
    VIDEO_HOLD = "video_hold"
    SUBTITLE_FILE = "subtitle_file"
    IMAGE_FILE = "image_file"
    AUDIO_FILE = "audio_file"
    PDF_FILE = "pdf_file"
    KINDLE = "kindle"
    YOUTUBE = "youtube"


class CaptureMode(str, Enum):
    INSTANT = "instant"
    BATCH = "batch"
    MONITOR = "monitor"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    SKIPPED = "skipped"


class RetryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DEAD = "dead"
    SUCCEEDED = "succeeded"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    LOW = 10
    NORMAL = 5
    HIGH = 2
    CRITICAL = 1


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class SilenceLevel(int, Enum):
    OFF = 0
    TOAST_ONLY = 1
    FULL = 2


class AnalysisProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class OcrEngine(str, Enum):
    PADDLE = "paddle"
    MANGA_OCR = "manga_ocr"
    WINDOWS_OCR = "windows_ocr"


class AsrEngine(str, Enum):
    WHISPER_LOCAL = "whisper_local"
    WHISPER_API = "whisper_api"


class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ContentType(str, Enum):
    STORY = "story"
    SCRIPT = "script"
    GAME = "game"
'''

FILES["src/vocabchan/shared/errors.py"] = '''"""Unified exception hierarchy."""
from __future__ import annotations


class VocabChanError(Exception): ...
class ConfigError(VocabChanError): ...
class DatabaseError(VocabChanError): ...
class MigrationError(DatabaseError): ...
class CaptureError(VocabChanError): ...
class ClipboardError(CaptureError): ...
class ScreenshotError(CaptureError): ...
class AudioCaptureError(CaptureError): ...
class FileImportError(VocabChanError): ...
class AnalysisError(VocabChanError): ...
class ProviderError(AnalysisError): ...
class ProviderAuthError(ProviderError): ...
class ProviderRateLimitError(ProviderError): ...
class ParseError(AnalysisError): ...
class CacheError(AnalysisError): ...
class IntegrationError(VocabChanError): ...
class AnkiConnectError(IntegrationError): ...
class ObsidianError(IntegrationError): ...
class JobError(VocabChanError): ...
class JobCancelledError(JobError): ...
'''

FILES["src/vocabchan/shared/result.py"] = '''"""Result[T, E] type."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
U = TypeVar("U")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    @property
    def is_ok(self) -> bool: return True

    @property
    def is_err(self) -> bool: return False

    def unwrap(self) -> T: return self.value

    def map(self, fn: Callable[[T], U]) -> "Ok[U]": return Ok(fn(self.value))


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    @property
    def is_ok(self) -> bool: return False

    @property
    def is_err(self) -> bool: return True

    def unwrap(self) -> None: raise self.error

    def map(self, fn: object) -> "Err[E]": return self


Result = Ok[T] | Err[E]
'''

FILES["src/vocabchan/shared/ids.py"] = '''"""Type-safe domain identifiers."""
from __future__ import annotations
from typing import NewType

VocabId = NewType("VocabId", int)
WordStatId = NewType("WordStatId", int)
RetryJobId = NewType("RetryJobId", int)
ProfileId = NewType("ProfileId", str)
JobId = NewType("JobId", str)
GlossaryTermId = NewType("GlossaryTermId", int)
SessionId = NewType("SessionId", str)
ContentId = NewType("ContentId", int)
'''

FILES["src/vocabchan/shared/utils/__init__.py"] = ""
FILES["src/vocabchan/shared/utils/text_utils.py"] = '''"""Pure text utilities."""
from __future__ import annotations


def truncate(text: str, max_len: int, suffix: str = "\u2026") -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def is_cjk(char: str) -> bool:
    cp = ord(char)
    return (0x4E00 <= cp <= 0x9FFF or 0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF)
'''

FILES["src/vocabchan/shared/utils/file_utils.py"] = '''"""Pure file utilities."""
from __future__ import annotations
import os
from pathlib import Path


def safe_filename(name: str) -> str:
    return "".join("_" if c in r'\\/:*?"<>|' else c for c in name)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    os.replace(tmp, path)
'''

FILES["src/vocabchan/shared/utils/datetime_utils.py"] = '''"""Datetime utilities."""
from __future__ import annotations
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def iso_now() -> str:
    return utcnow().isoformat()
'''

for path, content in FILES.items():
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

print(f"Part 1 written: {len(FILES)} files")
