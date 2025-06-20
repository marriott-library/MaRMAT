"""

settings_model.py

This is the settings model for the MaRMAT application.
It handles the loading and saving of application settings using QSettings.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""

from PyQt6.QtCore import QSettings
from pathlib import Path

class SettingsModel:
    """

    SettingsModel class for managing application settings in MaRMAT.
    This class uses QSettings to store and retrieve settings such as
    popups, fullscreen mode, and default file paths for metadata, lexicons, and results.

    Attributes:
        settings (QSettings): The QSettings object used to store application settings.
        popups_enabled (bool): Whether popups are enabled in the application.
        fullscreen_enabled (bool): Whether fullscreen mode is enabled.
        default_metadata_path (str): Default path for metadata files.
        default_lexicon_path (str): Default path for lexicon files.
        default_results_path (str): Default path for saving results.

    """

    def __init__(self):
        """Initialize the SettingsModel with default values and load existing settings."""
        self.settings = QSettings("MaRMATTeam", "MaRMAT")
        self.popups_enabled = False
        self.fullscreen_enabled = False
        self.default_metadata_path = ""
        self.default_lexicon_path = ""
        self.default_results_path = ""
        self.load_settings()


    def save_settings(self):
        """Save the current settings to QSettings."""
        self.settings.setValue("popups", self.popups_enabled)
        self.settings.setValue("fullscreen", self.fullscreen_enabled)
        self.settings.setValue("default_metadata_path", self.default_metadata_path)
        self.settings.setValue("default_lexicon_path", self.default_lexicon_path)
        self.settings.setValue("default_results_path", self.default_results_path)

    def load_settings(self):
        """Load settings from QSettings."""
        self.popups_enabled = self.settings.value("popups", True, type=bool)
        self.fullscreen_enabled = self.settings.value("fullscreen", False, type=bool)
        self.default_metadata_path = self.settings.value("default_metadata_path", str(Path.cwd()), type=str)
        self.default_lexicon_path = self.settings.value("default_lexicon_path", str(Path.cwd()), type=str)
        self.default_results_path = self.settings.value("default_results_path", str(Path.cwd()), type=str)