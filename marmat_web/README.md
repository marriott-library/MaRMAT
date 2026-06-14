# MaRMAT — Web Edition (Flask + D3)

A local, single-user web frontend for the Marriott Reparative Metadata
Assessment Tool, themed to the University of Utah. It replaces the PyQt6
desktop UI while reusing the original matching engine.

## Requirements

Python 3.9+ and the dependencies in the project's top-level `requirements.txt`:

```bash
pip install -r requirements.txt
```

(Flask, pandas, numpy, beautifulsoup4, lxml. The PyQt6/matplotlib/wordcloud
stack is no longer needed by the web app.)

## Running

From the project root:

```bash
python marmat_web/app.py
```

The app starts a local server (default `http://127.0.0.1:5000`, auto-selecting a
free port if 5000 is taken) and opens your default browser. Set `MARMAT_PORT` to
choose a port.

## Workflow

A guided five-step wizard mirrors the original desktop flow:

1. **Metadata** — upload a CSV/TSV or EAD XML file (drag & drop or browse).
2. **Lexicon** — pick a bundled lexicon (from `Lexicons/` + the default) or upload your own `term,category` CSV.
3. **Configure** — choose the ID column, the metadata fields to scan, and the lexicon categories.
4. **Run & Results** — perform matching (live progress), browse paginated results, download CSV/TSV.
5. **Statistics** — an interactive D3 dashboard: 5 KPIs, category bar, top-terms bar, column pie, and a word cloud.

Instructions and Settings (default folder preferences) are available from the header.

## Architecture

```
marmat_web/
  app.py            Launcher (server + browser auto-open; multiprocessing-safe)
  server.py         Flask application factory (create_app)
  core/
    marmat_core.py  Framework-agnostic matching engine (decoupled from PyQt/Qt signals)
    stats.py        Pandas aggregations -> JSON for the D3 dashboard
    settings_store.py  JSON-file user preferences (replaces QSettings)
  web/
    routes.py       Page + JSON-API routes
    session_state.py  Single-session in-memory state + progress store
  templates/        Jinja templates (base + one per wizard step)
  static/
    css/marmat.css  University of Utah themed styles (hand-rolled)
    js/             app helpers, D3 chart modules, vendored D3 + d3-cloud
```

Matching runs in a background thread; the browser polls `/api/match/progress`.
The heavy work uses `ProcessPoolExecutor`, which is why `app.py` guards startup
under `if __name__ == "__main__"` with `multiprocessing.freeze_support()` and
disables the Flask reloader.

> The original PyQt6 desktop app remains under `src/` and is unaffected.
