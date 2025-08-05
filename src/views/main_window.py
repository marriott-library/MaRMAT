"""

main_window.py

Window for the main interface of the MaRMAT application.

Author:
  - Aiden deBoer

Date: 2025-06-18

"""

from pathlib import Path  # For file path handling

from PyQt6.QtCore import QCoreApplication, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """
    
    Main window for the MaRMAT application.
    This window serves as the entry point for the application, providing options to run MaRMAT,
    view instructions, access settings, and quit the application.
    
    Attributes:
        controller (MainController): The main controller for the application.
        path_to_image (Path): Path to the application icon image.
        path_to_small_image (Path): Path to the small icon image for alerts.
        msg_box (QMessageBox): Message box for displaying alerts.

    """
    def __init__(self, controller):
        """Initialize the main window.
        
        Args:
            controller (MainController): The main controller for the application.
        """
        super().__init__()

        # Set application name and icon
        self.path_to_image = Path(__file__).resolve().parent.parent / "data" / "sticker-transparent.png"

        self.setWindowIcon(QIcon(str(self.path_to_image)))  # Set the application icon

        # Set the application window name
        QCoreApplication.setApplicationName("MaRMAT")

        # Set the controller reference
        self.controller = controller
        
        self.init_ui()
        
        # Welcome message after a short delay
        # This is to ensure the UI is fully loaded before showing the alert
        QTimer.singleShot(500, lambda: self.show_alert("Welcome to MaRMAT 2.6.0-rc!", "The Marriott Reparative Metadata Assessment Tool (MaRMAT) is an open-source application created by librarians at the University of Utah’s J. Willard Marriott Library to help metadata practitioners flag various terms and phrases within metadata records using pre-curated and custom lexicons. MaRMAT is schema agnostic and supports library and museum professionals in assessing metadata for harmful, outdated, and otherwise problematic language as well as in performing text-based analyses of tabular metadata.<br><br><b>New to the tool?</b> Click Getting Started for a step-by-step walkthrough.<br><br>Click <b>OK</b> to continue."))


    def init_ui(self):
        """Initialize the user interface."""
        # Create the main layout for the window
        self.setWindowTitle("MaRMAT 2.6.0-rc")
        layout = QVBoxLayout()
        button_layout = QVBoxLayout()

        # Create UI elements
        self.image_label = QLabel()

        # Load MaRMAT Logo image and scale accordingly
        pixmap = QPixmap(str(self.path_to_image))
        if pixmap.isNull():
            print(f"Error: Unable to load image from {self.path_to_image}")
        else:
            scaled_pixmap = pixmap.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio)  # Resize to 512x512 while maintaining aspect ratio
            self.image_label.setPixmap(scaled_pixmap)

        # Create and center the label’s text
        self.title_label = QLabel("<i>Welcome to <b>The Marriott Reparative Metadata Assessment Tool (MaRMAT)</b>!</i>")
        self.title_label.setFont(QFont("Calibri", 36))  # Set font size
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create buttons
        self.next_button = QPushButton("Run MaRMAT")
        self.next_button.clicked.connect(self.controller.show_metadata_screen)
        self.next_button.setStyleSheet("background-color: #890000; color: white;")

        self.instructions_button = QPushButton("Getting Started")
        self.instructions_button.clicked.connect(self.controller.show_instructions_screen)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.controller.show_settings_screen)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)

        # Set a consistent maximum width for buttons (e.g., 500 pixels)
        for btn in [self.next_button, self.instructions_button, self.settings_button, self.quit_button]:
            btn.setMinimumWidth(500)
            btn.setMaximumWidth(500)

        # Add buttons to the button layout
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the buttons
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.instructions_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.quit_button)

        # Version label
        version_and_credit_container = QHBoxLayout()
        
        self.version_label = QLabel("""MaRMAT 2.6.0-rc<br>© 2025<br><b><a href="https://docs.google.com/forms/d/e/1FAIpQLScIxw2IEda2-GaUtNawuQCC4IrCrXiQgZybduVjKLj99peVLg/viewform?usp=dialog">Report Bug</a></b>""")
        self.version_label.setOpenExternalLinks(True)  # Enable clickable links in the label
        self.version_label.setFont(QFont("Calibri", 10))  # Set font size for version label
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.credit_label = """<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Main Title Window</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: Calibri, sans-serif;
      height: 100vh;
      position: relative;
    }

    .credits {
      position: absolute;
      bottom: 10px;
      left: 10px;
      font-size: 12px;
      color: #555;
    }

    .credits h2 {
      margin: 4px 0 2px 0;
      font-size: 13px;
    }

    .credits ul {
      margin: 0 0 8px 0;
      padding-left: 16px;
      list-style: none;
    }

    .credits li {
      margin: 0;
    }
  </style>
</head>
<body>

  <div class="credits">
    <h3>Concept and Design:</h3>
    <ul>
      <li>Rachel Wittmann</li>
      <li>Kaylee Alexander</li>
    </ul>

    <h3>Programming and Development:</h3>
    <ul>
      <li>Aiden DeBoer</li>
    </ul>
  </div>

</body>
</html>"""

        self.credit_label = QLabel(self.credit_label)
        self.credit_label.setFont(QFont("Calibri", 10))  # Set font size for credit label
        self.credit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.credit_label.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text formatting

        # Add the version and credit labels to the container layout
        version_and_credit_container.addWidget(self.credit_label)
        version_and_credit_container.addStretch(1)  # Add stretchable space between credit and version labels
        version_and_credit_container.addWidget(self.version_label)
        

        # Add the label, image, and buttons to the layout and center the widget itself
        layout.addStretch(1)  # Add stretchable space at the top
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)  # Add stretchable space between title and image
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)  # Add stretchable space between image and buttons
        layout.addLayout(button_layout)
        layout.addStretch(1)  # Add stretchable space at the bottom
        layout.addLayout(version_and_credit_container)

        # Create the container widget and set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def show_alert(self, title, message):
        """
        
        Show an alert message box with a custom icon and message.

        Args:
            title (str): The title of the message box.
            message (str): The message to display in the message box.
        
        """

        if self.controller.settings_model.popups_enabled is False:
            return

        self.msg_box = QMessageBox(self)
        self.msg_box.setWindowTitle(title)
        self.msg_box.setText(message)
        
        # Load and set a custom icon
        self.path_to_small_image = Path(__file__).resolve().parent.parent / "data" / "sticker-transparent-(64x64).png" 
        if not self.path_to_small_image.exists():
            print(f"Error: Icon file not found at {self.path_to_small_image}")
        else:
            pixmap = QPixmap(str(self.path_to_small_image))
        self.msg_box.setIconPixmap(pixmap)

        self.msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.msg_box.setStyleSheet("QMessageBox { font-size: 16px; }")
        self.msg_box.setBaseSize(400, 200)
        
        self.msg_box.exec()
        self.msg_box.deleteLater()
    
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
  
  
    def resizeEvent(self, event):
        # Get new size
        width = self.width()
        height = self.height()

        # Use width or height to calculate font size
        self.title_label.setFont(QFont("Calibri", width//45))  # Set font size

        # Always call base implementation
        super().resizeEvent(event)