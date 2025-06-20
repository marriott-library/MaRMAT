"""

perform_matching_window.py

Window for performing matching in the MaRMAT application.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""

from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

class PerformMatchingWindow(QMainWindow):
    """
    
    Window for performing matching in the MaRMAT application.
    This window allows users to select an output file location, perform matching,
    and view the results in a table format. The matching process is performed in a separate thread
    to keep the UI responsive.

    Attributes:
        controller (Controller): The controller instance that manages the application logic.
        output_file_path (str): The path to the output file where matching results will be saved.
        worker (Worker): The worker thread that performs the matching process.
        output_file_textedit (QLineEdit): Line edit to display the selected output file path.
        table_widget (QTableWidget): Table widget to display the matching results.
        progress_bar (ProgressBar): Progress bar to show the matching progress.
        msg_box (QMessageBox): Message box for displaying alerts.
        path_to_small_image (Path): Path to the small icon image for alerts.

    """
    def __init__(self, controller):
        """
        
        Initialize the PerformMatchingWindow with a controller instance.

        Args:
            controller (Controller): The controller instance that manages the application logic.

        """
        super().__init__()

        self.controller = controller
        self.output_file_path = ""  # Store the selected output file path
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components for the Perform Matching window."""

        # Worker thread for performing matching
        self.worker = None  # Initialize worker reference

        # Set window title and size
        self.setWindowTitle("Instructions - MaRMAT")
        self.resize(1280, 720)

        # Create a label for perform matching text
        perform_matching = "Click the <b>Select Output Location</b> button to select the location you would like MaRMAT to save the output file to. The file name will default to <b>MaRMAT_output.csv</b>. Once you have selected the output file location, click <b>Save</b>. When you are ready to run MaRMAT, click the <b>Perform Analysis</b> button. The output file will automatically save to your chosen location."

        # Create a Label for the title
        title_label = QLabel("<b>Welcome to the Perform Matching screen!</b>")
        title_label.setFont(QFont("Calibri", 36))

        # Create a QLabel to display the instructions
        instructions_label = QLabel(perform_matching)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        instructions_label.setWordWrap(True)

        # When finished label
        finished_label = QLabel("When you’re done, click the <b>Open Output File</b> button to open the <b>MaRMAT_output.csv</b> file. Click the <b>Finish</b> button below to return to the MaRMAT homepage.")
        finished_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        finished_label.setWordWrap(True)

        # Select the output file location label
        select_output_label = QLabel("Select the output file path:")
        select_output_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        select_output_label.setWordWrap(True)


        # Create a button to select output file location and label to display the selected file path
        file_location_layout = QHBoxLayout()

        # Create a line edit to display the selected file path
        self.output_file_textedit = QLineEdit("Output file: Not selected")
        self.output_file_textedit.setAlignment(Qt.AlignmentFlag.AlignTop)
        file_location_layout.addWidget(self.output_file_textedit)

        # Create a button to select the output file location
        self.select_file_button = QPushButton("Select Output Location")
        self.select_file_button.clicked.connect(self.select_output_file)
        self.select_file_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color

        # Set the size policy to Fixed for both horizontal and vertical directions
        self.select_file_button.setFixedWidth(400) # Set the desired width

        file_location_layout.addWidget(self.select_file_button)




        # Create a perform matching button
        self.perform_matching_button = QPushButton("Perform Analysis")

        # Modify the button to use multithreading
        self.perform_matching_button.clicked.connect(self.perform_matching)
        self.perform_matching_button.setEnabled(False)  # Disable the button initially
        
        # Create a button to go back to the previous screen or close
        self.back_button = QPushButton("Finish")
        self.back_button.clicked.connect(self.controller.show_main_screen)
        self.back_button.setEnabled(False)  # Disable the button initially

        # Create a table to display the matching results
        self.table_widget = QTableWidget()


        # Create a progress bar to show the matching progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Open the file explorer to path of created output file button
        self.open_file_explorer_button = QPushButton("Open Output File")
        self.open_file_explorer_button.clicked.connect(self.controller.open_output_file_location)
        self.open_file_explorer_button.setEnabled(False)  # Disable the button initially


        # Create a layout for the perform matching window
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Set margins for the layout
        layout.setSpacing(10)  # Set spacing between widgets
        layout.addWidget(title_label)
        layout.addWidget(instructions_label)
        layout.addWidget(select_output_label)
        layout.addLayout(file_location_layout)
        layout.addWidget(self.perform_matching_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.table_widget)  # Add the table widget to the layout
        layout.addWidget(finished_label)
        layout.addWidget(self.open_file_explorer_button)
        layout.addWidget(self.back_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Set the central widget of the window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_output_file(self):
        """Open a file dialog to select the output file location."""
        options = QFileDialog.Option(0)  # Initialize with no special options

        directory = str(Path(self.controller.settings_model.default_results_path) / "MaRMAT_output.csv") # Use the default results path from settings

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            directory,
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if file_path:
            self.output_file_path = file_path
            print(f"Output file selected: {self.output_file_path}")
            self.controller.set_output_path(file_path)

            # Update the text edit to show the selected file path
            self.output_file_textedit.setText(f"{self.output_file_path}")
            self.perform_matching_button.setEnabled(True)  # Enable the perform matching button
            self.perform_matching_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
            self.select_file_button.setStyleSheet("")  # Set button color
    
    def show_matching_results(self):
        """Display the matching results in the table widget."""
        df = self.controller.get_matching_results()

        if df is not None and not df.empty:
            self.update_table(df)
        else:
            print("No matching results to display.")
        
        # Enable the buttons after matching is complete
        self.show_alert("Matching Complete", "The matching process is complete. You can now view the results.")
        self.perform_matching_button.setEnabled(False)
        self.select_file_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.open_file_explorer_button.setEnabled(True)  # Enable the button to open the output file location
        self.open_file_explorer_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        self.back_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        self.perform_matching_button.setStyleSheet("")  # Set button color

    def update_table(self, df):
        """
        
        Display the matching results in the table widget.
        
        Args:
            df (pd.DataFrame): The DataFrame containing the matching results to display.
        
        """     
        if df is not None and not df.empty:
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels(df.columns)

            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QTableWidgetItem(str(df.iloc[row, col]))
                    self.table_widget.setItem(row, col, item)
        else:
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            self.table_widget.setItem(0, 0, QTableWidgetItem("No matching results to display."))
            print("No matching results to display.")
        
    def perform_matching(self):
        """Perform the matching process."""

        print("Performing matching...")
        
        self.controller.set_output_path(self.output_file_textedit.text())  # Ensure the output path is set before starting matching

        self.perform_matching_button.setEnabled(False)
        self.select_file_button.setEnabled(False)
        self.back_button.setEnabled(False)

        # Create a worker thread to perform matching
        self.thread = QThread()
        self.worker = Worker(self.controller)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.show_matching_results)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)

        # Start the worker thread
        self.thread.start()
        self.controller = self.worker.controller  # Update the controller reference in the worker



    def update_progress_bar(self, value):
        """
        
        Update the progress bar value.
        
        Args:
            value (int): The value to set the progress bar to, typically between 0 and 100.
        
        """
        self.progress_bar.setValue(value)
    
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

class Worker(QThread):
    """
    
    Worker thread for performing the matching process in the MaRMAT application.
    This class inherits from QThread and emits signals to update the progress bar
    and indicate when the matching process is finished.

    Attributes:
        progress (pyqtSignal): Signal to update the progress bar.
        finished (pyqtSignal): Signal to indicate that the matching process is finished.
        controller (Controller): The controller instance that manages the application logic.

    """
    progress = pyqtSignal(int)  # Signal to update progress bar
    finished = pyqtSignal()  # Signal to indicate completion

    def __init__(self, controller):
        """
        
        Initialize the Worker with a controller instance.

        Args:
            controller (Controller): The controller instance that manages the application logic.

        """
        super().__init__()
        self.controller = controller

    def run(self):
        """Run the matching process."""
        self.controller.perform_matching(self.progress)
        self.finished.emit()  # Emit signal when finished