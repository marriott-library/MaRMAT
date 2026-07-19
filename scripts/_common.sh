#!/usr/bin/env bash
set -euo pipefail

MARMAT_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARMAT_ENV_FILE="$MARMAT_PROJECT_ROOT/.env.local"

if [ ! -f "$MARMAT_ENV_FILE" ]; then
  echo "Missing .env.local. Copy .env.local.example to .env.local before running this script." >&2
  exit 1
fi

set -a
source "$MARMAT_ENV_FILE"
set +a

require_env() {
  for name in "$@"; do
    if [ "${!name+x}" != "x" ]; then
      echo "Missing required setting: $name" >&2
      exit 1
    fi

    if [ -z "${!name}" ]; then
      echo "Empty required setting: $name" >&2
      exit 1
    fi
  done
}

project_path() {
  case "$1" in
    /*)
      printf '%s\n' "$1"
      ;;
    *)
      printf '%s/%s\n' "$MARMAT_PROJECT_ROOT" "$1"
      ;;
  esac
}

require_file() {
  for path in "$@"; do
    if [ ! -f "$path" ]; then
      echo "Missing required file: $path" >&2
      exit 1
    fi
  done
}

require_dir() {
  for path in "$@"; do
    if [ ! -d "$path" ]; then
      echo "Missing required directory: $path" >&2
      exit 1
    fi
  done
}

require_env \
  MARMAT_APP_NAME \
  MARMAT_PYTHON \
  MARMAT_VENV_DIR \
  MARMAT_SRC_SUBDIR \
  MARMAT_RUNTIME_REQUIREMENTS \
  MARMAT_BUILD_REQUIREMENTS \
  MARMAT_BUILD_DIR \
  MARMAT_RELEASE_DIR \
  MARMAT_ZIP_NAME \
  MARMAT_QT_PLATFORM \
  MARMAT_SMOKE_TIMEOUT_SECONDS

MARMAT_VENV_PATH="$(project_path "$MARMAT_VENV_DIR")"
MARMAT_SRC_PATH="$(project_path "$MARMAT_SRC_SUBDIR")"
MARMAT_RUNTIME_REQUIREMENTS_PATH="$(project_path "$MARMAT_RUNTIME_REQUIREMENTS")"
MARMAT_BUILD_REQUIREMENTS_PATH="$(project_path "$MARMAT_BUILD_REQUIREMENTS")"
MARMAT_BUILD_PATH="$(project_path "$MARMAT_BUILD_DIR")"
MARMAT_RELEASE_PATH="$(project_path "$MARMAT_RELEASE_DIR")"
MARMAT_PYTHON_BIN="$MARMAT_VENV_PATH/bin/python"
MARMAT_PYINSTALLER_BIN="$MARMAT_VENV_PATH/bin/pyinstaller"
MARMAT_APP_BUNDLE_PATH="$MARMAT_BUILD_PATH/dist/$MARMAT_APP_NAME.app"
MARMAT_RELEASE_ZIP_PATH="$MARMAT_RELEASE_PATH/$MARMAT_ZIP_NAME"
