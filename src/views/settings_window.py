"""

settings_window.py

Window for configuring settings in the MaRMAT application.

Author:
    - Aiden deBoer

Date: 2025-08-28

"""
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QPushButton, QGridLayout
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from views.base_widget import BaseWidget

class SettingsWindow(BaseWidget):
    """
    
    SettingsWindow class for configuring application settings in MaRMAT.
    This window allows users to toggle popups, fullscreen mode, and set default file paths
    for metadata, lexicons, and results.

    Attributes:
        controller (Controller): The controller instance that manages the application logic.
        popups_enabled_button (QPushButton): Button to toggle popups.
        popups_enabled_label (QLabel): Label to display the current state of popups.
        fullscreen_button (QPushButton): Button to toggle fullscreen mode.
        fullscreen_label (QLabel): Label to display the current state of fullscreen mode.
        metadata_button (QPushButton): Button to set the default metadata directory.
        metadata_scroll_area (QScrollArea): Scroll area to display the default metadata path.
        metadata_label (QLabel): Label to display the default metadata path.
        lexicon_button (QPushButton): Button to set the default lexicon directory.
        lexicon_scroll_area (QScrollArea): Scroll area to display the default lexicon path.
        lexicon_label (QLabel): Label to display the default lexicon path.
        save_results_button (QPushButton): Button to set the default results directory.
        save_results_scroll_area (QScrollArea): Scroll area to display the default results path.
        save_results_label (QLabel): Label to display the default results path.
    
    """
    def __init__(self, controller):
        """
        
        Initialize the SettingsWindow with a controller instance.
        
        Args:
            controller (Controller): The controller instance that manages the application logic.
        
        """

        super().__init__()

        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface for the settings window."""

        # Create a QLabel to display the instructions
        title_label = QLabel("Settings Window")
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Calibri", 36))

        # Create a button to go back to the previous screen or close
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.controller.show_main_screen)
        back_button.setStyleSheet("background-color: #890000; color: white;")
        back_button.setFont(QFont("Calibri", 18))
        back_button.setFixedSize(200, 50)

        # --- Use a QGridLayout for perfectly aligned columns ---
        settings_layout = QGridLayout()
        settings_layout.setHorizontalSpacing(30) # Spacing between buttons and text
        settings_layout.setVerticalSpacing(20)   # Spacing between rows

        # 1. Popups
        self.popups_enabled_button = QPushButton("Toggle Popups")
        self.popups_enabled_label = QLabel(f"Popups are currently: {'<b>Enabled</b>' if self.controller.settings_model.popups_enabled else '<b>Disabled</b>'}")
        self.popups_enabled_button.clicked.connect(self.toggle_popups)
        # Add to Grid: (Widget, Row, Column)
        settings_layout.addWidget(self.popups_enabled_button, 0, 0)
        settings_layout.addWidget(self.popups_enabled_label, 0, 1)

        # 2. Fullscreen
        self.fullscreen_button = QPushButton("Toggle Fullscreen")
        self.fullscreen_button.clicked.connect(self.controller.toggle_fullscreen)
        self.fullscreen_label = QLabel(f"Fullscreen is currently: {'<b>Enabled</b>' if self.controller.settings_model.fullscreen_enabled else '<b>Disabled</b>'}")
        settings_layout.addWidget(self.fullscreen_button, 1, 0)
        settings_layout.addWidget(self.fullscreen_label, 1, 1)

        # 3. Metadata Path
        self.metadata_button = QPushButton("Set Default Metadata Directory")
        self.metadata_button.clicked.connect(self.controller.set_default_metadata_path)
        self.metadata_scroll_area = QScrollArea()
        self.metadata_scroll_area.setMaximumWidth(1000)
        self.metadata_scroll_area.setWidgetResizable(True)
        self.metadata_label = QLabel(f"Default Metadata Path: {self.controller.settings_model.default_metadata_path}")
        self.metadata_scroll_area.setWidget(self.metadata_label)
        settings_layout.addWidget(self.metadata_button, 2, 0)
        settings_layout.addWidget(self.metadata_scroll_area, 2, 1)

        # 4. Lexicon Path
        self.lexicon_button = QPushButton("Set Default Lexicon Directory")
        self.lexicon_button.clicked.connect(self.controller.set_default_lexicon_path)
        self.lexicon_scroll_area = QScrollArea()
        self.lexicon_scroll_area.setMaximumWidth(1000)
        self.lexicon_scroll_area.setWidgetResizable(True)
        self.lexicon_label = QLabel(f"Default Lexicon Path: {self.controller.settings_model.default_lexicon_path}")
        self.lexicon_scroll_area.setWidget(self.lexicon_label)
        settings_layout.addWidget(self.lexicon_button, 3, 0)
        settings_layout.addWidget(self.lexicon_scroll_area, 3, 1)
        
        # 5. Results Path
        self.save_results_button = QPushButton("Set Default Results Directory")
        self.save_results_button.clicked.connect(self.controller.set_default_results_path)
        self.save_results_scroll_area = QScrollArea()
        self.save_results_scroll_area.setMaximumWidth(1000)
        self.save_results_scroll_area.setWidgetResizable(True)
        self.save_results_label = QLabel(f"Default Results Path: {self.controller.settings_model.default_results_path}")
        self.save_results_scroll_area.setWidget(self.save_results_label)
        settings_layout.addWidget(self.save_results_button, 4, 0)
        settings_layout.addWidget(self.save_results_scroll_area, 4, 1)

        # Force the text column (column 1) to stretch and fill remaining space
        settings_layout.setColumnStretch(1, 1)

        # Create a layout for the main window
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Set margins for the layout
        layout.setSpacing(20)  # Set spacing between widgets
        layout.addWidget(title_label)
        layout.addStretch(1)   # Add stretchable space at the top
        
        # Add the unified grid layout here
        layout.addLayout(settings_layout)
        
        layout.addStretch(1)   # Add stretchable space at the bottom
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the central widget of the window
        self.setLayout(layout)
    
    def toggle_popups(self):
        """Toggle the popups setting and update the label."""
        self.controller.settings_model.popups_enabled = not self.controller.settings_model.popups_enabled
        self.controller.save_settings()
        self.popups_enabled_label.setText(f"Popups are currently: {'<b>Enabled</b>' if self.controller.settings_model.popups_enabled else '<b>Disabled</b>'}")