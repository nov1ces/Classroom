#!/usr/bin/env python3
"""Audit CO Markdown -> Pandoc AST -> LaTeX source; never build/read a PDF."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "editorial/revision3/baseline"
FORMAT = "markdown+raw_tex+tex_math_dollars+tex_math_single_backslash"
checks = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(name, actual, expected):
    passed = actual == expected
    checks.append(dict(id=name, actual=actual, expected=expected, passed=passed))
    assert passed, (name, actual, expected)


def pandoc(text, target, filtered=False):
    command = ["pandoc", "--from=" + FORMAT, "--to=" + target, "--wrap=none"]
    if filtered:
        command += ["--lua-filter=tools/book_images.lua", "--no-highlight"]
    return subprocess.run(command, input=text, text=True, capture_output=True,
                          cwd=ROOT, check=True).stdout


def walk(node, kind):
    if isinstance(node, dict):
        if node.get("t") == kind:
            yield node
        for value in node.values():
            yield from walk(value, kind)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value, kind)


def fenced(text):
    return re.findall(r"^```[^\n]*\n(.*?)^```\s*$", text, re.M | re.S)


def pipe_rows(text):
    return [[cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            for line in text.splitlines() if line.startswith("|")]


def norm(text):
    return " ".join(text.split())


def section(text, anchor):
    start = re.search(r"^#{1,4} .*\{#" + re.escape(anchor) + r"\}\s*$", text, re.M)
    assert start, anchor
    rest = text[start.end():]
    end = re.search(r"^#{1,4} ", rest, re.M)
    return rest[:end.start()] if end else rest


def table(text, first_header):
    lines = text.splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith(first_header))
    result = []
    while i < len(lines) and lines[i].startswith("|"):
        result.append(lines[i])
        i += 1
    return "\n".join(result)


conversion = HERE / "source_conversion"
conversion.mkdir(exist_ok=True)
chapters = []
for path in sorted((ROOT / "manuscript/CO").glob("*.md")):
    rel = path.relative_to(ROOT)
    text = path.read_text()
    baseline = (BASE / rel).read_text()
    ast = json.loads(pandoc(text, "json"))
    raw_blocks = [block.rstrip("\n") for block in fenced(text)]
    ast_blocks = [node["c"][1] for node in walk(ast, "CodeBlock")]
    add(path.stem + ":fences_equal_AST", ast_blocks, raw_blocks)
    prose = re.sub(r"^```[^\n]*\n.*?^```\s*$", "", text, flags=re.M | re.S)
    raw_inline = re.findall(r"(?<!`)`([^`]+)`(?!`)", prose)
    add(path.stem + ":all_inline_code_equal_AST",
        [node["c"][1] for node in walk(ast, "Code")], raw_inline)
    raw_tables = re.findall(r"(?:^\|[^\n]+\|[ \t]*\n){2,}", prose, re.M)
    raw_shapes = []
    for source_table in raw_tables:
        rows = pipe_rows(source_table)
        raw_shapes.append([len(rows[0]), [len(row) for row in rows[2:]]])
    ast_shapes = []
    for node in walk(ast, "Table"):
        cols, bodies = node["c"][2], node["c"][4]
        data_rows = [row for body in bodies for row in body[3]]
        ast_shapes.append([len(cols), [len(row[1]) for row in data_rows]])
    add(path.stem + ":all_pipe_table_rows_columns_equal_AST", ast_shapes, raw_shapes)
    latex = pandoc(text, "latex", filtered=True)
    tex_blocks = re.findall(r"\\begin\{verbatim\}\n(.*?)\n\\end\{verbatim\}", latex, re.S)
    add(path.stem + ":AST_equal_verbatim", tex_blocks, ast_blocks)
    # Includes spaces, comments, brackets, punctuation and every explicit newline.
    old_blocks = [block.rstrip("\n") for block in fenced(baseline)]
    cursor = 0
    for block in old_blocks:
        cursor = ast_blocks.index(block, cursor) + 1
    add(path.stem + ":all_previous_code_blocks_retained", cursor > 0 or not old_blocks, True)
    old_anchors = re.findall(r"\{#([^}\s]+)[^}]*\}", baseline)
    add(path.stem + ":all_anchors_preserved", re.findall(r"\{#([^}\s]+)[^}]*\}", text), old_anchors)
    old_markers = re.findall(r"^(?:【\d{4}】|〖[^〗]+〗|典型示例（)[^\n]*", baseline, re.M)
    new_markers = re.findall(r"^(?:【\d{4}】|〖[^〗]+〗|典型示例（)[^\n]*", text, re.M)
    # CO6-5 changes only the format/table introduction, separately checked below.
    if path.name.startswith("06_"):
        old_markers = [m.split("下表给出")[0] if m.startswith("【2012】 某16位") else m for m in old_markers]
        new_markers = [m.split("下面给出")[0] if m.startswith("【2012】 某16位") else m for m in new_markers]
    add(path.stem + ":source_markers_retained", new_markers, old_markers)
    (conversion / (path.stem + ".json")).write_text(json.dumps(ast, ensure_ascii=False, indent=2))
    tex_path = conversion / (path.stem + ".tex")
    tex_path.write_text(latex)
    chapters.append(dict(manuscript=str(rel), sha256=sha(path),
                         old_code_blocks=len(old_blocks), code_blocks=len(ast_blocks),
                         inline_code=len(list(walk(ast, "Code"))),
                         tables=len(list(walk(ast, "Table"))),
                         ast=str((conversion / (path.stem + ".json")).relative_to(ROOT)),
                         latex=str(tex_path.relative_to(ROOT))))

ch4 = next((ROOT / "manuscript/CO").glob("04_*.md"))
old4 = section((BASE / ch4.relative_to(ROOT)).read_text(), "co-ex4-6")
new4 = section(ch4.read_text(), "co-ex4-6")
old_machine_table = table(old4, "| 行号 | 虚拟地址 |")
old_fields = pipe_rows(old_machine_table)[2:]
machine_block = next(block for block in fenced(new4) if "00401000" in block)
new_fields = [re.split(r"\s{2,}", line.strip()) for line in machine_block.splitlines()]
add("CO4-6:four_fields_each_row", [len(row) for row in new_fields], [4] * 16)
add("CO4-6:all_four_fields_preserved", [[norm(c) for c in row] for row in new_fields],
    [[norm(c) for c in row] for row in old_fields])
add("CO4-6:omitted_rows_preserved", sum(row == ["…"] * 4 for row in new_fields), 4)
add("CO4-6:source_code_and_all_questions_solutions_unchanged",
    [new4[:new4.index("以下按")], new4.split("其中，机器级代码行包括", 1)[1]],
    [old4[:old4.index(old_machine_table)], old4.split("其中，机器级代码行包括", 1)[1]])

ch6 = next((ROOT / "manuscript/CO").glob("06_*.md"))
old6 = section((BASE / ch6.relative_to(ROOT)).read_text(), "co-ex6-5")
new6 = section(ch6.read_text(), "co-ex6-5")
old_format_rows = pipe_rows(table(old6, "| 名称 | 汇编格式 |"))[2:]
new_formats = next(block for block in fenced(new6) if block.startswith("ADD   Rs, Rd"))
add("CO6-5:all_assembly_formats_preserved", [norm(row) for row in new_formats.splitlines()],
    [norm(row[1]) for row in old_format_rows])
new_function_rows = pipe_rows(table(new6, "| 名称 | 助记符 |"))[2:]
add("CO6-5:all_names_mnemonics_functions_preserved", new_function_rows,
    [[row[0], row[1].split()[0], row[2]] for row in old_format_rows])
add("CO6-5:original_pipeline_table_including_empty_cells_preserved",
    table(new6, "| 指令 | 1 |"), table(old6, "| 指令 | 1 |"))
add("CO6-5:all_question_lines_preserved", re.findall(r"^（[1-4]）.*", new6, re.M)[:4],
    re.findall(r"^（[1-4]）.*", old6, re.M)[:4])
add("CO6-5:machine_conditions_preserved",
    new6.split("该计算机采用5段流水方式", 1)[1].split("（1）", 1)[0],
    old6.split("该计算机采用5段流水方式", 1)[1].split("（1）", 1)[0])
add("CO6-5:all_solutions_preserved", new6.split("**解析。**", 1)[1],
    old6.split("**解析。**", 1)[1])

for anchor, filename in [("co-ex2-10", "02_"), ("co-ex3-12", "03_"),
                         ("co-ex3-13", "03_"), ("co-ex8-7", "08_")]:
    path = next((ROOT / "manuscript/CO").glob(filename + "*.md"))
    add(anchor + ":whole_example_unchanged", section(path.read_text(), anchor),
        section((BASE / path.relative_to(ROOT)).read_text(), anchor))

result = dict(status="PASS", scope="Markdown, AST and TeX source only; no lecture PDF build or page inspection",
              checks=len(checks), chapters=chapters, results=checks,
              filter=dict(path="tools/book_images.lua", sha256=sha(ROOT / "tools/book_images.lua")),
              preamble=dict(path="tools/book_preamble.tex", sha256=sha(ROOT / "tools/book_preamble.tex")))
(HERE / "source_structure_checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(dict(status="PASS", checks=len(checks), chapters=len(chapters),
                      code_blocks=sum(ch["code_blocks"] for ch in chapters)), ensure_ascii=False))
