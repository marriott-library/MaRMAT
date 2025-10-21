"""

marmat_processing.py

Handles the processing of metadata and lexicon files for the MaRMAT tool.

Author: 
    - Aiden deBoer

Adapted from:
    - Rachel Wittman (Creator of MaRMAT)
    - Kaylee Alexander (Creator of MaRMAT)

Date: 2025-10-14

"""

from logging import root
from pathlib import Path
from bs4 import BeautifulSoup # BeautifulSoup for XML parsing
import pandas as pd # Pandas for data manipulation
import re # Regex for pattern matching
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np # Needed for handling missing values

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
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.xml':
                # Use the new, powerful EAD processor
                self.metadata_df = self._process_ead_xml(file_path)
                # Set the identifier column automatically for EAD
                self.identifier_column = 'identifier'
            else:
                # Handle CSV/TSV files as before
                self.metadata_df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8', on_bad_lines='warn')
            
            print("Metadata loaded successfully.")
            
            # Normalize column names to lowercase
            try:
                self.metadata_df.rename(columns=str.lower, inplace=True)
            except Exception:
                pass
                
            return True
        except Exception as e:
            print(f"An error occurred while loading metadata: {e}")
            return False


    def _process_ead_xml(self, file_path):
        """
        Parses an EAD XML file using BeautifulSoup to extract relevant text fields
        into a structured DataFrame, including a detailed inventory of components.

        Args:
            file_path (str): Path to the EAD XML file.

        Returns:
            DataFrame: DataFrame containing extracted fields, with a 'components'
                    column listing each box/folder and its details.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'xml')

            # --- COLLECTION-LEVEL METADATA ---
            eadid = soup.find('eadid').text if soup.find('eadid') else Path(file_path).stem
            collection_title_tag = soup.find('unittitle')
            collection_title = ' '.join(collection_title_tag.text.split()) if collection_title_tag else "No Title Found"
            biohist_tag = soup.find('bioghist')
            biohist_text = ' '.join(biohist_tag.get_text(separator=" ", strip=True).split()) if biohist_tag else ""

            # --- NEW: COMPONENT-LEVEL EXTRACTION (Boxes and Folders) ---
            components_list = []
            # Find all component tags like <c>, <c01>, <c02>... using a regular expression
            component_tags = soup.find_all(re.compile(r'^c\d{,2}$'))

            for c_tag in component_tags:
                # Process a component only if it contains a <container> tag (i.e., it's a physical unit)
                if c_tag.find('container'):
                    component_data = {
                        'box': None,
                        'folder': None,
                        'title': '',
                        'description': ''
                    }

                    # <did> usually holds the title and container info
                    did_tag = c_tag.find('did', recursive=False)
                    if did_tag:
                        # Extract title for the component
                        unittitle_tag = did_tag.find('unittitle')
                        if unittitle_tag:
                            component_data['title'] = ' '.join(unittitle_tag.text.split())

                        # Extract box and folder numbers from <container> tags
                        for container in did_tag.find_all('container'):
                            container_type = container.get('type', '').lower()
                            if container_type in ['box', 'folder']:
                                component_data[container_type] = container.text.strip()
                    
                    # Extract descriptive text like <scopecontent> for this specific component
                    scopecontent_tag = c_tag.find('scopecontent', recursive=False)
                    if scopecontent_tag:
                        component_data['description'] = ' '.join(scopecontent_tag.get_text(separator=' ', strip=True).split())
                    
                    # Add the extracted component data to our list
                    components_list.append(component_data)

            # --- AGGREGATED SEARCHABLE TEXT (Maintained for broad searches) ---
            all_text_parts = [p.get_text(separator=" ", strip=True) for p in soup.find_all('p')]
            all_text_parts.extend([s.get_text(separator=" ", strip=True) for s in soup.find_all('scopecontent')])
            searchable_text = ' '.join(all_text_parts)

            # --- DATAFRAME CREATION (Updated with new 'components' column) ---
            data = {
                'identifier': [eadid],
                'collection_title': [collection_title],
                'biographical_note': [biohist_text],
                'searchable_text': [searchable_text],
                'components': [components_list] # Add the list of components here
            }
            df = pd.DataFrame(data)
            
            print(f"Successfully processed EAD file: {file_path}")
            # return df
            return self.pivot_boxes_to_columns(df)

        except Exception as e:
            print(f"Could not process EAD file with BeautifulSoup: {e}")
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            # Fallback still returns a DataFrame for consistency
            return pd.DataFrame({
                'identifier': [Path(file_path).stem],
                'collection_title': ["Parsing Failed"],
                'biographical_note': [""],
                'searchable_text': [xml_content],
                'components': [[]]
            })


    def pivot_boxes_to_columns(self, df_original):
        """
        Reshapes a DataFrame from the EAD processor to a wide format.

        In the new format, each row represents a folder and each unique box
        number becomes a column.

        Args:
            df_original (DataFrame): The DataFrame generated by _process_ead_xml.

        Returns:
            DataFrame: A new, pivoted DataFrame or an empty DataFrame if no
                    components exist.
        """
        # 1. Explode the 'components' list to give each folder its own row
        # This duplicates the collection-level info (identifier, title) for each row.
        df_long = df_original.explode('components').dropna(subset=['components'])

        if df_long.empty:
            print("No components to pivot.")
            return pd.DataFrame()

        # 2. Normalize the 'components' column
        # This turns the dictionary in 'components' into its own set of columns (box, folder, title, etc.)
        components_df = df_long['components'].apply(pd.Series)
        
        # Combine the new component columns with the collection-level info
        df_long = pd.concat([
            df_long.drop(columns=['components']).reset_index(drop=True),
            components_df.reset_index(drop=True)
        ], axis=1)

        # 3. Prepare for pivoting
        # Create a clean 'contents' column to be the values in our new table
        df_long['contents'] = df_long['title'].fillna('')
        # Fill NaN descriptions with an empty string before concatenating
        descriptions = df_long['description'].fillna('')
        # Add description in parentheses if it exists
        df_long['contents'] += np.where(descriptions != '', ' (' + descriptions + ')', '')
        
        # Create a clear column name for the boxes, e.g., "Box 1", "Box 2"
        df_long['box_column'] = 'Box ' + df_long['box'].astype(str)

        # 4. Pivot the table
        # - index: What to use for the rows (collection identifier and folder number).
        # - columns: What to use for the columns (the new box_column).
        # - values: What to fill the cells with (the 'contents').
        df_wide = df_long.pivot_table(
            index=['identifier', 'collection_title', 'folder'],
            columns='box_column',
            values='contents',
            aggfunc='first' # Use 'first' to handle any potential duplicates
        ).reset_index()

        # Clean up the column names for better presentation
        df_wide.columns.name = None
        
        return df_wide

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

        self.matches_df = self.matches_df.sort_values(by='Identifier')
        
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
