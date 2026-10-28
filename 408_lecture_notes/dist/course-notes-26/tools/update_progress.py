#!/usr/bin/env python3
"""Record the observed status without treating source mapping as full verification."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz
from build_notes import build_input_fingerprint

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


records = []
for ch in sorted((ROOT / 'chapters').iterdir()):
    if not ch.is_dir() or not (ch / 'notes.pdf').exists():
        continue
    with fitz.open(ch / 'notes.pdf') as doc:
        pages = len(doc)
    sources = ch / 'sources'
    coverage = read(sources / 'course_coverage.json')
    sync = read(sources / 'content-sync.json')
    current = (sync['canonical_sha256'] == digest(ch / 'content.md') and
               sync['markdown_sha256'] == digest(ch / 'notes.md'))
    inputs = sources / 'build-inputs.json'
    if inputs.exists():
        current = current and read(inputs) == build_input_fingerprint(ch)
    review_path = sources / 'visual_review.json'
    qa = read(sources / 'qa.json')
    visual = False
    if review_path.exists():
        review = read(review_path)
        visual = (qa.get('human_visual_review') == 'passed' and
                  review.get('status') == 'passed' and
                  review.get('pdf_sha256') == digest(ch / 'notes.pdf') and
                  review.get('viewed_pages') == list(range(1, pages + 1)))
    records.append({'id': ch.name, 'pages': pages,
                    'lecture_files': len(coverage.get('lecture_files', [])),
                    'content_current': current, 'visual': 'passed' if visual else 'pending',
                    'coverage_unresolved': coverage.get('unresolved', [])})

now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
out = ROOT / 'sources'
(out / 'progress.json').write_text(json.dumps({'status': 'in_progress', 'updated_utc': now,
                                               'chapters': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
lines = ['# 四科笔记检查点', '', f'更新时间：{now}。王道课件为主母本。课件映射数和未决条目数不能证明每幅源图已复核；视觉状态仅指对应指纹的 PDF 版面。', '',
         '| 章 | 页数 | 映射课件 | 来源未决条目 | PDF对应正文及已记录构建输入 | PDF视觉 |',
         '|---|---:|---:|---:|---|---|']
for r in records:
    lines.append(f"| {r['id']} | {r['pages']} | {r['lecture_files']} | {len(r['coverage_unresolved'])} | {'是' if r['content_current'] else '需重建'} | {'已复核' if r['visual'] == 'passed' else '待复核'} |")
lines += ['', '具体未决范围见各章 sources/course_coverage.json。旧构建未保存全部输入指纹时，正文一致性依据 content-sync.json；视觉记录与 PDF 指纹绑定。', '']
(out / 'progress.md').write_text('\n'.join(lines), encoding='utf8')
print(f'{len(records)} chapters; updated {now}')
