"""

session_state.py

Single-session, in-memory application state for the local MaRMAT web app.

Because MaRMAT runs locally for one user, a single module-level ``AppState``
holds everything that must survive between HTTP requests: the
``MarmatProcessing`` instance (loaded metadata/lexicon, selections, results),
user settings, and the live matching-progress store. A ``threading.Lock``
guards the progress store and the "is a job running?" flag so the background
matching thread and the polling requests never race.

Author:
    - Aiden deBoer
"""

import threading

from core.marmat_core import MarmatProcessing
from core.settings_store import SettingsStore


class AppState:
    """Holds all per-session state for the single local user."""

    def __init__(self):
        # Core processing engine (loads the default lexicon on construction).
        self.core = MarmatProcessing()
        self.settings = SettingsStore()

        # Loaded-file bookkeeping for nav guards and UI hints.
        self.metadata_loaded = False
        self.metadata_filename = None
        self.metadata_is_ead = False
        self.lexicon_loaded = False
        self.lexicon_name = None

        # Matching job + progress tracking.
        self._lock = threading.Lock()
        self._job_thread = None
        self.progress = {"status": "idle", "percent": 0, "message": ""}

    # ---- Progress / job control -------------------------------------- #

    def is_job_running(self):
        with self._lock:
            return self.progress["status"] == "running"

    def start_job(self, target):
        """
        Start a matching job in a background thread if none is running.

        Args:
            target (callable): The function to run in the background. It receives
                no arguments and should use ``set_progress``/``finish_job``.

        Returns:
            bool: True if the job was started, False if one is already running.
        """
        with self._lock:
            if self.progress["status"] == "running":
                return False
            self.progress = {"status": "running", "percent": 0, "message": "Starting analysis..."}

        thread = threading.Thread(target=target, daemon=True)
        self._job_thread = thread
        thread.start()
        return True

    def set_progress(self, percent, message=None):
        with self._lock:
            self.progress["percent"] = int(percent)
            if message is not None:
                self.progress["message"] = message

    def finish_job(self, message="Analysis complete."):
        with self._lock:
            self.progress = {"status": "done", "percent": 100, "message": message}

    def fail_job(self, message):
        with self._lock:
            self.progress = {"status": "error", "percent": self.progress.get("percent", 0), "message": message}

    def get_progress(self):
        with self._lock:
            return dict(self.progress)

    def reset_progress(self):
        with self._lock:
            self.progress = {"status": "idle", "percent": 0, "message": ""}


# Module-level singleton, created lazily by the app factory.
state = None


def init_state():
    """Create (once) and return the global AppState singleton."""
    global state
    if state is None:
        state = AppState()
    return state


def get_state():
    """Return the global AppState singleton (initialising it if needed)."""
    return init_state()
