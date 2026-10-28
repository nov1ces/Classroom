#!/usr/bin/env python3
"""Audit and assemble the editable 26-chapter course notes without source PDFs."""
from pathlib import Path
import argparse, hashlib, json, re, zipfile
from urllib.parse import unquote, urlsplit
import fitz
from build_notes import build_input_fingerprint

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = {'DS': ('数据结构', 8), 'CO': ('计算机组成原理', 7),
            'OS': ('操作系统', 5), 'CN': ('计算机网络', 6)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')

def chapter_ids(subject):
    return [f'{subject}{i:02}' for i in range(1, SUBJECTS[subject][1] + 1)]

def markdown_prose_lines(text):
    """Track fenced code so examples keep their exact literal contents."""
    fence=None
    for line in text.splitlines(keepends=True):
        marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if marker:
            token=marker[1]
            if fence is None:
                fence=token
            elif token[0]==fence[0] and len(token)>=len(fence):
                fence=None
            yield False,line
            continue
        yield fence is None,line

def relocate_chapter_links(text, ident):
    """Adjust links from a chapter to the subject-book Markdown directory."""
    parts=[]
    for prose,line in markdown_prose_lines(text):
        if prose:
            line=re.sub(r'(\]\()figures/', rf'\1../chapters/{ident}/figures/', line)
            line=line.replace('](chapter-map.pdf)', f'](../chapters/{ident}/chapter-map.pdf)')
        parts.append(line)
    return ''.join(parts)

def missing_markdown_targets(path):
    text = path.read_text(encoding='utf8')
    targets = [target for prose,line in markdown_prose_lines(text) if prose
               for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)',line)]
    missing=[]
    for target in targets:
        url=urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        if not (path.parent / unquote(url.path)).exists():
            missing.append(target)
    return missing

def assemble():
    all_doc = fitz.open()
    all_toc, manifest = [], []
    for subject, (name, _) in SUBJECTS.items():
        doc, toc, markdown = fitz.open(), [], [f'# {name}完整笔记\n']
        subject_start = len(all_doc)
        all_toc.append([1, name, subject_start + 1])
        for ident in chapter_ids(subject):
            ch = ROOT / 'chapters' / ident
            pdf = fitz.open(ch / 'notes.pdf')
            title = json.loads((ch / 'map.json').read_text())['title']
            start, all_start = len(doc), len(all_doc)
            doc.insert_pdf(pdf)
            all_doc.insert_pdf(pdf)
            toc.append([1, title, start + 1])
            all_toc.append([2, title, all_start + 1])
            own_toc = pdf.get_toc()
            for level, text, page in own_toc:
                if level >= 2:
                    toc.append([min(level, 3), text, start + page])
                    all_toc.append([min(level + 1, 4), text, all_start + page])
            text = (ch / 'notes.md').read_text()
            text = relocate_chapter_links(text, ident)
            markdown.append(text)
            manifest.append({'id': ident, 'title': title, 'pages': len(pdf),
                             'pdf': f'chapters/{ident}/notes.pdf',
                             'markdown': f'chapters/{ident}/notes.md',
                             'pdf_sha256': sha(ch / 'notes.pdf'),
                             'content_sha256': sha(ch / 'content.md'),
                             'combined_start_page': all_start + 1})
            pdf.close()
        doc.set_toc(toc)
        doc.set_metadata({'title': name + '完整课程笔记', 'subject': '408 · 单面边栏',
                          'creator': 'XeLaTeX / PyMuPDF'})
        output = ROOT / 'books' / (name + '_完整笔记.pdf')
        doc.save(output, garbage=4, deflate=True)
        doc.close()
        (ROOT / 'books' / (name + '_完整笔记.md')).write_text('\n\n'.join(markdown), encoding='utf8')
        broken=missing_markdown_targets(ROOT / 'books' / (name + '_完整笔记.md'))
        if broken:
            raise RuntimeError(f'{name}: broken merged Markdown targets: {broken[:10]}')
    all_doc.set_toc(all_toc)
    all_doc.set_metadata({'title': '408四科26章完整笔记', 'subject': '408 · 单面边栏',
                         'creator': 'XeLaTeX / PyMuPDF'})
    all_doc.save(ROOT / '408四科26章_完整笔记.pdf', garbage=4, deflate=True)
    all_doc.close()
    dump(ROOT / 'manifest.json', {'chapters': manifest, 'total_pages': sum(x['pages'] for x in manifest)})
    return manifest

def audit():
    errors, warnings, chapters = [], [], []
    for subject in SUBJECTS:
        for ident in chapter_ids(subject):
            ch = ROOT / 'chapters' / ident
            required = ['content.md', 'notes.md', 'chapter.tex', 'main.tex',
                        'notes.pdf', 'map.json', 'sidebars.json',
                        'sources/course_coverage.json', 'sources/qa.json']
            for relative in required:
                if not (ch / relative).is_file():
                    errors.append(f'{ident}: missing {relative}')
            if not (ch / 'notes.md').is_file():
                continue
            text = (ch / 'notes.md').read_text()
            for target in missing_markdown_targets(ch/'notes.md'):
                errors.append(f'{ident}: missing Markdown target {target}')
            for target in re.findall(r'!\[[^\]]*\]\(([^\s)]+)', text):
                if target.startswith(('http:', 'https:', 'data:')):
                    errors.append(f'{ident}: non-local image {target}')
                    continue
                image = ch / target
                if not image.is_file():
                    errors.append(f'{ident}: missing image {target}')
                if image.suffix == '.png' and not image.with_suffix('.svg').is_file():
                    errors.append(f'{ident}: missing editable SVG {target}')
            ids = re.findall(r'\{#([^}\s]+)', text)+re.findall(r'<a id="([^"]+)"',text)
            if len(ids) != len(set(ids)):
                errors.append(f'{ident}: duplicate Markdown anchors')
            if re.search(r'\bTODO\b|待补充|待核实|占位符|临时占位', text):
                warnings.append(f'{ident}: review possible editorial placeholder')
            if (ch / 'sources/qa.json').is_file():
                qa = json.loads((ch / 'sources/qa.json').read_text())
                for warning in qa.get('warnings', []):
                    errors.append(f'{ident}: {warning}')
                if qa.get('human_visual_review') != 'passed':
                    warnings.append(f'{ident}: visual review not recorded as passed')
                review_path=ch/'sources/visual_review.json'
                if review_path.is_file():
                    review=json.loads(review_path.read_text())
                    if review.get('pdf_sha256')!=sha(ch/'notes.pdf'):
                        errors.append(f'{ident}: visual review is for a different PDF')
                    if review.get('status')!='passed':
                        errors.append(f'{ident}: visual review not passed')
                    if review.get('viewed_pages')!=list(range(1,qa['pages']+1)):
                        errors.append(f'{ident}: incomplete recorded visual page range')
                elif qa.get('human_visual_review')=='passed':
                    errors.append(f'{ident}: no fingerprint-bound visual evidence')
            if (ch / 'sources/content-sync.json').is_file():
                sync = json.loads((ch / 'sources/content-sync.json').read_text())
                if sync['canonical_sha256'] != sha(ch / 'content.md'):
                    errors.append(f'{ident}: content changed since build')
                if sync['markdown_sha256'] != sha(ch / 'notes.md'):
                    errors.append(f'{ident}: Markdown changed since build')
            inputs_path = ch / 'sources/build-inputs.json'
            if inputs_path.is_file():
                if json.loads(inputs_path.read_text()) != build_input_fingerprint(ch):
                    errors.append(f'{ident}: source or figure changed since build')
            chapters.append({'id': ident, 'markdown_bytes': len(text.encode()),
                             'code_blocks': len(re.findall(r'^```(?:c|cpp|c\+\+|text)', text, re.M)),
                             'images': len(re.findall(r'!\[', text))})
    result = {'structural_errors': errors, 'review_warnings': warnings, 'chapters': chapters,
              'scope': 'Structure and fingerprints; knowledge accuracy and visual review are separately recorded.'}
    dump(ROOT / 'sources/delivery_checks.json', result)
    print(json.dumps({'structural_errors': errors, 'review_warnings': warnings}, ensure_ascii=False))
    return result

def package():
    target = ROOT.parent / '408四科26章_完整笔记_源码素材.zip'
    exclude_dirs = {'build', 'previews', '__pycache__', 'extracted', 'ocr-previews', 'build-logs', 'source_previews', 'source-previews'}
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or any(x in exclude_dirs for x in path.relative_to(ROOT).parts):
                continue
            if path.suffix in {'.aux', '.log', '.out', '.toc', '.pyc', '.o', '.bin'}:
                continue
            if path.name.startswith('wangdao-ds-filepage-') and path.suffix=='.png':
                continue
            with path.open('rb') as probe:
                if probe.read(4) == b'\x7fELF':
                    continue
            # Chapter font/vendor links are recreated by the build entrypoint.
            if path.is_symlink():
                continue
            archive.write(path, str(Path('course-notes-26') / path.relative_to(ROOT)))
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'Corrupt archive entry: {bad}')
    dump(ROOT / 'sources/package.json', {'filename': target.name, 'bytes': target.stat().st_size,
                                        'sha256': sha(target), 'zip_crc_check': 'passed'})
    print(target)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['assemble', 'audit', 'package'])
    args = parser.parse_args()
    if args.action == 'assemble':
        assemble()
    elif args.action == 'audit':
        audit()
    else:
        package()
