#!/usr/bin/env python3
"""对实际落盘讲义做机械检查；检查通过不表示知识/题源/视觉通过。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ANCHOR = re.compile(r'\{#([^\s}]+)')
KID = re.compile(r'\b(?:DS|CO|OS|CN)-\d{2}-\d{2}\b', re.I)
YEAR = re.compile(r'【(\d{4})([^】]*)】')
BOOK = re.compile(r'〖([^〗]*)〗')
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(#([^\s)]+)\)')
IMAGE = re.compile(r'!\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)')
RULES = [
    ('PERSONAL_RECORD', 'error', re.compile(r'你(?:原|当时)?选|原(?:错)?选|错选|你的(?:另一道)?错题|个人错题|ERR[-‑－](?:DS|CO|OS|CN)[-‑－]')),
    ('WORKBOOK_TITLE', 'error', re.compile(r'做题本')),
    ('LONG_PROVENANCE', 'error', re.compile(r'(?:来源[：:].*(?:PDF|第\s*\d+\s*题|印刷|个人))|(?:PDF\s*第?\s*\d+\s*页)')),
    ('UNSUPPORTED_FREQUENCY', 'review', re.compile(r'高频(?!率)|近年趋势|大题常考|常考|历年.*?%')),
    ('PLACEHOLDER', 'review', re.compile(r'TODO|待补(?!齐|偿|足|给|货)(?:充|选|图|题|写|解析)?|后续补|解析略|此处略|待完善|尚未撰写')),
    ('JUMP_STEP', 'review', re.compile(r'显然|代入即可|类似可得|不难看出|容易得到')),
    ('TEMPLATE_PROMOTION', 'review', re.compile(r'终极指南|一文搞懂|高分密码|接下来让我们|相信通过本')),
]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def inspect(path: Path) -> dict:
    content = path.read_text(encoding='utf-8')
    findings = []
    def report(code, severity, line, message, sample=''):
        findings.append(dict(code=code, severity=severity, line=line, message=message, sample=sample[:240]))
    anchors, targets, images, years, book_labels = [], [], [], [], []
    fences = []
    math_open = None
    for n, line in enumerate(content.splitlines(), 1):
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            token = fence.group(1)[0]
            if not fences:
                fences = [(token, n)]
            elif fences[-1][0] == token:
                fences = []
            continue
        for code, severity, pattern in RULES:
            if pattern.search(line):
                report(code, severity, n, '按当前用户标准或人工审读要求检查', line)
        if fences:
            continue
        for code_span in re.finditer(r'`([^`\n]*)`', line):
            if code_span.group(1).count('$')>=2:
                report('MATH_IN_CODE', 'review', n, '反引号内的数学定界符会按字面显示，检查是否误把公式排成代码', code_span.group(1))
        if re.match(r'^\s*\$\$\s*$', line):
            math_open = n if math_open is None else None
        for a in ANCHOR.findall(line):
            anchors.append(dict(id=a, line=n))
        for a in LINK.findall(line):
            targets.append(dict(id=a, line=n))
        for image in IMAGE.findall(line):
            images.append(dict(path=image, line=n))
            if '://' not in image:
                candidates = [path.parent/image, ROOT/image, ROOT/'figures'/image,
                              ROOT/'figures'/path.parent.name/image,
                              ROOT/'figures'/path.parent.name.lower()/image]
                if not any(c.exists() for c in candidates):
                    report('MISSING_IMAGE', 'error', n, '图片路径未在正文目录/项目/图稿目录找到', image)
        for y, suffix in YEAR.findall(line):
            years.append(dict(year=int(y), suffix=suffix, line=n))
            if int(y) < 2009 or int(y) > 2026:
                report('YEAR_RANGE', 'error', n, '408真题年份超出当前可能核验范围2009—2026', y)
            if suffix.strip():
                report('LONG_YEAR_LABEL', 'review', n, '真题短标签宜只含年份，改编身份写在标签外', f'【{y}{suffix}】')
        for b in BOOK.findall(line):
            book_labels.append(dict(label=b, line=n))
            if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?-\d{3}', b):
                report('BOOK_LABEL_FORMAT', 'error', n, '非真题短标签采用节号-三位题号', b)
        for math in re.finditer(r'(?<!\$)\$(?!\$)([^$\n]*)(?<!\$)\$(?!\$)', line):
            formula = math.group(1)
            if re.search(r'[\u3400-\u9fff]', formula) and '\\text' not in formula and '\\mathrm' not in formula:
                report('CJK_IN_MATH', 'review', n, '检查中文是否需移到数学模式外或使用text', formula)
    if fences:
        report('UNCLOSED_FENCE', 'error', fences[0][1], '代码围栏未关闭')
    if math_open:
        report('UNCLOSED_DISPLAY_MATH', 'error', math_open, '独占行显示公式未关闭')
    counts = Counter(a['id'] for a in anchors)
    for a in anchors:
        if counts[a['id']] > 1:
            report('DUPLICATE_ANCHOR', 'error', a['line'], '同一文件锚点重复', a['id'])
    return dict(path=str(path.relative_to(ROOT)), sha256=sha(content), characters=len(content),
                lines=len(content.splitlines()), headings=sum(bool(re.match(r'^#{1,6}\s', l)) for l in content.splitlines()),
                anchors=anchors, local_link_targets=targets, images=images,
                real_exam_labels=years, non_exam_labels=book_labels,
                knowledge_ids_mentioned=sorted(set(x.upper() for x in KID.findall(content))),
                findings=findings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', choices=['DS','CO','OS','CN'])
    parser.add_argument('--output', type=Path, default=OUT/'mechanical_checks.json')
    args = parser.parse_args()
    manuscript = ROOT/'manuscript'
    paths = sorted((manuscript/args.subject).glob('*.md')) if args.subject else sorted(manuscript.glob('*/*.md'))
    files = [inspect(p) for p in paths if not p.name.startswith('_')]
    cross_findings=[]
    for subject in ['DS','CO','OS','CN']:
        book = [f for f in files if f['path'].split('/')[1] == subject]
        anchor_files=defaultdict(list)
        for f in book:
            for a in f['anchors']:
                anchor_files[a['id']].append((f['path'],a['line']))
        for a, positions in anchor_files.items():
            if len(positions)>1:
                cross_findings.append(dict(code='DUPLICATE_BOOK_ANCHOR',severity='error',subject=subject,anchor=a,positions=positions))
        for f in book:
            for t in f['local_link_targets']:
                if t['id'] not in anchor_files:
                    cross_findings.append(dict(code='UNRESOLVED_BOOK_LINK',severity='error',path=f['path'],line=t['line'],anchor=t['id']))
    counts=Counter(i['code'] for f in files for i in f['findings'])
    counts.update(i['code'] for i in cross_findings)
    data=dict(generated_at=datetime.now(timezone.utc).isoformat(),scope='实际落盘Markdown机械检查；不是知识、题源或PDF视觉通过',
              root=str(ROOT),files=files,cross_file_findings=cross_findings,counts=dict(counts),
              inspected_file_count=len(files),total_characters=sum(f['characters'] for f in files))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(files=len(files),characters=data['total_characters'],counts=dict(counts),output=str(args.output)),ensure_ascii=False))


if __name__=='__main__':
    main()
