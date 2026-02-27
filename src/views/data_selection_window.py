"""

data_selection_window.py

Data selection window for the MaRMAT application.
This module provides a GUI for users to select columns and categories from their metadata and lexicon files.

Author:
    - Aiden deBoer

Date: 2025-08-28

"""
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QListWidget, QPushButton, QWidget, QLabel, QListWidgetItem)
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QCursor
from views.base_widget import BaseWidget

class DataSelectionWindow(BaseWidget):
    """
    
    DataSelectionWindow class for selecting columns and categories from metadata and lexicon files.

    Attributes:
        controller (Controller): The controller instance that manages the application logic.
        column_combo (QComboBox): Dropdown for selecting the ID column from the metadata file.
        column_list_widget (QListWidget): List widget for selecting columns to analyze.
        lexicon_list_widget (QListWidget): List widget for selecting categories from the lexicon.
        select_all_button_column (QPushButton): Button to select or deselect all columns.
        select_all_button_lexicon (QPushButton): Button to select or deselect all lexicon categories.
        previous_button (QPushButton): Button to go back to the previous screen.
        next_button (QPushButton): Button to proceed to the next screen.

    """

    def __init__(self, controller):
        """Initialize the DataSelectionWindow with a controller."""
        super().__init__()

        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface for the data selection window."""

        # Main layout
        main_layout = QVBoxLayout()

        # Title and instructions
        title_desc_layout = QVBoxLayout()
        title_label = QLabel("<b>Configure Analysis</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        title_label.setFont(QFont("Calibri", 48))
        title_desc_layout.addWidget(title_label)
        description_text = """
            On this screen, you will select the ID column from your metadata file that you want to use as a unique identifier (i.e., key column) between your original file and MaRMAT’s output file. 
            You will then select the fields from your metadata file that you want MaRMAT to analyze and the categories of terms from the lexicon that you want MaRMAT to check for in your metadata file.
        """
        instructions_label = QLabel(description_text)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        instructions_label.setWordWrap(True)
        title_desc_layout.addWidget(instructions_label)
        main_layout.addLayout(title_desc_layout)

        # Dropdown row
        dropdown_layout = QVBoxLayout()
        dropdown_layout.addWidget(QLabel("<b>Select the ID column from your metadata file:</b><br>(Defaults to the first column in your file)"))

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.controller.get_metadata_columns())
        self.column_combo.currentTextChanged.connect(self.update_identifier_column)
        self.column_combo.currentTextChanged.connect(self.update_button_state)

        dropdown_layout.addWidget(self.column_combo)
        main_layout.addLayout(dropdown_layout)

        # Lists row
        lists_layout = QHBoxLayout()

        # Column list - Columns to check for matching
        self.column_list_widget = QListWidget()
        self.column_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.column_list_widget.addItems(self.controller.get_metadata_columns())

        # # Print the self.column_list_widget items
        # print("Metadata columns in list:")
        # for index in range(self.column_list_widget.count()):
        #     item = self.column_list_widget.item(index)
        #     print(f" - {item.text()}")

        # print("Metadata columns:")
        # for col in self.controller.get_metadata_columns():
        #     print(f" - {col}")

        for index in range(self.column_list_widget.count()):
            item = self.column_list_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

        # Create select all and deselect all button for column list
        self.select_all_button_column = QPushButton("Select All Fields")
        self.select_all_button_column.clicked.connect(lambda: self.select_all_items(self.column_list_widget, self.select_all_button_column))

        # Create a container for the column list and its label
        column_list_container = QVBoxLayout()
        column_list_container.setContentsMargins(0, 0, 0, 0)  # Remove margins for better alignment
        column_list_container.setSpacing(5)  # Add some spacing between elements

        column_list_label = QLabel("<b>Check the boxes next to the names of the columns from your metadata file that you want MaRMAT to analyze:</b>")
        column_list_label.setWordWrap(True)
        column_list_container.addWidget(column_list_label)
        column_list_container.addWidget(self.column_list_widget, 1)  # stretch=1 lets the list grow/shrink
        column_list_container.addWidget(self.select_all_button_column)

        lists_layout.addLayout(column_list_container)

        # Lexicon list - Unique categories to check for matching
        self.lexicon_list_widget = QListWidget()
        self.lexicon_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.lexicon_list_widget.addItems(self.controller.get_lexicon_columns())

        for index in range(self.lexicon_list_widget.count()):
            item = self.lexicon_list_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

        # Create select all and deselect all button for column list
        self.select_all_button_lexicon = QPushButton("Select All Fields")
        self.select_all_button_lexicon.clicked.connect(lambda: self.select_all_items(self.lexicon_list_widget, self.select_all_button_lexicon))

        unique_values_container = QVBoxLayout()
        unique_values_container.setContentsMargins(0, 0, 0, 0)  # Remove margins for better alignment
        unique_values_container.setSpacing(5)  # Add some spacing between elements

        unique_values_label = QLabel("<b>Check the boxes next to the categories of terms from your selected lexicon that you want MaRMAT to check for in your metadata file:</b>")
        unique_values_label.setWordWrap(True)
        unique_values_container.addWidget(unique_values_label)
        unique_values_container.addWidget(self.lexicon_list_widget, 1)  # stretch=1 lets the list grow/shrink
        unique_values_container.addWidget(self.select_all_button_lexicon)

        lists_layout.addLayout(unique_values_container)

        lists_layout.setSpacing(20)
        lists_layout.setContentsMargins(0, 0, 0, 0)


        # Connect the itemClicked signal to the toggle_item_check_state method
        self.column_list_widget.itemPressed.connect(self.handle_item_pressed)
        self.lexicon_list_widget.itemPressed.connect(self.handle_item_pressed)

        # Connect the itemChanged signal to the update_button_state method
        self.column_list_widget.itemChanged.connect(self.update_button_state)
        self.lexicon_list_widget.itemChanged.connect(self.update_button_state)

        # Add the column and lexicon list containers to the main layout.
        # The stretch factor of 1 lets the lists area absorb extra vertical
        # space when the window grows, and release it when the window shrinks.
        main_layout.addLayout(lists_layout, 1)

        # Navigation Buttons
        button_layout = QHBoxLayout()

        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.go_to_previous_page)
        button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)  # Initially disabled
        self.next_button.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_button)

        # Add a final instructions label
        final_instructions_label = QLabel("Once you have finished making your selections, click <b>Next</b>.")
        final_instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        final_instructions_label.setWordWrap(True)

        main_layout.setSpacing(20)  # Add some spacing between elements
        main_layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the main layout

        main_layout.addWidget(final_instructions_label)
        main_layout.addLayout(button_layout)

        # Set the layout to the window
        self.setLayout(main_layout)

    def toggle_item_check_state(self, item: QListWidgetItem):
        """
        
        Toggle the check state when the item is clicked.

        Args:
            item (QListWidgetItem): The item whose check state is to be toggled.

        """
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def handle_item_pressed(self, item: QListWidgetItem):
        """
        Handle the item pressed signal to toggle the check state of the item.

        When the user clicks the text portion of a list item (not the checkbox
        itself), Qt does not automatically toggle the check state.  This method
        detects whether the click landed outside the checkbox area and performs
        the toggle manually.

        The checkbox indicator in a QListWidget is rendered in the left ~20 px
        of the item row inside the widget's *viewport*.  The position must be
        mapped into viewport coordinates — mapping into the QListWidget widget
        coordinates directly gives wrong values because the viewport has its own
        coordinate space offset by scrollbars and frame borders.

        Args:
            item (QListWidgetItem): The item that was pressed.
        """
        widget = self.sender()

        # QCursor.pos() returns the cursor position in global screen coordinates.
        # We map it into the list widget's viewport (not the widget itself) so
        # that the x value is correct regardless of scroll position or window
        # placement on screen.
        pos = widget.viewport().mapFromGlobal(QCursor.pos())

        # The checkbox indicator occupies roughly the first 20 px on the left.
        # Clicks inside that zone are handled natively by Qt; clicks outside
        # need a manual toggle so that clicking anywhere on the row works.
        if pos.x() > 20:
            new_state = (
                Qt.CheckState.Unchecked
                if item.checkState() == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            item.setCheckState(new_state)

    def select_all_items(self, list_widget: QListWidget, button: QPushButton):
        """
        
        Select all items in the given list widget.
        
        Args:
            list_widget (QListWidget): The list widget containing items to select or deselect.
            button (QPushButton): The button that toggles between "Select All Fields" and "Deselect All Fields".

        """

        if button.text() == "Select All Fields":
            button.setText("Deselect All Fields")
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                item.setCheckState(Qt.CheckState.Checked)
        else:
            button.setText("Select All Fields")
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                item.setCheckState(Qt.CheckState.Unchecked)


    def update_identifier_column(self):
        """ Update the unique values list when a new column is selected from the dropdown """
        selected_column = self.column_combo.currentText()
        if selected_column:
            self.controller.set_identifier_column(selected_column)

    def update_button_state(self):
        """ Enable the Next button only if there is at least one selection in each widget. """
        column_selected = self.column_combo.currentText() != ""

        columns_checked = any(
            self.column_list_widget.item(i).checkState() == Qt.CheckState.Checked
            for i in range(self.column_list_widget.count())
        )

        lexicon_values_checked = any(
            self.lexicon_list_widget.item(i).checkState() == Qt.CheckState.Checked
            for i in range(self.lexicon_list_widget.count())
        )

        if column_selected and columns_checked and lexicon_values_checked:
            self.next_button.setEnabled(True)
            self.next_button.setStyleSheet("background-color: #890000; color: white;")  # Set button color
        else:
            self.next_button.setEnabled(False)
            self.next_button.setStyleSheet("")

    def apply_selection(self):
        """ Handle the user selection """
        selected_column_checkboxes = [
            item.text() for item in self.column_list_widget.findItems("", Qt.MatchFlag.MatchContains)
            if item.checkState() == Qt.CheckState.Checked
        ]
        selected_lexicon_value_checkboxes = [
            item.text() for item in self.lexicon_list_widget.findItems("", Qt.MatchFlag.MatchContains)
            if item.checkState() == Qt.CheckState.Checked
        ]

        print(f"Selected columns: {selected_column_checkboxes}")
        print(f"Selected unique values: {selected_lexicon_value_checkboxes}")

        self.controller.set_selected_columns(selected_column_checkboxes)
        self.controller.set_selected_categories(selected_lexicon_value_checkboxes)
        self.controller.set_identifier_column(self.column_combo.currentText())

        self.close()

    def refresh_data(self):
        """
        Refresh the metadata and lexicon lists from the controller.
        Safe to call after controller loads files.
        """

        # --- Identifier dropdown ---
        self.column_combo.clear()
        metadata_columns = self.controller.get_metadata_columns() or []
        self.column_combo.addItems(metadata_columns)

        # --- Metadata list ---
        self.column_list_widget.clear()
        self.column_list_widget.addItems(metadata_columns)
        for i in range(self.column_list_widget.count()):
            self.column_list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

        # --- Lexicon list ---
        self.lexicon_list_widget.clear()
        lexicon_columns = self.controller.get_lexicon_columns() or []
        self.lexicon_list_widget.addItems(lexicon_columns)
        for i in range(self.lexicon_list_widget.count()):
            self.lexicon_list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

        # --- Reset buttons ---
        self.select_all_button_column.setText("Select All Fields")
        self.select_all_button_lexicon.setText("Select All Fields")

        # Update button state
        self.update_button_state()


    def go_to_next_page(self):
        """ Action when the 'Next' button is clicked """
        self.apply_selection()
        self.controller.show_perform_matching_screen()

    def go_to_previous_page(self):
        """ Return to the previous page, the metadata loading screen """
        self.controller.show_lexicon_screen()  # Go back to the metadata loading screen