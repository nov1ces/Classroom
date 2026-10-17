#!/usr/bin/env python3
"""把统计表与问题条数填进润色说明。"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "editorial" / "polish" / "润色说明.md"
ISSUES = ROOT / "editorial" / "polish" / "疑似问题与编辑处理.md"


def main() -> None:
    stats = subprocess.run(
        [sys.executable, str(ROOT / "editorial/polish/tools/stat_summary.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()

    issue_text = ISSUES.read_text(encoding="utf-8")
    section = issue_text.split("## 一、保留原文", 1)[1].split("## 二、", 1)[0]
    count = len(re.findall(r"^\|\s*\d+\s*\|", section, re.M))

    report = REPORT.read_text(encoding="utf-8")
    report = report.replace("{{STAT_TABLE}}", stats)
    report = report.replace("{{ISSUE_COUNT}}", str(count))
    if "{{" in report:
        raise SystemExit("仍有未替换的占位符")
    REPORT.write_text(report, encoding="utf-8", newline="\r\n")
    print(f"统计表已填入；疑似问题 {count} 条。")


if __name__ == "__main__":
    main()
