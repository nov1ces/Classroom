#!/usr/bin/env python3
"""Bind all example navigation to exact PDF headings, rows, and destination pages."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import unquote
import argparse
import hashlib
import json
import re

import fitz
from build_solutions import quick_answer

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true',
                        help='Validate without writing the report.')
    args = parser.parse_args()
    navigation_path = ROOT / 'sources/navigation.json'
    navigation = json.loads(navigation_path.read_text())['examples']
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    chapters = {r['id']: r for r in manifest['chapters']}
    source_examples = []
    note_order = []
    errors = []
    for subject in SUBJECTS:
        for chapter in sorted((ROOT / 'chapters').glob(subject + '*')):
            authored = json.loads((chapter / 'examples.json').read_text())
            placement = re.findall(r'\{\{example:([^}]+)\}\}',
                                   (chapter / 'content.md').read_text())
            by_id = {e['id']: e for e in authored}
            if placement != [e['id'] for e in authored]:
                errors.append(f'{chapter.name}: examples array differs from body reading order')
            for position, ident in enumerate(placement, 1):
                if ident not in by_id or by_id[ident]['number'] != f'{int(chapter.name[2:])}-{position}':
                    errors.append(f'{ident}: number is not consecutive in body reading order')
            source_examples.extend(authored)
            note_order.extend(placement)
    source_by_id = {e['id']: e for e in source_examples}
    nav_by_id = {e['id']: e for e in navigation}
    # Derive every output's order from the body, never from its own numbering.
    expected = [nav_by_id[ident] for ident in note_order if ident in nav_by_id]
    if (len(source_by_id) != len(source_examples) or len(note_order) != len(set(note_order))
            or set(note_order) != set(source_by_id)):
        errors.append('Authored IDs repeat or differ from body placements.')
    if len(nav_by_id) != len(navigation) or set(nav_by_id) != set(source_by_id):
        errors.append('Navigation IDs differ from the authored examples or repeat.')
    if [e['id'] for e in navigation] != note_order:
        errors.append('Navigation differs from body reading order (DS, CO, OS, CN).')
    indexed = json.loads((ROOT / 'sources/example_index.json').read_text())['examples']
    if [e['id'] for e in indexed] != note_order:
        errors.append('Source index differs from body reading order (DS, CO, OS, CN).')
    for e in indexed:
        if e['id'] not in source_by_id:
            errors.append(f'{e["id"]}: source index ID is not authored')
            continue
        for field in ['number', 'question', 'answer', 'solution']:
            if e.get(field) != source_by_id[e['id']][field]:
                errors.append(f'{e["id"]}: source index has stale {field}')
    for e in navigation:
        if e['id'] in source_by_id:
            for field in ['number', 'answer']:
                if e[field] != source_by_id[e['id']][field]:
                    errors.append(f'{e["id"]}: stale {field}')
            if e['chapter'] != e['id'].split('-')[0] or e['subject'] != e['chapter'][:2]:
                errors.append(f'{e["id"]}: navigation has stale chapter/subject')

    # Bind the editable quick table and solution headings/answers to the same IDs.
    solution_markdown = (ROOT / 'solutions/notes.md').read_text()
    quick_rows = re.findall(r'^\| [^|]+ \| \[([^]]+)\]\(#a-([^)]+)\) \| (.*) \| (\d+) \|$',
                            solution_markdown, re.M)
    expected_rows = [(e['number'], e['id'],
                      quick_answer(source_by_id[e['id']]).replace('\n', ' ').replace('|', r'\|'),
                      str(e['note_page'])) for e in expected]
    if quick_rows != expected_rows:
        errors.append('Editable quick-answer rows differ from body order, numbers, answers or pages.')
    solution_blocks = list(re.finditer(
        r'^<a id="a-([^"]+)"></a>\n### (.+)\n\n', solution_markdown, re.M))
    if [m[1] for m in solution_blocks] != note_order:
        errors.append('Editable solution headings differ from body reading order.')
    for position, match in enumerate(solution_blocks):
        ident = match[1]
        if ident not in source_by_id or ident not in nav_by_id:
            continue
        e = nav_by_id[ident]
        heading = ('[例 ' + e['number'] + '](../books/' + SUBJECTS[e['subject']]
                   + '_强化笔记.md#' + ident + ')')
        end = solution_blocks[position + 1].start() if position + 1 < len(solution_blocks) else len(solution_markdown)
        if match[2] != heading or not solution_markdown[match.end():end].startswith(source_by_id[ident]['answer'] + '\n\n'):
            errors.append(f'{ident}: editable solution has stale heading, return link or answer')

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

    # Notes, solutions and quick answers share the body's consecutive numbering.
    for file in filenames:
        subject = next((s for s, name in SUBJECTS.items()
                        if file == name + '_强化笔记.pdf'), None)
        entries = [e for e in expected if subject is None or e['subject'] == subject]
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
        'method': 'Derive consecutive chapter numbers and all output order from body placeholders; compare authored '
                  'and indexed IDs/answers, editable quick/solution rows, all actual PDF heading order/pages, '
                  'every external annotation at those headings, and every PDF quick-table row/internal destination.',
        'navigation_sha256': sha(navigation_path),
        'pdfs': [{'file': 'books/' + file, 'sha256': sha(ROOT / 'books' / file),
                  'pages': len(doc)} for file, doc in docs.items()],
        'examples': len(navigation), 'heading_instances_checked': len(records),
        'external_annotations_checked': len(checked_external),
        'quick_links_checked': len(quick_records),
        'errors': errors, 'headings': records, 'quick_answers': quick_records,
    }
    if not args.check_only:
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
