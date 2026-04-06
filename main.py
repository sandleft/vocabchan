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


if __name__ == "__main__":
    # Launch core daemon in background daemon thread FIRST
    _core_thread = threading.Thread(target=_run_core, daemon=True)
    _core_thread.start()

    # Import config_ui AFTER core thread is dispatched to avoid competing init_db() calls
    from config_ui import IzumiOmniUI
    app = IzumiOmniUI()
    app.mainloop()
    os._exit(0)  # Force-terminate keyboard hook threads; prevents onefile temp-lock on relaunch
