#!/usr/bin/env python3
"""核对润色稿是否保住结构、公式、代码、表格、图表锚点与题源标记。

用法:
    python editorial/polish/tools/check_manuscript.py            # 全部科目
    python editorial/polish/tools/check_manuscript.py --subject DS

基线取 editorial/polish/baseline/<科目>/*.md，现稿取 manuscript/<科目>/*.md。
只报差异，不改文件。退出码 1 表示存在硬性结构差异。
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")

FENCE = re.compile(r"^```([^\n`]*)\n(.*?)^```[ \t]*$", re.S | re.M)
INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)
ANCHOR = re.compile(r"\{#([^}]+)\}")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LABEL = re.compile(r"【\d{4}】|〖[^〗]+〗")
DIGIT = re.compile(r"\d+(?:\.\d+)?")
REF = re.compile(r"例\s?\d+-\d+|图\s?\d+\.\d+|表\s?\d+\.\d+|第\s?\d+\s?章")
PARA = re.compile(r"\n\s*\n")


def display_math_blocks(text: str) -> list[str]:
    """收集 $$...$$ 块：支持单行与跨行两种写法。"""
    blocks: list[str] = []
    buf: list[str] | None = None
    for line in text.splitlines():
        s = line.strip()
        if buf is None:
            if s.startswith("$$") and s.count("$$") >= 2 and len(s) > 4:
                blocks.append(s)
            elif s.startswith("$$"):
                buf = [s]
        else:
            buf.append(s)
            if s.endswith("$$") and not s.startswith("$$"):
                blocks.append("\n".join(buf))
                buf = None
            elif s.endswith("$$") and len(buf) > 1:
                blocks.append("\n".join(buf))
                buf = None
    if buf:
        blocks.append("\n".join(buf))
    return blocks


def tables(text: str) -> list[list[int]]:
    """每张表的行数与该表每行的单元格数。"""
    out: list[list[int]] = []
    cur: list[int] = []
    for line in text.splitlines():
        if line.startswith("|"):
            cur.append(line.count("|") - 1)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def answer_letters(text: str) -> collections.Counter:
    c: collections.Counter = collections.Counter()
    for line in text.splitlines():
        if "答案" in line or "选" in line:
            for m in re.findall(r"\*\*([ABCD])\*\*|(?:答案|选)\s*([ABCD])(?![A-Za-z])", line):
                letter = m[0] or m[1]
                if letter:
                    c[letter] += 1
    return c


def signature(text: str) -> dict:
    headings = HEADING.findall(text)
    fences = [(info.strip(), body) for info, body in FENCE.findall(text)]
    return {
        "heading_levels": collections.Counter(len(h) for h, _ in headings),
        "anchors": collections.Counter(ANCHOR.findall(text)),
        "images": collections.Counter(IMAGE.findall(text)),
        "fences": collections.Counter((i, b) for i, b in fences),
        "display_math": collections.Counter(display_math_blocks(text)),
        "inline_math": collections.Counter(m.strip() for m in INLINE_MATH.findall(text)),
        "labels": collections.Counter(LABEL.findall(text)),
        "refs": collections.Counter(REF.findall(text)),
        "tables": tables(text),
        "answers": answer_letters(text),
        "digits": collections.Counter(DIGIT.findall(text)),
        "paras": len([p for p in PARA.split(text) if p.strip()]),
        "hanzi": len(re.findall(r"[\u4e00-\u9fff]", text)),
    }


def diff_counter(name: str, base: collections.Counter, cur: collections.Counter) -> list[str]:
    problems = []
    for key in (base - cur):
        problems.append(f"{name} 丢失 x{base[key] - cur[key]}: {key!r}")
    for key in (cur - base):
        problems.append(f"{name} 新增 x{cur[key] - base[key]}: {key!r}")
    return problems


def check_file(base_path: Path, cur_path: Path) -> tuple[list[str], list[str]]:
    base = signature(base_path.read_text(encoding="utf-8"))
    cur = signature(cur_path.read_text(encoding="utf-8"))
    hard: list[str] = []
    soft: list[str] = []

    if base["anchors"] != cur["anchors"]:
        hard += diff_counter("锚点", base["anchors"], cur["anchors"])
    if base["heading_levels"] != cur["heading_levels"]:
        hard.append(f"标题层级计数 {dict(base['heading_levels'])} -> {dict(cur['heading_levels'])}")
    if base["refs"] != cur["refs"]:
        soft += diff_counter("例图章引用", base["refs"], cur["refs"])
    if base["images"] != cur["images"]:
        hard += diff_counter("图片", base["images"], cur["images"])
    if base["fences"] != cur["fences"]:
        hard += diff_counter("代码块", base["fences"], cur["fences"])
    if base["display_math"] != cur["display_math"]:
        hard += diff_counter("独立公式", base["display_math"], cur["display_math"])
    if base["inline_math"] != cur["inline_math"]:
        hard += diff_counter("行内公式", base["inline_math"], cur["inline_math"])
    if base["labels"] != cur["labels"]:
        hard += diff_counter("题源标记", base["labels"], cur["labels"])
    if base["tables"] != cur["tables"]:
        hard.append(f"表格结构变化 {base['tables']} -> {cur['tables']}")
    if base["answers"] != cur["answers"]:
        hard.append(f"答案字母统计 {dict(base['answers'])} -> {dict(cur['answers'])}")
    if base["paras"] and abs(cur["paras"] - base["paras"]) > max(2, base["paras"] * 0.06):
        soft.append(f"段落数 {base['paras']} -> {cur['paras']}")

    ratio = cur["hanzi"] / base["hanzi"] if base["hanzi"] else 1.0
    if not 0.95 <= ratio <= 1.05:
        hard.append(f"汉字数变化 {base['hanzi']} -> {cur['hanzi']} ({ratio - 1:+.1%})，超出 ±5%")
    digit_delta = (base["digits"] - cur["digits"]) + (cur["digits"] - base["digits"])
    if digit_delta:
        delta = {k: (base["digits"][k], cur["digits"][k]) for k in digit_delta}
        soft.append(f"数字标记差异 {len(digit_delta)} 种: {dict(list(delta.items())[:12])}")
    if base["hanzi"]:
        soft.append(f"汉字 {base['hanzi']} -> {cur['hanzi']} ({ratio - 1:+.1%})")
    return hard, soft


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=SUBJECTS)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    subjects = [args.subject] if args.subject else list(SUBJECTS)
    failed = False
    for subject in subjects:
        base_dir = ROOT / "editorial" / "polish" / "baseline" / subject
        cur_dir = ROOT / "manuscript" / subject
        for base_path in sorted(base_dir.glob("*.md")):
            cur_path = cur_dir / base_path.name
            if not cur_path.exists():
                print(f"[FAIL] {subject}/{base_path.name}: 现稿缺失")
                failed = True
                continue
            hard, soft = check_file(base_path, cur_path)
            flag = "FAIL" if hard else "ok  "
            print(f"[{flag}] {subject}/{base_path.name}")
            for msg in hard:
                print(f"    HARD {msg}")
            if hard or args.verbose:
                for msg in soft:
                    print(f"    soft {msg}")
            failed = failed or bool(hard)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
