#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"
API_HOST="127.0.0.1"
API_PORT="8001"
WEB_HOST="127.0.0.1"
WEB_PORT="3001"
DB_PATH="$ROOT_DIR/data/winlong.db"
API_VENV_DIR="$API_DIR/.venv"

API_PID=""

cleanup() {
  if [[ -n "${API_PID:-}" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_port_free() {
  local port="$1"
  if lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $port is already in use. Stop the conflicting process and retry." >&2
    exit 1
  fi
}

find_python() {
  local candidate
  for candidate in python3.12 python3.11; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

install_python_with_brew() {
  if ! command -v brew >/dev/null 2>&1; then
    return 1
  fi

  echo "Python 3.11+ not found. Installing python@3.11 via Homebrew..."
  brew install python@3.11
}

write_web_env() {
  printf 'NEXT_PUBLIC_API_BASE_URL=http://%s:%s\nAPI_BASE_URL=http://%s:%s\n' \
    "$API_HOST" "$API_PORT" "$API_HOST" "$API_PORT" > "$WEB_DIR/.env.local"
}

echo "Checking local environment..."
require_cmd npm
require_cmd lsof

PYTHON_BIN="$(find_python || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  install_python_with_brew || {
    echo "Python 3.11+ is required for apps/api. Install python3.11 or python3.12 and retry." >&2
    exit 1
  }
  PYTHON_BIN="$(find_python || true)"
fi

if [[ -z "$PYTHON_BIN" ]]; then
  echo "python@3.11 installation finished, but python3.11 is still not on PATH." >&2
  echo "Run: export PATH=\"/opt/homebrew/opt/python@3.11/bin:$PATH\"" >&2
  exit 1
fi

ensure_port_free "$API_PORT"
ensure_port_free "$WEB_PORT"

if [[ ! -d "$API_VENV_DIR" ]]; then
  echo "Creating backend virtualenv with $PYTHON_BIN..."
  "$PYTHON_BIN" -m venv "$API_VENV_DIR"
fi

echo "Installing backend dependencies..."
"$API_VENV_DIR/bin/pip" install -e "$API_DIR[dev]"

echo "Installing frontend dependencies..."
npm --prefix "$WEB_DIR" install

echo "Writing apps/web/.env.local..."
write_web_env

export WINLONG_DB_PATH="$DB_PATH"
export WINLONG_ALLOWED_ORIGINS="http://localhost:$WEB_PORT,http://127.0.0.1:$WEB_PORT"
export WINLONG_ENABLE_SYNC_ON_START="${WINLONG_ENABLE_SYNC_ON_START:-true}"

echo "Backend live sync on start: $WINLONG_ENABLE_SYNC_ON_START"

echo "Starting backend on http://$API_HOST:$API_PORT ..."
(
  cd "$API_DIR"
  exec "$API_VENV_DIR/bin/python" -m uvicorn app.main:app --reload --host "$API_HOST" --port "$API_PORT"
) &
API_PID=$!

echo "Starting frontend on http://$WEB_HOST:$WEB_PORT ..."
cd "$WEB_DIR"
exec env \
  NEXT_PUBLIC_API_BASE_URL="http://$API_HOST:$API_PORT" \
  API_BASE_URL="http://$API_HOST:$API_PORT" \
  npm run dev -- --hostname "$WEB_HOST" --port "$WEB_PORT"
