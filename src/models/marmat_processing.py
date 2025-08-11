"""

marmat_processing.py

Handles the processing of metadata and lexicon files for the MaRMAT tool.

Author: 
    - Aiden deBoer

Adapted from:
    - Rachel Wittman (Creator of MaRMAT)
    - Kaylee Alexander (Creator of MaRMAT)

Date: 2025-08-11

"""

from pathlib import Path # Pathlib for file path handling
import pandas as pd # Pandas for data manipulation
import re # Regex for pattern matching
from PyQt6.QtCore import QObject, pyqtSignal

class marmat_processing(QObject):
    """
    A tool for assessing metadata and identifying matches based on a provided lexicon.
    This class handles loading lexicon and metadata files, selecting columns and categories,
    performing matching, and saving results to a CSV file.

    Attributes:
        metadata_df (DataFrame): DataFrame containing metadata to be processed.
        lexicon_df (DataFrame): DataFrame containing lexicon to be used for matching.
        selected_columns (list): List of columns selected for matching.
        categories (list): List of categories selected for matching.
        matches_df (DataFrame): DataFrame to store matches found during processing.
        filtered_lexicon (DataFrame): DataFrame to store filtered lexicon based on selected categories.
        progress_update (pyqtSignal): Signal to update progress bar during matching.
        finished (pyqtSignal): Signal emitted when matching completes with the results DataFrame.

    """

    metadata_df = None # Metadata to be processed
    lexicon_df = None # Lexicon to be used for matching
    selected_columns = [] # Columns selected for matching
    categories = [] # Categories selected for matching
    matches_df = pd.DataFrame # DataFrame to store matches
    filtered_lexicon = pd.DataFrame # DataFrame to store filtered lexicon
    output_file_type = '.csv' # Default output file type

    # Multithreading signals
    progress_update = pyqtSignal(int) # Signal to update progress bar
    finished = pyqtSignal(pd.DataFrame)  # Signal when matching completes

    def __init__(self):
        """Creates model with default lexicon or metadata"""

        QObject.__init__(self)

        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "data" / "lexicon-reparative-metadata.csv" # Data directory for lexicon and metadata files

        try:
            self.lexicon_df = pd.read_csv(DATA_DIR, encoding='latin1')
            print("Default lexicon loaded successfully.")

        except Exception as e:
            print(f"An error occurred while loading the default lexicon: {e}")

    @classmethod
    def with_lex_and_metadata(self, lexicon, metadata):
        """
        
        Initialize the assessment tool with lexicon and metadata.
        
        Args:
            lexicon (DataFrame): Lexicon data to be used for matching.
            metadata (DataFrame): Metadata data to be processed.

        """
        self.metadata_df = metadata
        self.lexicon_df = lexicon
        

    def load_lexicon(self, file_path) -> bool:
        """
        
        Load the lexicon file. 

        Args:
            file_path (str): Path to the lexicon CSV file.

        Returns:
            bool: True if lexicon loaded successfully, False otherwise.

        """
        file_path = re.sub(r'["]', '', file_path)
        try:
            self.lexicon_df = pd.read_csv(file_path, encoding='latin1')
            print("Lexicon loaded successfully.")
            self.lexicon_df = self.lexicon_df.rename(columns=str.lower)
            return True
        except Exception as e:
            print(f"An error occurred while loading lexicon: {e}")
            return False

    def load_metadata(self, file_path, delimiter=',') -> bool:
        """
        
        Load the metadata file.

        Args:
            file_path (str): Path to the metadata CSV file.

        Returns:
            bool: True if metadata loaded successfully, False otherwise.

        """
        file_path = re.sub(r'["]', '', file_path)
        try:
            self.metadata_df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8', on_bad_lines='warn')
            print("Metadata loaded successfully.")
            self.metadata_df = self.metadata_df.rename(columns=str.lower)
            return True
        except Exception as e:
            print(f"An error occurred while loading metadata: {e}")
            return False

    def select_columns(self, columns):
        """
        
        Select columns from the metadata for matching.

        Args:
            columns (list of str): List of column names in the metadata.
            
        """

        columns = [column.strip() for column in columns]

        self.selected_columns = columns

    def get_selecteable_columns(self) -> list:
        """
        
        Get the list of columns that can be selected for matching.
        
        Returns:
            list: List of column names in the metadata.
        
        """
        return self.metadata_df.columns.tolist()

    def get_selecteable_categories(self) -> list:
        """
        
        Get the list of categories that can be selected for matching.
        
        Returns:
            list: List of unique category names in the lexicon.

        """
        return self.lexicon_df['category'].unique().tolist()

    def select_identifier_column(self, column):
        """
        
        Select the identifier column used for uniquely identifying rows.

        Args:
            column (str): Name of the identifier column in the metadata.

        """
        self.identifier_column = column

    def select_categories(self, categories):
        """
        
        Select categories from the lexicon for matching.

        Args:
            categories (list of str): List of category names in the lexicon.

        """
        categories = [category.strip() for category in categories]
        
        self.filtered_lexicon = self.lexicon_df[self.lexicon_df['category'].isin(categories)]
        
        print(self.filtered_lexicon.head())

    def perform_matching(self, output_file, progress_callback=None) -> None:
        """
        
        Perform matching between selected columns and categories and save results to a CSV file.

        Args:
            output_file (str): Path to the output CSV file to save matching results.
            progress_callback (function, optional): Callback function to update progress. Defaults to None.
        
        Returns:
            None: The results are saved to the specified output file.

        """
        if self.lexicon_df is None or self.metadata_df is None:
            print("Please load lexicon and metadata files first.")
            return

        # Reference the progress callback function
        if progress_callback:
            self.progress_update = progress_callback

        # DEBUGGING: Print the selected columns and categories
        print("DEBUGGING: Selected columns and categories")
        print(f"Selected columns: {self.selected_columns}")
        print(f"Selected categories: {self.categories}")


        self.matches_df = self.find_matches(self.selected_columns)
        print(self.matches_df)

        # Write results to CSV
        try:
            print(output_file)
            if output_file.endswith('.csv'):
                print("Saving results as CSV")
                self.matches_df.to_csv(output_file, index=False)
            else:
                print("Saving results as TSV")
                self.matches_df.to_csv(output_file, sep='\t', index=False)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while saving results: {e}")

    def get_matching_results(self) -> pd.DataFrame:
        """
        
        Get the matching results.

        Returns:
            DataFrame: DataFrame containing the matching results. If no matches found, returns None.

        """
        if self.matches_df is not None and not self.matches_df.empty:
            return self.matches_df
        else:
            print("No matching results available.")
            return None

    def find_matches(self, sel_col) -> pd.DataFrame:
        """
        
        Find matches between metadata and lexicon based on selected columns and categories.
        This method iterates through the selected columns in the metadata and searches for terms from the lexicon.
        It uses regex to match whole words, ensuring case-insensitive matching.
        This method emits progress updates during the matching process.

        Args:
            selected_columns (list of str): List of column names from metadata for matching.

        Returns:
            list of tuple: List of tuples containing matched results (Identifier, Term, Category, Column).

        """
        
        lex = self.filtered_lexicon
        meta = self.metadata_df
        matches = []
        
        total_cells_to_search = len(meta) * len(lex) * len(sel_col)
        self.progress = 0  # Initialize progress variable
        
        progress_update_threshold = int(total_cells_to_search * 0.01)  # Update progress every 0.1% of total cells
        
        progress_percent = 0
        
        print(f"Searching {total_cells_to_search} cells for matches...")

        print(f"Progress update threshold: {progress_update_threshold}")
        
        # Iterate through each selected column
        for col in sel_col:
            # Iterate through each row in the lexicon
            for _, row in lex.iterrows():
                term = row['term']
                category = row['category']
                
                # Create a regex pattern that matches the whole word, case-insensitive
                pattern = r'\b' + re.escape(term) + r'\b'

                # Iterate through each row in the metadata
                for index, value in meta[col].items():
                    if isinstance(value, str) and re.search(pattern, value, flags=re.IGNORECASE):
                        matches.append({
                            'Identifier': meta[self.identifier_column][index],
                            'Term': term,
                            'Category': category,
                            'Column': col,
                            'Original Text': value
                        })
                    
                    # Update progress
                    self.progress += 1
                    
                    if (self.progress % progress_update_threshold == 0):
                        progress_percent += 1
                        self.progress_update.emit(progress_percent)  # Emit progress update

        
        
        self.matches_df = pd.DataFrame(matches)
        
        self.progress_update.emit(100)
        self.finished.emit(self.matches_df)  # Emit signal when matching completes
        
        
        return self.matches_df
    
    def open_output_file_location(self):
        """Open the output file location in the file explorer."""
        try:
            output_path = Path(self.output_file)
            if output_path.exists():
                output_path.parent.open()
            else:
                print("Output file does not exist.")
        except Exception as e:
            print(f"An error occurred while opening the output file location: {e}")
