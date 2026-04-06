import threading
import sys
import os


def _run_core():
    """Start core daemon in background thread (core.py blocks on while True: loop)."""
    try:
        import core
    except Exception as e:
        import logging
        logging.error(f"Core daemon startup error: {e}")


# Launch core daemon in background daemon thread
_core_thread = threading.Thread(target=_run_core, daemon=True)
_core_thread.start()

# Launch settings UI on main thread
from config_ui import IzumiOmniUI

if __name__ == "__main__":
    app = IzumiOmniUI()
    app.mainloop()
    os._exit(0)  # Force-terminate keyboard hook threads; prevents onefile temp-lock on relaunch
