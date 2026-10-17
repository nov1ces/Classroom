#!/usr/bin/env python3
"""Pandoc filter: align A-D choices and Roman-numbered statements.

Keep Math, Code, emphasis and all option text as native Pandoc inlines. Only
complete, ordered label sequences are treated as question groups. This also
handles choices inside a self-check list item and groups spanning paragraphs.
"""
from __future__ import annotations

import copy
import json
import re
import sys

LABEL = re.compile(r"(?<![A-Za-z0-9])([A-D]|VIII|VII|VI|IV|III|II|IX|I|V|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ])\.")
ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
UNICODE_ROMAN = tuple("ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ")
BLOCKS = {"Para", "Plain", "Header", "Div", "BlockQuote", "OrderedList",
          "BulletList", "DefinitionList", "CodeBlock", "RawBlock", "Table",
          "HorizontalRule", "LineBlock", "Figure", "Null"}
SPACE = {"Space", "SoftBreak", "LineBreak"}


def plain(inlines):
    text = []
    for node in inlines:
        if node["t"] == "Str":
            text.append(node["c"])
        elif node["t"] in SPACE:
            text.append(" ")
        elif node["t"] in {"Strong", "Emph", "SmallCaps", "Strikeout", "Superscript", "Subscript"}:
            text.append(plain(node["c"]))
        elif node["t"] in {"Code", "Math"}:
            text.append(node["c"][-1])
    return "".join(text)


def tokenize(inlines):
    result = []
    for node in inlines:
        if node["t"] != "Str":
            result.append(copy.deepcopy(node))
            continue
        offset = 0
        for match in LABEL.finditer(node["c"]):
            if match.start() > offset:
                result.append({"t": "Str", "c": node["c"][offset:match.start()]})
            result.append({"t": "Str", "c": match[0]})
            offset = match.end()
        if offset < len(node["c"]):
            result.append({"t": "Str", "c": node["c"][offset:]})
    return result


def trim(inlines):
    result = copy.deepcopy(inlines)
    while result and result[0]["t"] in SPACE:
        result.pop(0)
    while result and result[-1]["t"] in SPACE:
        result.pop()
    if result and result[0]["t"] == "Str":
        result[0]["c"] = result[0]["c"].lstrip()
    if result and result[-1]["t"] == "Str":
        result[-1]["c"] = result[-1]["c"].rstrip()
    # A source line wrap within one option is not an imposed print break.
    return [{"t": "Space"} if x["t"] in SPACE else x for x in result]


def group_at(blocks, start):
    joined = []
    for end in range(start, min(start + 10, len(blocks))):
        block = blocks[end]
        if block["t"] not in {"Para", "Plain"}:
            break
        if end > start:
            joined.append({"t": "Space"})
        joined.extend(tokenize(block["c"]))
        marks = [(i, x["c"][:-1]) for i, x in enumerate(joined)
                 if x["t"] == "Str" and LABEL.fullmatch(x["c"])]
        if not marks:
            break
        labels = [label for _, label in marks]
        first = labels[0]
        choices = first == "A"
        expected = tuple("ABCD") if choices else UNICODE_ROMAN if first == "Ⅰ" else ROMAN if first == "I" else ()
        if not expected or tuple(labels) != expected[:len(labels)]:
            break
        prefix = trim(joined[:marks[0][0]])
        # Only a question stem may precede an embedded A-D sequence.
        if prefix and (not choices or not re.search(r"[。？?）):：]$", plain(prefix).rstrip())):
            break
        if len(labels) < (4 if choices else 2):
            continue
        # Continue a Roman run if the next paragraph begins with its next label.
        if not choices and end + 1 < len(blocks) and len(labels) < len(expected):
            nxt = blocks[end + 1]
            if nxt["t"] in {"Para", "Plain"} and plain(nxt["c"]).lstrip().startswith(expected[len(labels)] + "."):
                continue
        contents = []
        for j, (offset, _) in enumerate(marks):
            stop = marks[j + 1][0] if j + 1 < len(marks) else len(joined)
            content = trim(joined[offset + 1:stop])
            if not content or not plain(content).strip():
                return None
            contents.append(content)
        return end + 1, prefix, labels, contents
    return None


def transform(document, output_format="json"):
    inventory = []

    def render(labels, contents):
        kind = "choices" if labels == list("ABCD") else "statements"
        ident = f"book-{kind}-{len(inventory) + 1:04d}"
        inventory.append(dict(id=ident, kind=kind, labels=labels, contents=copy.deepcopy(contents)))
        attr = ["", ["book-" + kind], [["data-choice-id", ident]]]
        if output_format not in {"latex", "beamer"}:
            children = [{"t": "Plain", "c": [{"t": "Str", "c": label + "."}, {"t": "Space"}] + content}
                        for label, content in zip(labels, contents)]
        elif kind == "choices":
            inlines = [{"t": "RawInline", "c": ["latex", "\\BookChoiceSet{" + ident + "}{"]}]
            for j, content in enumerate(contents):
                if j:
                    inlines.append({"t": "RawInline", "c": ["latex", "}{"]})
                inlines.extend(content)
            inlines.append({"t": "RawInline", "c": ["latex", "}"]})
            children = [{"t": "Para", "c": inlines}]
        else:
            children = [{"t": "RawBlock", "c": ["latex", "\\begin{BookStatements}{" + ident + "}"]}]
            for label, content in zip(labels, contents):
                inlines = [{"t": "RawInline", "c": ["latex", "\\BookStatement{" + label + "}{"]}]
                inlines += content + [{"t": "RawInline", "c": ["latex", "}"]}]
                children.append({"t": "Para", "c": inlines})
            children.append({"t": "RawBlock", "c": ["latex", "\\end{BookStatements}"]})
        return {"t": "Div", "c": [attr, children]}

    def block_sequence(blocks):
        expanded = []
        for block in blocks:
            if block["t"] == "OrderedList":
                attributes, items = block["c"]
                start, style, delimiter = attributes
                if (style["t"] == "UpperRoman" and delimiter["t"] == "Period"
                        and 1 <= start <= len(ROMAN)
                        and start + len(items) - 1 <= len(ROMAN)
                        and all(len(item) == 1 and item[0]["t"] in {"Para", "Plain"} for item in items)):
                    for index, item in enumerate(items, start - 1):
                        expanded.append({"t": "Para", "c": [{"t": "Str", "c": ROMAN[index] + "."},
                            {"t": "Space"}] + item[0]["c"]})
                    continue
            expanded.append(block)
        blocks = expanded
        out = []
        i = 0
        while i < len(blocks):
            found = group_at(blocks, i)
            if found:
                end, prefix, labels, contents = found
                if prefix:
                    out.append({"t": blocks[i]["t"], "c": prefix})
                out.append(render(labels, contents))
                i = end
            else:
                out.append(blocks[i])
                i += 1
        return out

    def walk(value):
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        if isinstance(value, list):
            result = [walk(v) for v in value]
            if result and all(isinstance(v, dict) and v.get("t") in BLOCKS for v in result):
                return block_sequence(result)
            return result
        return value

    return walk(copy.deepcopy(document)), inventory


if __name__ == "__main__":
    document = json.load(sys.stdin)
    transformed, _ = transform(document, sys.argv[1] if len(sys.argv) > 1 else "json")
    json.dump(transformed, sys.stdout, ensure_ascii=False)
