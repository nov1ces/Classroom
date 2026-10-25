#!/usr/bin/env python3
"""Compile, inspect and render a chapter; human content and visual review remain required."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import fitz
from PIL import Image, ImageDraw


def aux_state(folder):
    return hashlib.sha256(b''.join(
        (folder/('main'+ext)).read_bytes() if (folder/('main'+ext)).exists() else b''
        for ext in ['.aux','.out','.toc'])).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--draft', action='store_true', help='Allow unresolved coverage for intermediate layout review.')
    args = parser.parse_args()
    root = args.directory.resolve()
    for name in ['main.tex','chapter.tex','notes.md','sources/coverage.json']:
        if not (root/name).is_file():
            raise SystemExit('Required file is missing: '+name)
    for name in ['chapter.tex','notes.md']:
        if 'CHAPTER-NOTES-PLACEHOLDER' in (root/name).read_text(encoding='utf-8'):
            raise SystemExit('Write and review the chapter before building: '+name)
    items = json.loads((root/'sources/coverage.json').read_text(encoding='utf-8')).get('items',[])
    valid = {'covered','omitted_by_request','unresolved'}
    if not args.draft and not items:
        raise SystemExit('Source coverage inventory must not be empty.')
    ids = set()
    unresolved = []
    for item in items:
        if item.get('id') in ids or not item.get('id') or item.get('status') not in valid:
            raise SystemExit('Coverage contains duplicate/missing IDs or invalid status.')
        ids.add(item['id'])
        if not item.get('source') or not item.get('locator'):
            raise SystemExit('Every coverage item needs a source and locator.')
        if item['status'] == 'covered' and not item.get('target'):
            raise SystemExit('Covered items need a target.')
        if item['status'] == 'omitted_by_request' and not item.get('note'):
            raise SystemExit('Omissions need the user requirement recorded in note.')
        if item['status'] == 'unresolved':
            unresolved.append(item['id'])
    if unresolved and not args.draft:
        raise SystemExit('Unresolved coverage items: '+', '.join(unresolved))
    if not shutil.which('xelatex'):
        raise SystemExit('XeLaTeX is unavailable; do not claim that a PDF was produced.')
    build = root/'build'; build.mkdir(exist_ok=True)
    old = None
    for run in range(1,6):
        with (build/f'pass-{run}.txt').open('w',encoding='utf-8') as output:
            result = subprocess.run(['xelatex','-no-shell-escape','-interaction=nonstopmode',
                                     '-halt-on-error','-file-line-error',f'-output-directory={build}',
                                     'main.tex'],cwd=root,stdout=output,stderr=subprocess.STDOUT,timeout=240)
        if result.returncode:
            raise SystemExit(f'Compilation failed; inspect {build}/pass-{run}.txt')
        new = aux_state(build)
        if run >= 2 and new == old:
            break
        old = new
    else:
        raise SystemExit('Auxiliary files did not stabilize in five passes.')
    log = (build/'main.log').read_text(errors='replace')
    match = re.search(r'SIDENOTES-PRINT-MODE:\s*(simplex|duplex)',log)
    print_mode = match.group(1) if match else None
    if print_mode is None:
        raise SystemExit('Update the legacy template before export; no declared print mode was found in the compilation log.')
    layout_path = root/'sources/layout.json'
    if layout_path.exists():
        expected_mode = json.loads(layout_path.read_text(encoding='utf-8')).get('print_mode')
        if expected_mode != print_mode:
            raise SystemExit(f'Print mode mismatch: recorded {expected_mode}, compiled {print_mode}. Reconcile the entry class and layout record.')
    for issue in ['Missing character:', 'Overfull \\hbox', 'Overfull \\vbox',
                  'undefined references', 'Label(s) may have changed']:
        if issue in log:
            raise SystemExit('Repair compilation/layout issue: '+issue)
    doc = fitz.open(build/'main.pdf')
    warnings = []
    for i, page in enumerate(doc):
        if len(page.get_text().strip()) < 15:
            warnings.append(f'page {i+1}: almost no text; inspect blank or illustration-only page')
        if abs(page.rect.width-595.276) > 1 or abs(page.rect.height-841.89) > 1:
            raise SystemExit('Unexpected page size.')
        for word in page.get_text('words'):
            if word[0] < -1 or word[2] > page.rect.width+1 or word[1] < -1 or word[3] > page.rect.height+1:
                raise SystemExit(f'Out-of-page word on page {i+1}: {word[4]}')
        for link in page.get_links():
            if link['kind'] == fitz.LINK_GOTO and not 0 <= link['page'] < len(doc):
                raise SystemExit('Broken internal link.')
        for font in page.get_fonts():
            if not doc.extract_font(font[0])[3]:
                raise SystemExit('Font is not embedded: '+font[3])
    previews = root/'previews'; previews.mkdir(exist_ok=True)
    for obsolete in previews.glob('page-*.png'):
        obsolete.unlink()
    thumbs = []
    for i,page in enumerate(doc):
        path = previews/f'page-{i+1:03}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(path)
        thumb = Image.open(path); thumb.thumbnail((260,368))
        tile = Image.new('RGB',(280,400),'#e7e7e7')
        tile.paste(thumb,((280-thumb.width)//2,8))
        ImageDraw.Draw(tile).text((10,383),str(i+1),fill='black')
        thumbs.append(tile)
    for obsolete in previews.glob('contact-*.png'):
        obsolete.unlink()
    for start in range(0,len(thumbs),12):
        part = thumbs[start:start+12]
        sheet = Image.new('RGB',(1120,400*((len(part)+3)//4)),'#d8d8d8')
        for j,tile in enumerate(part):
            sheet.paste(tile,((j%4)*280,(j//4)*400))
        sheet.save(previews/f'contact-{start//12+1:02}.png')
    pdf = root/('notes-draft.pdf' if args.draft else 'notes.pdf')
    shutil.copy2(build/'main.pdf',pdf)
    result = {'pdf':pdf.name,'pages':len(doc),'passes':run,'coverage_items':len(items),
              'print_mode':print_mode,
              'unresolved':unresolved,'warnings':warnings,'draft':args.draft,
              'all_fonts_embedded':True,'machine_checks_passed':True,
              'human_source_and_visual_review':'required; not performed by this script'}
    (root/'sources/qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
