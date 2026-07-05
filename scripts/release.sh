#!/bin/bash
# HymnFlow release — thin wrapper around the cross-platform Python script.
# Usage: scripts/release.sh [version] [--publish] [--rebuild] [--dry-run]
# See scripts/release.py and doc/RELEASING.md for details.
exec python "$(dirname "$0")/release.py" "$@"
