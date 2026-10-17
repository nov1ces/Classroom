#!/usr/bin/env python3
"""核对正文引用的图片是否存在于 figures/。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
FIG = ROOT / "figures"


def main() -> None:
    missing = []
    total = 0
    for path in sorted((ROOT / "manuscript").rglob("*.md")):
        if "合并稿" in path.name:
            continue
        for ref in IMAGE.findall(path.read_text(encoding="utf-8")):
            total += 1
            name = Path(ref).name
            if not (FIG / name).exists():
                missing.append(f"{path.parent.name}/{path.name}: {ref}")
    print(f"图片引用 {total} 处，缺失 {len(missing)} 处")
    for m in missing:
        print(" ", m)


if __name__ == "__main__":
    main()
