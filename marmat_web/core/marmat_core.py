"""

marmat_core.py

Framework-agnostic core of the MaRMAT metadata assessment tool.

This is a decoupled port of ``src/models/marmat_processing.py``. The original
class extended ``PyQt6.QtCore.QObject`` and reported progress via Qt signals
(``pyqtSignal``). For the Flask web frontend those Qt dependencies have been
removed: progress is reported through an optional plain ``progress_callback``
and all mutable state lives on the instance (not the class) so a single
long-lived instance can be reused safely across web requests.

The heavy matching work is unchanged: vectorized pandas ``str.contains`` regex
matching distributed across CPU cores via ``concurrent.futures.ProcessPoolExecutor``.

Author:
    - Aiden deBoer

Adapted from:
    - Rachel Wittman (Creator of MaRMAT)
    - Kaylee Alexander (Creator of MaRMAT)
"""

from pathlib import Path
import concurrent.futures  # Process-based parallelism to bypass the GIL
import os  # CPU core count detection for worker pool sizing
import re  # Regex for pattern matching

import numpy as np  # Needed for handling missing values
import pandas as pd  # Pandas for data manipulation
from bs4 import BeautifulSoup  # BeautifulSoup for XML parsing


# Path to the bundled default lexicon (shipped under src/data so it stays
# colocated with the existing project data files).
DEFAULT_LEXICON_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "data"
    / "lexicon-reparative-metadata.csv"
)


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
            - collection_title_values (list, optional): Row-aligned values from the
              selected collection-title metadata column.

    Returns:
        list of dict: Matched results. Each dict contains 'Identifier',
        'Collection Title', 'Term', 'Category', 'Column', 'Original Text'.
    """
    col_values, id_values, col_name, term_batch, collection_title_values = args

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
                    'Collection Title': collection_title_values[idx] if collection_title_values is not None else None,
                    'Term': term,
                    'Category': category,
                    'Column': col_name,
                    'Original Text': col_values[idx]
                })

    return matches


class MarmatProcessing:
    """
    A tool for assessing metadata and identifying matches based on a provided lexicon.

    Handles loading lexicon and metadata files, selecting columns and categories,
    performing matching, and saving results. All state is held on the instance so a
    single instance can be reused safely by the Flask app between requests.
    """

    def __init__(self, lexicon_path=DEFAULT_LEXICON_PATH):
        """
        Create the processor and load the bundled default lexicon.

        Args:
            lexicon_path (Path | str): Path to the default lexicon CSV.
        """
        # Per-instance state (was class-level in the PyQt version, which risked
        # cross-instance bleed-through under a long-lived web singleton).
        self.metadata_df = None
        self.lexicon_df = None
        self.filtered_lexicon = pd.DataFrame()
        self.matches_df = pd.DataFrame()
        self.selected_columns = []
        self.categories = []
        self.identifier_column = None
        self.output_file_type = '.csv'
        self.include_collection_title = False
        self.collection_title_column = None

        try:
            self.lexicon_df = pd.read_csv(lexicon_path, encoding='latin1')
            self.lexicon_df = self.lexicon_df.rename(columns=str.lower)
            print("Default lexicon loaded successfully.")
        except Exception as e:
            print(f"An error occurred while loading the default lexicon: {e}")

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
            # Match metadata behaviour: try UTF-8 (with BOM) first, fall back to latin1.
            try:
                self.lexicon_df = pd.read_csv(file_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                self.lexicon_df = pd.read_csv(file_path, encoding='latin1')
            self.lexicon_df = self.lexicon_df.rename(columns=str.lower)
            print("Lexicon loaded successfully.")
            return True
        except Exception as e:
            print(f"An error occurred while loading lexicon: {e}")
            return False

    def load_metadata(self, file_path, delimiter=',') -> bool:
        """
        Load the metadata file (CSV/TSV or EAD XML).

        Args:
            file_path (str): Path to the metadata file.
            delimiter (str): Field delimiter for CSV/TSV files.

        Returns:
            bool: True if metadata loaded successfully, False otherwise.
        """
        file_path = re.sub(r'["]', '', file_path)
        try:
            file_extension = Path(file_path).suffix.lower()

            if file_extension == '.xml':
                # Use the EAD processor and auto-set the identifier column.
                self.metadata_df = self._process_ead_xml(file_path)
                self.identifier_column = 'identifier'
            else:
                # CSV/TSV: try UTF-8 (with BOM), then fall back to latin1.
                try:
                    self.metadata_df = pd.read_csv(
                        file_path, delimiter=delimiter, encoding='utf-8-sig', on_bad_lines='warn'
                    )
                except UnicodeDecodeError:
                    self.metadata_df = pd.read_csv(
                        file_path, delimiter=delimiter, encoding='latin1', on_bad_lines='warn'
                    )

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

    def is_ead(self) -> bool:
        """Return True if the loaded metadata came from an EAD XML file."""
        return self.identifier_column == 'identifier' and (
            self.metadata_df is not None and 'identifier' in self.metadata_df.columns
        )

    def _process_ead_xml(self, file_path):
        """
        Parse an EAD XML file using BeautifulSoup into a structured DataFrame,
        including a detailed inventory of components (boxes/folders).

        Args:
            file_path (str): Path to the EAD XML file.

        Returns:
            DataFrame: Extracted fields pivoted to a wide (box-as-column) format.
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

            # --- COMPONENT-LEVEL EXTRACTION (Boxes and Folders) ---
            components_list = []
            component_tags = soup.find_all(re.compile(r'^c\d{,2}$'))

            for c_tag in component_tags:
                if c_tag.find('container'):
                    component_data = {'box': None, 'folder': None, 'title': '', 'description': ''}

                    did_tag = c_tag.find('did', recursive=False)
                    if did_tag:
                        unittitle_tag = did_tag.find('unittitle')
                        if unittitle_tag:
                            component_data['title'] = ' '.join(unittitle_tag.text.split())

                        for container in did_tag.find_all('container'):
                            container_type = container.get('type', '').lower()
                            if container_type in ['box', 'folder']:
                                component_data[container_type] = container.text.strip()

                    scopecontent_tag = c_tag.find('scopecontent', recursive=False)
                    if scopecontent_tag:
                        component_data['description'] = ' '.join(scopecontent_tag.get_text(separator=' ', strip=True).split())

                    components_list.append(component_data)

            # --- AGGREGATED SEARCHABLE TEXT ---
            all_text_parts = [p.get_text(separator=" ", strip=True) for p in soup.find_all('p')]
            all_text_parts.extend([s.get_text(separator=" ", strip=True) for s in soup.find_all('scopecontent')])
            searchable_text = ' '.join(all_text_parts)

            data = {
                'identifier': [eadid],
                'collection_title': [collection_title],
                'biographical_note': [biohist_text],
                'searchable_text': [searchable_text],
                'components': [components_list]
            }
            df = pd.DataFrame(data)

            print(f"Successfully processed EAD file: {file_path}")
            return self.pivot_boxes_to_columns(df)

        except Exception as e:
            print(f"Could not process EAD file with BeautifulSoup: {e}")
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            return pd.DataFrame({
                'identifier': [Path(file_path).stem],
                'collection_title': ["Parsing Failed"],
                'biographical_note': [""],
                'searchable_text': [xml_content],
                'components': [[]]
            })

    def pivot_boxes_to_columns(self, df_original):
        """
        Reshape the EAD DataFrame to a wide format where each row is a folder and
        each unique box number becomes a column.

        Args:
            df_original (DataFrame): DataFrame generated by _process_ead_xml.

        Returns:
            DataFrame: Pivoted DataFrame, or empty DataFrame if no components exist.
        """
        df_long = df_original.explode('components').dropna(subset=['components'])

        if df_long.empty:
            print("No components to pivot.")
            return pd.DataFrame()

        components_df = df_long['components'].apply(pd.Series)

        df_long = pd.concat([
            df_long.drop(columns=['components']).reset_index(drop=True),
            components_df.reset_index(drop=True)
        ], axis=1)

        df_long['contents'] = df_long['title'].fillna('')
        descriptions = df_long['description'].fillna('')
        df_long['contents'] += np.where(descriptions != '', ' (' + descriptions + ')', '')

        df_long['box_column'] = 'Box ' + df_long['box'].astype(str)

        df_wide = df_long.pivot_table(
            index=['identifier', 'collection_title', 'folder'],
            columns='box_column',
            values='contents',
            aggfunc='first'
        ).reset_index()

        df_wide.columns.name = None

        return df_wide

    def select_columns(self, columns):
        """Select the metadata columns to search."""
        self.selected_columns = [column.strip() for column in columns]

    def get_selecteable_columns(self) -> list:
        """Return the list of metadata column names available for selection."""
        if self.metadata_df is None:
            return []
        return self.metadata_df.columns.tolist()

    def get_selecteable_categories(self) -> list:
        """Return the list of unique lexicon category names."""
        if self.lexicon_df is None or 'category' not in self.lexicon_df.columns:
            return []
        return self.lexicon_df['category'].dropna().unique().tolist()

    def select_identifier_column(self, column):
        """Set the identifier (unique key) column."""
        self.identifier_column = column

    def select_categories(self, categories):
        """Filter the lexicon down to the selected categories."""
        categories = [category.strip() for category in categories]
        self.categories = categories
        self.filtered_lexicon = self.lexicon_df[self.lexicon_df['category'].isin(categories)]

    def set_include_collection_title(self, include_collection_title: bool):
        """Set whether to include the collection title in output."""
        self.include_collection_title = include_collection_title

    def select_collection_title_column(self, column: str):
        """Set the metadata column to use as the collection title in output."""
        self.collection_title_column = column

    def perform_matching(self, output_file=None, progress_callback=None) -> pd.DataFrame:
        """
        Perform matching between selected columns and categories, optionally saving
        results to a CSV/TSV file.

        Args:
            output_file (str, optional): Path to write results. If None, results are
                only stored on the instance (and returned).
            progress_callback (callable, optional): Called with an int percentage
                (0-100) as work completes.

        Returns:
            DataFrame: The matching results.
        """
        if self.lexicon_df is None or self.metadata_df is None:
            print("Please load lexicon and metadata files first.")
            return pd.DataFrame()

        self.matches_df = self.find_matches(self.selected_columns, progress_callback=progress_callback)

        if output_file:
            try:
                if output_file.endswith('.csv'):
                    self.matches_df.to_csv(output_file, index=False)
                else:
                    self.matches_df.to_csv(output_file, sep='\t', index=False)
                print(f"Results saved to {output_file}")
            except Exception as e:
                print(f"An error occurred while saving results: {e}")

        return self.matches_df

    def get_matching_results(self) -> pd.DataFrame:
        """Return the matching results, or None if there are none."""
        if self.matches_df is not None and not self.matches_df.empty:
            return self.matches_df
        print("No matching results available.")
        return None

    def find_matches(self, sel_col, progress_callback=None) -> pd.DataFrame:
        """
        Find matches between metadata and lexicon based on selected columns and categories.

        Uses vectorized pandas str.contains() distributed across CPU cores via
        ProcessPoolExecutor, with a single-process vectorized fallback if process
        spawning is unavailable.

        Args:
            sel_col (list of str): Metadata column names to search.
            progress_callback (callable, optional): Called with an int percentage.

        Returns:
            DataFrame: Matched results sorted by Identifier, or empty if none found.
        """
        def emit(percent):
            if progress_callback:
                progress_callback(percent)

        lex = self.filtered_lexicon
        meta = self.metadata_df

        if lex is None or lex.empty or meta is None or meta.empty:
            print("No data available for matching.")
            self.matches_df = pd.DataFrame()
            emit(100)
            return self.matches_df

        terms_categories = list(zip(lex['term'], lex['category']))

        collection_title_values = None
        if (
            self.include_collection_title
            and self.collection_title_column
            and self.collection_title_column in meta.columns
        ):
            collection_title_values = meta[self.collection_title_column].tolist()

        print(f"Matching {len(terms_categories)} terms across {len(sel_col)} columns "
              f"in {len(meta)} metadata rows...")

        # --- Work Partitioning ---
        num_cores = os.cpu_count() or 4
        batch_count = max(1, num_cores * 2)
        batch_size = max(1, len(terms_categories) // batch_count)
        term_batches = [
            terms_categories[i:i + batch_size]
            for i in range(0, len(terms_categories), batch_size)
        ]

        work_items = []
        for col in sel_col:
            col_data = meta[col].tolist()
            id_data = meta[self.identifier_column].tolist()
            for batch in term_batches:
                work_items.append((col_data, id_data, col, batch, collection_title_values))

        total_work_items = len(work_items)
        num_workers = min(total_work_items, num_cores) if total_work_items else 1

        print(f"Dispatching {total_work_items} work units across up to {num_workers} processes...")

        all_matches = []

        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
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

                    completed_count += 1
                    emit(int((completed_count / total_work_items) * 99))

        except Exception as e:
            # Fallback: single-process vectorized matching.
            print(f"Multiprocessing unavailable ({e}). Falling back to single-process vectorized mode.")
            for i, item in enumerate(work_items):
                result = _match_terms_in_column(item)
                all_matches.extend(result)
                emit(int(((i + 1) / total_work_items) * 99))

        # --- Result Assembly ---
        self.matches_df = pd.DataFrame(all_matches)

        if not self.matches_df.empty:
            self.matches_df = self.matches_df.sort_values(
                by=['Identifier', 'Column', 'Term']
            ).reset_index(drop=True)

            if not self.include_collection_title and 'Collection Title' in self.matches_df.columns:
                self.matches_df = self.matches_df.drop(columns=['Collection Title'])

            if self.include_collection_title and 'Collection Title' in self.matches_df.columns:
                ordered_columns = [
                    'Identifier', 'Collection Title', 'Term', 'Category', 'Column', 'Original Text'
                ]
                existing_ordered_columns = [col for col in ordered_columns if col in self.matches_df.columns]
                self.matches_df = self.matches_df[existing_ordered_columns]

        emit(100)
        return self.matches_df
