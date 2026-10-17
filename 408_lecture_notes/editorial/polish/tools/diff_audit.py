#!/usr/bin/env python3
"""按行对比基线与现稿，列出增删整行、明显扩写/压缩的改动，供主编抽检。"""
from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
HANZI = re.compile(r"[\u4e00-\u9fff]")


def hz(s: str) -> int:
    return len(HANZI.findall(s))


def audit(subject: str, name: str, base: str, cur: str, limit: int) -> None:
    b = [x for x in base.splitlines() if x.strip()]
    c = [x for x in cur.splitlines() if x.strip()]
    sm = difflib.SequenceMatcher(None, b, c, autojunk=False)
    events = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            for line in b[i1:i2]:
                events.append(("删行", line, "", hz(line)))
        elif tag == "insert":
            for line in c[j1:j2]:
                events.append(("增行", "", line, -hz(line)))
        elif tag == "replace":
            for k in range(max(i2 - i1, j2 - j1)):
                old = b[i1 + k] if i1 + k < i2 else ""
                new = c[j1 + k] if j1 + k < j2 else ""
                if not old or not new:
                    events.append(("删行" if old else "增行", old, new, hz(old) if old else -hz(new)))
                    continue
                delta = hz(new) - hz(old)
                ratio = difflib.SequenceMatcher(None, old, new).ratio()
                if abs(delta) >= 12 or ratio <= 0.78:
                    events.append(("改写", old, new, delta))
    if not events:
        return
    print(f"\n### {subject}/{name}  事件 {len(events)}")
    for kind, old, new, delta in events[:limit]:
        print(f"- [{kind} {delta:+d}字]")
        print(f"  旧：{old[:220]}")
        print(f"  新：{new[:220]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=SUBJECTS)
    ap.add_argument("--limit", type=int, default=6)
    args = ap.parse_args()
    subjects = [args.subject] if args.subject else list(SUBJECTS)
    for subject in subjects:
        for base_path in sorted((ROOT / "editorial/polish/baseline" / subject).glob("*.md")):
            cur_path = ROOT / "manuscript" / subject / base_path.name
            audit(
                subject,
                base_path.stem,
                base_path.read_text(encoding="utf-8"),
                cur_path.read_text(encoding="utf-8"),
                args.limit,
            )


if __name__ == "__main__":
    main()
