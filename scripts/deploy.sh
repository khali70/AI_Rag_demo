#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: scripts/deploy.sh [up|down|logs] [options]

Commands:
  up       Build and start the stack (default).
  down     Stop the stack and remove containers.
  logs     Tail backend and frontend logs.

Options:
  --no-chroma   Skip starting the optional Chroma container.
  --attach      Run docker compose up in the foreground.
  --no-build    Do not re-build images before starting.
  -h, --help    Show this help text.
EOF
}

ACTION="up"
ENABLE_CHROMA="true"
DETACHED="true"
BUILD_IMAGES="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    up|down|logs)
      ACTION="$1"
      ;;
    --no-chroma)
      ENABLE_CHROMA="false"
      ;;
    --attach)
      DETACHED="false"
      ;;
    --no-build)
      BUILD_IMAGES="false"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

compose() {
  (cd "$ROOT_DIR" && docker compose "$@")
}

case "$ACTION" in
  up)
    export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000/api}"
    export CHROMA_SERVER_HOST="${CHROMA_SERVER_HOST:-}"
    export CHROMA_SERVER_PORT="${CHROMA_SERVER_PORT:-8000}"
    export CHROMA_SERVER_SSL="${CHROMA_SERVER_SSL:-false}"

    args=()
    if [[ "$ENABLE_CHROMA" == "true" ]]; then
      args+=(--profile chroma)
    fi
    args+=(up)
    if [[ "$DETACHED" == "true" ]]; then
      args+=(-d)
    fi
    if [[ "$BUILD_IMAGES" == "true" ]]; then
      args+=(--build)
    fi
    compose "${args[@]}"
    ;;
  down)
    compose down
    ;;
  logs)
    compose logs -f backend frontend
    ;;
  *)
    usage
    exit 1
    ;;
esac
