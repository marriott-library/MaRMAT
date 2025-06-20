"""

instructions_window.py

This module defines the InstructionsWindow class, which provides detailed instructions for using the MaRMAT application.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QPushButton
from PyQt6.QtGui import QFont

class InstructionsWindow(QMainWindow):
    """
    
    InstructionsWindow class for displaying detailed instructions on how to use the MaRMAT application.
    This class inherits from QMainWindow and provides a user interface for displaying instructions
    and navigating back to the main screen.

    Attributes:
        controller (Controller): The controller instance that manages the application logic.

    """
    def __init__(self, controller):
        """
        
        Initialize the InstructionsWindow.
        
        Args:
            controller (Controller): The controller instance that manages the application logic.
        
        """
        super().__init__()

        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface for the InstructionsWindow."""
        # Set window title and size
        self.setWindowTitle("Instructions - MaRMAT")
        self.resize(1280, 720)

        # Create a label for instructions text
        instructions_text = """
        
        <h1 style="font-size: 2em;">Getting Started</h1>

        From the MaRMAT homepage, click <b>Run MaRMAT</b>, then you’ll follow the prompts on each screen perform the analysis. Below is an overview of each step as well as additional information about how you can use MaRMAT.
        
        <h2 style="font-size: 2em;">Step 1: Load Your Metadata File (.csv)</h2>

        <p style="margin-left: 1em;">
        Click the <b>Load Metadata</b> button and select the metadata file you want MaRMAT to analyze. This should be a <b>CSV (Comma-Separated Values)</b> file containing the records you’d like to assess (e.g., collections metadata, bibliographic metadata, archival descriptions, catalog entries). Your file should include:
        
        <ul>
            <li>Descriptive fields (e.g., Title, Description, Subject)</li>
            <li>A unique identifier (e.g., ID, Accession Number) in one of the columns</li>
        </ul>
        </p>

        <p style="margin-left: 1em;">
        Once your file is successfully loaded, click <b>Next</b> to proceed.
        </p>
        
        <h2 style="font-size: 2em;">Step 2: Load a Lexicon File (.csv)</h2>

        <p style="margin-left: 1em;">
        Click the <b>Load Lexicon</b> button and choose the lexicon file MaRMAT will use to analyze your metadata. The lexicon should also be in CSV format and contain the terms or phrases you want to flag during analysis, grouped into categories. You may either use a pre-curated lexicon or upload your own custom list:<br>

        <b>Option A: <a href="https://www.marmatproject.org/lexicons/">Use a Pre-Curated Lexicon</a></b>

        <ul>
            <li><b>Reparative Metadata Lexicon</b><br>The Reparative Metadata Lexicon includes potentially harmful terminology organized by category (aggrandizement, ability, gender, LGBTQ, mental health, race, slavery, US Japanese Incarceration, etc.). This lexicon is best suited for uncontrolled metadata fields (e.g. Title, Description). The review and decision to change any terms flagged in this lexicon is up to collection stewards. To research reparative subject areas, the <a href="https://osf.io/yf96h">Inclusive Metadata Toolkit</a>, developed by the Digital Library Federation Cultural Assessment Working Group and its <a href="https://docs.google.com/spreadsheets/d/1pdyZz6t2TFj9sHamWSSPxcf7lFkfyV_Zb7_ygC8AbHc/edit?usp=sharing">Resource Directory</a> provide resources on many topics.
            <br>If you are running this lexicon against a large set of metadata, processing times may be delayed. To improve processing speed, we recommend selecting a subset of these categories in MaRMAT's interface rather than assessing for all categories at once. 
            </li><br>
            <li><b>Library of Congress Subject Headings (LCSH) Lexicon</b><br>The LCSH Lexicon includes selected changed and canceled Library of Congress Subject Headings as well as headings that have been identified as problematic (<a href="https://cataloginglab.org/">crowdsourced Problem LCSH, Cataloginglab.org</a>). Select changed and canceled headings, mostly relating to people and places, were culled from the <a href="https://classweb.org/approved-subjects/">Library of Congress Subject Heading Approved Monthly Lists</a> from 2023-2024 along with a few notable changes in recent years. The LCSH Lexicon is best suited to analyze metadata fields that use LCSH as a controlled vocabulary (e.g. Subject, or other fields that contain LCSH terms).
            </li><br>
            <li><b>Sensitive Content Lexicon</b><br>The Sensitive Content Lexicon includes terms that could identify records with sensitive content which may be suitable for either a sensitive content viewer or removal from public display. Sensitive topics identified include deceased people, graphic, violent, nudity, and sexual, content, and Indigenous American material that may need restriction or removal due to their cultural sensitivity and their potential violation of the Native American Graves Protection and Repatriation Act (NAGPRA). Each organization has their own set of parameters for implementing content warnings and criteria for sensitive content. Please use this lexicon directionally and adhere to your organizations established policies or guidelines.
            </li>
        </ul>
        </p>
        <p style="margin-left: 1em;">
        <b>Option B: Upload a Custom Lexicon</b><br>

        MaRMAT can be used with any custom lexicon, making it a great tool for querying metadata in bulk for a variety of use cases beyond reparative metadata practice. To use a custom lexicon, create a CSV file with the following columns:

        <ul>
            <li><b>Term</b>: The word or phrase you want to identify</li>
            <li><b>Category</b>: A grouping or classification label for the term (e.g., “GenderTerm”)</li>
        </ul>
        </p>

        <p style="margin-left: 1em;">
        <i>Note: MaRMAT identifies full strings of terms and it does not identify words within words, so make sure custom lexicons include all potential versions of a word or phrase you want to search for. For example, if you include “potatoes” in your lexicon, MaRMAT will not identify “potato” in your metadata unless “potato” is also included as an entry in the lexicon. </i>
        </p>
        <p style="margin-left: 1em;">
        Once your file is successfully loaded, click <b>Next</b> to proceed.
        </p>

        <h2 style="font-size: 2em;">Step 3: Configure the Analysis</h2>
        <p style="margin-left: 1em;">
        <b>Select the ID Column</b><br>
        Choose the column that uniquely identifies each record, such as an identifier or accession number. This ensures accurate linking between original records and flagged results. If you do not select one, MaRMAT will default to the first column in your metadata file.
        </p>
        <p style="margin-left: 1em;">
        <b>Select the Metadata Fields to Analyze</b><br>
        Check the boxes for the columns you want MaRMAT to examine (e.g., Title, Description, Subject). These are the areas where the terms you are looking to identify may appear in the metadata file.
        </p>
        <p style="margin-left: 1em;">
        <b>Select the Lexicon Categories</b><br>
        Choose one or more categories from your loaded lexicon that you want MaRMAT to check for. This helps you narrow the focus of your analysis based on the specific types of language you’re concerned with.
        </p>
        <p style="margin-left: 1em;">
        Click <b>Next</b> once you’ve made your selections. 
        </p>

        <h2 style="font-size: 2em;">Step 4: Perform the Analysis</h2>
        <p style="margin-left: 1em;">
        <b>Select an Output Location</b><br>
        Click the <b>Select Output Location</b> button and choose where you want the results saved. By default, the output file will be named <b>MaRMAT_output.csv</b>.
        </p>
        <p style="margin-left: 1em;">
        <b>Run the Analysis</b><br>
        Click <b>Perform Analysis</b>. MaRMAT will compare your selected metadata fields against the terms in the selected lexicon categories. The output will include:
        <ul>
            <li><b>Record ID</b>: The unique identifier for each record</li>
            <li><b>Field Name</b>: The metadata field where the term was found</li>
            <li><b>Term</b>: The term from the lexicon that was identified</li>
            <li><b>Category</b>: The category of the identified term</li>
            <li><b>Original Contents</b>: The original contents of the metadata field where the term was found</li>
        </ul>
        </p>
        <p style="margin-left: 1em;">
        The output will appear in the app screen and automatically be saved to the location you indicated.
        </p>
        <p style="margin-left: 1em;">
        <i>Note: Records with multiple matches will appear in multiple rows—one row per term found.</i>
        </p>
        <p style="margin-left: 1em;">
        When the process is complete, click <b>Finish</b> to return to the MaRMAT homepage.
        </p>


        """

        # Create a QLabel to display the instructions
        instructions_label = QLabel(instructions_text)
        instructions_label.setOpenExternalLinks(True)  # Allow links to be clickable
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        instructions_label.setWordWrap(True)

        # Set up a scroll area for the instructions (to handle long content)
        scroll_area = QScrollArea()
        scroll_area.setWidget(instructions_label)
        scroll_area.setWidgetResizable(True)

        # Create a button to go back to the previous screen or close
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.controller.show_main_screen)

        # Create a layout for the instructions window
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the central widget of the window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event):
        """
        
        Override the key press event to handle specific key actions.
        
        Args:
            event (QKeyEvent): The key press event that occurred.

        """
        if event.key() == Qt.Key.Key_F11:
            self.controller.toggle_fullscreen()  # Call the controller's toggle_fullscreen method
        elif event.key() == Qt.Key.Key_Escape:
            # Close the application
            QCoreApplication.instance().quit()
        else:
            super().keyPressEvent(event)  # Keep default behavior