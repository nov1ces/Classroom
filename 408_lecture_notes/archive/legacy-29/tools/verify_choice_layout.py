#!/usr/bin/env python3
"""Verify source preservation and the coordinates of every printed choice set."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

import fitz

from book_choices import ROMAN, transform

ROOT = Path(__file__).resolve().parents[1]
NAMES = dict(DS='数据结构', CO='计算机组成原理', OS='操作系统', CN='计算机网络')
FORMAT = 'markdown+raw_tex+tex_math_dollars+tex_math_single_backslash'
OUT = ROOT / 'editorial/final'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ast(path):
    return json.loads(subprocess.check_output(['pandoc', '-f', FORMAT, '-t', 'json', str(path)], cwd=ROOT))


def nodes(value, kind):
    if isinstance(value, dict):
        if value.get('t') == kind:
            yield value
        for child in value.values():
            yield from nodes(child, kind)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child, kind)


def reader_stream(value):
    if isinstance(value, dict):
        kind = value.get('t')
        if kind == 'Str':
            return value['c']
        if kind in {'Space', 'SoftBreak', 'LineBreak'}:
            return ' '
        if kind in {'Code', 'CodeBlock', 'Math', 'RawInline', 'RawBlock'}:
            return value['c'][-1]
        if kind == 'OrderedList':
            attrs, items = value['c']
            if attrs[1]['t'] == 'UpperRoman':
                return ''.join(ROMAN[attrs[0] + i - 1] + '.' + reader_stream(item)
                               for i, item in enumerate(items))
            return reader_stream(items)
        return ''.join(reader_stream(child) for child in value.values())
    if isinstance(value, list):
        return ''.join(reader_stream(child) for child in value)
    return ''


def normalize(value):
    return re.sub(r'\s+', '', value)


def source_checks():
    books = []
    source_sha = {}
    for sub in NAMES:
        chapters = []
        for path in sorted((ROOT / 'manuscript' / sub).glob('[0-9][0-9]_*.md')):
            original = ast(path)
            adjusted, groups = transform(original)
            assert normalize(reader_stream(original)) == normalize(reader_stream(adjusted)), path
            for kind in ['Code', 'CodeBlock', 'Math', 'Image', 'Header', 'Table']:
                signature = lambda doc: Counter(json.dumps(n, ensure_ascii=False, sort_keys=True) for n in nodes(doc, kind))
                assert signature(original) == signature(adjusted), (path, kind)
            # Every actual A. marker in the input is accounted for by a full A-D group.
            letters = sum(len(re.findall(r'(?<![A-Za-z0-9])A\.', node['c']))
                          for node in nodes(original, 'Str'))
            choices = sum(g['kind'] == 'choices' for g in groups)
            assert letters == choices, (path, 'unhandled A-D set', letters, choices)
            code_choices = [node['c'][-1] for node in nodes(original, 'CodeBlock')
                            if re.findall(r'^([A-D])\. ', node['c'][-1], re.M) == list('ABCD')]
            relative = str(path.relative_to(ROOT))
            source_sha[relative] = sha(path)
            chapters.append(dict(path=relative, sha256=source_sha[relative],
                choices=choices, statements=sum(g['kind'] == 'statements' for g in groups),
                already_aligned_monospaced_code_choices=len(code_choices),
                complete_text_preserved=True, code_math_images_headings_tables_preserved=True))
        books.append(dict(subject=sub, chapters=chapters,
            choices=sum(c['choices'] for c in chapters), statements=sum(c['statements'] for c in chapters)))
    report = dict(status='PASS', scope='29章全量源码与选项转换核对；忽略排版空白，正文字符及代码、公式、图、标题、表格保全。',
        source_sha256=source_sha, books=books,
        choices=sum(b['choices'] for b in books), statements=sum(b['statements'] for b in books))
    OUT.mkdir(exist_ok=True)
    (OUT / 'choice_source_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:report[k] for k in ['status', 'choices', 'statements']}, ensure_ascii=False), flush=True)
    return report


def pdf_checks():
    OUT.mkdir(exist_ok=True)
    books = []
    for sub in NAMES:
        build = ROOT / 'build' / sub
        manifest = json.loads((build / 'build_manifest.json').read_text())
        _, groups = transform(ast(build / 'body.md'))
        doc = fitz.open(ROOT / manifest['pdf'])
        names = doc.resolve_names()
        log = (build / 'xelatex-3.log').read_text(errors='replace')
        columns = {ident:int(n) for ident,n in re.findall(r'BOOKCHOICES:([^:]+):columns=([124])', log)}
        assert len(columns) == sum(g['kind'] == 'choices' for g in groups)
        group_anchors = {}
        for group in groups:
            ident = group['id']
            assert ident in names, (sub, ident, 'missing PDF destination')
            dest = names[ident]
            group_anchors[ident] = (dest['page'], dest['to'][0], doc[dest['page']].rect.height - dest['to'][1])
        records = []
        for group in groups:
            ident = group['id']
            page_index, x, y = group_anchors[ident]
            page = doc[page_index]
            next_y = min([top for other,(p,_,top) in group_anchors.items()
                          if other != ident and p == page_index and top > y + 2] + [page.rect.height - 35])
            positions = []
            for label in group['labels']:
                target = unicodedata.normalize('NFKC', label + '.')
                candidates = [w for w in page.get_text('words')
                    if unicodedata.normalize('NFKC', w[4]) == target
                    and y - 2 < w[1] < next_y and w[0] >= x - .6]
                assert candidates, (sub, ident, label, 'missing printed label', page_index + 1, x, y, next_y)
                positions.append(min(candidates, key=lambda w: (w[1], w[0])))
            count = columns[ident] if group['kind'] == 'choices' else 1
            assert abs(positions[0][0] - x) < .6, (sub, ident, 'unexpected first-line indent')
            for i,pos in enumerate(positions):
                if count == 1:
                    assert abs(pos[0] - x) < .6, (sub, ident, 'vertical label misalignment')
                    if i:
                        assert pos[1] > positions[i-1][1] + 3
                else:
                    row, col = divmod(i, count)
                    assert abs(pos[1] - positions[row * count][1]) < .6, (sub, ident, 'row misalignment')
                    if row:
                        assert abs(pos[0] - positions[col][0]) < .6, (sub, ident, 'column misalignment')
                    if col:
                        assert pos[0] > positions[i-1][0] + 20
            if count == 4:
                gaps = [positions[i+1][0] - positions[i][0] for i in range(3)]
                assert max(gaps) - min(gaps) < .6, (sub, ident, 'unequal grid columns')
            records.append(dict(id=ident, kind=group['kind'], physical_page=page_index+1,
                page_label=page.get_label(), columns=count, labels=group['labels'],
                label_positions=[[round(w[0],3),round(w[1],3)] for w in positions], alignment='PASS'))
        books.append(dict(subject=sub, pdf=manifest['pdf'], sha256=sha(ROOT / manifest['pdf']),
            choices=sum(r['kind']=='choices' for r in records), statements=sum(r['kind']=='statements' for r in records),
            groups=records, status='PASS'))
        print(json.dumps(dict(subject=sub, groups=len(records), status='PASS'), ensure_ascii=False), flush=True)
    report = dict(status='PASS', scope='逐组检查最终PDF中的全部选项及题组标签：无首行缩进、行列对齐、组内不跨页、标签齐全；人工预览另记。', books=books)
    (OUT / 'choice_pdf_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()
    if args.pdf:
        pdf_checks()
    else:
        source_checks()
