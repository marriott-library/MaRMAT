"""

settings_window.py

Window for configuring settings in the MaRMAT application.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont

class SettingsWindow(QMainWindow):
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

        # Create a setting for toggling popups
        popups_setting_layout = QHBoxLayout()
        self.popups_enabled_button = QPushButton("Toggle Popups")
        self.popups_enabled_label = QLabel(f"Popups are currently: {'<b>Enabled</b>' if self.controller.settings_model.popups_enabled else '<b>Disabled</b>'}")
        self.popups_enabled_button.clicked.connect(self.toggle_popups)
        popups_setting_layout.addWidget(self.popups_enabled_button)
        popups_setting_layout.addWidget(self.popups_enabled_label)
        popups_setting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a setting for toggling fullscreen mode
        fullscreen_setting_layout = QHBoxLayout()
        self.fullscreen_button = QPushButton("Toggle Fullscreen")
        self.fullscreen_button.clicked.connect(self.controller.toggle_fullscreen)
        self.fullscreen_label = QLabel(f"Fullscreen is currently: {'<b>Enabled</b>' if self.controller.settings_model.fullscreen_enabled else '<b>Disabled</b>'}")
        fullscreen_setting_layout.addWidget(self.fullscreen_button)
        fullscreen_setting_layout.addWidget(self.fullscreen_label)
        fullscreen_setting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a setting for setting a default file path for loading metadata files
        metadata_setting_layout = QHBoxLayout()
        self.metadata_button = QPushButton("Set Default Metadata Directory")
        self.metadata_button.clicked.connect(self.controller.set_default_metadata_path)
        self.metadata_scroll_area = QScrollArea()
        self.metadata_scroll_area.setMaximumWidth(1000)
        self.metadata_scroll_area.setWidgetResizable(True)
        self.metadata_label = QLabel(f"Default Metadata Path: {self.controller.settings_model.default_metadata_path}")
        self.metadata_scroll_area.setWidget(self.metadata_label)
        metadata_setting_layout.addWidget(self.metadata_button)
        metadata_setting_layout.addWidget(self.metadata_scroll_area)
        metadata_setting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a setting for setting a default file path for loading lexicon files
        lexicon_setting_layout = QHBoxLayout()
        self.lexicon_button = QPushButton("Set Default Lexicon Directory")
        self.lexicon_button.clicked.connect(self.controller.set_default_lexicon_path)
        self.lexicon_scroll_area = QScrollArea()
        self.lexicon_scroll_area.setMaximumWidth(1000)
        self.lexicon_scroll_area.setWidgetResizable(True)
        self.lexicon_label = QLabel(f"Default Lexicon Path: {self.controller.settings_model.default_lexicon_path}")
        self.lexicon_scroll_area.setWidget(self.lexicon_label)
        lexicon_setting_layout.addWidget(self.lexicon_button)
        lexicon_setting_layout.addWidget(self.lexicon_scroll_area)
        lexicon_setting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a setting for setting a default file path for saving results
        save_results_setting_layout = QHBoxLayout()
        self.save_results_button = QPushButton("Set Default Results Directory")
        self.save_results_button.clicked.connect(self.controller.set_default_results_path)
        self.save_results_scroll_area = QScrollArea()
        self.save_results_scroll_area.setMaximumWidth(1000)
        self.save_results_scroll_area.setWidgetResizable(True)
        self.save_results_label = QLabel(f"Default Results Path: {self.controller.settings_model.default_results_path}")
        self.save_results_scroll_area.setWidget(self.save_results_label)
        save_results_setting_layout.addWidget(self.save_results_button)
        save_results_setting_layout.addWidget(self.save_results_scroll_area)
        save_results_setting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a layout for the instructions window
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Set margins for the layout
        layout.setSpacing(20)  # Set spacing between widgets
        layout.addWidget(title_label)
        layout.addStretch(1)  # Add stretchable space at the top
        layout.addLayout(popups_setting_layout)
        layout.addLayout(fullscreen_setting_layout)
        layout.addLayout(metadata_setting_layout)
        layout.addLayout(lexicon_setting_layout)
        layout.addLayout(save_results_setting_layout)
        layout.addStretch(1)  # Add stretchable space at the bottom
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the central widget of the window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event):
        """
        
        Override the key press event to handle specific key actions.
        
        Args:
            event (QKeyEvent): The key press event to handle.

        """
        if event.key() == Qt.Key.Key_F11:
            self.controller.toggle_fullscreen()  # Call the controller's toggle_fullscreen method
        elif event.key() == Qt.Key.Key_Escape:
            # Close the application
            QCoreApplication.instance().quit()
        else:
            super().keyPressEvent(event)  # Keep default behavior
    
    def toggle_popups(self):
        """Toggle the popups setting and update the label."""
        self.controller.settings_model.popups_enabled = not self.controller.settings_model.popups_enabled
        self.controller.save_settings()
        self.popups_enabled_label.setText(f"Popups are currently: {'<b>Enabled</b>' if self.controller.settings_model.popups_enabled else '<b>Disabled</b>'}")