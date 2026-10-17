#!/usr/bin/env python3
"""对比基线，检查限定词是否被削弱、绝对化表述是否增加。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
HEDGES = ("通常", "一般", "可能", "往往", "多数", "在多数", "除非", "仅当", "未必", "不一定", "并不总是")
ABSOLUTES = ("一定", "必然", "总是", "绝不", "所有", "任何", "完全")


def counts(text: str) -> dict[str, int]:
    return {w: text.count(w) for w in HEDGES + ABSOLUTES}


def main() -> None:
    print(f"{'章':<38} {'限定词前':>6} {'后':>4} {'绝对词前':>6} {'后':>4}")
    for subject in SUBJECTS:
        for base_path in sorted((ROOT / "editorial/polish/baseline" / subject).glob("*.md")):
            cur_path = ROOT / "manuscript" / subject / base_path.name
            b = counts(base_path.read_text(encoding="utf-8"))
            c = counts(cur_path.read_text(encoding="utf-8"))
            hb = sum(b[w] for w in HEDGES)
            hc = sum(c[w] for w in HEDGES)
            ab = sum(b[w] for w in ABSOLUTES)
            ac = sum(c[w] for w in ABSOLUTES)
            if hb != hc or ab != ac:
                print(f"{subject}/{base_path.stem:<34} {hb:>6} {hc:>4} {ab:>6} {ac:>4}")


if __name__ == "__main__":
    main()
