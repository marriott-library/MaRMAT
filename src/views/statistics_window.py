"""

statistics_window.py

Statistics dashboard window for the MaRMAT application.
This module provides KPIs and visualizations for MaRMAT output results.

Author:
    - Aiden deBoer

Date: 2026-03-22

"""

from PyQt6.QtCore import Qt, QEvent
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
    QFileDialog,
)

from views.base_widget import BaseWidget

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.patches import Patch
    from matplotlib import cm as mpl_cm
    from matplotlib import style as mpl_style
    import numpy as np
    HAS_MATPLOTLIB = True
except Exception:
    FigureCanvas = None
    Figure = None
    Patch = None
    mpl_cm = None
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
        self.chart_frames = {}
        self.chart_positions = {}
        self.chart_messages = {}
        self.chart_export_buttons = {}
        self.no_data_label = None
        self.scroll_area = None
        self.charts_widget = None
        self.charts_layout = None
        self.back_to_grid_button = None
        self.maximized_chart_key = None
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

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)

        self.kpi_container = self._build_kpi_section()
        content_layout.addWidget(self.kpi_container)

        self.charts_widget = QWidget()
        self.charts_layout = QGridLayout()
        self.charts_layout.setSpacing(12)

        chart_specs = [
            ("category_distribution", "Category Distribution (Horizontal Bar Chart)"),
            ("top_terms", "Top 10 Most Frequent Terms (Vertical Bar Chart)"),
            ("category_pie", "Category Distribution (Pie Chart)"),
            ("word_cloud", "Word Cloud (Term Frequency)"),
        ]

        for idx, (chart_key, chart_title) in enumerate(chart_specs):
            chart_frame = self._build_chart_frame(chart_key, chart_title)
            row = idx // 2
            col = idx % 2
            self.charts_layout.addWidget(chart_frame, row, col)
            self.chart_frames[chart_key] = chart_frame
            self.chart_positions[chart_key] = (row, col)

        self.charts_widget.setLayout(self.charts_layout)
        content_layout.addWidget(self.charts_widget)

        self.back_to_grid_button = QPushButton("Back to 4 Graph View")
        self.back_to_grid_button.clicked.connect(self.restore_chart_grid)
        self.back_to_grid_button.setVisible(False)
        content_layout.addWidget(self.back_to_grid_button)

        content_widget.setLayout(content_layout)
        self.scroll_area.setWidget(content_widget)
        main_layout.addWidget(self.scroll_area)

        # Enable wheel scrolling regardless of cursor location in the dashboard.
        self.installEventFilter(self)
        self._install_scroll_event_filter(content_widget)
        self._install_scroll_event_filter(self.kpi_container)
        self._install_scroll_event_filter(self.charts_widget)

        button_layout = QHBoxLayout()
        self.export_all_button = QPushButton("Export All Graphs")
        self.export_all_button.clicked.connect(self.export_all_charts)
        self.export_all_button.setEnabled(HAS_MATPLOTLIB)
        button_layout.addWidget(self.export_all_button)

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
            canvas.mpl_connect('button_press_event', lambda _, key=chart_key: self.maximize_chart(key))
            layout.addWidget(canvas)
        else:
            canvas = None

        message_label = QLabel("")
        message_label.setWordWrap(True)
        if not HAS_MATPLOTLIB:
            message_label.setText("Install matplotlib to render this visualization.")
        layout.addWidget(message_label)
        self.chart_messages[chart_key] = message_label

        export_button = QPushButton("Export Graph")
        export_button.clicked.connect(lambda _, key=chart_key: self.export_chart(key))
        export_button.setEnabled(HAS_MATPLOTLIB)
        layout.addWidget(export_button)
        self.chart_export_buttons[chart_key] = export_button

        frame.setLayout(layout)
        self._install_scroll_event_filter(frame)
        if HAS_MATPLOTLIB and chart_key in self.chart_canvases:
            self._install_scroll_event_filter(self.chart_canvases[chart_key])
        return frame

    def _install_scroll_event_filter(self, widget):
        """Install this widget as an event filter recursively for wheel scrolling."""
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, watched, event):
        """Route wheel events to the scroll area so scrolling works anywhere."""
        if event.type() == QEvent.Type.Wheel and self.scroll_area is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                return False

            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() - event.angleDelta().y())
            return True

        return super().eventFilter(watched, event)

    def export_chart(self, chart_key: str):
        """Export a rendered chart to an image file."""
        canvas = self.chart_canvases.get(chart_key)
        if canvas is None:
            return

        default_name = f"marmat_{chart_key}.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Graph",
            default_name,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            self.show_alert("Export Complete", f"Graph exported to: {file_path}")
        except Exception as error:
            self.show_alert("Export Failed", f"Could not export graph: {error}")

    def export_all_charts(self):
        """Export all rendered charts to a selected folder as PNG files."""
        if not HAS_MATPLOTLIB or not self.chart_canvases:
            return

        target_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Export All Graphs", "")
        if not target_folder:
            return

        try:
            for chart_key, canvas in self.chart_canvases.items():
                output_path = f"{target_folder}/marmat_{chart_key}.png"
                canvas.figure.savefig(output_path, dpi=300, bbox_inches='tight')
            self.show_alert("Export Complete", f"All graphs exported to: {target_folder}")
        except Exception as error:
            self.show_alert("Export Failed", f"Could not export all graphs: {error}")

    def maximize_chart(self, chart_key: str):
        """Maximize a chart into a focused single-chart view."""
        if self.maximized_chart_key == chart_key:
            return

        self.maximized_chart_key = chart_key

        for key, frame in self.chart_frames.items():
            if key != chart_key:
                frame.setVisible(False)

        selected_frame = self.chart_frames.get(chart_key)
        if selected_frame is None:
            return

        self.charts_layout.removeWidget(selected_frame)
        self.charts_layout.addWidget(selected_frame, 0, 0, 2, 2)
        selected_frame.setVisible(True)
        self.back_to_grid_button.setVisible(True)

    def restore_chart_grid(self):
        """Restore the default 4-chart grid view."""
        for key, frame in self.chart_frames.items():
            self.charts_layout.removeWidget(frame)
            row, col = self.chart_positions[key]
            self.charts_layout.addWidget(frame, row, col)
            frame.setVisible(True)

        self.maximized_chart_key = None
        self.back_to_grid_button.setVisible(False)

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

    def _build_category_color_map(self, categories):
        """Build a deterministic category -> color mapping for charts/legends."""
        if not categories:
            return {}

        color_map = {}
        if mpl_cm is not None:
            try:
                cmap = mpl_cm.get_cmap('tab20')
                denominator = max(len(categories) - 1, 1)
                for idx, category in enumerate(categories):
                    color_position = idx / denominator if len(categories) > 1 else 0
                    color_map[category] = cmap(color_position)
                return color_map
            except Exception:
                pass

        for idx, category in enumerate(categories):
            color_map[category] = f"C{idx % 10}"
        return color_map

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
        self._plot_category_pie(df)
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
            term_labels = top_terms.index.astype(str).tolist()

            dominant_category_by_term = {}
            if 'Category' in df.columns:
                category_by_term = (
                    df[
                        df['Term'].notna()
                        & df['Term'].astype(str).isin(term_labels)
                    ]
                    .assign(
                        Term=df['Term'].astype(str),
                        Category=df['Category'].fillna('Uncategorized').astype(str),
                    )
                    .groupby(['Term', 'Category'])
                    .size()
                    .reset_index(name='count')
                    .sort_values(['Term', 'count'], ascending=[True, False])
                    .drop_duplicates(subset='Term', keep='first')
                )
                dominant_category_by_term = dict(
                    zip(category_by_term['Term'], category_by_term['Category'])
                )

            bar_categories = [
                dominant_category_by_term.get(term, 'Uncategorized')
                for term in term_labels
            ]
            ordered_categories = list(dict.fromkeys(bar_categories))
            category_colors = self._build_category_color_map(ordered_categories)
            bar_colors = [category_colors[category] for category in bar_categories]

            bars = axis.bar(
                range(len(term_labels)),
                top_terms.values,
                color=bar_colors,
                edgecolor='white',
                linewidth=0.7,
            )
            axis.set_ylabel("Count")
            axis.set_xticks(range(len(term_labels)))
            axis.set_xticklabels(term_labels, rotation=45, ha='right')

            if Patch is not None and ordered_categories:
                legend_handles = [
                    Patch(
                        facecolor=category_colors[category],
                        edgecolor='white',
                        label=category,
                    )
                    for category in ordered_categories
                ]
                axis.legend(
                    handles=legend_handles,
                    title='Category',
                    loc='upper left',
                    bbox_to_anchor=(1.01, 1),
                    fontsize=8,
                    frameon=False,
                )

            self._annotate_vertical_bars(axis, bars)
        else:
            axis.text(0.5, 0.5, "No Term data", ha='center', va='center', transform=axis.transAxes)

        self._style_axis(axis, "Top 10 Most Frequent Terms")
        canvas.draw_idle()

    def _plot_category_pie(self, df):
        canvas = self.chart_canvases.get('category_pie')
        if canvas is None:
            return

        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot(111)

        if 'Category' in df.columns and not df['Category'].dropna().empty:
            category_counts = (
                df['Category']
                .fillna('Uncategorized')
                .astype(str)
                .value_counts()
            )
            categories = category_counts.index.tolist()
            category_colors = self._build_category_color_map(categories)
            pie_colors = [category_colors[category] for category in categories]
            total_count = int(category_counts.sum())

            wedges, _, autotexts = axis.pie(
                category_counts.values,
                labels=None,
                autopct=lambda pct: (
                    f"{pct:.1f}%\n({int(round(pct * total_count / 100.0))})"
                    if pct >= 4
                    else ""
                ),
                startangle=90,
                colors=pie_colors,
                wedgeprops={'linewidth': 0.7, 'edgecolor': 'white'},
                pctdistance=0.75,
            )
            for autotext in autotexts:
                autotext.set_fontsize(8)

            axis.legend(
                wedges,
                categories,
                title='Category',
                loc='center left',
                bbox_to_anchor=(1.02, 0.5),
                fontsize=8,
                frameon=False,
            )
            axis.axis('equal')
        else:
            axis.text(0.5, 0.5, "No Category data", ha='center', va='center', transform=axis.transAxes)

        axis.set_title("Category Distribution", loc='left', fontsize=12, fontweight='bold', pad=10)
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