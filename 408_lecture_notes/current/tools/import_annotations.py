#!/usr/bin/env python3
"""Typeset user annotations in unused PDF margins without rebuilding body pages.

The unannotated PDFs and protected source hashes are retained in sources/annotations.
Every overlay is searchable vector PDF. Original page streams, text coordinates,
links and page geometry are retained and checked independently of margin layout.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

import fitz

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'sources/annotations'
BUILD = DATA / 'build'
LEFT, RIGHT, TOP, BOTTOM = 391.35, 527.40, 82.0, 765.0
WIDTH = RIGHT - LEFT
GAP = 13.0
SUBJECTS = {'DS': '数据结构', 'CO': '计算机组成原理', 'OS': '操作系统', 'CN': '计算机网络'}


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def esc(text):
    return ''.join({'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}.get(c, c)
                   for c in str(text))


SYMBOLS = {'≥': r'\ge', '≤': r'\le', '≡': r'\equiv', '≈': r'\approx',
           '×': r'\times', '÷': r'\div', '−': '-', '＋': '+', '＝': '=',
           '＜': '<', '≫': r'\gg', '→': r'\to', '↑': r'\uparrow', '↓': r'\downarrow',
           '∑': r'\sum', 'Σ': r'\sum', 'Θ': r'\Theta', 'α': r'\alpha',
           'τ': r'\tau', 'φ': r'\varphi', 'μ': r'\mu', 'ℓ': r'\ell',
           '∞': r'\infty', '⋯': r'\cdots', '…': r'\ldots', '⊕': r'\oplus',
           '∧': r'\land', '¬': r'\neg', '⌈': r'\lceil', '⌉': r'\rceil',
           '⌊': r'\lfloor', '⌋': r'\rfloor', '·': r'\cdot', '／': '/', '｜': '|'}
SUP = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁻ⁿᵏʰʳᴿ', '0123456789-nkhrR'))
SUB = dict(zip('₀₁₂₃₄₅₆₇₈₉₊₋₌ₐₖₙᵢᵣⱼᵦ', '0123456789+-=akn irjb'.replace(' ', '')))


def mathtex(text):
    text = text.strip()
    # Normalize the source's textual summation conventions before token conversion.
    text = text.replace('Σ(r=1..i−1)', r'\sum_{r=1}^{i-1}')
    text = text.replace('∑ᵢ≥₂', r'\sum_{i\ge2}').replace('∑ₖ≥₁', r'\sum_{k\ge1}')
    text = text.replace('Σᵢ₌₁ⁿ', r'\sum_{i=1}^{n}')
    text = text.replace('Σᵣ₌₀ʰ⁻²', r'\sum_{r=0}^{h-2}').replace('Σᵣ₌₀ʰ⁻¹', r'\sum_{r=0}^{h-1}')
    text = re.sub(r'\^\(([^()]*)\)', r'^{\1}', text)
    text = re.sub(r'\^(\d+|[A-Za-z])', r'^{\1}', text)
    text = re.sub(r'√\(([^()]*)\)', r'\\sqrt{\1}', text)
    text = re.sub(r'√([A-Za-z]|\d+)', r'\\sqrt{\1}', text)
    text = re.sub('[' + ''.join(SUP) + ']+', lambda m: '^{' + ''.join(SUP[c] for c in m[0]) + '}', text)
    text = re.sub('[' + ''.join(SUB) + ']+', lambda m: '_{' + ''.join(SUB[c] for c in m[0]) + '}', text)
    text = re.sub(r'([A-Za-z])_\{([^{}]+)\},_\{([^{}]+)\}', r'\1_{\2,\3}', text)
    # Commands include an empty group so a following variable cannot join the name.
    text = ''.join((SYMBOLS[c] + ' ' if SYMBOLS[c].startswith('\\') else SYMBOLS[c])
                   if c in SYMBOLS else c for c in text)
    text = re.sub(r'(?<![A-Za-z\\])(log|min|max|gcd|mod)(?![A-Za-z])', r'\\operatorname{\1}', text)
    text = re.sub(r'(?<![A-Za-z\\])(sum|ASL|OF|SF|CF|IPC|CPI|WPL|MSS|RTT|ACK)(?![A-Za-z])', r'\\mathrm{\1}', text)
    text = text.replace('%', r'\%').replace('&', r'\mathbin{\&}')
    # Permit native formula wrapping at the source's operators; never scale a box.
    text = re.sub(r'([=+,/<>])', r'\1\\allowbreak{}', text)
    return r'\(' + text + r'\)'


def prose(text):
    """Keep all source wording, with native math and breakable code punctuation."""
    chunks = re.split(r'([\u3400-\u9fff、。，；：“”（）～\n]+)', str(text))
    result = []
    for part in chunks:
        if not part:
            continue
        if re.search(r'[\u3400-\u9fff、。，；：“”（）～\n]', part):
            result.append(esc(part).replace('\n', r'\par '))
            continue
        if any(c in part for c in '①②③④⑤⑥⑦⑧⑨⑩'):
            result.append(''.join(r'{\symfont ' + c + '}' if c in '①②③④⑤⑥⑦⑧⑨⑩' else prose(c) for c in part))
            continue
        code = ('->' in part or '<<' in part or '>>' in part or ';' in part or
                re.search(r'\b(?:while|for|if|int|unsigned|return)\b', part) or
                ('_' in part and not any(c in part for c in 'Σ∑')))
        ismath = (not code and bool(re.search(r'[=<>≥≤√^∑Σ×÷⊕∧¬≡≈⌈⌊Θατφℓ]|[' + ''.join(SUP) + ''.join(SUB) + ']', part)))
        if ismath:
            result.append(mathtex(part))
        else:
            plain = []
            for c in part:
                if c in SYMBOLS:
                    plain.append(mathtex(c))
                elif c in SUP:
                    plain.append(r'\textsuperscript{' + esc(SUP[c]) + '}')
                elif c in SUB:
                    plain.append(r'\textsubscript{' + esc(SUB[c]) + '}')
                else:
                    plain.append(esc(c))
                if c in ',;=+/':
                    plain.append(r'\allowbreak{}')
            result.append(''.join(plain))
    return ''.join(result)


def preamble():
    fonts = (ROOT / 'common/fonts').as_posix() + '/'
    return r'''\documentclass{article}
\usepackage[paperwidth=136.05bp,paperheight=2000bp,margin=0bp]{geometry}
\usepackage{fontspec,xeCJK,amsmath,amssymb,mathtools,tikz,booktabs,array,xcolor}
\usetikzlibrary{arrows.meta,calc,positioning}
\setmainfont{NimbusRoman}[Path=@@F@@,Extension=.otf,UprightFont=*-Regular,BoldFont=*-Bold,ItalicFont=*-Italic]
\setCJKmainfont{NotoSerifSC-Regular.otf}[Path=@@F@@,BoldFont=NotoSerifSC-Bold.otf]
\newfontfamily\symfont{NotoSerifSC-Regular.otf}[Path=@@F@@]
\xeCJKsetup{PunctStyle=quanjiao,CJKmath=true}
\pagestyle{empty}\setlength{\parindent}{0pt}\setlength{\parskip}{2.5bp}
\setlength{\emergencystretch}{1em}
\definecolor{ink}{HTML}{466C82}
\definecolor{blue}{HTML}{DDEFF5}
\definecolor{pink}{HTML}{F7E0EB}
\definecolor{green}{HTML}{DFEFE6}
\definecolor{orange}{HTML}{FFF1B4}
\newsavebox{\annotationbox}
\begin{document}
\fontsize{8.5}{10.7}\selectfont
'''.replace('@@F@@', fonts)


def compile_pieces(pieces):
    BUILD.mkdir(parents=True, exist_ok=True)
    chunks = [preamble()]
    for i, piece in enumerate(pieces):
        measure = '132bp' if piece['kind'] == 'text' else '136.05bp'
        source = (r'\sbox{\annotationbox}{\begin{minipage}[t]{' + measure + '}'
                  r'\raggedright\fontsize{8.5}{10.7}\selectfont ' + piece['tex'] +
                  r'\end{minipage}}' + '\n' +
                  r'\typeout{ANNOTHEIGHT:' + str(i) + r':\the\ht\annotationbox:\the\dp\annotationbox}' + '\n' +
                  r'\noindent\usebox{\annotationbox}\par\newpage' + '\n')
        chunks.append(source)
        target = DATA / 'tex' / (piece['key'] + '.tex')
        target.parent.mkdir(exist_ok=True)
        target.write_text(piece['tex'] + '\n')
    chunks.append(r'\end{document}')
    (BUILD / 'sidebars.tex').write_text('\n'.join(chunks))
    env = os.environ.copy()
    env['TEXINPUTS'] = str(ROOT / 'common') + '//:' + env.get('TEXINPUTS', '')
    process = subprocess.run(['xelatex', '-no-shell-escape', '-interaction=nonstopmode',
                              '-halt-on-error', 'sidebars.tex'], cwd=BUILD, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (BUILD / 'compile-output.txt').write_text(process.stdout)
    if process.returncode:
        raise RuntimeError(process.stdout[-4500:])
    log = (BUILD / 'sidebars.log').read_text(errors='replace')
    missing = [line for line in log.splitlines() if 'Missing character' in line]
    if missing:
        raise RuntimeError('Missing glyphs: ' + '\n'.join(missing[:25]))
    doc = fitz.open(BUILD / 'sidebars.pdf')
    if len(doc) != len(pieces):
        raise RuntimeError(f'Expected {len(pieces)} overlay pages, got {len(doc)}')
    for i, (piece, page) in enumerate(zip(pieces, doc)):
        boxes = [b for typ, b in page.get_bboxlog() if typ != 'ignore-text']
        bounds = fitz.Rect(boxes[0])
        for b in boxes[1:]:
            bounds |= fitz.Rect(b)
        if bounds.x0 < -1.5 or bounds.x1 > WIDTH + 1.5:
            raise RuntimeError(f"Overlay exceeds margin width: {piece['key']}: {bounds}")
        reserve = piece.pop('reserve', 0)
        piece.update(source_page=i, clip=[0, max(0, bounds.y0 - 1), WIDTH, bounds.y1 + 1 + reserve],
                     height=bounds.y1 - max(0, bounds.y0 - 1) + 1 + reserve)
    return doc


def all_pdf_targets(manifest):
    return ([ROOT / 'books/408四科_强化笔记.pdf'] +
            [ROOT / 'books' / (name + '_强化笔记.pdf') for name in SUBJECTS.values()] +
            [ROOT / 'chapters' / c['id'] / 'notes.pdf' for c in manifest['chapters']])


def snapshot(refresh=False):
    DATA.mkdir(parents=True, exist_ok=True)
    manifest = read(ROOT / 'manifest.json')
    record = DATA / 'baseline.json'
    old = read(record) if record.exists() else None
    if old and not refresh:
        prior = read(DATA/'checks.json')['outputs'] if (DATA/'checks.json').exists() else []
        known_outputs = {x['file']:x['after_sha256'] for x in prior}
        for source in old['files']:
            current = ROOT/source['file']
            if sha(current) not in {source['sha256'],known_outputs.get(source['file'])}:
                raise RuntimeError('PDF changed since the recorded import; refusing to replace it: '+source['file'])
        for rel,expected in old['protected_sources'].items():
            if sha(ROOT/rel) != expected:
                raise RuntimeError('Body source changed; rebuild clean PDFs before refreshing the sidebar baseline: '+rel)
        return old
    if old and refresh:
        for path in all_pdf_targets(manifest):
            with fitz.open(path) as doc:
                if 'codex-sidebar-import:' in (doc.metadata.get('keywords') or ''):
                    raise RuntimeError('Cannot snapshot annotated PDFs. Rebuild clean PDFs first.')
    protected = {}
    for directory in ['chapters', 'books', 'common', 'solutions']:
        for p in (ROOT / directory).rglob('*'):
            if not p.is_file() or p.is_symlink():
                continue
            if p.suffix.lower() in {'.md', '.tex', '.json', '.svg', '.cls', '.otf', '.ttf'}:
                rel = p.relative_to(ROOT)
                if not any(s in {'build', 'previews', 'sources'} for s in rel.parts):
                    protected[str(rel)] = sha(p)
    # The independent solutions edition remains outside this import.
    protected['books/408强化例题解析.pdf'] = sha(ROOT / 'books/408强化例题解析.pdf')
    records = []
    for p in all_pdf_targets(manifest):
        rel = p.relative_to(ROOT)
        target = DATA / 'baseline' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        records.append({'file': str(rel), 'sha256': sha(p)})
    value = {'manifest': manifest, 'files': records, 'protected_sources': protected}
    write(record, value)
    return value


def intervals(page):
    free = [(TOP, BOTTOM)]
    for typ, bbox in page.get_bboxlog():
        x0, y0, x1, y1 = bbox
        if typ == 'ignore-text' or x1 < LEFT - 2 or x0 > RIGHT + 2 or y1 < TOP or y0 > BOTTOM:
            continue
        a, b = max(TOP, y0 - 5), min(BOTTOM, y1 + 5)
        free = subtract(free, a, b)
    return [(a, b) for a, b in free if b - a >= 16]


def subtract(free, start, end):
    result = []
    for a, b in free:
        if end <= a or start >= b:
            result.append((a, b))
        else:
            if a < start:
                result.append((a, start))
            if end < b:
                result.append((end, b))
    return result


def infer_context(item, baseline, manifest):
    p = item['location']['pdf_page']
    chapter = next(c for c in manifest['chapters']
                   if c['combined_start_page'] <= p < c['combined_start_page'] + c['pages'])
    ident = chapter['id']
    if not item['chapter'].startswith(SUBJECTS[ident[:2]]):
        raise ValueError(f"Wrong chapter mapping for {item['id']}")
    loc = item['location']
    bbox = loc['anchor_bbox']
    if abs(baseline[p-1].rect.width - bbox['page_width']) > .1:
        raise ValueError('Coordinate system mismatch')
    # Validate the supplied anchor box against original page characters, allowing
    # font encodings and line-wrap spaces to differ from the supplied anchor text.
    nearby = baseline[p-1].get_textbox(fitz.Rect(bbox['x0']-2, bbox['y0']-3, bbox['x1']+2, bbox['y1']+3))
    if not nearby.strip():
        raise ValueError(f"Empty anchor for {item['id']}")
    title = loc['anchor_text']
    if loc['anchor_type'] == 'example':
        examples = []
        for k in range(chapter['combined_start_page']-1, p):
            for b in baseline[k].get_text('blocks'):
                match = re.search(r'例\s*(\d+-\d+)', b[4])
                if match and (k < p-1 or b[1] <= bbox['y0'] + 3):
                    examples.append(match[1])
        if examples:
            title = '例 ' + examples[-1]
            questions=[]
            heading_y=0
            for block in baseline[p-1].get_text('blocks'):
                if re.search(r'例\s*'+re.escape(examples[-1])+r'(?!\d)',block[4]) and block[1] <= bbox['y0']+3:
                    heading_y=max(heading_y,block[1])
            for block in baseline[p-1].get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    if line['bbox'][0] < LEFT-8 and heading_y <= line['bbox'][1] <= bbox['y0']+3:
                        text=''.join(s['text'] for s in line['spans'])
                        match=re.match(r'^[（(](\d+)[）)]',text)
                        if match:questions.append(match[1])
            if questions and not re.fullmatch(r'例\s*\d+-\d+',loc['anchor_text']):
                title += ' · 第'+questions[-1]+'问'
    elif loc['anchor_type'] == 'code' and re.search(r'\b([A-Za-z_]\w*)\s*\(',title):
        title = re.search(r'\b([A-Za-z_]\w*)\s*\(',title)[1]
    elif len(title) > 20:
        title = item['section'].split()[0] + ' · ' + title[:16]
    return {'chapter_id': ident, 'chapter_start': chapter['combined_start_page'],
            'chapter_end': chapter['combined_start_page'] + chapter['pages'] - 1,
            'anchor_page': p, 'anchor_y': bbox['y0'], 'title': title, 'anchor_extracted': nearby.strip()}


def allocate_texts(pieces, free):
    bypage = collections.defaultdict(list)
    for piece in pieces:
        if piece['kind'] == 'text':
            bypage[piece['anchor_page']].append(piece)
    for number, group in sorted(bypage.items()):
        group.sort(key=lambda x: (x['anchor_y'], x['key']))
        # Search in reading order. Reserve enough room for remaining annotations.
        def fits(remaining, slots):
            for piece in remaining:
                chosen = next(((a, b) for a, b in slots if b-a >= piece['height']), None)
                if chosen is None:
                    return False
                slots = subtract(slots, chosen[0], chosen[0] + piece['height'] + GAP)
            return True
        if not fits(group, free[number]):
            raise RuntimeError(f'Annotations cannot all fit page {number} at the original sidebar font size')
        for i, piece in enumerate(group):
            candidates = []
            for a, b in free[number]:
                maximum = b - piece['height']
                if maximum < a:
                    continue
                desired = max(a, min(maximum, piece['anchor_y']))
                # Select the latest safe point up to the anchor, with a subpoint search.
                low, high = a, desired
                if not fits(group[i+1:], subtract(free[number], a, a+piece['height']+GAP)):
                    continue
                for _ in range(16):
                    mid = (low+high)/2
                    slots = [(max(c, mid+piece['height']+GAP), d) for c, d in free[number]
                             if d > mid+piece['height']+GAP]
                    if fits(group[i+1:], slots):
                        low = mid
                    else:
                        high = mid
                candidates.append((abs(low-piece['anchor_y']), low))
            if not candidates:
                raise RuntimeError('No safe ordered slot for ' + piece['key'])
            y = min(candidates)[1]
            piece.update(page=number, rect=[LEFT, y, RIGHT, y+piece['height']])
            free[number] = [(max(a, y+piece['height']+GAP), b) for a, b in free[number]
                            if b > y+piece['height']+GAP]


def allocate_figures(pieces, free):
    from functools import lru_cache
    groups = collections.defaultdict(list)
    for piece in pieces:
        if piece['kind'] == 'figure':
            groups[piece['chapter_id']].append(piece)
    for chapter, group in groups.items():
        first = group[0]
        slots = [(n,a,b) for n in range(first['chapter_start'],first['chapter_end']+1)
                 for a,b in free[n] if b-a >= min(p['height'] for p in group)]
        # Allocate contiguous runs to ascending page slots. Dynamic programming
        # preserves figure/panel reading order while finding room near the anchor.
        @lru_cache(None)
        def solve(i,j):
            if i == len(group):
                return (0, ())
            if j == len(slots):
                return (float('inf'), ())
            best = solve(i,j+1)
            number,a,b = slots[j]
            height = 0
            for end in range(i,len(group)):
                height += group[end]['height'] + (GAP if end>i else 0)
                if height > b-a:
                    break
                tail,plan = solve(end+1,j+1)
                y = max(a,min(b-height,group[i]['anchor_y']))
                score = tail + sum(abs(number-group[k]['anchor_page'])*10000 for k in range(i,end+1))
                score += abs(y-group[i]['anchor_y'])/100
                if score < best[0]:
                    best = (score, ((i,end,j,y),)+plan)
            return best
        score,plan = solve(0,0)
        if not math.isfinite(score):
            raise RuntimeError('No ordered figure layout at original font size: '+chapter)
        for start,end,j,y in plan:
            number,_,_ = slots[j]
            for piece in group[start:end+1]:
                piece.update(page=number,rect=[LEFT,y,RIGHT,y+piece['height']])
                free[number] = subtract(free[number],y-8,y+piece['height']+GAP)
                y += piece['height']+GAP


def pages_for_target(rel, manifest):
    if rel == 'books/408四科_强化笔记.pdf':
        return list(range(1, manifest['total_pages']+1))
    if rel.startswith('chapters/'):
        chapter = next(c for c in manifest['chapters'] if c['id'] == rel.split('/')[1])
        return list(range(chapter['combined_start_page'], chapter['combined_start_page']+chapter['pages']))
    subject = next(s for s, name in SUBJECTS.items() if rel == f'books/{name}_强化笔记.pdf')
    return [n for c in manifest['chapters'] if c['id'].startswith(subject)
            for n in range(c['combined_start_page'], c['combined_start_page']+c['pages'])]


def apply_overlays(snapshot_record, pieces, overlays):
    records = []
    manifest = snapshot_record['manifest']
    bypage = collections.defaultdict(list)
    for piece in pieces:
        bypage[piece['page']].append(piece)
    for source in snapshot_record['files']:
        rel = source['file']
        original = DATA / 'baseline' / rel
        target = ROOT / rel
        if sha(original) != source['sha256']:
            raise RuntimeError('Baseline was modified: ' + rel)
        doc = fitz.open(original)
        numbers = pages_for_target(rel, manifest)
        if len(doc) != len(numbers):
            raise RuntimeError('Page count changed: ' + rel)
        for local, number in enumerate(numbers):
            for piece in bypage[number]:
                doc[local].show_pdf_page(fitz.Rect(piece['rect']), overlays, piece['source_page'],
                                        clip=fitz.Rect(piece['clip']), keep_proportion=False, overlay=True)
        if any(bypage[n] for n in numbers):
            metadata = doc.metadata
            metadata['keywords'] = '; '.join(filter(None,[metadata.get('keywords'), 'codex-sidebar-import:'+sha(DATA/'input.json')]))
            doc.set_metadata(metadata)
            temp = target.with_suffix('.annotations.pdf')
            doc.save(temp, garbage=3, deflate=True)
            doc.close()
            temp.replace(target)
        else:
            doc.close()
            shutil.copy2(original, target)
        records.append({'file': rel, 'before_sha256': source['sha256'], 'after_sha256': sha(target),
                        'pages': len(numbers)})
    # Assembly indices describe the PDFs that actually ship, without touching any body source.
    current = read(ROOT / 'manifest.json')
    for c in current['chapters']:
        c['pdf_sha256'] = sha(ROOT / 'chapters' / c['id'] / 'notes.pdf')
    write(ROOT / 'manifest.json', current)
    return records


def verify(snapshot_record, pieces, outputs):
    import numpy as np
    protected = []
    for rel, expected in snapshot_record['protected_sources'].items():
        if sha(ROOT / rel) != expected:
            raise RuntimeError('Protected source changed: ' + rel)
        protected.append(rel)
    bypage = collections.defaultdict(list)
    for piece in pieces:
        if piece['rect'][0] < LEFT-.01 or piece['rect'][2] > RIGHT+.01:
            raise RuntimeError('Outside sidebar: ' + piece['key'])
        bypage[piece['page']].append(piece)
    for number, group in bypage.items():
        for i, a in enumerate(group):
            for b in group[i+1:]:
                if fitz.Rect(a['rect']).intersects(fitz.Rect(b['rect'])):
                    raise RuntimeError('Overlapping sidebar pieces: ' + a['key'] + ' and ' + b['key'])
    checked = 0
    for output in outputs:
        rel = output['file']
        original = fitz.open(DATA / 'baseline' / rel)
        current = fitz.open(ROOT / rel)
        if len(original) != len(current) or original.get_toc() != current.get_toc():
            raise RuntimeError('Page count or bookmarks changed: ' + rel)
        numbers = pages_for_target(rel, snapshot_record['manifest'])
        for i, number in enumerate(numbers):
            a, b = original[i], current[i]
            if a.rect != b.rect or a.rotation != b.rotation:
                raise RuntimeError('Page geometry changed')
            old_streams = [original.xref_stream(x) for x in a.get_contents()]
            new_streams = [current.xref_stream(x) for x in b.get_contents()]
            if not all(stream in new_streams for stream in old_streams):
                raise RuntimeError(f'Original content stream changed: {rel} page {i+1}')
            def link_values(page):
                return [{k: str(v) for k, v in l.items() if k not in {'xref', 'id'}} for l in page.get_links()]
            if link_values(a) != link_values(b):
                raise RuntimeError(f'Original links changed: {rel} page {i+1}')
            # Compare the entire physical page at 144 dpi, allowing differences
            # exclusively inside the newly allocated right-margin rectangles.
            pa, pb = a.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False), b.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False)
            ia = np.frombuffer(pa.samples, dtype=np.uint8).reshape(pa.height, pa.width, pa.n)
            ib = np.frombuffer(pb.samples, dtype=np.uint8).reshape(pb.height, pb.width, pb.n)
            diff = np.any(ia != ib, axis=2)
            for piece in bypage[number]:
                r = fitz.Rect(piece['rect'])
                diff[max(0, math.floor(r.y0*2)-2):math.ceil(r.y1*2)+2,
                     math.floor(r.x0*2)-2:math.ceil(r.x1*2)+2] = False
            if diff.any():
                y, x = np.argwhere(diff)[0]
                raise RuntimeError(f'Pixels outside new sidebars changed: {rel} page {i+1}, ({x/2},{y/2})')
            checked += 1
            if checked % 30 == 0:
                print(f'Preservation verified: {checked}/558 PDF pages', flush=True)
        output['original_content_streams_unchanged'] = True
        output['outside_sidebar_pixels_identical_at_144dpi'] = True
        output['original_links_and_bookmarks_unchanged'] = True
    return {'protected_sources': len(protected), 'protected_source_hashes_unchanged': True,
            'pdf_pages_checked': checked, 'comparison_dpi': 144,
            'original_text_images_tables_coordinates_pagination_unchanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path)
    parser.add_argument('--refresh-baseline', action='store_true')
    parser.add_argument('--typeset-only', action='store_true')
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    if args.input:
        dest = DATA / 'input.json'
        if args.input.resolve() != dest.resolve():
            shutil.copy2(args.input, dest)
    annotations = read(DATA / 'input.json')
    if len({x['id'] for x in annotations}) != len(annotations):
        raise ValueError('Duplicate annotation IDs')
    baseline_record = snapshot(args.refresh_baseline)
    baseline = fitz.open(DATA / 'baseline/books/408四科_强化笔记.pdf')
    from annotation_figures import figure_pieces
    pieces, contexts = [], {}
    for item in annotations:
        context = infer_context(item, baseline, baseline_record['manifest'])
        contexts[item['id']] = context
        title = context['title']
        content = prose(item['annotation']['content'])
        # Reserve one short figure reference line, filled after figure allocation.
        figures = figure_pieces(item, context)
        suffix = r'\par {\color{ink}图示见同页或邻页侧栏。}' if figures else ''
        pieces.append(dict(context, key=item['id'], annotation_id=item['id'], kind='text',
                           reserve=24 if figures else 0,
                           tex=r'{\color{ink}\bfseries ' + prose(title) + r'}\par\vspace{1bp}' + content + suffix))
        pieces.extend(figures)
    overlays = compile_pieces(pieces)
    # Wording is supplied by the user: check every Chinese character survives the
    # typesetting, independently of mathematical Unicode normalization.
    annotation_by_id = {a['id']:a for a in annotations}
    for piece in pieces:
        if piece['kind'] == 'text':
            expected = ''.join(re.findall(r'[\u3400-\u9fff]',annotation_by_id[piece['annotation_id']]['annotation']['content']))
            rendered = ''.join(re.findall(r'[\u3400-\u9fff]',overlays[piece['source_page']].get_text()))
            if expected not in rendered:
                raise RuntimeError('Annotation wording lost in typesetting: '+piece['key'])
    free = {i+1: intervals(page) for i, page in enumerate(baseline)}
    original_free = {i: list(v) for i, v in free.items()}
    allocate_texts(pieces, free)
    # Figure panels may use free space above an anchor note; text allocation's
    # forward cursor is discarded so every genuinely unused margin slot remains available.
    free = {i: list(v) for i, v in original_free.items()}
    for piece in pieces:
        if piece['kind'] == 'text':
            free[piece['page']] = subtract(free[piece['page']], piece['rect'][1]-7, piece['rect'][3]+GAP)
    allocate_figures(pieces, free)
    # Replace generic figure references with exact pages and recompile. Short
    # references have the same line count as the reserved line above.
    for piece in pieces:
        if piece['kind'] == 'text':
            pages = sorted({p['page'] for p in pieces if p['kind']=='figure' and p['annotation_id']==piece['annotation_id']})
            if pages:
                refs = '、'.join(str(p) for p in pages)
                piece['tex'] = piece['tex'].replace('图示见同页或邻页侧栏。', f'图示见合订本第{refs}页侧栏。')
    prior_heights = {p['key']: p['height'] for p in pieces}
    overlays.close()
    overlays = compile_pieces(pieces)
    for piece in pieces:
        if piece['height'] > prior_heights[piece['key']] + .1:
            raise RuntimeError('Figure reference changed reserved height: ' + piece['key'])
        piece['rect'][3] = piece['rect'][1] + piece['height']
    write(DATA / 'placement.json', {'input_sha256': sha(DATA / 'input.json'), 'pieces': pieces,
                                  'contexts': contexts, 'sidebar_bounds': [LEFT,TOP,RIGHT,BOTTOM]})
    md = ['# 强化笔记新增侧栏', '', '本文件保存侧栏批注；正文文件保持原样。', '']
    for item in annotations:
        ctx = contexts[item['id']]
        md += [f"## {item['id']} · 合订本第{ctx['anchor_page']}页 · {ctx['title']}", '',
               item['annotation']['content'], '']
        if item['annotation'].get('diagram_spec'):
            write(DATA / 'diagram_specs' / (item['id']+'.json'), item['annotation']['diagram_spec'])
    (DATA / 'sidebars.md').write_text('\n'.join(md))
    print(f'Typeset {len(annotations)} annotations and {sum(p["kind"]=="figure" for p in pieces)} figure panels', flush=True)
    if args.typeset_only:
        return
    outputs = apply_overlays(baseline_record, pieces, overlays)
    checks = verify(baseline_record, pieces, outputs)
    write(DATA / 'checks.json', dict(checks, annotations=len(annotations), diagrams=sum(bool(x['annotation'].get('diagram_spec')) for x in annotations),
                                    input_sha256=sha(DATA / 'input.json'), outputs=outputs,
                                    visual_review='pending'))
    print(json.dumps(checks, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
