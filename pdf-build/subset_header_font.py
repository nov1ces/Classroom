"""Derive the small header font from PyMuPDF's bundled CJK font."""

import ast
import io

import fitz
from fontTools import subset
from fontTools.ttLib import TTFont

from config import ROOT, BUILD, read_items
from topics import TOPICS


def main():
    tree = ast.parse((ROOT / "compose_book.py").read_text(encoding="utf-8"))
    text = "".join(
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    text += "".join(topic["title"] + topic["focus"] for topic in TOPICS)
    for group in read_items().values():
        for item in group:
            text += "".join(item.get(key, "") for key in ("label", "bookmark", "note"))
    text += "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz /._-+#§→·，：；（）"
    with TTFont(io.BytesIO(fitz.Font("cjk").buffer)) as font:
        missing = set(map(ord, text)) - set(font.getBestCmap()) - {9, 10, 13}
        if missing:
            raise ValueError("页眉字体缺少字符: " + " ".join(f"U+{v:04X}" for v in sorted(missing)))
        subsetter = subset.Subsetter(options=subset.Options())
        subsetter.populate(text=text)
        subsetter.subset(font)
        BUILD.mkdir(parents=True, exist_ok=True)
        font.save(BUILD / "HeaderCJK-subset.ttf")
    print(f"页眉字体已生成，{len(set(text))} 个字符")


if __name__ == "__main__":
    main()
