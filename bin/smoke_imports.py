from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

MODULES = [
    "vocabchan.app.bootstrap",
    "vocabchan.app.container",
    "vocabchan.gui.shell.main_window",
    "vocabchan.gui.presenters.event_bridge",
    "vocabchan.task_engine.api.task_engine",
    "vocabchan.task_engine.runtime.async_host",
    "vocabchan.unified_interface.ports.analysis",
    "vocabchan.unified_interface.ports.capture",
    "vocabchan.storage_adapter.contracts.repositories",
    "vocabchan.infrastructure.event_bus.event_bus",
]


def main() -> int:
    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"OK {module_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
