"""

load_lexicon_window.py

Window for loading a lexicon file in the MaRMAT project.

Author:
    - Aiden deBoer

Date: 2025-08-11

"""
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QPixmap, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QMessageBox,
)

import pandas as pd
from pathlib import Path  # For file path handling


class LexiconWindow(QWidget):
    """
    Window for loading a lexicon file in the MaRMAT project.
    This window allows users to load a CSV file containing lexicon data,
    which will be used for analyzing metadata files.
    
    Attributes:
        controller (Controller): The controller instance that manages the application logic.
        title_label (QLabel): Label for the title of the window.
        info_label (QLabel): Label to display information about the CSV file.
        load_button (QPushButton): Button to load the CSV file.
        table_widget (QTableWidget): Table to display the content of the loaded CSV file.
        previous_button (QPushButton): Button to go back to the previous page.
        next_button (QPushButton): Button to go to the next page after loading the CSV.
    
    """
    def __init__(self, controller):
        """

        Initialize the LexiconWindow with a controller instance.
        
        Args:
            controller (Controller): The controller instance that manages the application logic.

        """
        super().__init__()

        self.controller = controller
        self.init_ui()
        
                # Shortcuts
        zoom_in = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in.activated.connect(lambda: self.controller.adjust_font_size(1))

        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(lambda: self.controller.adjust_font_size(-1))
        
        reset_zoom = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_zoom.activated.connect(lambda: self.controller.adjust_font_size(0))

    def init_ui(self):
        """ Initialize the user interface for the LexiconWindow """
        # Layout for the window
        layout = QVBoxLayout()

        # Label for the title
        self.title_label = QLabel("<b>Please load a lexicon file (.csv)</b>")
        self.title_label.setFont(QFont("Calibri", 36))  # Set font size
        layout.addWidget(self.title_label)

        # Label to display information about the CSV
        self.info_label = QLabel("Click the <b>Load Lexicon</b> button to load the lexicon file you want MaRMAT to analyze your metadata file against.<br>MaRMAT only supports CSV file uploads. Once loaded, click <b>Next</b>. ") # Initial text
        layout.addWidget(self.info_label)

        # Button to load the CSV file
        self.load_button = QPushButton("Load Lexicon")
        self.load_button.clicked.connect(self.load_csv)
        self.load_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        layout.addWidget(self.load_button)

        # Table to display the CSV content
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Create a horizontal layout for the Previous and Next buttons
        button_layout = QHBoxLayout()

        # Previous button, initially disabled if no previous window is provided
        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.go_to_previous_page)
        button_layout.addWidget(self.previous_button)

        # Next button, initially greyed out (disabled)
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)  # Greyed out initially
        self.next_button.clicked.connect(self.go_to_next_page)  # Action when clicked
        button_layout.addWidget(self.next_button)

        # Add the horizontal button layout to the main layout
        layout.addLayout(button_layout)

        # Set the layout to the window
        self.setLayout(layout)

    def load_csv(self):
        """ Opens a file dialog and loads the CSV file into a table """
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", self.controller.get_default_lexicon_path(), "CSV Files (*.csv)")

        if self.file_path:
            try:
                # Load the CSV file into a DataFrame
                df = pd.read_csv(self.file_path, nrows=1000)  # Limit to first 1000 rows
                self.display_csv(df)  # Display the data in the table

                # Once a CSV is loaded, enable the 'Next' button
                self.next_button.setEnabled(True)

                self.info_label.setText(f"CSV loaded successfully: {self.file_path}")

                # Load the metadata into the model
                if self.controller.load_lexicon(self.file_path):
                    self.show_alert("Success", "Lexicon loaded successfully!")

                    self.load_button.setStyleSheet("")
                    self.next_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
                else:
                    self.show_alert("Error", "Failed to load metadata. Please check the file format.")
                    self.info_label.setText("Failed to load metadata. Please try again.")

            except Exception as e:
                self.info_label.setText(f"Failed to load CSV: {e}")

    def display_csv(self, df):
        """
        
        Display the CSV data in the table widget
        
        Args:
            df (pd.DataFrame): The DataFrame containing the CSV data to display.

        """
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                self.table_widget.setItem(row, col, item)

    def go_to_next_page(self):
        """ Action when the 'Next' button is clicked """
        self.controller.show_data_selection_screen()

    def go_to_previous_page(self):
        """ Return to the previous page, the metadata loading screen """
        self.controller.show_metadata_screen()  # Go back to the metadata loading screen

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
    
    def show_alert(self, title, message) -> None:
        """ 
        
        Show an alert message
        
        Args:
            title (str): The title of the alert message box.
            message (str): The message to display in the alert box.
        
        Returns:
            None

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
    
    def resizeEvent(self, event):
        # Get new size
        width = self.width()
        height = self.height()

        # Use width or height to calculate font size
        self.info_label.setFont(QFont("Calibri", width//60))  # Set font size

        # Always call base implementation
        super().resizeEvent(event)