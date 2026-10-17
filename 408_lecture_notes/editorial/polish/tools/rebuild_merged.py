#!/usr/bin/env python3
"""按 tools/build_books.py 的合并规则重建四科合并稿（不调用 LaTeX/Pandoc）。

规则与 build_books.prepare 一致：
- 章文件按文件名排序，用两个换行连接；
- 没有显式锚点的 1～4 级标题补 `{#<科目小写>-c<章号>-h<章内行号>}`；
- 合并稿中的图片链接改写成 ../figures/<文件名>。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = {
    "DS": ("数据结构", 8),
    "CO": ("计算机组成原理", 8),
    "OS": ("操作系统", 7),
    "CN": ("计算机网络", 6),
}
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def annotate(subject: str, chapter: int, lines: list[str]) -> list[str]:
    out: list[str] = []
    block = False
    for ln, line in enumerate(lines, 1):
        if re.match(r"^\s*(```|~~~)", line):
            block = not block
        m = None if block else HEADING.match(line)
        if m and not re.search(r"\{#[^}]+\}\s*$", line):
            line += f" {{#{subject.lower()}-c{chapter:02d}-h{ln}}}"
        out.append(line)
    return out


def build(subject: str) -> str:
    title, wanted = SUBJECTS[subject]
    paths = sorted((ROOT / "manuscript" / subject).glob("[0-9][0-9]_*.md"))
    nums = [int(p.name[:2]) for p in paths]
    if nums != list(range(1, wanted + 1)):
        raise SystemExit(f"{subject}: 期望第1..{wanted}章，实际 {nums}")
    chunks = []
    for path in paths:
        chapter = int(path.name[:2])
        lines = path.read_text(encoding="utf-8").splitlines()
        if not any(line.startswith("# ") for line in lines):
            raise SystemExit(f"{path}: 缺少章标题")
        chunks.append("\n".join(annotate(subject, chapter, lines)) + "\n")
    body = "\n\n".join(chunks)
    return re.sub(
        r"(!\[[^\]]*\]\()([^\s)]+\.png)",
        lambda m: m[1] + "../figures/" + Path(m[2]).name,
        body,
    )


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for subject, (title, _) in SUBJECTS.items():
        if only and subject != only:
            continue
        merged = build(subject)
        out = ROOT / "manuscript" / f"{title}_合并稿.md"
        out.write_text(merged, encoding="utf-8", newline="\r\n")
        print(f"{out.name}: {len(merged)} 字符")


if __name__ == "__main__":
    main()
