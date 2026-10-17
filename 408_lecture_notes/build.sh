#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build dist
python tools/build_all.py "$@"
