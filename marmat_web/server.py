"""

server.py

Flask application factory for MaRMAT. Kept separate from the launcher so it can
also be imported by a WSGI server if ever needed.

Run with the ``marmat_web`` directory on ``sys.path`` (the launcher handles this)
so ``core`` and ``web`` import as top-level packages.

Author:
    - Aiden deBoer
"""

from flask import Flask


def create_app():
    """Build and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Cap uploads at a generous-but-bounded size for a local tool (256 MB).
    app.config["MAX_CONTENT_LENGTH"] = 256 * 1024 * 1024

    # Initialise the single-session state up front so the default lexicon loads
    # on boot (mirrors the desktop app constructing its model at startup).
    from web.session_state import init_state
    init_state()

    from web.routes import bp
    app.register_blueprint(bp)

    return app
