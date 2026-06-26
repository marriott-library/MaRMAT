#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

require_file "$MARMAT_APP_BUNDLE_PATH/Contents/MacOS/$MARMAT_APP_NAME"

QT_QPA_PLATFORM="$MARMAT_QT_PLATFORM" "$MARMAT_PYTHON_BIN" - "$MARMAT_APP_BUNDLE_PATH/Contents/MacOS/$MARMAT_APP_NAME" "$MARMAT_SMOKE_TIMEOUT_SECONDS" <<'PY'
import os
import subprocess
import sys

app_path = sys.argv[1]
timeout_seconds = int(sys.argv[2])

try:
    result = subprocess.run(
        [app_path],
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
except subprocess.TimeoutExpired:
    print(f"Packaged app started and stayed running for {timeout_seconds} seconds.")
    raise SystemExit(0)

if result.returncode == 0:
    print("Packaged app exited cleanly before the smoke-test timeout.")
    raise SystemExit(0)

if result.stdout:
    print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
print(f"Packaged app smoke test failed with exit code {result.returncode}.", file=sys.stderr)
raise SystemExit(result.returncode)
PY
