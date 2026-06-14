"""

app.py

Launcher for the MaRMAT web application. Replaces the PyQt ``src/main.py``
entry point.

Starts the Flask development server bound to localhost and opens the user's
default browser at the app once the server is up. Designed for a local,
single-user deployment.

Multiprocessing notes (important):
    - The matching engine uses a ``ProcessPoolExecutor``. On Windows/macOS the
      "spawn" start method re-imports the main module, so the server must be
      launched under an ``if __name__ == "__main__"`` guard with
      ``multiprocessing.freeze_support()`` called first.
    - Flask's auto-reloader is disabled (``use_reloader=False``) because it
      conflicts with the process pool (it would re-spawn the server/pool).
    - ``threaded=True`` so progress-poll requests are served while a match runs.

Author:
    - Aiden deBoer
"""

import multiprocessing
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

# Ensure this directory (marmat_web/) is on sys.path so `core` and `web`
# import as top-level packages regardless of how the script is invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from server import create_app  # noqa: E402


HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def _find_open_port(host, start_port, attempts=20):
    """Return the first open port at or after ``start_port``."""
    for offset in range(attempts):
        port = start_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) != 0:  # nonzero => nothing listening
                return port
    return start_port


def _open_browser(url, delay=1.0):
    """Open the default browser at ``url`` after a short delay."""
    threading.Timer(delay, lambda: webbrowser.open(url)).start()


def main():
    port = _find_open_port(HOST, int(os.environ.get("MARMAT_PORT", DEFAULT_PORT)))
    url = f"http://{HOST}:{port}"

    app = create_app()

    # Only the parent process should open the browser.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print(f"MaRMAT is running at {url}")
        _open_browser(url)

    app.run(host=HOST, port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
