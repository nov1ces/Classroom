#!/usr/bin/env python3
"""检查题干、选项与答案行是否被改动（只报差异，不改稿）。"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
QUESTION = re.compile(r"^\s*(【\d{4}】|〖[^〗]+〗)|（\s*）|^\s*[ABCD]\.[ 　]|答案")

def main() -> None:
    for subject in SUBJECTS:
        for base_path in sorted((ROOT / "editorial/polish/baseline" / subject).glob("*.md")):
            cur_path = ROOT / "manuscript" / subject / base_path.name
            b = base_path.read_text(encoding="utf-8").splitlines()
            c = cur_path.read_text(encoding="utf-8").splitlines()
            sm = difflib.SequenceMatcher(None, b, c, autojunk=False)
            hits = []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal":
                    continue
                for line in b[i1:i2]:
                    if QUESTION.search(line):
                        new = c[j1] if j1 < len(c) else ""
                        hits.append((line, new))
            if hits:
                print(f"\n### {subject}/{base_path.stem}  题干/选项/答案行改动 {len(hits)} 处")
                for old, new in hits[:8]:
                    print(f"  旧：{old[:150]}")
                    print(f"  新：{new[:150]}")


if __name__ == "__main__":
    main()
