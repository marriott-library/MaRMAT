#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

require_file "$MARMAT_PYTHON_BIN" "$MARMAT_SRC_PATH/main.py"

cd "$MARMAT_SRC_PATH"
exec "$MARMAT_PYTHON_BIN" main.py
