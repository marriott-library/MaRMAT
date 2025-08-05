"""

gui_controller.py

Controller for the GUI application of the MaRMAT project.
This module handles user input, processes it using the MaRMAT processing class,
and manages the different views of the application.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""

# Standard library
import os
import platform
import subprocess
import pandas as pd

# PyQt6
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QStackedWidget, QFileDialog

# Application views
from views import (
    MainWindow, MetadataWindow, LexiconWindow,
    InstructionsWindow, DataSelectionWindow,
    PerformMatchingWindow, SettingsWindow
)

# Application models
from models.marmat_processing import marmat_processing
from models.settings_model import SettingsModel


class MainController:

    """
    
    Main controller for the GUI application.
    This class manages the different views and user interactions,
    and handles the processing of metadata and lexicon files.

    Attributes:
        stack (QStackedWidget): The main widget that holds all views.
        model (marmat_processing): The model for processing metadata and lexicon.
        settings_model (SettingsModel): The model for application settings.
        output_path (str): Path to save the results.

    """

    def __init__(self):
        """Main controller initialization."""

        self.output_path = "output.csv"  # Default output path

        self.stack = QStackedWidget()

        # Create model
        self.model = marmat_processing()
        self.settings_model = SettingsModel()

        # Create views
        self.main_window = MainWindow(self)
        self.metadata_window = MetadataWindow(self)
        self.lexicon_window = LexiconWindow(self)
        self.instructions_window = InstructionsWindow(self)
        self.data_selection_window = DataSelectionWindow(self)
        self.perform_matching_window = PerformMatchingWindow(self)
        self.settings_window = SettingsWindow(self)

        # Add views to stack
        self.stack.addWidget(self.main_window)
        self.stack.addWidget(self.metadata_window)
        self.stack.addWidget(self.lexicon_window)
        self.stack.addWidget(self.instructions_window)
        self.stack.addWidget(self.data_selection_window)
        self.stack.addWidget(self.perform_matching_window)
        self.stack.addWidget(self.settings_window)



    # The screen switch functions

    def show_metadata_screen(self):
        """Switch to the metadata loading screen"""
        self.stack.setCurrentWidget(self.metadata_window)

    def show_lexicon_screen(self):
        """Switch to the lexicon loading screen"""
        self.stack.setCurrentWidget(self.lexicon_window)

    def show_main_screen(self):
        """Switch to the main screen"""
        self.stack.setCurrentWidget(self.main_window)

    def show_instructions_screen(self):
        """Switch to the instructions screen"""
        self.stack.setCurrentWidget(self.instructions_window)

    def show_data_selection_screen(self):
        """Switch to the data selection screen"""
        self.data_selection_window.init_ui()  # Initialize the data selection window
        self.stack.setCurrentWidget(self.data_selection_window)

    def show_perform_matching_screen(self):
        """Switch to the perform matching screen"""
        self.perform_matching_window.init_ui()
        self.stack.setCurrentWidget(self.perform_matching_window)
        
    def show_settings_screen(self):
        """Switch to the settings screen"""
        self.stack.setCurrentWidget(self.settings_window)


    # Run function to start the application

    def run(self):
        """
        Run the application and show the main window.
        """

        self.stack.setCurrentWidget(self.main_window)
        self.stack.showMaximized()  # Show the main window in full screen mode
        self.stack.setWindowIcon(self.main_window.windowIcon())  # Set the window icon
        self.stack.setWindowTitle("MaRMAT 2.6.0-rc")  # Set the window title
        
        self.stack.setMinimumSize(540, 420)
        
          # Start the event loop
        self.stack.show()  # Show the main window in normal mode

        if self.settings_model.fullscreen_enabled:
            self.stack.showFullScreen()
        else:
            self.stack.showNormal()
            # self.stack.setFixedSize(1280, 720) 
            self.stack.resize(1280, 720)  # Set a fixed size for the window
            
            # Get current screen geometry
            screen = self.stack.screen()
            geometry = screen.availableGeometry()

            # Center the window on the screen
            x = (geometry.width() - self.stack.width()) // 2
            y = (geometry.height() - self.stack.height()) // 2
            self.stack.move(x, y)


    # Functions to handle user input and actions
    def set_output_path(self, path):
        """Set the output path for saving results."""
        self.output_path = path
        print("Output path set:", path)


    # Functions to handle model operations

    def load_metadata(self, file_path, delimiter=',') -> bool:
        """
        Load metadata from file path.
        
        Args:
            file_path (str): Path to the metadata file.
        
        Returns:
            bool: True if metadata is loaded successfully, False otherwise.

        """
        if self.model.load_metadata(file_path, delimiter=delimiter):
            print("Metadata loaded:", file_path)
            print("Metadata shape:", self.model.metadata_df.shape)
            return True
        else:
            print("Failed to load metadata:", file_path)
            return False

    def load_lexicon(self, file_path) -> bool:  
        """
        
        Load lexicon from file path.
        
        Args:
            file_path (str): Path to the lexicon file.

        Returns:
            bool: True if lexicon is loaded successfully, False otherwise.
        
        """

        if self.model.load_lexicon(file_path):
            print("Lexicon loaded:", file_path)
            print("Lexicon shape:", self.model.lexicon_df.shape)
            return True
        else:
            print("Failed to load lexicon:", file_path)
            return False

    
    def get_metadata_columns(self) -> list:
        """
        
        Get the columns of the metadata.
        
        Returns:
            list: List of column names in the metadata.

        """
        try:
            return list(self.model.get_selecteable_columns())
        except:
            print("No metadata loaded.")
            return []

    def get_lexicon_columns(self) -> list:
        """
        
        Get the columns of the lexicon.
        
        Returns:
            list: List of column names in the lexicon.

        """
        return list(self.model.get_selecteable_categories())
    
    def set_identifier_column(self, column):
        """
        
        Set the identifier column.
        
        Args:
            column (str): Name of the identifier column.
        
        """
        self.model.select_identifier_column(column)
        print("Identifier column set:", column)

    def set_selected_columns(self, columns):
        """
        
        Set the selected columns.
        
        Args:
            columns (list of str): List of column names to select for matching.
        
        """
        
        self.model.select_columns(columns)
        print("Selected columns set:", columns)

    def set_selected_categories(self, categories):
        """
        
        Set the selected categories.
        
        Args:
            categories (list of str): List of category names to select for matching.

        """
        self.model.select_categories(categories)
        print("Selected categories set:", categories)

    def perform_matching(self, progress_callback=None):
        """

        Perform matching between selected columns and categories.

        Args:
            progress_callback (callable, optional): Function to call for progress updates.
        
        """

        self.model.perform_matching(output_file=self.output_path, progress_callback=progress_callback)
        print("Matching performed.")
    
    def get_matching_results(self) -> pd.DataFrame:
        """
        
        Get the matching results.
        
        Returns:
            pd.DataFrame: DataFrame containing the matching results.

        """
        return self.model.get_matching_results()
    
    def start_matching(self):
        """Start the matching process in a separate thread."""

        self.thread = QThread()
        self.model.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(lambda: self.model.perform_matching(self.output_path))  
        self.model.progress_update.connect(self.perform_matching_window.update_progress_bar)
        self.model.finished.connect(self.on_thread_finished)
        self.model.finished.connect(self.thread.quit)
        self.model.finished.connect(self.model.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()

    
    def on_thread_finished(self, results):
        """
        
        Handle the thread finished signal and update the matching results.

        Args:
            results (pd.DataFrame): DataFrame containing the matching results.

        """
        self.model.matches_df = results
        self.perform_matching_window.show_matching_results()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.settings_model.fullscreen_enabled:
            self.settings_model.fullscreen_enabled = False
            self.save_settings()
            print("Exiting fullscreen mode...")
            self.stack.showNormal()
            # self.stack.setFixedSize(1280, 720)  # Set a fixed size for the window
            self.stack.resize(1280, 720)
            # Get current screen geometry
            screen = self.stack.screen()
            geometry = screen.availableGeometry()

            # Center the window on the screen
            x = (geometry.width() - self.stack.width()) // 2
            y = (geometry.height() - self.stack.height()) // 2
            self.stack.move(x, y)
        else:
            self.settings_model.fullscreen_enabled = True
            self.save_settings()
            print("In fullscreen mode, exiting...")
            self.stack.showFullScreen()

        self.settings_window.fullscreen_label.setText(f"Fullscreen is currently: {'<b>Enabled</b>' if self.settings_model.fullscreen_enabled else '<b>Disabled</b>'}")
    
    def open_output_file_location(self):
        """Open the output file location in the file explorer."""
        if platform.system() == "Windows":
            os.startfile(os.path.normpath(self.output_path))
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", self.output_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", self.output_path])
        else:
            raise OSError("Unsupported operating system")
    
    def save_settings(self):
        """Save settings."""
        self.settings_model.save_settings()
    
    def check_popups_enabled(self) -> bool:
        """
        
        Check if popups are enabled.
        
        Returns:
            bool: True if popups are enabled, False otherwise.
        
        """
        return self.settings_model.popups_enabled
    
    def set_default_metadata_path(self):
        """Set the default metadata path. Saves the selected folder path to the settings model."""
        folder_path = QFileDialog.getExistingDirectory(self.main_window, "Select Folder", "")
        if folder_path:
            self.settings_model.default_metadata_path = folder_path
            self.settings_window.metadata_label.setText(f"Default Metadata Path: {folder_path}")
            print("Default metadata path set:", folder_path)
            self.save_settings()

    def get_default_metadata_path(self) -> str:
        """
        
        Get the default metadata path.
        
        Returns:
            str: The default metadata path, or the current working directory if not set.
        
        """
        return self.settings_model.default_metadata_path if self.settings_model.default_metadata_path else str(os.getcwd())
    
    def set_default_lexicon_path(self):
        """Set the default lexicon path. Saves the selected folder path to the settings model."""
        folder_path = QFileDialog.getExistingDirectory(self.main_window, "Select Folder", "")
        if folder_path:
            self.settings_model.default_lexicon_path = folder_path
            self.settings_window.lexicon_label.setText(f"Default Lexicon Path: {folder_path}")
            print("Default lexicon path set:", folder_path)
            self.save_settings()
    
    def get_default_lexicon_path(self) -> str:
        """
        
        Get the default lexicon path.
        
        Returns:
            str: The default lexicon path, or the current working directory if not set.

        """
        return self.settings_model.default_lexicon_path if self.settings_model.default_lexicon_path else str(os.getcwd())
    
    def set_default_results_path(self):
        """Set the default results path. Saves the selected folder path to the settings model."""
        folder_path = QFileDialog.getExistingDirectory(self.main_window, "Select Folder", "")
        if folder_path:
            self.settings_model.default_results_path = folder_path
            self.settings_window.save_results_label.setText(f"Default Results Path: {folder_path}")
            print("Default results path set:", folder_path)
            self.save_settings()
    
    def get_default_results_path(self) -> str:
        """
        
        Get the default results path.
        
        Returns:
            str: The default results path, or the current working directory if not set.
        
        """
        return self.settings_model.default_results_path if self.settings_model.default_results_path else str(os.getcwd())