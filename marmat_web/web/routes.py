"""

routes.py

Flask page and JSON-API routes for the MaRMAT web app.

Pages are server-rendered templates forming a guided wizard that mirrors the
original PyQt screen flow:
    index -> upload-metadata -> upload-lexicon -> configure -> run -> statistics
plus standalone Instructions and Settings pages.

The JSON API drives each step (upload + preview, column/category selection,
background matching with polled progress, paginated results, downloads, and the
statistics document for the D3 dashboard).

Author:
    - Aiden deBoer
"""

import io
import tempfile
from pathlib import Path

import pandas as pd
from flask import (
    Blueprint, render_template, request, jsonify, send_file, redirect, url_for, current_app
)
from werkzeug.utils import secure_filename

from core import stats
from web.session_state import get_state


bp = Blueprint("marmat", __name__)

# Project root (two levels up from this file: marmat_web/web/routes.py -> MaRMAT/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEXICONS_DIR = PROJECT_ROOT / "Lexicons"
DEFAULT_LEXICON = PROJECT_ROOT / "src" / "data" / "lexicon-reparative-metadata.csv"

PREVIEW_ROWS = 50


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _save_upload_to_temp(file_storage):
    """Write an uploaded file to a temp path and return it. Caller deletes it."""
    suffix = Path(secure_filename(file_storage.filename or "upload")).suffix
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    import os
    os.close(fd)
    file_storage.save(temp_path)
    return temp_path


def _dataframe_preview(df, rows=PREVIEW_ROWS):
    """Return a JSON-friendly preview {columns, rows} of the first ``rows`` rows."""
    if df is None or df.empty:
        return {"columns": [], "rows": []}
    head = df.head(rows).fillna("")
    return {
        "columns": [str(c) for c in head.columns],
        "rows": head.astype(str).values.tolist(),
    }


def _bundled_lexicons():
    """Discover bundled lexicons: the default plus any CSV in Lexicons/."""
    items = []

    def describe(path, name, lex_id):
        try:
            term_count = max(0, sum(1 for _ in open(path, "r", encoding="latin1")) - 1)
        except Exception:
            term_count = None
        return {"id": lex_id, "name": name, "path": str(path), "termCount": term_count}

    if DEFAULT_LEXICON.exists():
        items.append(describe(DEFAULT_LEXICON, "Reparative Metadata Lexicon (default)", "default"))

    if LEXICONS_DIR.exists():
        for csv_path in sorted(LEXICONS_DIR.glob("*.csv")):
            # Build a friendly display name from the filename.
            pretty = csv_path.stem.replace("_", " ").replace("-", " ").strip().title()
            items.append(describe(csv_path, pretty, csv_path.name))

    return items


def _resolve_bundled_path(lex_id):
    """Map a bundled-lexicon id back to a filesystem path."""
    if lex_id == "default":
        return DEFAULT_LEXICON if DEFAULT_LEXICON.exists() else None
    candidate = (LEXICONS_DIR / lex_id).resolve()
    # Guard against path traversal: must stay within Lexicons/.
    if LEXICONS_DIR.resolve() in candidate.parents and candidate.exists():
        return candidate
    return None


def _auto_select_collection_title(columns):
    """Port of auto_select_collection_title_column: prefer 'title', else contains 'title'."""
    for name in columns:
        if str(name).strip().lower() == "title":
            return name
    for name in columns:
        if "title" in str(name).strip().lower():
            return name
    return columns[0] if columns else None


# --------------------------------------------------------------------------- #
#  Page routes                                                                 #
# --------------------------------------------------------------------------- #

@bp.route("/")
def index():
    return render_template("index.html", step="home")


@bp.route("/upload-metadata")
def upload_metadata_page():
    s = get_state()
    return render_template("upload_metadata.html", step="metadata",
                           metadata_filename=s.metadata_filename)


@bp.route("/upload-lexicon")
def upload_lexicon_page():
    s = get_state()
    if not s.metadata_loaded:
        return redirect(url_for("marmat.upload_metadata_page"))
    return render_template("upload_lexicon.html", step="lexicon",
                           lexicon_name=s.lexicon_name)


@bp.route("/configure")
def configure_page():
    s = get_state()
    if not s.metadata_loaded:
        return redirect(url_for("marmat.upload_metadata_page"))
    if not s.lexicon_loaded:
        return redirect(url_for("marmat.upload_lexicon_page"))
    return render_template("configure.html", step="configure", is_ead=s.metadata_is_ead)


