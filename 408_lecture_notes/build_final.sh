#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python tools/verify_choice_layout.py
python tools/verify_conversion.py
python tools/build_books.py
python tools/audit_books.py
python tools/verify_choice_layout.py --pdf
python tools/verify_reader_layout.py
python tools/export_final.py
