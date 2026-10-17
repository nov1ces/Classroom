#!/usr/bin/env python3
"""粗查讲义行文问题，供润色前定位。只读，不改稿。"""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ("DS", "CO", "OS", "CN")
CJK = re.compile(r"[\u4e00-\u9fff]")
CODE_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
MATH_DISPLAY = re.compile(r"\$\$.*?\$\$", re.S)
TABLE_LINE = re.compile(r"^\|.*$", re.M)
HEADING = re.compile(r"^#{1,6} .*$", re.M)


def strip_non_prose(text: str) -> str:
    text = CODE_FENCE.sub("", text)
    text = MATH_DISPLAY.sub("", text)
    text = TABLE_LINE.sub("", text)
    text = HEADING.sub("", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", "", text)
    text = re.sub(r"\{#[^}]+\}", "", text)
    return text


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])|\n{2,}", text)
    out = []
    for p in parts:
        p = p.strip()
        if len(CJK.findall(p)) >= 8:
            out.append(p)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=SUBJECTS)
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    subjects = [args.subject] if args.subject else list(SUBJECTS)
    for subject in subjects:
        print(f"\n{'=' * 20} {subject} {'=' * 20}")
        for path in sorted((ROOT / "manuscript" / subject).glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            prose = strip_non_prose(raw)
            sents = sentences(prose)
            if not sents:
                continue
            lens = [len(CJK.findall(s)) for s in sents]
            long_s = [s for s in sents if len(CJK.findall(s)) > 90]
            starts = collections.Counter(s[:3] for s in sents)
            buneng = sum(s.count("不能") for s in sents)
            ruo = sum(1 for s in sents if s.startswith("若"))
            print(
                f"{path.name:<34} 汉字{len(CJK.findall(prose)):>6} "
                f"句{len(sents):>4} "
                f"均长{sum(lens) / len(lens):>5.1f} 超90字{len(long_s):>3} "
                f"不能{buneng:>3} 若起句{ruo:>3} "
                f"高频起句{starts.most_common(3)}"
            )
            for s in sorted(long_s, key=lambda x: -len(CJK.findall(x)))[: args.top]:
                print(f"    [{len(CJK.findall(s))}] {s[:160]}")
        # 术语与标点
        corpus = "\n".join(
            p.read_text(encoding="utf-8") for p in (ROOT / "manuscript" / subject).glob("*.md")
        )
        pairs = {
            "结点/节点": ("结点", "节点"),
            "分组的份": ("份组", "分组"),
            "其它/其他": ("其它", "其他"),
            "作出/做出": ("作出", "做出"),
            "称为/叫做": ("称为", "叫做"),
        }
        stats = {k: {w: corpus.count(w) for w in v} for k, v in pairs.items()}
        print("  术语:", stats)
        bad_punct = re.findall(r"[\u4e00-\u9fff][,;:!?()]|[,;:!?()][\u4e00-\u9fff]", corpus)
        print(f"  中文旁半角标点: {len(bad_punct)} 例 {bad_punct[:8]}")


if __name__ == "__main__":
    main()
