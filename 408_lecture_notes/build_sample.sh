#!/usr/bin/env bash
# Accepted sample remains separately reproducible. The full books use build.sh.
set -euo pipefail
cd "$(dirname "$0")"
python tools/resolve_fonts.py
python tools/verify_models.py
python tools/draw_figures.py
python tools/build_books.py --subjects OS --chapters 3
cp build/OS/操作系统_预览.pdf dist/操作系统_同步互斥与信号量_样章.pdf
