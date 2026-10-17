#!/usr/bin/env python3
"""扫描段落内的句式重复：连续否定、连续条件句、连续同头句。"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
SENT = re.compile(r"[^。！？\n]+[。！？]")
CODE = re.compile(r"```.*?```", re.S)
TABLE = re.compile(r"^\|.*$", re.M)
HEAD = re.compile(r"^#{1,6} .*$", re.M)
NEG = ("不能", "不应", "不可", "不要")
COND = ("若", "如果", "当", "只要")


def paragraphs(text: str):
    text = CODE.sub("", text)
    text = TABLE.sub("", text)
    text = HEAD.sub("", text)
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if len(block) < 30:
            continue
        yield block


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=SUBJECTS)
    ap.add_argument("--min-run", type=int, default=3)
    args = ap.parse_args()
    subjects = [args.subject] if args.subject else list(SUBJECTS)
    total = 0
    for subject in subjects:
        for path in sorted((ROOT / "manuscript" / subject).glob("*.md")):
            for block in paragraphs(path.read_text(encoding="utf-8")):
                sents = [s.strip() for s in SENT.findall(block)]
                runs = {"否定": [], "条件": []}
                for label, keys in (("否定", NEG), ("条件", COND)):
                    run = []
                    for s in sents:
                        if s.startswith(keys):
                            run.append(s)
                        else:
                            if len(run) >= args.min_run:
                                runs[label].append(run)
                            run = []
                    if len(run) >= args.min_run:
                        runs[label].append(run)
                for label, groups in runs.items():
                    for g in groups:
                        total += 1
                        print(f"{subject}/{path.name}: {label}连续 {len(g)} 句")
                        for s in g:
                            print("   ", s[:90])
    print(f"\n合计 {total} 处")


if __name__ == "__main__":
    main()
