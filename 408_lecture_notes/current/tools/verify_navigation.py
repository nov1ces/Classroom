#!/usr/bin/env python3
"""Bind all example navigation to exact PDF headings, rows, and destination pages."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import unquote
import hashlib
import json
import re

import fitz

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = {'DS': '数据结构', 'CO': '计算机组成原理',
            'OS': '操作系统', 'CN': '计算机网络'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def headings(doc):
    result = []
    for page_index, page in enumerate(doc):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                text = ''.join(span['text'] for span in line['spans'])
                match = re.fullmatch(r'例\s*(\d+-\d+)\s*', text)
                if match:
                    result.append({'page': page_index + 1,
                                   'number': match[1],
                                   'rect': fitz.Rect(line['bbox'])})
    return sorted(result, key=lambda h: (h['page'], h['rect'].y0, h['rect'].x0))


def main():
    navigation_path = ROOT / 'sources/navigation.json'
    navigation = json.loads(navigation_path.read_text())['examples']
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    chapters = {r['id']: r for r in manifest['chapters']}
    source_examples = []
    note_order = []
    for subject in SUBJECTS:
        for chapter in sorted((ROOT / 'chapters').glob(subject + '*')):
            source_examples.extend(json.loads((chapter / 'examples.json').read_text()))
            note_order.extend(re.findall(r'\{\{example:([^}]+)\}\}',
                                         (chapter / 'content.md').read_text()))
    source_by_id = {e['id']: e for e in source_examples}
    nav_by_id = {e['id']: e for e in navigation}
    expected = sorted(navigation, key=lambda e: (
        list(SUBJECTS).index(e['subject']), int(e['chapter'][2:]),
        int(e['number'].split('-')[1])))
    errors = []
    if len(nav_by_id) != len(navigation) or set(nav_by_id) != set(source_by_id):
        errors.append('Navigation IDs differ from the authored examples or repeat.')
    for e in navigation:
        if e['id'] in source_by_id:
            for field in ['number', 'answer']:
                if e[field] != source_by_id[e['id']][field]:
                    errors.append(f'{e["id"]}: stale {field}')

    filenames = ['408四科_强化笔记.pdf', '408强化例题解析.pdf'] + [
        name + '_强化笔记.pdf' for name in SUBJECTS.values()]
    docs = {name: fitz.open(ROOT / 'books' / name) for name in filenames}
    pdf_headings = {name: headings(doc) for name, doc in docs.items()}
    checked_external = set()
    records = []

    def check_heading(file, heading, destination, destination_page, ident):
        page = docs[file][heading['page'] - 1]
        links = [link for link in page.get_links()
                 if link['kind'] == fitz.LINK_GOTOR
                 and not (link['from'] & heading['rect']).is_empty]
        if not links:
            errors.append(f'{ident}: {file} p{heading["page"]} heading has no external link')
        for link in links:
            checked_external.add((file, heading['page'], link['xref']))
            if (Path(unquote(link['file'])).name != destination
                    or link.get('page') != destination_page - 1):
                errors.append(f'{ident}: {file} p{heading["page"]} links to '
                              f'{unquote(link["file"])} p{link.get("page", -1) + 1}; '
                              f'expected {destination} p{destination_page}')
        return len(links)

    # Notes follow authored placement order, which may differ from example numbering.
    # Solutions and quick answers use numeric order.
    for file in filenames:
        subject = next((s for s, name in SUBJECTS.items()
                        if file == name + '_强化笔记.pdf'), None)
        ordered = expected if file == '408强化例题解析.pdf' else [nav_by_id[i] for i in note_order]
        entries = [e for e in ordered if subject is None or e['subject'] == subject]
        actual = pdf_headings[file]
        if len(actual) != len(entries):
            errors.append(f'{file}: {len(actual)} headings for {len(entries)} examples')
        for e, heading in zip(entries, actual):
            is_solution = file == '408强化例题解析.pdf'
            chapter = chapters[e['chapter']]
            expected_page = (e['solution_page'] if is_solution else
                             chapter['subject_start_page'] + e['note_local_page'] - 1
                             if subject else e['note_page'])
            derived_combined = chapter['combined_start_page'] + e['note_local_page'] - 1
            if e['note_page'] != derived_combined:
                errors.append(f'{e["id"]}: note page disagrees with chapter/local page')
            if heading['number'] != e['number'] or heading['page'] != expected_page:
                errors.append(f'{e["id"]}: {file} heading {heading["number"]} '
                              f'p{heading["page"]}; expected {e["number"]} p{expected_page}')
            destination = '408四科_强化笔记.pdf' if is_solution else '408强化例题解析.pdf'
            destination_page = e['note_page'] if is_solution else e['solution_page']
            count = check_heading(file, heading, destination, destination_page, e['id'])
            records.append({'example_id': e['id'], 'file': file,
                            'actual_heading_page': heading['page'],
                            'expected_heading_page': expected_page,
                            'expected_destination_page': destination_page,
                            'checked_external_annotations': count})
    for file, doc in docs.items():
        for page_index, page in enumerate(doc, 1):
            for link in page.get_links():
                if (link['kind'] == fitz.LINK_GOTOR
                        and (file, page_index, link['xref']) not in checked_external):
                    errors.append(f'{file} p{page_index}: unaccounted external link xref {link["xref"]}')

    # The answer table has exactly one internal link per example, in subject order.
    solution = docs['408强化例题解析.pdf']
    first_solution_page = min(h['page'] for h in pdf_headings['408强化例题解析.pdf'])
    quick_links = []
    for page_index in range(first_solution_page - 1):
        page = solution[page_index]
        for link in sorted(page.get_links(), key=lambda x: (x['from'].y0, x['from'].x0)):
            if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                quick_links.append((page_index + 1, link))
    if len(quick_links) != len(expected):
        errors.append(f'Quick answers: {len(quick_links)} internal links for {len(expected)} examples')
    quick_records = []
    for e, (page_number, link) in zip(expected, quick_links):
        page = solution[page_number - 1]
        rect = link['from']
        band = fitz.Rect(0, rect.y0 - .5, page.rect.width, rect.y1 + .5)
        words = [w for w in page.get_text('words') if
                 band.y0 <= (w[1] + w[3]) / 2 <= band.y1]
        number = ''.join(w[4] for w in words if w[0] < 110)
        # Clip by character geometry: extraction may merge the final answer word
        # with a page-number cell when both sit on the same baseline.
        note_page = ''.join(page.get_textbox(fitz.Rect(386, band.y0, 430, band.y1)).split())
        printed_destination = ''.join(page.get_textbox(fitz.Rect(445, band.y0, 490, band.y1)).split())
        if number != e['number'] or note_page != str(e['note_page']):
            errors.append(f'{e["id"]}: quick row has number {number!r}, note page {note_page!r}')
        if printed_destination != str(e['solution_page']) or link.get('page') != e['solution_page'] - 1:
            errors.append(f'{e["id"]}: quick answer prints {printed_destination!r}, '
                          f'links to p{link.get("page", -1) + 1}; expected p{e["solution_page"]}')
        quick_records.append({'example_id': e['id'], 'quick_table_page': page_number,
                              'printed_note_page': note_page,
                              'printed_solution_page': printed_destination,
                              'actual_destination_page': link.get('page', -1) + 1})
    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'method': 'Compare authored IDs, answers and placement order, all actual heading order/pages, every external '
                  'annotation at those headings, and every quick-table row/internal destination.',
        'navigation_sha256': sha(navigation_path),
        'pdfs': [{'file': 'books/' + file, 'sha256': sha(ROOT / 'books' / file),
                  'pages': len(doc)} for file, doc in docs.items()],
        'examples': len(navigation), 'heading_instances_checked': len(records),
        'external_annotations_checked': len(checked_external),
        'quick_links_checked': len(quick_records),
        'errors': errors, 'headings': records, 'quick_answers': quick_records,
    }
    (ROOT / 'sources/navigation_exact_checks.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for doc in docs.values():
        doc.close()
    print(json.dumps({k: report[k] for k in ['examples', 'heading_instances_checked',
                                           'external_annotations_checked', 'quick_links_checked',
                                           'errors']}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
