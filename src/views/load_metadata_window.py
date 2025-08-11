"""

load_metadata_window.py

Window for loading a metadata file in the MaRMAT project.

Author:
    - Aiden deBoer

Date: 2025-08-11

"""
import os
from pathlib import Path

import pandas as pd
from PyQt6.QtCore import QCoreApplication, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QComboBox,
    QSizePolicy
)


class MetadataWindow(QWidget):
    """
    
    Window for loading a metadata file in the MaRMAT project.
    This window allows users to load a CSV file containing metadata,
    which will be used for analyzing the data in the MaRMAT application.

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
        
        Initialize the MetadataWindow with a controller instance.
        
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
        """ Initialize the user interface for the MetadataWindow """
        # Layout for the window
        layout = QVBoxLayout()

        # Label for the title
        self.title_label = QLabel("<b>Please load a metadata file (.csv or .tsv)</b>")
        self.title_label.setFont(QFont("Calibri", 36))  # Set font size
        layout.addWidget(self.title_label)

        # Label to display information about the CSV
        self.info_label = QLabel("Click the <b>Load Metadata</b> button to load the metadata file you want MaRMAT to analyze.<br>MaRMAT only supports CSV and TSV file uploads. Once loaded, click Next.") # Initial text
        layout.addWidget(self.info_label)

        # Button to load the CSV file
        button_tab_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Metadata")
        self.load_button.clicked.connect(self.load_csv)
        self.load_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        
        self.delimiter_box = QComboBox()
        self.delimiter_box.setStyleSheet("background-color: #f0f0f0; color: black;")  # Set background and text color
        self.delimiter_box.setToolTip("Select the delimiter used in your CSV file")
        self.delimiter_box.setFont(QFont("Calibri", 14))  # Set font size
        self.delimiter_box.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.load_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.delimiter_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.delimiter_box.addItem("Select Delimiter")
        self.delimiter_box.addItem("Comma (,)")
        self.delimiter_box.addItem("Tab (\\t)")
        self.delimiter_box.addItem("Semicolon (;)")
        self.delimiter_box.addItem("Space ( )")
        self.delimiter_box.addItem("Pipe (|)")
        self.delimiter_box.adjustSize()

        self.delimiter_box.setCurrentIndex(0)  # Default to "Select Delimiter"
        
        button_tab_layout.addWidget(self.load_button)
        button_tab_layout.addWidget(self.delimiter_box)

        layout.addLayout(button_tab_layout)

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
        self.next_button.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_button)

        # Add the horizontal button layout to the main layout
        layout.addLayout(button_layout)

        # Set the layout to the window
        self.setLayout(layout)

    def load_csv(self):
        """ Load a CSV file and display its content in the table widget. Uses a thread to handle long-running tasks. """

        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV/TSV",
            self.controller.get_default_metadata_path(),
            "Data Files (*.csv *.tsv);;CSV Files (*.csv);;TSV Files (*.tsv);;All Files (*)"
        )
        
        if self.file_path:
            try:

                self.next_button.setEnabled(False)  # Disable the next button until the file is loaded
                self.next_button.setStyleSheet("")  # Change button color to grey

                # Determine delimiter based on file extension
                _, file_extension = os.path.splitext(self.file_path)
                if self.delimiter_box.currentText() == "Select Delimiter":
                    delimiter = '\t' if file_extension.lower() == '.tsv' else ','
                elif self.delimiter_box.currentText() == "Comma (,)":
                    delimiter = ','
                elif self.delimiter_box.currentText() == "Tab (\\t)":
                    delimiter = '\t'
                elif self.delimiter_box.currentText() == "Semicolon (;)":
                    delimiter = ';'
                elif self.delimiter_box.currentText() == "Space ( )":
                    delimiter = ' '
                elif self.delimiter_box.currentText() == "Pipe (|)":
                    delimiter = '|'
                else:
                    delimiter = ','  # Default to comma if somehow nothing is selected

                # Load the file into a DataFrame with TSV-specific handling
                self.df = pd.read_csv(self.file_path, delimiter=delimiter, encoding='utf-8', on_bad_lines='warn', nrows=1000)

                self.load_button.setDisabled(True)  # Disable the load button after loading the file
                self.load_button.setStyleSheet("")  # Change button color to grey
                self.info_label.setText(f"Loading CSV: {self.file_path} <br> <b>Please wait...</b>")

                file_size = os.path.getsize(self.file_path)
                print(f"File size: {file_size} bytes")

                if file_size > 100 * 1024 * 1024:  # Check if file size is greater than 100 MB
                    self.show_alert("Warning", "The file is larger than 100 MB. This may take a while to load.")

                self.thread = QThread()
                self.worker = Worker(self.controller, self.file_path, delimiter)  # Pass the file path to the worker
                self.worker.moveToThread(self.thread)

                self.thread.started.connect(self.worker.run)
                self.worker.finished.connect(self.worker.deleteLater)
                self.worker.finished.connect(self.file_successfully_loaded)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.finished.connect(self.thread.quit)

                self.thread.start()
                self.controller = self.worker.controller  # Update the controller reference in the worker

            except Exception as e:
                self.info_label.setText(f"Failed to load CSV: {e}")

    def file_successfully_loaded(self, success):
        """
        
        Update the status of whether a file has been successfully loaded
        
        Args:
            success (bool): Indicates whether the file was loaded successfully.

        """
        if success:
            # Once a CSV is loaded, enable the 'Next' button
            self.next_button.setEnabled(True)
            self.info_label.setText(f"CSV loaded successfully: {self.file_path}")

            self.display_csv()
            self.show_alert("Success", "Metadata loaded successfully!<br>Only the <b>first 1000 rows</b> are displayed in the table widget. <br>Click Next to proceed to the next step.")

            # Reset the styles of the buttons
            self.load_button.setStyleSheet("")
            self.next_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        else:
            self.show_alert("Error", "Failed to load metadata. Please check the file format.")
            self.info_label.setText("Failed to load metadata. Please try again.")
        self.load_button.setDisabled(False)  # Re-enable the load button


    def display_csv(self):
        """ Display the CSV data in the table widget """
        self.table_widget.setRowCount(self.df.shape[0])
        self.table_widget.setColumnCount(self.df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)

        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                item = QTableWidgetItem(str(self.df.iloc[row, col]))
                self.table_widget.setItem(row, col, item)

    def go_to_next_page(self):
        """ Action when the 'Next' button is clicked """
        self.controller.show_lexicon_screen()

    def go_to_previous_page(self):
        """ Return to the previous page, the home screen """
        self.controller.show_main_screen()  # Go back to the metadata loading screen
        
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
        
        Show an alert message box with a custom icon.
        This method displays a message box with the specified title and message. 
        
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
            pixmap = QPixmap(str(self.path_to_small_image))  # Replace with your image path
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

        self.info_label.setFont(QFont("Calibri", width//70))  # Set font size
        # Always call base implementation
        super().resizeEvent(event)

class Worker(QThread):
    """
    
    Worker class for loading metadata in a separate thread.
    This class is responsible for performing the long-running task of loading metadata
    from a CSV file without blocking the main GUI thread.

    Attributes:
        finished (pyqtSignal): Signal emitted when the worker has finished its task.
        controller (Controller): The controller instance that manages the application logic.
        file_path (str): The path to the CSV file to be loaded.
    
    """
    
    finished = pyqtSignal(bool)

    def __init__(self, controller, file_path, delimiter):
        """ 

        Initialize the worker with a controller and file path 

        Args:
            controller (Controller): The controller instance that manages the application logic.
            file_path (str): The path to the CSV file to be loaded.
        
        """
        super().__init__()
        self.controller = controller
        self.file_path = file_path
        self.delimiter = delimiter

    def run(self):
        """ Run the long-running task in a separate thread """
        if self.controller.load_metadata(self.file_path, self.delimiter):
            self.finished.emit(True)
        else:
            self.finished.emit(False)