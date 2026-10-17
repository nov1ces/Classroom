#!/usr/bin/env python3
"""Content-field/identity checks only; never generate or inspect lecture PDFs.

All outputs stay in the independent review directory. The manual content read,
source-image read, and independent calculations remain separate evidence.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "editorial/revision3/baseline"
FORMAT = "markdown+raw_tex+tex_math_dollars+tex_math_single_backslash"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nodes(value, kind):
    if isinstance(value, dict):
        if value.get("t") == kind:
            yield value
        for v in value.values():
            yield from nodes(v, kind)
    elif isinstance(value, list):
        for v in value:
            yield from nodes(v, kind)


def pandoc(source, target="json", filtered=False):
    args = ["pandoc", "-f", FORMAT, "-t", target, "--wrap=none", "--no-highlight"]
    if filtered:
        args.append("--lua-filter=tools/book_images.lua")
    return subprocess.run(args, input=source, text=True, capture_output=True,
                          check=True, cwd=ROOT).stdout


def pipe_cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])]


def md_tables(source):
    groups, current = [], []
    for line in source.splitlines() + [""]:
        if line.startswith("|") and line.rstrip().endswith("|"):
            current.append(line)
        elif current:
            groups.append(current)
            current = []
    shapes = []
    for group in groups:
        assert len(group) >= 2, group
        cells = [pipe_cells(line) for line in group]
        assert all(re.fullmatch(r":?-+:?", x.replace(" ", "")) for x in cells[1]), group
        n = len(cells[0])
        assert all(len(row) == n for row in cells), (n, [len(x) for x in cells], group)
        shapes.append([n, len(cells)-2, [len(row) for row in cells[2:]]])
    return shapes


def ast_table_shapes(ast):
    shapes = []
    for table in nodes(ast, "Table"):
        c = table["c"]
        body_rows = [r for body in c[4] for r in body[2]+body[3]]
        shapes.append([len(c[2]), len(body_rows), [len(row[1]) for row in body_rows]])
    return shapes


checks = []
chapters = {}
for path in sorted((ROOT/"manuscript").glob("*/*.md")):
    rel = str(path.relative_to(ROOT))
    old = BASE/rel
    source = path.read_text()
    old_anchors = re.findall(r"\{#([^\s}]+)", old.read_text())
    anchors = re.findall(r"\{#([^\s}]+)", source)
    assert len(anchors) == len(set(anchors)), rel
    assert [a for a in anchors if a in set(old_anchors)] == old_anchors, rel
    ast = json.loads(pandoc(source))
    expected = md_tables(source)
    actual = ast_table_shapes(ast)
    assert actual == expected, (rel, actual, expected)
    chapters[rel] = {"sha256": sha(path), "baseline_sha256": sha(old),
                     "changed": path.read_bytes() != old.read_bytes(),
                     "old_anchor_count": len(old_anchors),
                     "pipe_table_count": len(expected),
                     "pipe_table_shapes_match_AST": True}
checks.append("all_29_chapters_preserve_old_anchor_identities_and_source_table_cells")

# Complete newly introduced question stems: count every original subquestion.
expected_questions = {
    "os-ex2-7":2, "os-ex5-8":2, "os-ex5-9":3, "os-ex6-7":4,
    "os-ex6-8":3, "os-ex7-6":4, "os-ex7-7":3,
    "cn-ex3-12":4, "cn-ex4-10":2, "cn-ex4-11":3, "cn-ex4-12":5,
    "cn-ex4-13":3, "cn-ex5-8":3, "cn-ex5-9":4, "cn-ex6-8":4, "cn-ex6-9":3,
}
question_records = {}
for path in sorted((ROOT/"manuscript").glob("*/*.md")):
    source = path.read_text()
    for anchor, count in expected_questions.items():
        match = re.search(r"^### .*\{#"+re.escape(anchor)+r"\}\s*$", source, re.M)
        if not match:
            continue
        tail = source[match.end():]
        stem = tail.split("**解析。**", 1)[0]
        actual = [int(x) for x in re.findall(r"^（(\d+)）", stem, re.M)]
        assert actual == list(range(1,count+1)), (anchor, actual, count)
        adapted = "】改编" in stem
        assert adapted == (anchor in {"cn-ex4-12","cn-ex5-8","cn-ex5-9"}), anchor
        question_records[anchor] = {"manuscript": str(path.relative_to(ROOT)),
                                    "complete_numbered_subquestions": actual,
                                    "identity": "adapted" if adapted else "exam_question"}
assert set(question_records) == set(expected_questions)
checks.append("seven_OS_and_nine_CN_complete_stems_with_52_numbered_subquestions")
checks.append("CN_six_exam_questions_and_three_explicit_adaptations")

# Reconcile the converted CO code records with the independently saved old AST.
co4 = (ROOT/"manuscript/CO/04_指令系统与程序表示.md").read_text()
co6 = (ROOT/"manuscript/CO/06_流水线与并行处理.md").read_text()
old4 = json.loads((HERE/"04_指令系统与程序表示_baseline_AST_tables.json").read_text())
asm = next(t for t in old4 if t["head"][0][0]["text"] == "行号")
expected = [" ".join(" ".join(c["text"] for c in row).split()) for row in asm["rows"]]
block = next(b["c"][1] for b in nodes(json.loads(pandoc(co4)),"CodeBlock")
             if "00401025" in b["c"][1])
assert [" ".join(line.split()) for line in block.splitlines()] == expected
old6 = json.loads((HERE/"06_流水线与并行处理_baseline_AST_tables.json").read_text())
formats = next(t for t in old6 if t["head"][0][1]["text"] == "汇编格式")
block = next(b["c"][1] for b in nodes(json.loads(pandoc(co6)),"CodeBlock")
             if b["c"][1].startswith("ADD "))
assert [" ".join(line.split()) for line in block.splitlines()] == [row[1]["text"] for row in formats["rows"]]
checks.append("CO_16_assembly_records_and_five_instruction_formats_preserved")

fixture = "| 指令 | 操作 |\n|---|---|\n| `ADD Rs, Rd` | `a[i]` |\n"
tex = pandoc(fixture,"latex",True)
assert not re.search(r"(?:^|&)\s*\\allowbreak\{\}",tex,re.M)
assert r"\texttt{ADD\ Rs,}\allowbreak{}\texttt{\ Rd}" in tex
checks.append("shared_Code_filter_removes_initial_bare_penalty_and_preserves_internal_break")

# Inspect actual SVG text rather than only the author drawing constants.
svg = ET.parse(ROOT/"figures/CN25_packets_2012.svg")
hex_rows = [" ".join(t.split()).lower() for node in svg.iter()
            if node.tag.endswith("text")
            for t in ["".join(node.itertext())]
            if re.fullmatch(r"(?:[0-9a-fA-F]{2}\s+){19}[0-9a-fA-F]{2}", t.strip())]
assert len(hex_rows) == 12
packet_rows = [hex_rows[i]+" "+hex_rows[i+1] for i in range(0,12,2)]
cn = json.loads((ROOT/"editorial/revision3/CN_independent_sources/results.json").read_text())
expected = [p["first_40_bytes"] for p in cn["calculations"]["2012q47"]["packets"]]
expected += [cn["calculations"]["2012q47"]["server_original"]["first_40_bytes"]]
assert packet_rows == expected
checks.append("CN_2012_actual_SVG_all_240_hex_bytes_match_independent_source_transcription")

payload = {"status":"PASS_CONTENT_FIELD_INTEGRITY", "checks":checks,
           "chapters":chapters, "new_question_stems":question_records,
           "new_subquestion_count":sum(expected_questions.values()),
           "shared_lua_sha256":sha(ROOT/"tools/book_images.lua"),
           "scope":"Editable source identities and content fields only. No lecture PDF, layout, pagination, cropping, or visual inspection."}
(HERE/"final_content_integrity.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":payload["status"],"chapters":len(chapters),
                  "changed_chapters":sum(c["changed"] for c in chapters.values()),
                  "source_tables":sum(c["pipe_table_count"] for c in chapters.values()),
                  "new_complete_questions":len(question_records),
                  "new_subquestions":sum(expected_questions.values())},ensure_ascii=False))
