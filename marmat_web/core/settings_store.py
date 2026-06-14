"""

settings_store.py

JSON-file-backed application settings, replacing the PyQt ``QSettings``-based
``SettingsModel``. For the local single-user web app we only keep the
default-folder preferences the user asked to retain (notably the default
results path); the desktop-only toggles (fullscreen, font zoom, popups) are
dropped.

Author:
    - Aiden deBoer
"""

import json
from pathlib import Path


# Store settings next to the user's home directory so they persist across runs
# and survive re-installs of the app folder.
SETTINGS_PATH = Path.home() / ".marmat" / "settings.json"

DEFAULTS = {
    "default_metadata_path": str(Path.cwd()),
    "default_lexicon_path": str(Path.cwd()),
    "default_results_path": str(Path.home() / "Downloads"),
}


class SettingsStore:
    """Load, hold, and persist user preferences as a small JSON file."""

    def __init__(self, path=SETTINGS_PATH):
        self.path = Path(path)
        self.values = dict(DEFAULTS)
        self.load()

    def load(self):
        """Load settings from disk, falling back to defaults for missing keys."""
        try:
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                for key in DEFAULTS:
                    if key in stored and stored[key]:
                        self.values[key] = stored[key]
        except Exception as e:
            print(f"Could not load settings ({e}); using defaults.")

    def save(self):
        """Persist the current settings to disk."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.values, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")

    def get(self, key, default=None):
        """Return a single setting value."""
        return self.values.get(key, default)

    def update(self, new_values):
        """Update one or more settings and persist them. Returns the new values."""
        for key, value in new_values.items():
            if key in DEFAULTS:
                self.values[key] = value
        self.save()
        return self.values
