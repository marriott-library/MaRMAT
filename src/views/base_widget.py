from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QWidget, QMessageBox)

from pathlib import Path  # For file path handling

class BaseWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        zoom_in = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in.activated.connect(lambda: self.controller.adjust_font_size(1))

        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(lambda: self.controller.adjust_font_size(-1))
        
        reset_zoom = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_zoom.activated.connect(lambda: self.controller.adjust_font_size(0))

    def wheelEvent(self, event):
        # Check if Ctrl is being held
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                print("Ctrl + Mouse Wheel Up")
                # Example: zoom in font
                self.controller.adjust_font_size(1)
            else:
                print("Ctrl + Mouse Wheel Down")
                # Example: zoom out font
                self.controller.adjust_font_size(-1)
        else:
            super().wheelEvent(event)  # Let normal scrolling happen

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