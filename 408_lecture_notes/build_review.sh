#!/usr/bin/env bash
# Export the current content-review edition without running PDF layout audits.
set -euo pipefail
cd "$(dirname "$0")"
python editorial/revision3/CO_sources/check_source_structure.py
for review_subject in DS CO OS CN; do
    python "editorial/full/${review_subject}/verification.py"
done
python editorial/revision2/OS_verification.py
python editorial/revision3/verify_conversion.py
python tools/sync_full_editorial.py --content-review --review-edition revision3
python tools/index_chapters.py --review --review-edition revision3
python tools/index_figures.py --content-only
python tools/build_books.py --review --review-edition revision3 "$@"
