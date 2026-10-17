#!/usr/bin/env python3
"""Inspect PDF structure and render every page; human visual review is separate."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NAMES = dict(DS='数据结构', CO='计算机组成原理', OS='操作系统', CN='计算机网络')

def audit(subject, partial=False):
    title = NAMES[subject]
    build = ROOT / 'build' / subject
    mf = json.loads((build / 'build_manifest.json').read_text())
    pdf = ROOT / mf['pdf']
    if mf['partial'] and not partial:
        raise ValueError('Refusing to audit a preview as a final book')
    doc = fitz.open(pdf)
    out = ROOT / 'editorial' / 'full' / 'pdf' / subject
    render = build / 'rendered'
    out.mkdir(parents=True, exist_ok=True)
    render.mkdir(parents=True, exist_ok=True)
    for old in render.glob('*.png'): old.unlink()
    report = dict(subject=subject, pdf=mf['pdf'],
        sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(), page_count=len(doc),
        page_labels=doc.get_page_labels(), bookmarks=doc.get_toc(), pages=[],
        bad_internal_links=[], internal_link_count=0,
        scope='PDF结构、文本边界与实际逐页渲染；不能代替知识核验或人工视觉检查。')
    texts = []
    for i, page in enumerate(doc):
        spans = [s for b in page.get_text('dict')['blocks'] if b['type'] == 0
                 for ln in b['lines'] for s in ln['spans']]
        outside = []
        for s in spans:
            r = fitz.Rect(s['bbox'])
            if r.x0 < -1 or r.y0 < -1 or r.x1 > page.rect.width + 1 or r.y1 > page.rect.height + 1:
                outside.append(dict(text=s['text'], bbox=list(r)))
        text = page.get_text()
        texts.append(text)
        report['pages'].append(dict(physical_page=i + 1, label=page.get_label(),
            characters=len(text), outside=outside, replacement_glyphs=text.count('\ufffd'),
            media_box=list(page.rect),
            text_sizes=sorted({round(s['size'], 2) for s in spans})))
        for link in page.get_links():
            if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                report['internal_link_count'] += 1
                if not (0 <= link.get('page', -1) < len(doc)):
                    report['bad_internal_links'].append(dict(source_page=i + 1, link=str(link)))
        page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35), alpha=False).save(render / f'page_{i+1:03}.png')
    log = (build / f'{subject}.log').read_text(errors='replace')
    kinds = {'missing_glyph': 'Missing character:', 'overfull': 'Overfull',
             'undefined': 'undefined', 'float_too_large': 'Float too large',
             'duplicate_destination': 'destination with the same identifier'}
    report['latex'] = {name: [line for line in log.splitlines() if term.lower() in line.lower()]
                       for name, term in kinds.items()}
    report['embedded_font_names'] = sorted({font[3] for p in doc for font in p.get_fonts()})
    fm = json.loads((ROOT / 'editorial/verification/font_manifest.json').read_text())
    report['font_faces_verified'] = all(fm[role]['normal']['index'] == idx
        for role, idx in [('main', 2), ('sans', 2), ('mono', 7)]) and '.ttc:2]' in log and '.ttc:7]' in log
    report['font_note'] = 'SC由TTC面索引2/2/7及cmap确定；共享CFF的jp内部名不表示选用了日文字形。'
    leak = []
    for pattern in [r'ERR[-‑—]', r'做题本', r'你原选', r'原错选', r'你的错题', r'个人错题', r'原作答']:
        for i, text in enumerate(texts):
            if re.search(pattern, text): leak.append(dict(page=i+1, pattern=pattern))
    report['reader_text_policy_findings'] = leak
    contacts = []
    # Four pages per sheet retain readable page geometry for an overview.
    for start in range(0, len(doc), 4):
        sheet = Image.new('RGB', (1660, 2430), '#d5d5d5')
        draw = ImageDraw.Draw(sheet)
        for j, n in enumerate(range(start, min(start + 4, len(doc)))):
            im = Image.open(render / f'page_{n+1:03}.png').convert('RGB')
            im.thumbnail((805, 1140))
            x = 15 + (j % 2) * 830
            y = 40 + (j // 2) * 1210
            draw.text((x, y-22), f'{subject} Physical {n+1} / label {doc[n].get_label()}', fill='black')
            sheet.paste(im, (x, y))
        name = f'contact_{start//4+1:03}.png'
        sheet.save(render / name)
        contacts.append(dict(path=str((render / name).relative_to(ROOT)),
                             pages=list(range(start+1,min(start+4,len(doc))+1))))
    report['contact_sheets'] = contacts
    report['all_pages_rendered'] = True
    report['visual_status'] = '未由本脚本判断；人工检查记录另存，须绑定本PDF的SHA256。'
    report['structural_status'] = 'PASS' if not any([
        report['bad_internal_links'], *report['latex'].values(),
        not report['font_faces_verified'], leak,
        any(p['outside'] or p['replacement_glyphs'] for p in report['pages'])]) else 'REVIEW'
    (out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (out / 'pdf_text.txt').write_text('\n\f\n'.join(texts))
    print(json.dumps(dict(subject=subject, pages=len(doc), bookmarks=len(report['bookmarks']),
        links=report['internal_link_count'], status=report['structural_status'],
        warnings={k:len(v) for k,v in report['latex'].items()},
        policy_findings=leak), ensure_ascii=False), flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--subjects', nargs='+', choices=list(NAMES), default=list(NAMES))
    p.add_argument('--partial', action='store_true')
    args = p.parse_args()
    for sub in args.subjects: audit(sub, args.partial)

if __name__ == '__main__': main()
