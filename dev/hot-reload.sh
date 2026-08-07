#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "${DATA_DIR:-}" ]]; then
  if [[ -d "$ROOT/../data" ]]; then
    DATA_DIR="$(cd "$ROOT/../data" && pwd)"
  else
    DATA_DIR="$ROOT/dev/data"
  fi
fi

API_PORT="${API_PORT:-9000}"
UI_PORT="${UI_PORT:-3000}"
API_URL="${API_URL:-http://localhost:${API_PORT}}"
BASE_URL="${BASE_URL:-http://localhost:${UI_PORT}}"
PRODUCTION="${PRODUCTION:-false}"
API_DOCS="${API_DOCS:-true}"
NUXT_TELEMETRY_DISABLED="${NUXT_TELEMETRY_DISABLED:-1}"

api_pid=""
ui_pid=""

cleanup() {
  if [[ -n "$api_pid" ]]; then
    kill "$api_pid" 2>/dev/null || true
  fi
  if [[ -n "$ui_pid" ]]; then
    kill "$ui_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting Mealie hot reload"
echo "  API:  http://localhost:${API_PORT}"
echo "  UI:   http://localhost:${UI_PORT}"
echo "  Data: ${DATA_DIR}"
echo
echo "If this DATA_DIR is also mounted by Docker with SQLite, stop Docker before dev writes."
echo

(
  cd "$ROOT"
  DATA_DIR="$DATA_DIR" API_PORT="$API_PORT" BASE_URL="$BASE_URL" PRODUCTION="$PRODUCTION" API_DOCS="$API_DOCS" uv run python mealie/app.py
) &
api_pid="$!"

(
  cd "$ROOT/frontend"
  API_URL="$API_URL" NUXT_TELEMETRY_DISABLED="$NUXT_TELEMETRY_DISABLED" yarn run dev --host 0.0.0.0 --port "$UI_PORT" --no-fork
) &
ui_pid="$!"

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$ui_pid" 2>/dev/null; do
  sleep 1
done

cleanup
wait "$api_pid" 2>/dev/null || true
wait "$ui_pid" 2>/dev/null || true
