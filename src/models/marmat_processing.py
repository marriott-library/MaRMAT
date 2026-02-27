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
import concurrent.futures # Process-based parallelism to bypass the GIL
import os # CPU core count detection for worker pool sizing


def _match_terms_in_column(args):
    """
    Process-safe worker function that searches a single metadata column for a batch
    of lexicon terms using vectorized pandas string operations.

    This function is designed to run in a separate process via ProcessPoolExecutor,
    bypassing Python's Global Interpreter Lock (GIL) for true parallel execution.
    It must remain at module level (not inside a class) so that the multiprocessing
    framework can pickle and transfer it to worker processes.

    Each invocation handles one (column, term_batch) unit of work. Pandas'
    str.contains() is used instead of a Python-level row loop, delegating the
    per-row iteration to optimized C-level code for a significant speed improvement.

    Args:
        args (tuple): A packed tuple containing:
            - col_values (list): Raw values from the metadata column to search.
            - id_values (list): Corresponding identifier values for each row.
            - col_name (str): Name of the metadata column being searched.
            - term_batch (list of tuple): (term, category) pairs from the lexicon.

    Returns:
        list of dict: Matched results. Each dict contains:
            - 'Identifier': The row's identifier value.
            - 'Term': The lexicon term that was matched.
            - 'Category': The category of the matched term.
            - 'Column': The metadata column where the match was found.
            - 'Original Text': The full text of the cell containing the match.
    """
    col_values, id_values, col_name, term_batch = args

    # Rebuild a pandas Series in this worker process for vectorized string operations.
    # Converting from a list is fast and avoids the pickling overhead of a full DataFrame.
    col_series = pd.Series(col_values)
    matches = []

    for term, category in term_batch:
        # Build a whole-word, case-insensitive regex pattern for the current term
        pattern = r'\b' + re.escape(term) + r'\b'

        try:
            # Vectorized regex search across the entire column.
            # This runs at C level inside pandas/numpy, far faster than a Python loop.
            mask = col_series.str.contains(pattern, case=False, na=False, regex=True)
        except re.error:
            # Skip terms that produce invalid regex patterns gracefully
            continue

        # Only iterate over the (typically small) set of matching rows
        if mask.any():
            matched_indices = mask[mask].index
            for idx in matched_indices:
                matches.append({
                    'Identifier': id_values[idx],
                    'Term': term,
                    'Category': category,
                    'Column': col_name,
                    'Original Text': col_values[idx]
                })

    return matches


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

        Uses a two-pronged optimization strategy to maximize throughput:
          1. **Vectorized string operations**: pandas' str.contains() replaces the inner
             Python-level loop over metadata rows, delegating per-row regex matching
             to C-level code for ~10-100x speedup on the innermost loop.
          2. **Process-based parallelism**: concurrent.futures.ProcessPoolExecutor
             distributes (column, term_batch) work units across CPU cores, bypassing
             the Global Interpreter Lock (GIL) for true parallel execution.

        Work is divided into granular (column, term_batch) units to balance CPU
        utilization and provide responsive progress bar updates.

        Progress signals are emitted from the calling thread (QThread) as worker
        processes complete their units, keeping the GUI responsive.

        If multiprocessing is unavailable (e.g., in a frozen/packaged environment),
        the method falls back to single-process vectorized matching, which is still
        substantially faster than the naive triple-nested Python loop.

        Args:
            sel_col (list of str): Column names from the metadata DataFrame to
                search for lexicon term matches.

        Returns:
            DataFrame: Matched results sorted by 'Identifier', with columns:
                'Identifier', 'Term', 'Category', 'Column', 'Original Text'.
                Returns an empty DataFrame if no matches are found.
        """
        lex = self.filtered_lexicon
        meta = self.metadata_df

        # Guard against missing or empty data before starting expensive work
        if lex is None or lex.empty or meta is None or meta.empty:
            print("No data available for matching.")
            self.matches_df = pd.DataFrame()
            self.progress_update.emit(100)
            self.finished.emit(self.matches_df)
            return self.matches_df

        # Build (term, category) pairs from the filtered lexicon for serialization
        terms_categories = list(zip(lex['term'], lex['category']))

        print(f"Matching {len(terms_categories)} terms across {len(sel_col)} columns "
              f"in {len(meta)} metadata rows...")

        # --- Work Partitioning ---
        # Determine CPU core count and split terms into batches.
        # Targeting ~2 batches per core per column gives fine-grained progress
        # updates while keeping per-batch serialization overhead low.
        num_cores = os.cpu_count() or 4
        batch_count = max(1, num_cores * 2)
        batch_size = max(1, len(terms_categories) // batch_count)
        term_batches = [
            terms_categories[i:i + batch_size]
            for i in range(0, len(terms_categories), batch_size)
        ]

        # Build work items: one per (column, term_batch) combination.
        # Each item is a self-contained, picklable tuple for a worker process.
        work_items = []
        for col in sel_col:
            col_data = meta[col].tolist()
            id_data = meta[self.identifier_column].tolist()
            for batch in term_batches:
                work_items.append((col_data, id_data, col, batch))

        total_work_items = len(work_items)
        num_workers = min(total_work_items, num_cores)

        print(f"Dispatching {total_work_items} work units across up to "
              f"{num_workers} processes...")

        # --- Parallel Execution (bypasses the GIL via separate processes) ---
        all_matches = []

        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                # Submit all work items; map each future to its index for tracking
                futures = {
                    executor.submit(_match_terms_in_column, item): i
                    for i, item in enumerate(work_items)
                }

                completed_count = 0
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        all_matches.extend(result)
                    except Exception as e:
                        print(f"Worker process error: {e}")

                    # Emit progress as each work unit finishes (cap at 99% until final assembly)
                    completed_count += 1
                    progress_percent = int((completed_count / total_work_items) * 99)
                    self.progress_update.emit(progress_percent)

        except Exception as e:
            # Fallback: single-process vectorized matching if process spawning fails
            # (e.g., in frozen/packaged environments or restricted OS configurations).
            # Still uses vectorized pandas operations, so performance remains good.
            print(f"Multiprocessing unavailable ({e}). "
                  f"Falling back to single-process vectorized mode.")
            for i, item in enumerate(work_items):
                result = _match_terms_in_column(item)
                all_matches.extend(result)
                progress_percent = int(((i + 1) / total_work_items) * 99)
                self.progress_update.emit(progress_percent)

        # --- Result Assembly ---
        self.matches_df = pd.DataFrame(all_matches)

        if not self.matches_df.empty:
            # Sort by Identifier for consistent output, with secondary keys
            # for deterministic ordering regardless of process completion order
            self.matches_df = self.matches_df.sort_values(
                by=['Identifier', 'Column', 'Term']
            ).reset_index(drop=True)

        # Signal completion to the GUI layer
        self.progress_update.emit(100)
        self.finished.emit(self.matches_df)

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
