"""

statistics_window.py

Statistics dashboard window for the MaRMAT application.
This module provides KPIs and visualizations for MaRMAT output results.

Author:
    - Aiden deBoer

Date: 2026-03-22

"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGridLayout,
    QScrollArea,
    QFrame,
)

from views.base_widget import BaseWidget

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import style as mpl_style
    import numpy as np
    HAS_MATPLOTLIB = True
except Exception:
    FigureCanvas = None
    Figure = None
    mpl_style = None
    np = None
    HAS_MATPLOTLIB = False

try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except Exception:
    WordCloud = None
    HAS_WORDCLOUD = False


class StatisticsWindow(BaseWidget):
    """Statistics dashboard for MaRMAT output."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.kpi_labels = {}
        self.chart_canvases = {}
        self.chart_messages = {}
        self.no_data_label = None
        self.init_ui()

        if HAS_MATPLOTLIB:
            self._apply_modern_chart_style()

    def init_ui(self):
        self.setWindowTitle("Statistics - MaRMAT")
        self.resize(1280, 720)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        title_label = QLabel("<b>Results Statistics Dashboard</b>")
        title_label.setFont(QFont("Calibri", 36))

        subtitle_label = QLabel(
            "Review key performance indicators and visual summaries of the current MaRMAT results."
        )
        subtitle_label.setWordWrap(True)

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        self.no_data_label = QLabel("")
        self.no_data_label.setWordWrap(True)
        self.no_data_label.setStyleSheet("color: #890000;")
        main_layout.addWidget(self.no_data_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)

        self.kpi_container = self._build_kpi_section()
        content_layout.addWidget(self.kpi_container)

        charts_widget = QWidget()
        charts_layout = QGridLayout()
        charts_layout.setSpacing(12)

        chart_specs = [
            ("category_distribution", "Category Distribution (Horizontal Bar Chart)"),
            ("top_terms", "Top 10 Most Frequent Terms (Vertical Bar Chart)"),
            ("top_terms_by_category", "Top Terms by Category (Stacked Bar Chart)"),
            ("word_cloud", "Word Cloud (Term Frequency)"),
        ]

        for idx, (chart_key, chart_title) in enumerate(chart_specs):
            chart_frame = self._build_chart_frame(chart_key, chart_title)
            row = idx // 2
            col = idx % 2
            charts_layout.addWidget(chart_frame, row, col)

        charts_widget.setLayout(charts_layout)
        content_layout.addWidget(charts_widget)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back to Results")
        self.back_button.clicked.connect(self.controller.show_perform_matching_screen)
        button_layout.addWidget(self.back_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _build_kpi_section(self):
        kpi_frame = QFrame()
        kpi_frame.setFrameShape(QFrame.Shape.StyledPanel)

        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(10)

        kpi_titles = [
            "Total Flagged Instances",
            "Total Unique Collections Affected",
            "Total Unique Terms Found",
            "Most Frequent Category",
            "Most Frequent Term",
        ]

        for idx, title in enumerate(kpi_titles):
            row = idx // 3
            col = idx % 3

            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card_layout = QVBoxLayout()

            label_title = QLabel(f"<b>{title}</b>")
            label_title.setWordWrap(True)

            label_value = QLabel("-")
            label_value.setFont(QFont("Calibri", 28))
            label_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(label_title)
            card_layout.addWidget(label_value)
            card.setLayout(card_layout)

            self.kpi_labels[title] = label_value
            kpi_layout.addWidget(card, row, col)

        kpi_frame.setLayout(kpi_layout)
        return kpi_frame

    def _build_chart_frame(self, chart_key: str, title: str):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if HAS_MATPLOTLIB:
            figure = Figure(figsize=(6.2, 3.8), tight_layout=True)
            canvas = FigureCanvas(figure)
            self.chart_canvases[chart_key] = canvas
            layout.addWidget(canvas)
        else:
            canvas = None

        message_label = QLabel("")
        message_label.setWordWrap(True)
        if not HAS_MATPLOTLIB:
            message_label.setText("Install matplotlib to render this visualization.")
        layout.addWidget(message_label)
        self.chart_messages[chart_key] = message_label

        frame.setLayout(layout)
        return frame

    def _apply_modern_chart_style(self):
        """Apply a cohesive, modern plotting style across all dashboard charts."""
        try:
            mpl_style.use('seaborn-v0_8-whitegrid')
        except Exception:
            pass

    def _style_axis(self, axis, title: str):
        """Apply consistent modern axis formatting."""
        axis.set_title(title, loc='left', fontsize=12, fontweight='bold', pad=10)
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.grid(axis='x', linestyle='--', alpha=0.25)
        axis.grid(axis='y', linestyle='-', alpha=0.12)
        axis.tick_params(axis='x', labelsize=9)
        axis.tick_params(axis='y', labelsize=9)

    def _annotate_horizontal_bars(self, axis, values):
        for idx, value in enumerate(values):
            axis.text(value, idx, f" {int(value)}", va='center', fontsize=8)

    def _annotate_vertical_bars(self, axis, bars):
        for bar in bars:
            height = bar.get_height()
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{int(height)}",
                ha='center',
                va='bottom',
                fontsize=8,
            )

    def load_statistics_data(self):
        """Load and render KPIs/charts from current matching results."""
        df = self.controller.get_matching_results()

        if df is None or df.empty:
            self.no_data_label.setText(
                "No results are available yet. Run Perform Analysis first, then open Statistics."
            )
            self._reset_kpis()
            self._clear_charts()
            return

        self.no_data_label.setText("")
        self._update_kpis(df)
        self._update_charts(df)

    def _reset_kpis(self):
        for label in self.kpi_labels.values():
            label.setText("-")

    def _update_kpis(self, df):
        total_flagged_instances = int(len(df))

        if 'Collection Title' in df.columns and df['Collection Title'].notna().any():
            total_unique_collections = int(df['Collection Title'].nunique())
        else:
            total_unique_collections = int(df['Identifier'].nunique()) if 'Identifier' in df.columns else 0

        total_unique_terms = int(df['Term'].nunique()) if 'Term' in df.columns else 0
        most_frequent_category = (
            df['Category'].value_counts().idxmax()
            if 'Category' in df.columns and not df['Category'].dropna().empty
            else "N/A"
        )
        most_frequent_term = (
            df['Term'].value_counts().idxmax()
            if 'Term' in df.columns and not df['Term'].dropna().empty
            else "N/A"
        )

        self.kpi_labels["Total Flagged Instances"].setText(f"{total_flagged_instances:,}")
        self.kpi_labels["Total Unique Collections Affected"].setText(f"{total_unique_collections:,}")
        self.kpi_labels["Total Unique Terms Found"].setText(f"{total_unique_terms:,}")
        self.kpi_labels["Most Frequent Category"].setText(str(most_frequent_category))
        self.kpi_labels["Most Frequent Term"].setText(str(most_frequent_term))

    def _clear_charts(self):
        if not HAS_MATPLOTLIB:
            return

        for canvas in self.chart_canvases.values():
            figure = canvas.figure
            figure.clear()
            canvas.draw_idle()

    def _update_charts(self, df):
        if not HAS_MATPLOTLIB:
            return

        self._plot_category_distribution(df)
        self._plot_top_terms(df)
        self._plot_top_terms_by_category(df)
        self._plot_word_cloud(df)

    def _plot_category_distribution(self, df):
        canvas = self.chart_canvases.get('category_distribution')
        if canvas is None:
            return

        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot(111)

        if 'Category' in df.columns and not df['Category'].dropna().empty:
            category_counts = df['Category'].value_counts().sort_values(ascending=True)
            bars = axis.barh(
                category_counts.index.astype(str),
                category_counts.values,
                color='tab:blue',
                edgecolor='white',
                linewidth=0.7,
            )
            axis.set_xlabel("Count")
            axis.set_ylabel("Category")
            self._annotate_horizontal_bars(axis, category_counts.values)
        else:
            axis.text(0.5, 0.5, "No Category data", ha='center', va='center', transform=axis.transAxes)

        self._style_axis(axis, "Category Distribution")
        canvas.draw_idle()

    def _plot_top_terms(self, df):
        canvas = self.chart_canvases.get('top_terms')
        if canvas is None:
            return

        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot(111)

        if 'Term' in df.columns and not df['Term'].dropna().empty:
            top_terms = df['Term'].value_counts().head(10)
            colors = None
            if np is not None:
                colors = [
                    f"C{int(i % 10)}"
                    for i in np.linspace(0, 9, len(top_terms.index))
                ]

            bars = axis.bar(
                top_terms.index.astype(str),
                top_terms.values,
                color=colors,
                edgecolor='white',
                linewidth=0.7,
            )
            axis.set_ylabel("Count")
            axis.set_xticks(range(len(top_terms.index)))
            axis.set_xticklabels(top_terms.index.astype(str), rotation=45, ha='right')
            self._annotate_vertical_bars(axis, bars)
        else:
            axis.text(0.5, 0.5, "No Term data", ha='center', va='center', transform=axis.transAxes)

        self._style_axis(axis, "Top 10 Most Frequent Terms")
        canvas.draw_idle()

    def _plot_top_terms_by_category(self, df):
        canvas = self.chart_canvases.get('top_terms_by_category')
        if canvas is None:
            return

        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot(111)

        if (
            'Category' in df.columns
            and 'Term' in df.columns
            and not df['Category'].dropna().empty
            and not df['Term'].dropna().empty
        ):
            top_categories = df['Category'].value_counts().head(5).index
            subset = df[df['Category'].isin(top_categories)]

            grouped = (
                subset.groupby(['Category', 'Term'])
                .size()
                .reset_index(name='count')
                .sort_values(['Category', 'count'], ascending=[True, False])
            )

            top_terms_per_category = (
                grouped.groupby('Category', group_keys=False)
                .head(3)
            )

            pivot_df = top_terms_per_category.pivot_table(
                index='Category', columns='Term', values='count', fill_value=0
            )

            pivot_df.plot(kind='bar', stacked=True, ax=axis, colormap='tab20c', width=0.8)
            axis.set_xlabel("Category")
            axis.set_ylabel("Count")
            axis.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8, frameon=False, title='Term')
        else:
            axis.text(0.5, 0.5, "No Category/Term data", ha='center', va='center', transform=axis.transAxes)

        self._style_axis(axis, "Top Terms by Category")
        canvas.draw_idle()

    def _plot_word_cloud(self, df):
        canvas = self.chart_canvases.get('word_cloud')
        message_label = self.chart_messages.get('word_cloud')

        if canvas is None:
            return

        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot(111)

        if 'Term' not in df.columns or df['Term'].dropna().empty:
            axis.text(0.5, 0.5, "No Term data", ha='center', va='center', transform=axis.transAxes)
            axis.set_title("Word Cloud")
            canvas.draw_idle()
            return

        if not HAS_WORDCLOUD:
            axis.text(
                0.5,
                0.5,
                "Install wordcloud to render\nthis visualization.",
                ha='center',
                va='center',
                transform=axis.transAxes,
            )
            if message_label is not None:
                message_label.setText("Optional dependency missing: wordcloud")
            axis.set_title("Word Cloud")
            canvas.draw_idle()
            return

        term_text = " ".join(df['Term'].dropna().astype(str).tolist())
        if not term_text.strip():
            axis.text(0.5, 0.5, "No Term data", ha='center', va='center', transform=axis.transAxes)
            axis.set_title("Word Cloud")
            canvas.draw_idle()
            return

        word_cloud = WordCloud(
            width=1200,
            height=700,
            background_color='white',
            colormap='viridis',
            collocations=False,
            max_words=120,
        ).generate(term_text)
        axis.imshow(word_cloud, interpolation='bilinear')
        axis.axis('off')
        axis.set_title("Word Cloud", loc='left', fontsize=12, fontweight='bold', pad=10)
        if message_label is not None:
            message_label.setText("")
        canvas.draw_idle()