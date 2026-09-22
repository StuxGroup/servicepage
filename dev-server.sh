#!/bin/bash
# Soonpage - Local dev server
# Usage: ./dev-server.sh [port]
#   port   default: 8000
#
# Static site, nothing to build - this just serves the directory locally so
# you can preview index.html the way GitHub Pages will serve it.
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8000}"

case "$PORT" in
    ''|*[!0-9]*) echo "Port must be numeric" >&2; exit 1 ;;
esac

echo "Soonpage running at http://127.0.0.1:$PORT"
php -S "127.0.0.1:$PORT" -t "$DIR"
