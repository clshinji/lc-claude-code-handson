#\!/usr/bin/env bash
# Thin wrapper for bake.py (互換のため残置)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/bake.py" "$@"
