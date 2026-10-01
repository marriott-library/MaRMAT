#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script builds the macOS app bundle and must run on macOS." >&2
  exit 1
fi

require_file "$MARMAT_PYTHON_BIN" "$MARMAT_PYINSTALLER_BIN" "$MARMAT_SRC_PATH/main.py"
require_dir "$MARMAT_SRC_PATH/data"

rm -rf "$MARMAT_BUILD_PATH"
mkdir -p "$MARMAT_BUILD_PATH" "$MARMAT_RELEASE_PATH"

"$MARMAT_PYTHON_BIN" -m compileall \
  "$MARMAT_SRC_PATH/main.py" \
  "$MARMAT_SRC_PATH/controllers" \
  "$MARMAT_SRC_PATH/models" \
  "$MARMAT_SRC_PATH/views"

cd "$MARMAT_SRC_PATH"
"$MARMAT_PYINSTALLER_BIN" \
  --noconfirm \
  --clean \
  --onedir \
  --windowed \
  --name "$MARMAT_APP_NAME" \
  --distpath "$MARMAT_BUILD_PATH/dist" \
  --workpath "$MARMAT_BUILD_PATH/work" \
  --specpath "$MARMAT_BUILD_PATH/spec" \
  --add-data "$MARMAT_SRC_PATH/data:data" \
  main.py

require_dir "$MARMAT_APP_BUNDLE_PATH"

rm -f "$MARMAT_RELEASE_ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$MARMAT_APP_BUNDLE_PATH" "$MARMAT_RELEASE_ZIP_PATH"

echo "Built app bundle: $MARMAT_APP_BUNDLE_PATH"
echo "Built release zip: $MARMAT_RELEASE_ZIP_PATH"