@bp.route("/run")
def run_page():
    s = get_state()
    if not s.metadata_loaded or not s.lexicon_loaded:
        return redirect(url_for("marmat.upload_metadata_page"))
    return render_template("run.html", step="run",
                           default_results_path=s.settings.get("default_results_path"))


@bp.route("/statistics")
def statistics_page():
    return render_template("statistics.html", step="statistics")


@bp.route("/instructions")
def instructions_page():
    return render_template("instructions.html", step="instructions")


@bp.route("/settings")
def settings_page():
    s = get_state()
    return render_template("settings.html", step="settings", settings=s.settings.values)


# --------------------------------------------------------------------------- #
#  Metadata API                                                                #
# --------------------------------------------------------------------------- #

@bp.route("/api/metadata", methods=["POST"])
def api_upload_metadata():
    s = get_state()
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"ok": False, "error": "No file provided."}), 400

    delimiter = request.form.get("delimiter", ",")
    delimiter = {"\\t": "\t", "tab": "\t"}.get(delimiter, delimiter)

    temp_path = _save_upload_to_temp(file)
    try:
        ok = s.core.load_metadata(temp_path, delimiter=delimiter)
    finally:
        try:
            Path(temp_path).unlink()
        except Exception:
            pass

    if not ok or s.core.metadata_df is None:
        return jsonify({"ok": False, "error": "Could not read the metadata file."}), 400

    s.metadata_loaded = True
    s.metadata_filename = secure_filename(file.filename)
    s.metadata_is_ead = s.core.is_ead()

    columns = s.core.get_selecteable_columns()
    return jsonify({
        "ok": True,
        "filename": s.metadata_filename,
        "columns": columns,
        "rowCount": int(len(s.core.metadata_df)),
        "isEad": s.metadata_is_ead,
        "preview": _dataframe_preview(s.core.metadata_df),
    })


# --------------------------------------------------------------------------- #
#  Lexicon API                                                                 #
# --------------------------------------------------------------------------- #

@bp.route("/api/lexicons/bundled", methods=["GET"])
def api_bundled_lexicons():
    return jsonify({"lexicons": _bundled_lexicons()})


def _lexicon_response(s):
    return jsonify({
        "ok": True,
        "name": s.lexicon_name,
        "categories": s.core.get_selecteable_categories(),
        "termCount": int(len(s.core.lexicon_df)) if s.core.lexicon_df is not None else 0,
        "preview": _dataframe_preview(s.core.lexicon_df),
    })


@bp.route("/api/lexicon", methods=["POST"])
def api_upload_lexicon():
    s = get_state()
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"ok": False, "error": "No file provided."}), 400

    temp_path = _save_upload_to_temp(file)
    try:
        ok = s.core.load_lexicon(temp_path)
    finally:
        try:
            Path(temp_path).unlink()
        except Exception:
            pass

    if not ok or s.core.lexicon_df is None or "category" not in s.core.lexicon_df.columns:
        return jsonify({"ok": False, "error": "Lexicon must be a CSV with 'term' and 'category' columns."}), 400

    s.lexicon_loaded = True
    s.lexicon_name = secure_filename(file.filename)
    return _lexicon_response(s)


@bp.route("/api/lexicon/bundled", methods=["POST"])
def api_select_bundled_lexicon():
    s = get_state()
    data = request.get_json(silent=True) or {}
    lex_id = data.get("id")
    path = _resolve_bundled_path(lex_id)
    if path is None:
        return jsonify({"ok": False, "error": "Unknown lexicon."}), 404

    if not s.core.load_lexicon(str(path)):
        return jsonify({"ok": False, "error": "Could not load the selected lexicon."}), 400

    s.lexicon_loaded = True
    s.lexicon_name = path.name
    return _lexicon_response(s)


# --------------------------------------------------------------------------- #
#  Configure API                                                               #
# --------------------------------------------------------------------------- #

@bp.route("/api/columns", methods=["GET"])
def api_columns():
    s = get_state()
    columns = s.core.get_selecteable_columns()
    return jsonify({
        "columns": columns,
        "isEad": s.metadata_is_ead,
        "identifierSuggestion": "identifier" if s.metadata_is_ead and "identifier" in columns else (columns[0] if columns else None),
        "collectionTitleSuggestion": _auto_select_collection_title(columns),
    })


@bp.route("/api/categories", methods=["GET"])
def api_categories():
    s = get_state()
    return jsonify({"categories": s.core.get_selecteable_categories()})


