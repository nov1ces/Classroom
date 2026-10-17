#!/usr/bin/env python3
"""汇总润色前后的量化指标，输出 Markdown 表格，供润色报告使用。"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
HANZI = re.compile(r"[\u4e00-\u9fff]")


def stats(base: str, cur: str) -> dict:
    b_lines = base.splitlines()
    c_lines = cur.splitlines()
    sm = difflib.SequenceMatcher(None, b_lines, c_lines, autojunk=False)
    changed = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    b_sent = [s for s in re.split(r"(?<=[。！？])", base) if len(HANZI.findall(s)) >= 8]
    c_sent = [s for s in re.split(r"(?<=[。！？])", cur) if len(HANZI.findall(s)) >= 8]
    return {
        "hanzi_b": len(HANZI.findall(base)),
        "hanzi_c": len(HANZI.findall(cur)),
        "sent_b": len(b_sent),
        "sent_c": len(c_sent),
        "changed_lines": changed,
        "lines_b": len(b_lines),
        "buneng_b": base.count("不能"),
        "buneng_c": cur.count("不能"),
    }


def main() -> None:
    rows = []
    totals = dict(hanzi_b=0, hanzi_c=0, buneng_b=0, buneng_c=0, changed_lines=0)
    for subject in SUBJECTS:
        for base_path in sorted((ROOT / "editorial/polish/baseline" / subject).glob("*.md")):
            cur_path = ROOT / "manuscript" / subject / base_path.name
            s = stats(
                base_path.read_text(encoding="utf-8"),
                cur_path.read_text(encoding="utf-8"),
            )
            for k in totals:
                totals[k] += s[k]
            rows.append((subject, base_path.stem, s))
    print("| 科目 | 章 | 汉字（前→后） | 变化 | 改动行 | “不能”（前→后） |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for subject, name, s in rows:
        pct = (s["hanzi_c"] - s["hanzi_b"]) / s["hanzi_b"] * 100
        print(
            f"| {subject} | {name} | {s['hanzi_b']} → {s['hanzi_c']} | {pct:+.1f}% | "
            f"{s['changed_lines']}/{s['lines_b']} | {s['buneng_b']} → {s['buneng_c']} |"
        )
    pct = (totals["hanzi_c"] - totals["hanzi_b"]) / totals["hanzi_b"] * 100
    print(
        f"| **合计** | 29 章 | {totals['hanzi_b']} → {totals['hanzi_c']} | {pct:+.1f}% | "
        f"{totals['changed_lines']} 行 | {totals['buneng_b']} → {totals['buneng_c']} |"
    )


if __name__ == "__main__":
    main()
