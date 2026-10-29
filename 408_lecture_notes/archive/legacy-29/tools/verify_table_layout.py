#!/usr/bin/env python3
"""Inspect every table's actual PDF column starts, rules and text wrapping."""
from pathlib import Path
import argparse
import hashlib
import json

import fitz

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ['DS', 'CO', 'OS', 'CN']
SCALE = 72 / 72.27


def inspect(subject):
    build = ROOT / 'build' / subject
    manifest = json.loads((build / 'build_manifest.json').read_text())
    plan = json.loads((build / 'table_plan.json').read_text())
    pdf = ROOT / manifest['pdf']
    doc = fitz.open(pdf)
    names = doc.resolve_names()
    records = []
    for table in plan['tables']:
        columns = table['columns']
        widths = [value * SCALE for value in table['widths_pt']]
        sep = table['tabcolsep_pt'] * SCALE
        line_width = table['line_width_pt'] * SCALE
        expected_x = [24 * 72 / 25.4]
        for width in widths[:-1]:
            expected_x.append(expected_x[-1] + width + 2 * sep)
        assert abs(sum(widths) + 2 * (columns - 1) * sep - line_width) < .01
        rows = []
        for r, cells in enumerate(table['rows'], 1):
            anchors = []
            for c in range(1, columns + 1):
                dest = names[f"{table['id']}-r{r}-c{c}"]
                page = doc[dest['page']]
                anchors.append((dest['page'], dest['to'][0], page.rect.height - dest['to'][1]))
            assert len({anchor[0] for anchor in anchors}) == 1, (table['id'], r, 'Row split across pages')
            assert all(abs(anchor[1] - expected_x[i]) < .08 for i, anchor in enumerate(anchors)), (table['id'], r, anchors, expected_x)
            rows.append(dict(page=anchors[0][0], baseline=min(a[2] for a in anchors),
                             anchors=anchors, cells=cells))
        pages = sorted({row['page'] for row in rows})
        fragments = []
        wrapping = []
        for page_index in pages:
            page = doc[page_index]
            current = [(i, row) for i, row in enumerate(rows) if row['page'] == page_index]
            first_y = min(row['baseline'] for _, row in current)
            last_y = max(row['baseline'] for _, row in current)
            rules = []
            for drawing in page.get_drawings():
                rect = drawing['rect']
                if rect.height < .2 and abs(rect.width - line_width) < .15 and abs(rect.x0 - expected_x[0]) < .15:
                    rules.append((rect.y0, rect.x0, rect.x1))
            above = sorted(rule for rule in rules if 60 < rule[0] < first_y)
            below = sorted(rule for rule in rules if rule[0] > last_y + 1)
            assert above, (table['id'], page_index + 1, 'Missing full-width table rule')
            top = above[-1][0]
            if page_index != rows[0]['page'] and len(above) > 1 and above[-1][0] - above[-2][0] < 65:
                top = above[-2][0]
            bottom = below[0][0] if below else page.rect.height - 23 * 72 / 25.4
            fragments.append(dict(physical_page=page_index + 1,
                bbox=[round(expected_x[0], 3), round(top, 3), round(expected_x[0] + line_width, 3), round(bottom, 3)],
                full_width_rule_verified=True))
            spans = [span for block in page.get_text('dict')['blocks'] if block['type'] == 0
                     for line in block['lines'] for span in line['spans'] if span['text'].strip()]
            for index, row in current:
                next_y = min([other['baseline'] for _, other in current if other['baseline'] > row['baseline'] + 2] + [bottom + 7])
                for col, cell in enumerate(row['cells']):
                    x0, x1 = expected_x[col], expected_x[col] + widths[col]
                    baseline = row['anchors'][col][2]
                    # Header minipages may bottom-align; retain their own first
                    # baseline, while math scripts may sit above the text line.
                    selected = [span for span in spans
                        if x0 - .1 <= span['origin'][0] < x1 + .1
                        and baseline - 6.7 <= span['origin'][1] < next_y - 6.7]
                    if not cell['text'].strip():
                        continue
                    assert selected, (table['id'], index + 1, col + 1, 'Missing cell text')
                    assert all(span['bbox'][2] <= x1 + 1.2 for span in selected), (table['id'], index + 1, col + 1, 'Text overlaps next column', selected, x1)
                    line_origins = []
                    for span in sorted(selected, key=lambda span:span['origin'][1]):
                        y = span['origin'][1]
                        if not line_origins or y - line_origins[-1] > .6:
                            line_origins.append(y)
                    lines = None if cell['has_math'] else len(line_origins)
                    fits = cell['natural_width_pt'] + .5 <= table['widths_pt'][col]
                    if fits and lines is not None:
                        assert lines == 1, (table['id'], index + 1, col + 1, 'Unnecessary wrap in a fitting cell', cell['text'], line_origins)
                    wrapping.append(dict(row=index + 1, column=col + 1, lines=lines,
                        natural_width_pt=round(cell['natural_width_pt'], 3), fits_one_line=fits))
        records.append(dict(id=table['id'], header=table['header'], columns=columns,
            widths_pt=[round(w, 4) for w in table['widths_pt']], rows=len(rows),
            all_cells_fit_one_line=table['all_cells_fit_one_line'],
            fragments=fragments, cell_checks=wrapping, status='PASS'))
    result = dict(subject=subject, pdf=manifest['pdf'], sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        table_count=len(records), tables=records, status='PASS')
    print(json.dumps(dict(subject=subject, tables=len(records), status='PASS'), ensure_ascii=False), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subjects', nargs='+', choices=SUBJECTS, default=SUBJECTS)
    args = parser.parse_args()
    books = [inspect(subject) for subject in args.subjects]
    out = ROOT / 'editorial/final/table_pdf_checks.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(status='PASS',
        scope='逐表核对实际PDF列起点和满宽横线，逐单元格核对可容纳短文本的换行与跨列；数学上下标不作为多行计数，长说明允许必要换行。',
        table_count=sum(book['table_count'] for book in books), books=books), ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
