#!/usr/bin/env python3
"""扫描编辑后可能出现的标点与空白异常。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
CODE = re.compile(r"```.*?```", re.S)
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
PATTERNS = {
    "连续逗号": r"，\s*，",
    "连续句号": r"。\s*。",
    "连续分号": r"；\s*；",
    "中文后英文逗号": r"[\u4e00-\u9fff],",
    "中文后英文句号": r"[\u4e00-\u9fff]\.",
    "重复的的": r"的的",
    "重复了了": r"了了",
    "多余空格": r"[\u4e00-\u9fff]  +[\u4e00-\u9fff]",
    "行首空格": r"^[ \t]+(?=\S)",
}


def main() -> None:
    for subject in SUBJECTS:
        for path in sorted((ROOT / "manuscript" / subject).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            text = CODE.sub("〔代码〕", text)
            text = MATH.sub("〔式〕", text)
            for name, pat in PATTERNS.items():
                for m in re.finditer(pat, text, re.M):
                    line = text.count("\n", 0, m.start()) + 1
                    ctx = text[max(0, m.start() - 20) : m.end() + 20].replace("\n", " ")
                    print(f"{subject}/{path.name}:{line} [{name}] ...{ctx}...")


if __name__ == "__main__":
    main()
