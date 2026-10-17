#!/usr/bin/env python3
"""核对四科正文中的内部链接是否都有对应锚点。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
LINK = re.compile(r"\]\(#([^)\s]+)\)")
ANCHOR = re.compile(r"\{#([^}\s]+)")


def main() -> None:
    total_links = 0
    missing = []
    for subject in SUBJECTS:
        files = sorted((ROOT / "manuscript" / subject).glob("*.md"))
        anchors = set()
        for path in files:
            anchors |= set(ANCHOR.findall(path.read_text(encoding="utf-8")))
        for path in files:
            text = path.read_text(encoding="utf-8")
            for target in LINK.findall(text):
                total_links += 1
                if target not in anchors:
                    missing.append(f"{subject}/{path.name} -> #{target}")
    print(f"内部链接 {total_links} 个，缺失锚点 {len(missing)} 个")
    for m in missing:
        print(" ", m)


if __name__ == "__main__":
    main()
