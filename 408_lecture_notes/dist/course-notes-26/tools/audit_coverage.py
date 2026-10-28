#!/usr/bin/env python3
"""Check author mappings against the actual source inventory and chapter anchors."""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT/'sources/source_inventory.json').read_text())
errors, unresolved, records = [], [], []
expected = {item['path']: item for item in inventory['files'] if item['kind'] == 'lecture'}
mapped = set()

for chapter in sorted((ROOT/'chapters').iterdir()):
    if not chapter.is_dir():
        continue
    coverage = chapter/'sources/course_coverage.json'
    if not coverage.exists():
        errors.append(f'{chapter.name}: missing course_coverage.json')
        continue
    data = json.loads(coverage.read_text())
    anchors = set(re.findall(r'\{#([^}\s]+)', (chapter/'content.md').read_text()))
    entries = data.get('lecture_files', [])
    for entry in entries:
        path = entry.get('path', '')
        candidates = [p for p in expected if p == path or Path(p).name == Path(path).name]
        if len(candidates) != 1:
            errors.append(f'{chapter.name}: source path is missing or ambiguous: {path}')
            continue
        source_path = candidates[0]
        source = expected[source_path]
        if source['chapter'] != chapter.name:
            errors.append(f'{chapter.name}: source belongs to {source["chapter"]}: {path}')
        mapped.add(source_path)
        targets = entry.get('targets', [])
        for target in targets:
            if target.lstrip('#') not in anchors:
                errors.append(f'{chapter.name}: nonexistent target {target} for {path}')
        if not targets:
            errors.append(f'{chapter.name}: no target for {path}')
        pages = entry.get('pages', [])
        if isinstance(pages, str):
            numbers = []
            for part in re.split(r'[,，;；、 ]+', pages):
                if not part:
                    continue
                bounds = re.findall(r'\d+', part)
                if len(bounds) == 1:
                    numbers.append(int(bounds[0]))
                elif len(bounds) == 2:
                    numbers.extend(range(int(bounds[0]), int(bounds[1])+1))
            pages = numbers
        if isinstance(pages, list) and all(isinstance(p, int) for p in pages):
            invalid = [p for p in pages if p < 1 or p > source['pdf_pages']]
            if invalid:
                errors.append(f'{chapter.name}: out-of-range file pages {invalid}: {path}')
            page_count = len(set(pages))
        else:
            page_count = None
            errors.append(f'{chapter.name}: unrecognized page range: {path}')
        if not entry.get('verification'):
            errors.append(f'{chapter.name}: missing verification scope: {path}')
        records.append({'chapter':chapter.name,'source':source_path,
                        'source_pages':source['pdf_pages'],'mapped_pages':page_count,
                        'targets':targets,'verification':entry.get('verification')})
    for item in data.get('unresolved', []):
        unresolved.append({'chapter':chapter.name,'item':item})

missing = sorted(set(expected)-mapped)
result = {'lecture_files_expected':len(expected),'lecture_files_mapped':len(mapped),
          'missing_sources':missing,'errors':errors,'unresolved':unresolved,'records':records,
          'limitation':'Checks file/page/anchor integrity. Author reports and independent checks establish actual knowledge and figure review; mappings alone do not prove it.'}
(ROOT/'sources/coverage_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:result[k] for k in ['lecture_files_expected','lecture_files_mapped','missing_sources','errors','unresolved']},ensure_ascii=False))
