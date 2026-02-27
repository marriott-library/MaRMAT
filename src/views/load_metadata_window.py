"""

load_metadata_window.py

Window for loading a metadata file in the MaRMAT project.

Author:
    - Aiden deBoer

Date: 2025-10-14

"""
import os
from pathlib import Path

import pandas as pd
from PyQt6.QtCore import QCoreApplication, QObject, QThread, Qt, pyqtSignal
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
    QProgressBar,
    QSizePolicy
)
from views.base_widget import BaseWidget

class MetadataWindow(BaseWidget):
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
        


    def init_ui(self):
        """ Initialize the user interface for the MetadataWindow """
        # Layout for the window
        layout = QVBoxLayout()

        # Label for the title
        self.title_label = QLabel("<b>Please load a metadata file (.csv or .tsv)</b>")
        self.title_label.setFont(QFont("Calibri", 36))  # Set font size
        layout.addWidget(self.title_label)

        # Label to display information about the CSV
        self.info_label = QLabel(
            "Select <span style='color: #FF7F7F;'>your spreadsheet’s</span> column delimiter from the dropdown menu, "
            "then click the <b>Load Metadata</b> button to upload your metadata file."
        )
        layout.addWidget(self.info_label)

        # Button to load the CSV file
        button_tab_layout = QHBoxLayout()
        
        self.delimiter_box = QComboBox()
        self.delimiter_box.setStyleSheet("background-color: #f0f0f0; color: black;")  # Set background and text color
        self.delimiter_box.setToolTip("Select the delimiter used in your CSV file")
        self.delimiter_box.setFont(QFont("Calibri", 14))  # Set font size
        self.delimiter_box.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.delimiter_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.delimiter_box.addItem("Select Column Delimiter")
        self.delimiter_box.addItem("Comma (,)")
        self.delimiter_box.addItem("Tab (\\t)")
        self.delimiter_box.addItem("Semicolon (;)")
        self.delimiter_box.addItem("Space ( )")
        self.delimiter_box.addItem("Pipe (|)")
        self.delimiter_box.adjustSize()

        # Connect method to make sure a delimeter is selected before loading
        self.delimiter_box.currentIndexChanged.connect(self.update_load_button_state)

        self.load_button = QPushButton("Load Metadata")
        self.load_button.clicked.connect(self.load_csv)

        self.load_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.delimiter_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # # Make the QComboBox editable to access its QLineEdit
        # self.delimiter_box.setEditable(True)

        # # Get the QLineEdit object
        # line_edit = self.delimiter_box.lineEdit()

        # # Set the alignment to center
        # line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # # Make the QLineEdit read-only if you don't want direct editing
        # line_edit.setReadOnly(True)

        self.load_button.setEnabled(False)  # Initially disabled until a delimiter is selected

        self.delimiter_box.setCurrentIndex(0)  # Default to "Select Delimiter"

        button_tab_layout.addWidget(self.delimiter_box)
        button_tab_layout.addWidget(self.load_button)

        layout.addLayout(button_tab_layout)

        # Progress bar shown during file loading (indeterminate / pulsing mode).
        # Range (0, 0) tells Qt to display a continuous animation instead of a
        # percentage, which is appropriate because CSV/XML reads cannot report
        # granular progress.  Hidden by default and revealed only while loading.
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)   # Indeterminate mode (pulsing)
        self.progress_bar.setVisible(False) # Hidden until a load starts
        layout.addWidget(self.progress_bar)

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

    def update_load_button_state(self):
        """ Update the state of the load button based on delimiter selection """
        if self.delimiter_box.currentText() == "Select Column Delimiter":
            self.load_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            self.delimiter_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.load_button.setEnabled(False)
            self.load_button.setStyleSheet("background-color: grey; color: white;")  # Greyed out
        else:
            self.load_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.delimiter_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            self.load_button.setEnabled(True)
            self.load_button.setStyleSheet("background-color: #890000; color: white;")  # Active color

    def _resolve_delimiter(self):
        """
        Map the human-readable delimiter dropdown text to the actual
        single-character delimiter string.

        Returns:
            str: The delimiter character (e.g. ',', '\t', ';', ' ', '|').
        """
        mapping = {
            "Comma (,)": ',',
            "Tab (\\t)": '\t',
            "Semicolon (;)": ';',
            "Space ( )": ' ',
            "Pipe (|)": '|',
        }
        return mapping.get(self.delimiter_box.currentText(), ',')

    def load_csv(self):
        """
        Open a file dialog and kick off metadata loading in a background thread.

        **All file I/O is performed off the main (GUI) thread** to prevent the
        interface from freezing on large files.  A pulsing progress bar provides
        visual feedback while loading is in progress, and all interactive controls
        are disabled so that stray clicks cannot corrupt application state.
        """
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV/TSV",
            self.controller.get_default_metadata_path(),
            "Data Files (*.csv *.tsv *.xml);;CSV Files (*.csv);;TSV Files (*.tsv);;XML Files (*.xml);;All Files (*)"
        )

        if not self.file_path:
            return  # User cancelled the dialog

        try:
            delimiter = self._resolve_delimiter()

            # --- Lock the UI while loading ---
            # Disabling all interactive widgets prevents user actions from
            # queuing up Qt events that would fire after the load completes,
            # which was the root cause of the freeze-on-click bug.
            self.next_button.setEnabled(False)
            self.next_button.setStyleSheet("")
            self.load_button.setEnabled(False)
            self.load_button.setStyleSheet("")
            self.delimiter_box.setEnabled(False)
            self.previous_button.setEnabled(False)

            # Show the pulsing progress bar so the user knows work is happening
            self.progress_bar.setVisible(True)
            self.info_label.setText(
                f"Loading Metadata: {self.file_path} <br> <b>Please wait...</b>"
            )

            file_size = os.path.getsize(self.file_path)
            print(f"File size: {file_size} bytes")
            if file_size > 100 * 1024 * 1024:
                self.show_alert(
                    "Warning",
                    "The file is larger than 100 MB. This may take a while to load."
                )

            # --- Spawn the background worker ---
            # Worker is a plain QObject (not a QThread subclass) that is moved
            # to a dedicated QThread.  This is the correct Qt pattern: the
            # QThread owns the event loop, and the Worker's slots run inside it.
            self.worker = MetadataLoadWorker(self.controller, self.file_path, delimiter)
            self.thread = QThread()
            self.worker.moveToThread(self.thread)

            # Wire signals: thread start -> worker.run, worker done -> cleanup
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.file_successfully_loaded)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        except Exception as e:
            self._restore_ui_after_load()
            self.info_label.setText(f"Failed to load file: {e}")

    def _restore_ui_after_load(self):
        """
        Re-enable all interactive controls and hide the progress bar.

        Called after loading completes (success or failure) to return the
        window to an interactable state.
        """
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        self.delimiter_box.setEnabled(True)
        self.previous_button.setEnabled(True)
        self.update_load_button_state()  # Re-apply correct button styling

    def file_successfully_loaded(self, success):
        """
        Slot called when the background worker finishes loading metadata.

        On success, populates the preview table with up to 1000 rows and
        enables navigation to the next screen.  On failure, shows an error
        alert and re-enables the load controls so the user can retry.

        Args:
            success (bool): True if the file was parsed and loaded without error.
        """
        # Always restore the UI first so the user can interact again
        self._restore_ui_after_load()

        if success:
            self.next_button.setEnabled(True)
            self.info_label.setText(f"Metadata loaded successfully: {self.file_path}")

            # Pull the authoritative DataFrame from the model.
            # The model's load_metadata handles CSV, TSV, and EAD XML uniformly.
            try:
                if hasattr(self.controller.model, 'metadata_df') and self.controller.model.metadata_df is not None:
                    self.df = self.controller.model.metadata_df
            except Exception:
                pass  # Fall back to whatever the view already has

            self.display_csv()
            self.show_alert(
                "Success",
                "Metadata loaded successfully!<br>Only the <b>first 1000 rows</b> "
                "are displayed in the table widget.<br>Click Next to proceed to the next step."
            )

            # Style the Next button to draw attention
            self.load_button.setStyleSheet("")
            self.next_button.setStyleSheet("background-color: #890000; color: white;")
        else:
            self.show_alert("Error", "Failed to load metadata. Please check the file format.")
            self.info_label.setText("Failed to load metadata. Please try again.")


    def display_csv(self, max_preview_rows=1000):
        """
        Display a preview of the loaded metadata in the table widget.

        QTableWidget allocates a QTableWidgetItem object for every visible cell.
        For large files (e.g. 100k rows × 20 columns = 2 million objects) this
        consumes enough memory to crash the application.  Capping the preview at
        ``max_preview_rows`` keeps the widget lightweight while still giving the
        user a representative view of their data.

        The full, uncapped DataFrame is preserved in the model for matching —
        only the *preview* is truncated.

        Args:
            max_preview_rows (int): Maximum number of rows to render in the
                table widget.  Defaults to 1000.
        """
        preview = self.df.head(max_preview_rows)

        self.table_widget.setRowCount(preview.shape[0])
        self.table_widget.setColumnCount(preview.shape[1])
        self.table_widget.setHorizontalHeaderLabels(preview.columns.astype(str))

        for row in range(preview.shape[0]):
            for col in range(preview.shape[1]):
                item = QTableWidgetItem(str(preview.iloc[row, col]))
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

        self.info_label.setFont(QFont("Calibri", width//80))  # Set font size
        # Always call base implementation
        super().resizeEvent(event)

class MetadataLoadWorker(QObject):
    """
    Background worker that loads a metadata file off the main GUI thread.

    This is a plain QObject (not a QThread subclass) that gets moved into
    a QThread via moveToThread().  This follows the recommended Qt pattern:
    the QThread owns the event loop and the worker's slots execute inside it,
    keeping the main thread free to process paint events and user input.

    The previous implementation subclassed QThread *and* called moveToThread()
    on the worker, which is an anti-pattern that caused signal delivery to
    happen on the wrong thread, leading to GUI freezes when the user clicked
    during a load.

    Attributes:
        finished (pyqtSignal[bool]): Emitted when loading completes.
            True = success, False = failure.
        controller: The application controller used to delegate the actual
            file parsing (CSV, TSV, or EAD XML) to the model layer.
        file_path (str): Absolute path to the metadata file.
        delimiter (str): Column delimiter for CSV/TSV files.
    """

    finished = pyqtSignal(bool)

    def __init__(self, controller, file_path, delimiter):
        """
        Args:
            controller: The application controller instance.
            file_path (str): Path to the metadata file to load.
            delimiter (str): The column delimiter character.
        """
        super().__init__()
        self.controller = controller
        self.file_path = file_path
        self.delimiter = delimiter

    def run(self):
        """
        Perform the file load.  Called automatically when the owning
        QThread starts.  Emits ``finished(True)`` on success or
        ``finished(False)`` on any exception.
        """
        try:
            success = self.controller.load_metadata(self.file_path, self.delimiter)
            self.finished.emit(success)
        except Exception as e:
            print(f"MetadataLoadWorker error: {e}")
            self.finished.emit(False)