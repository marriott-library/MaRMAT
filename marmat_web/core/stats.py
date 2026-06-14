"""

stats.py

Server-side statistics aggregations for the MaRMAT statistics dashboard.

Ports the KPI and chart computations from the PyQt ``StatisticsWindow``
(matplotlib/wordcloud) into pure-pandas functions that return plain Python
dicts/lists. The Flask ``/api/statistics`` endpoint serialises the output of
``build_statistics`` to JSON, and the browser renders it with D3.js.

Author:
    - Aiden deBoer
"""

import pandas as pd


# Deterministic categorical palette anchored on University of Utah "Utah Red".
# Mirrors _build_category_color_map in the PyQt StatisticsWindow but uses a
# brand-aligned palette so charts/legends stay consistent across the dashboard.
CATEGORY_PALETTE = [
    "#CC0000",  # Utah Red
    "#890000",  # Dark crimson
    "#2B6CB0",  # Blue
    "#2F855A",  # Green
    "#B7791F",  # Gold
    "#6B46C1",  # Purple
    "#C05621",  # Orange
    "#0987A0",  # Teal
    "#97266D",  # Magenta
    "#4A5568",  # Slate
    "#9B2C2C",  # Brick
    "#1A365D",  # Navy
    "#276749",  # Forest
    "#744210",  # Bronze
    "#553C9A",  # Indigo
    "#702459",  # Plum
]


def build_category_color_map(categories):
    """
    Build a deterministic ``category -> hex color`` mapping.

    Args:
        categories (iterable of str): Category labels (order is preserved).

    Returns:
        dict: Mapping of category label to a hex color string.
    """
    color_map = {}
    for idx, category in enumerate(categories):
        color_map[str(category)] = CATEGORY_PALETTE[idx % len(CATEGORY_PALETTE)]
    return color_map


def _empty_statistics():
    """Return a well-formed statistics document for an empty/None result set."""
    return {
        "hasData": False,
        "kpis": {
            "totalFlagged": 0,
            "uniqueCollections": 0,
            "uniqueTerms": 0,
            "mostFrequentCategory": "N/A",
            "mostFrequentTerm": "N/A",
        },
        "categoryDistribution": [],
        "topTerms": [],
        "columnDistribution": [],
        "wordCloud": [],
        "categoryColors": {},
    }


def _compute_kpis(df):
    """Compute the five dashboard KPIs (exact port of _update_kpis)."""
    total_flagged = int(len(df))

    if 'Collection Title' in df.columns and df['Collection Title'].notna().any():
        unique_collections = int(df['Collection Title'].nunique())
    elif 'Identifier' in df.columns:
        unique_collections = int(df['Identifier'].nunique())
    else:
        unique_collections = 0

    unique_terms = int(df['Term'].nunique()) if 'Term' in df.columns else 0

    most_frequent_category = (
        str(df['Category'].value_counts().idxmax())
        if 'Category' in df.columns and not df['Category'].dropna().empty
        else "N/A"
    )
    most_frequent_term = (
        str(df['Term'].value_counts().idxmax())
        if 'Term' in df.columns and not df['Term'].dropna().empty
        else "N/A"
    )

    return {
        "totalFlagged": total_flagged,
        "uniqueCollections": unique_collections,
        "uniqueTerms": unique_terms,
        "mostFrequentCategory": most_frequent_category,
        "mostFrequentTerm": most_frequent_term,
    }


def _category_distribution(df):
    """Counts of flagged instances per category (descending)."""
    if 'Category' not in df.columns or df['Category'].dropna().empty:
        return []
    counts = df['Category'].fillna('Uncategorized').astype(str).value_counts()
    return [{"category": str(cat), "count": int(n)} for cat, n in counts.items()]


def _top_terms(df, limit=10):
    """
    Top N most frequent terms, each annotated with its dominant category.

    Ports the groupby logic that assigns each term the category it most often
    appears under, so D3 can colour each bar by category.
    """
    if 'Term' not in df.columns or df['Term'].dropna().empty:
        return []

    term_counts = df['Term'].dropna().astype(str).value_counts().head(limit)
    term_labels = set(term_counts.index)

    dominant_category_by_term = {}
    if 'Category' in df.columns:
        subset = df[df['Term'].notna() & df['Term'].astype(str).isin(term_labels)].copy()
        subset['Term'] = subset['Term'].astype(str)
        subset['Category'] = subset['Category'].fillna('Uncategorized').astype(str)
        grouped = (
            subset.groupby(['Term', 'Category'])
            .size()
            .reset_index(name='count')
            .sort_values(['Term', 'count'], ascending=[True, False])
            .drop_duplicates(subset='Term', keep='first')
        )
        dominant_category_by_term = dict(zip(grouped['Term'], grouped['Category']))

    return [
        {
            "term": str(term),
            "count": int(n),
            "category": dominant_category_by_term.get(str(term), "Uncategorized"),
        }
        for term, n in term_counts.items()
    ]


def _column_distribution(df):
    """Distribution of matches across the metadata columns that were searched."""
    column_key = 'Column' if 'Column' in df.columns else ('column' if 'column' in df.columns else None)
    if column_key is None or df[column_key].dropna().empty:
        return []
    counts = df[column_key].fillna('Unknown Column').astype(str).value_counts()
    return [{"column": str(col), "count": int(n)} for col, n in counts.items()]


def _word_cloud(df, max_words=120):
    """Term frequencies for the D3 word cloud, as ``[{text, value}]``."""
    if 'Term' not in df.columns or df['Term'].dropna().empty:
        return []
    counts = df['Term'].dropna().astype(str).value_counts().head(max_words)
    return [{"text": str(term), "value": int(n)} for term, n in counts.items()]


def build_statistics(df):
    """
    Build the full statistics document for the dashboard.

    Args:
        df (pd.DataFrame | None): Matching results. May be None or empty.

    Returns:
        dict: KPIs and the four chart datasets, plus a shared category color map.
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return _empty_statistics()

    category_distribution = _category_distribution(df)
    top_terms = _top_terms(df)
    column_distribution = _column_distribution(df)

    # Build a shared color map covering every category that appears in any chart.
    category_labels = []
    seen = set()
    for entry in category_distribution:
        label = entry["category"]
        if label not in seen:
            seen.add(label)
            category_labels.append(label)
    for entry in top_terms:
        label = entry["category"]
        if label not in seen:
            seen.add(label)
            category_labels.append(label)

    return {
        "hasData": True,
        "kpis": _compute_kpis(df),
        "categoryDistribution": category_distribution,
        "topTerms": top_terms,
        "columnDistribution": column_distribution,
        "wordCloud": _word_cloud(df),
        "categoryColors": build_category_color_map(category_labels),
    }
