import pandas as pd
import re


class MaRMAT:
    """A tool for assessing metadata and identifying matches based on a provided lexicon."""

    def __init__(self):
        """Initialize the assessment tool."""
        self.lexicon_df = None
        self.metadata_df = None
        self.columns = []  # List of all available columns in the metadata
        self.categories = []  # List of all available categories in the lexicon
        self.selected_columns = []  # List of columns selected for matching
        self.identifier_column = None  # Identifier column used to uniquely identify rows

    def load_lexicon(self, file_path):
        """Load the lexicon file.

        Parameters:
        file_path (str): Path to the lexicon CSV file.

        """
        try:
            self.lexicon_df = pd.read_csv(file_path, encoding='latin1')
            print("Lexicon loaded successfully.")
        except Exception as e:
            print(f"An error occurred while loading lexicon: {e}")

    def load_metadata(self, file_path):
        """Load the metadata file.

        Parameters:
        file_path (str): Path to the metadata CSV file.

        """
        try:
            self.metadata_df = pd.read_csv(file_path, encoding='latin1')
            print("Metadata loaded successfully.")
        except Exception as e:
            print(f"An error occurred while loading metadata: {e}")

    def select_columns(self, columns):
        """Select columns from the metadata for matching.

        Parameters:
        columns (list of str): List of column names in the metadata.

        """
        self.selected_columns = columns

    def select_identifier_column(self, column):
        """Select the identifier column used for uniquely identifying rows.

        Parameters:
        column (str): Name of the identifier column in the metadata.

        """
        self.identifier_column = column

    def select_categories(self, categories):
        """Select categories from the lexicon for matching.

        Parameters:
        categories (list of str): List of category names in the lexicon.

        """
        self.categories = categories

    def perform_matching(self, output_file):
        """Perform matching between selected columns and categories and save results to a CSV file.

        Parameters:
        output_file (str): Path to the output CSV file to save matching results.

        """
        if self.lexicon_df is None or self.metadata_df is None:
            print("Please load lexicon and metadata files first.")
            return

        matches = self.find_matches(self.selected_columns, self.categories)
        matches_df = pd.DataFrame(matches, columns=['Identifier', 'Term', 'Category', 'Column'])
        print(matches_df)

        """Write results to CSV"""
        try:
            matches_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while saving results: {e}")

    def find_matches(self, selected_columns, selected_categories):
        """Find matches between metadata and lexicon based on selected columns and categories.

        Parameters:
        selected_columns (list of str): List of column names from metadata for matching.
        selected_categories (list of str): List of category names from the lexicon for matching.

        Returns:
        list of tuple: List of tuples containing matched results (Identifier, Term, Category, Column).

        """
        matches = []
        lexicon_df = self.lexicon_df[self.lexicon_df['category'].isin(selected_categories)]
        for index, row in self.metadata_df.iterrows():
            for col in selected_columns:
                if isinstance(row[col], str):
                    for term, category in zip(lexicon_df['term'], lexicon_df['category']):
                        if re.search(r'\b' + re.escape(term.lower()) + r'\b', row[col].lower()):
                            matches.append((row[self.identifier_column], term, category, col))
        return matches