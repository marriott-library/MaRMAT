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
                             QListWidget, QPushButton, QWidget, QLabel, QListWidgetItem,
                             QGroupBox, QFormLayout, QSizePolicy)
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
        self.setMinimumSize(980, 700)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 16, 20, 16)

        # Header and instructions
        title_label = QLabel("<b>Configure Analysis</b>")
        title_label.setFont(QFont("Calibri", 34))
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(title_label)

        instructions_label = QLabel(
            "Select your metadata ID column, choose which metadata fields to analyze, "
            "and select which lexicon categories MaRMAT should check against those fields."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(instructions_label)

        # Selection controls
        setup_group = QGroupBox("Matching Setup")
        setup_layout = QFormLayout()
        setup_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        setup_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        setup_layout.setHorizontalSpacing(24)
        setup_layout.setVerticalSpacing(12)

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.controller.get_metadata_columns())
        self.column_combo.currentTextChanged.connect(self.update_identifier_column)
        self.column_combo.currentTextChanged.connect(self.update_button_state)
        self.column_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        id_hint_label = QLabel("Used as the unique key column in MaRMAT output.")
        id_hint_label.setWordWrap(True)
        id_row_layout = QVBoxLayout()
        id_row_layout.setContentsMargins(0, 0, 0, 0)
        id_row_layout.setSpacing(4)
        id_row_layout.addWidget(self.column_combo)
        id_row_layout.addWidget(id_hint_label)
        setup_layout.addRow("ID Column", id_row_layout)

        self.include_collection_title_button = QPushButton("Include Collection Title: Off")
        self.include_collection_title_button.setCheckable(True)
        self.include_collection_title_button.setStyleSheet(
            "QPushButton:checked { background-color: #890000; color: white; }"
        )
        self.include_collection_title_button.clicked.connect(self.toggle_collection_title_option)

        self.collection_title_notice_label = QLabel(
            "Collection Title enabled: output will include a collection title value for each row."
        )
        self.collection_title_notice_label.setWordWrap(True)
        self.collection_title_notice_label.setVisible(False)

        self.collection_title_combo = QComboBox()
        self.collection_title_combo.addItems(self.controller.get_metadata_columns())
        self.collection_title_combo.currentTextChanged.connect(self.update_collection_title_column)
        self.collection_title_combo.setEnabled(False)
        self.collection_title_combo.setVisible(False)
        self.auto_select_collection_title_column()

        collection_title_row = QVBoxLayout()
        collection_title_row.setContentsMargins(0, 0, 0, 0)
        collection_title_row.setSpacing(6)
        collection_title_row.addWidget(self.include_collection_title_button)
        collection_title_row.addWidget(self.collection_title_notice_label)
        collection_title_row.addWidget(self.collection_title_combo)
        setup_layout.addRow("Optional Output", collection_title_row)

        setup_group.setLayout(setup_layout)
        main_layout.addWidget(setup_group)

        # Checklist panels
        lists_layout = QHBoxLayout()
        lists_layout.setSpacing(16)

        columns_group = QGroupBox("Metadata Fields to Analyze")
        columns_layout = QVBoxLayout()
        columns_layout.setContentsMargins(12, 12, 12, 12)
        columns_layout.setSpacing(8)

        column_list_label = QLabel(
            "Check all metadata columns that should be scanned during analysis."
        )
        column_list_label.setWordWrap(True)
        columns_layout.addWidget(column_list_label)

        self.column_list_widget = QListWidget()
        self.column_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.column_list_widget.setAlternatingRowColors(True)
        self.column_list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.column_list_widget.addItems(self.controller.get_metadata_columns())

        for index in range(self.column_list_widget.count()):
            item = self.column_list_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.select_all_button_column = QPushButton("Select All Fields")
        self.select_all_button_column.clicked.connect(
            lambda: self.select_all_items(self.column_list_widget, self.select_all_button_column)
        )
        self.select_all_button_column.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        columns_layout.addWidget(self.select_all_button_column, alignment=Qt.AlignmentFlag.AlignLeft)
        columns_layout.addWidget(self.column_list_widget, 1)
        columns_group.setLayout(columns_layout)
        lists_layout.addWidget(columns_group, 1)

        lexicon_group = QGroupBox("Lexicon Categories to Check")
        lexicon_layout = QVBoxLayout()
        lexicon_layout.setContentsMargins(12, 12, 12, 12)
        lexicon_layout.setSpacing(8)

        unique_values_label = QLabel(
            "Check all lexicon categories that should be matched against your metadata."
        )
        unique_values_label.setWordWrap(True)
        lexicon_layout.addWidget(unique_values_label)

        self.lexicon_list_widget = QListWidget()
        self.lexicon_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.lexicon_list_widget.setAlternatingRowColors(True)
        self.lexicon_list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lexicon_list_widget.addItems(self.controller.get_lexicon_columns())

        for index in range(self.lexicon_list_widget.count()):
            item = self.lexicon_list_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.select_all_button_lexicon = QPushButton("Select All Fields")
        self.select_all_button_lexicon.clicked.connect(
            lambda: self.select_all_items(self.lexicon_list_widget, self.select_all_button_lexicon)
        )
        self.select_all_button_lexicon.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        lexicon_layout.addWidget(self.select_all_button_lexicon, alignment=Qt.AlignmentFlag.AlignLeft)
        lexicon_layout.addWidget(self.lexicon_list_widget, 1)
        lexicon_group.setLayout(lexicon_layout)
        lists_layout.addWidget(lexicon_group, 1)

        # Connect the itemClicked signal to the toggle_item_check_state method
        self.column_list_widget.itemPressed.connect(self.handle_item_pressed)
        self.lexicon_list_widget.itemPressed.connect(self.handle_item_pressed)

        # Connect the itemChanged signal to the update_button_state method
        self.column_list_widget.itemChanged.connect(self.update_button_state)
        self.lexicon_list_widget.itemChanged.connect(self.update_button_state)

        # Let checklist area absorb most of the resize changes.
        main_layout.addLayout(lists_layout, 2)

        # Footer notes and navigation
        footer_layout = QHBoxLayout()

        final_instructions_label = QLabel("Once you have finished making your selections, click <b>Next</b>.")
        final_instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        final_instructions_label.setWordWrap(True)
        footer_layout.addWidget(final_instructions_label, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.previous_button = QPushButton("Previous")
        self.previous_button.setMinimumWidth(140)
        self.previous_button.clicked.connect(self.go_to_previous_page)
        button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        self.next_button.setMinimumWidth(140)
        self.next_button.setEnabled(False)  # Initially disabled
        self.next_button.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_button)

        footer_layout.addLayout(button_layout)
        main_layout.addLayout(footer_layout)

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

    def toggle_collection_title_option(self, checked: bool):
        """Enable or disable inclusion of a collection title column in output."""
        self.include_collection_title_button.setText(
            "Include Collection Title: On" if checked else "Include Collection Title: Off"
        )
        self.collection_title_notice_label.setVisible(checked)

        self.collection_title_combo.setEnabled(checked)
        self.collection_title_combo.setVisible(checked)

        if checked:
            self.controller.set_include_collection_title(True)
            self.update_collection_title_column()
        else:
            self.controller.set_include_collection_title(False)

    def update_collection_title_column(self):
        """Set the selected collection title column in the controller."""
        selected_column = self.collection_title_combo.currentText()
        if selected_column:
            self.controller.set_collection_title_column(selected_column)

    def auto_select_collection_title_column(self):
        """Auto-select a likely title column if one exists."""
        column_names = [
            self.collection_title_combo.itemText(i)
            for i in range(self.collection_title_combo.count())
        ]

        if not column_names:
            return

        # Prefer exact "title" first, then any column containing "title".
        exact_index = next(
            (idx for idx, name in enumerate(column_names) if name.strip().lower() == "title"),
            -1
        )

        if exact_index != -1:
            self.collection_title_combo.setCurrentIndex(exact_index)
            return

        contains_index = next(
            (idx for idx, name in enumerate(column_names) if "title" in name.strip().lower()),
            -1
        )

        if contains_index != -1:
            self.collection_title_combo.setCurrentIndex(contains_index)

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

        include_collection_title = self.include_collection_title_button.isChecked()
        self.controller.set_include_collection_title(include_collection_title)
        if include_collection_title:
            self.controller.set_collection_title_column(self.collection_title_combo.currentText())

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

        self.collection_title_combo.clear()
        self.collection_title_combo.addItems(metadata_columns)
        self.auto_select_collection_title_column()
        self.collection_title_combo.setEnabled(False)
        self.collection_title_combo.setVisible(False)
        self.include_collection_title_button.setChecked(False)
        self.include_collection_title_button.setText("Include Collection Title: Off")
        self.collection_title_notice_label.setVisible(False)
        self.controller.set_include_collection_title(False)

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