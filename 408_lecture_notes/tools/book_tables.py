#!/usr/bin/env python3
"""Plan full-width table columns using widths measured by the book's XeTeX fonts."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORMAT = 'markdown+raw_tex+tex_math_dollars+tex_math_single_backslash'


def nodes(value, kind):
    if isinstance(value, dict):
        if value.get('t') == kind:
            yield value
        for child in value.values():
            yield from nodes(child, kind)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child, kind)


def text(value):
    if isinstance(value, dict):
        if value.get('t') == 'Str':
            return value['c']
        if value.get('t') in {'Code', 'Math'}:
            return value['c'][-1]
        if value.get('t') in {'Space', 'SoftBreak', 'LineBreak'}:
            return ' '
        return ''.join(text(child) for child in value.values())
    if isinstance(value, list):
        return ''.join(text(child) for child in value)
    return ''


def rows(table):
    c = table['c']
    return c[3][1] + [row for body in c[4] for row in body[2] + body[3]] + c[5][1]


def bound_inlines(value):
    """An equation and adjacent closing punctuation cannot break apart."""
    if isinstance(value, dict):
        for child in value.values():
            yield from bound_inlines(child)
    elif isinstance(value, list):
        for i, node in enumerate(value):
            if isinstance(node, dict) and node.get('t') in {'Math', 'Code'}:
                if node['t'] == 'Code' and re.search('[,;]', node['c'][-1]):
                    continue
                group = [node]
                if i and isinstance(value[i-1], dict) and value[i-1].get('t') == 'Str':
                    match = re.search(r'[（【《“‘\[(]+$', value[i-1]['c'])
                    if match:
                        group.insert(0, dict(t='Str', c=match[0]))
                if i + 1 < len(value) and isinstance(value[i+1], dict) and value[i+1].get('t') == 'Str':
                    match = re.match(r'^[，。、；：！？）】》”’\]\),;:!?%％]+', value[i+1]['c'])
                    if match:
                        group.append(dict(t='Str', c=match[0]))
                if len(group) > 1:
                    yield group
        for child in value:
            yield from bound_inlines(child)


def allocate(cells, minima, available):
    """Keep short columns intact; trade width where it reduces wrapped rows."""
    count = len(minima)
    maxima = [max(row[i] for row in cells) + .9 for i in range(count)]
    if sum(maxima) <= available:
        spare = available - sum(maxima)
        total = sum(maxima)
        return [width + spare * width / total for width in maxima]
    assert sum(minima) <= available + .01, ('Unbreakable table content exceeds the line', minima, available)
    means = [sum(row[i] for row in cells) / len(cells) for i in range(count)]
    weights = [math.sqrt(max(1, means[i] * maxima[i])) for i in range(count)]
    widths = minima[:]
    remaining = available - sum(widths)
    active = set(range(count))
    while remaining > .0001 and active:
        total = sum(weights[i] for i in active)
        additions = {i:min(maxima[i] - widths[i], remaining * weights[i] / total) for i in active}
        for i, addition in additions.items():
            widths[i] += addition
            remaining -= addition
        active = {i for i in active if widths[i] < maxima[i] - .0001}

    def cost(values):
        line_counts = [[max(1, math.ceil((width + .5) / values[i] - 1e-7))
                        for i, width in enumerate(row)] for row in cells]
        return (sum(max(row) for row in line_counts) * 5
                + sum(sum(row) for row in line_counts) * .25
                + sum(line_counts[0]) * .8)

    # Candidate transfers cross actual line-count thresholds instead of getting
    # trapped on the plateaus of a one-point greedy adjustment.
    boundaries = [sorted({minima[i], maxima[i], *[
        min(maxima[i], max(minima[i], width / lines + .9))
        for row in cells for width in [row[i]] for lines in range(1, 9)]})
        for i in range(count)]
    for _ in range(6):
        changed = False
        for i in range(count):
            for j in range(i + 1, count):
                combined = widths[i] + widths[j]
                lower, upper = max(minima[i], combined - maxima[j]), min(maxima[i], combined - minima[j])
                candidates = {widths[i], lower, upper,
                    *[value for value in boundaries[i] if lower <= value <= upper],
                    *[combined - value for value in boundaries[j] if lower <= combined - value <= upper]}
                best, best_cost = widths[i], cost(widths)
                for value in sorted(candidates):
                    trial = widths[:]
                    trial[i], trial[j] = value, combined - value
                    candidate_cost = cost(trial)
                    if candidate_cost < best_cost - 1e-7:
                        best, best_cost = value, candidate_cost
                if abs(best - widths[i]) > .001:
                    widths[i], widths[j] = best, combined - best
                    changed = True
        if not changed:
            break
    widths[-1] += available - sum(widths)
    return widths


def plan(body, subject, out):
    document = json.loads(subprocess.check_output(
        ['pandoc', '-f', FORMAT, '-t', 'json', str(body)], cwd=ROOT))
    tables = list(nodes(document, 'Table'))
    measurements = deepcopy(document)
    measurements['blocks'] = []
    tokens, table_records = {}, []

    def measure(key, blocks):
        measurements['blocks'].extend([
            dict(t='RawBlock', c=['latex', r'\BookMeasureCell{' + key + '}{%']),
            *deepcopy(blocks), dict(t='RawBlock', c=['latex', '}'])])

    def token(inline):
        signature = json.dumps(inline, ensure_ascii=False, sort_keys=True)
        if signature not in tokens:
            key = 'word-' + str(len(tokens) + 1)
            tokens[signature] = key
            measure(key, [dict(t='Plain', c=inline if isinstance(inline, list) else [inline])])
        return tokens[signature]

    for number, table in enumerate(tables, 1):
        cols = len(table['c'][2])
        record = dict(id=f'booktable-{subject}-{number:03}', columns=cols,
                      header=[text(cell[-1]) for cell in rows(table)[0][1]], rows=[])
        for row_number, row in enumerate(rows(table), 1):
            assert len(row[1]) == cols and all(cell[2:4] == [1, 1] for cell in row[1])
            values = []
            for col, cell in enumerate(row[1], 1):
                key = f't{number}r{row_number}c{col}'
                measure(key, cell[-1])
                minimum_keys = []
                for node in nodes(cell[-1], 'Code'):
                    for part in re.findall(r'[^,;]+[,;]?', node['c'][-1]):
                        if part.strip():
                            minimum_keys.append(token(dict(t='Code', c=[node['c'][0], part])))
                for node in nodes(cell[-1], 'Math'):
                    minimum_keys.append(token(node))
                for node in nodes(cell[-1], 'Str'):
                    for word in re.findall(r'[A-Za-z0-9_./:-]+', node['c']):
                        minimum_keys.append(token(dict(t='Str', c=word)))
                minimum_keys.extend(token(group) for group in bound_inlines(cell[-1]))
                values.append(dict(key=key, text=text(cell[-1]), minimum_keys=minimum_keys,
                                   has_math=bool(list(nodes(cell[-1], 'Math')))))
            record['rows'].append(values)
        table_records.append(record)

    fragment = subprocess.run(['pandoc', '-f', 'json', '-t', 'latex', '--wrap=none',
        '--lua-filter=tools/book_images.lua'], cwd=ROOT, input=json.dumps(measurements),
        text=True, capture_output=True, check=True).stdout
    source = r'''\input{tools/book_preamble.tex}
\newcommand{\BookTitle}{表格列宽校准}
\newsavebox{\BookTableMeasure}
\long\def\BookMeasureCell#1#2{\sbox{\BookTableMeasure}{#2}%
\typeout{BKCELL:#1=\number\wd\BookTableMeasure}}
\begin{document}\small
\typeout{BKWIDTH:\number\linewidth;BKSEP:\number\tabcolsep;BKHEIGHT:\number\textheight}
''' + fragment + '\n\\end{document}\n'
    tex = out / 'table_measure.tex'
    tex.write_text(source)
    result = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
        '-output-directory=' + str(out), '-jobname=table_measure', str(tex)],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / 'table_measure.stdout.log').write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(result.stdout[-6000:])
    dimensions = {key:int(value) / 65536 for key,value in re.findall(r'BKCELL:([\w-]+)=(\d+)', result.stdout)}
    width, sep, page_height = map(lambda value:int(value) / 65536,
        re.search(r'BKWIDTH:(\d+);BKSEP:(\d+);BKHEIGHT:(\d+)', result.stdout).groups())
    for record in table_records:
        numeric = [[dimensions[cell['key']] for cell in row] for row in record['rows']]
        count = record['columns']
        available = width - 2 * (count - 1) * sep
        minima = [max(min(20, max(row[i] for row in numeric)) + .9,
                      max([dimensions[key] + .9 for row in record['rows'] for key in row[i]['minimum_keys']] + [0]))
                  for i in range(count)]
        # Complete short labels are more useful than spare width in a column
        # that must wrap long explanations anyway. Relax this preference only
        # when the sum cannot coexist with the genuinely unbreakable content.
        compact_limit = min(80, available * .22)
        compact_minima = [max(minima[i], max(row[i] for row in numeric) + .9)
            if max(row[i] for row in numeric) + .9 <= compact_limit else minima[i]
            for i in range(count)]
        if sum(compact_minima) <= available:
            minima = compact_minima
        widths = allocate(numeric, minima, available)
        record['widths_pt'] = widths
        record['line_width_pt'] = width
        record['tabcolsep_pt'] = sep
        record['natural_maxima_pt'] = [max(row[i] for row in numeric) for i in range(count)]
        record['minimum_widths_pt'] = minima
        record['all_cells_fit_one_line'] = all(numeric[r][c] + .5 <= widths[c]
            for r in range(len(numeric)) for c in range(count))
        estimated_height = 22 + sum(2.5 + 15.5 * max(
            max(1, math.ceil((value + .5) / widths[c] - 1e-7)) for c, value in enumerate(row))
            for row in numeric)
        record['keep_height_pt'] = estimated_height if estimated_height < .9 * page_height else 0
        for row in record['rows']:
            for cell in row:
                cell['natural_width_pt'] = dimensions[cell.pop('key')]
                cell.pop('minimum_keys')
    path = out / 'table_plan.json'
    path.write_text(json.dumps(dict(subject=subject, measurement='XeLaTeX at the actual table font size',
        tables=table_records), ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(subject=subject, measured_tables=len(tables),
        tables_without_wrapped_cells=sum(t['all_cells_fit_one_line'] for t in table_records)), ensure_ascii=False), flush=True)
    return path
