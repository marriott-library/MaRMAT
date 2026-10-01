#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

require_dir "$MARMAT_SRC_PATH"
require_file "$MARMAT_BUILD_REQUIREMENTS_PATH" "$MARMAT_SRC_PATH/main.py"

if [ ! -d "$MARMAT_VENV_PATH" ]; then
  "$MARMAT_PYTHON" -m venv "$MARMAT_VENV_PATH"
fi

"$MARMAT_PYTHON_BIN" -m pip install --upgrade pip
"$MARMAT_PYTHON_BIN" -m pip install -r "$MARMAT_BUILD_REQUIREMENTS_PATH"
"$MARMAT_PYTHON_BIN" -m compileall \
  "$MARMAT_SRC_PATH/main.py" \
  "$MARMAT_SRC_PATH/controllers" \
  "$MARMAT_SRC_PATH/models" \
  "$MARMAT_SRC_PATH/views"

echo "MaRMAT developer environment is ready."