@bp.route("/api/configure", methods=["POST"])
def api_configure():
    s = get_state()
    data = request.get_json(silent=True) or {}

    identifier_column = data.get("identifierColumn")
    selected_columns = data.get("selectedColumns") or []
    selected_categories = data.get("selectedCategories") or []
    include_collection_title = bool(data.get("includeCollectionTitle"))
    collection_title_column = data.get("collectionTitleColumn")

    if not identifier_column:
        return jsonify({"ok": False, "error": "Please choose an ID column."}), 400
    if not selected_columns:
        return jsonify({"ok": False, "error": "Select at least one metadata field to analyze."}), 400
    if not selected_categories:
        return jsonify({"ok": False, "error": "Select at least one lexicon category."}), 400

    s.core.select_identifier_column(identifier_column)
    s.core.select_columns(selected_columns)
    s.core.select_categories(selected_categories)
    s.core.set_include_collection_title(include_collection_title)
    if include_collection_title and collection_title_column:
        s.core.select_collection_title_column(collection_title_column)

    return jsonify({"ok": True})


# --------------------------------------------------------------------------- #
#  Matching API                                                                #
# --------------------------------------------------------------------------- #

@bp.route("/api/match", methods=["POST"])
def api_match():
    s = get_state()
    if s.is_job_running():
        return jsonify({"ok": False, "error": "A matching job is already running."}), 409

    if s.core.metadata_df is None or s.core.filtered_lexicon is None or s.core.filtered_lexicon.empty:
        return jsonify({"ok": False, "error": "Metadata and lexicon categories must be configured first."}), 400

    def run_job():
        try:
            s.set_progress(0, "Matching in progress...")
            s.core.perform_matching(
                output_file=None,
                progress_callback=lambda pct: s.set_progress(pct, "Matching in progress..."),
            )
            count = 0 if s.core.matches_df is None else int(len(s.core.matches_df))
            s.finish_job(f"Analysis complete — {count} flagged instance(s) found.")
        except Exception as e:
            s.fail_job(f"Matching failed: {e}")

    started = s.start_job(run_job)
    if not started:
        return jsonify({"ok": False, "error": "A matching job is already running."}), 409
    return jsonify({"ok": True, "status": "running"})


@bp.route("/api/match/progress", methods=["GET"])
def api_match_progress():
    s = get_state()
    progress = s.get_progress()
    if progress["status"] == "done":
        progress["resultCount"] = 0 if s.core.matches_df is None else int(len(s.core.matches_df))
    return jsonify(progress)


@bp.route("/api/results", methods=["GET"])
def api_results():
    s = get_state()
    df = s.core.matches_df
    if df is None or df.empty:
        return jsonify({"columns": [], "rows": [], "page": 1, "pageSize": 0, "total": 0})

    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(500, max(1, int(request.args.get("pageSize", 100))))
    except ValueError:
        page, page_size = 1, 100

    total = int(len(df))
    start = (page - 1) * page_size
    end = start + page_size
    slice_df = df.iloc[start:end].fillna("")

    return jsonify({
        "columns": [str(c) for c in df.columns],
        "rows": slice_df.astype(str).values.tolist(),
        "page": page,
        "pageSize": page_size,
        "total": total,
    })


@bp.route("/api/results/download", methods=["GET"])
def api_results_download():
    s = get_state()
    df = s.core.matches_df
    if df is None or df.empty:
        return jsonify({"ok": False, "error": "No results to download."}), 404

    fmt = request.args.get("format", "csv").lower()
    if fmt == "tsv":
        sep, mimetype, filename = "\t", "text/tab-separated-values", "marmat_results.tsv"
    else:
        sep, mimetype, filename = ",", "text/csv", "marmat_results.csv"

    buffer = io.StringIO()
    df.to_csv(buffer, sep=sep, index=False)
    data = io.BytesIO(buffer.getvalue().encode("utf-8-sig"))
    data.seek(0)
    return send_file(data, mimetype=mimetype, as_attachment=True, download_name=filename)


# --------------------------------------------------------------------------- #
#  Statistics API                                                              #
# --------------------------------------------------------------------------- #

@bp.route("/api/statistics", methods=["GET"])
def api_statistics():
    s = get_state()
    return jsonify(stats.build_statistics(s.core.matches_df))


# --------------------------------------------------------------------------- #
#  Settings API                                                                #
# --------------------------------------------------------------------------- #

@bp.route("/api/settings", methods=["GET"])
def api_get_settings():
    s = get_state()
    return jsonify(s.settings.values)


@bp.route("/api/settings", methods=["POST"])
def api_update_settings():
    s = get_state()
    data = request.get_json(silent=True) or {}
    updated = s.settings.update(data)
    return jsonify({"ok": True, "settings": updated})
