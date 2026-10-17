#!/usr/bin/env python3
"""Package the review edition without reading or certifying PDF page geometry.

Checks here bind the exported files to the current source and content ledgers.
No full-page render, pagination, clipping, font, bookmark or layout audit runs.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = dict(DS='数据结构', CO='计算机组成原理', OS='操作系统', CN='计算机网络')
EDITION = 'revision3'
OUT = ROOT / 'dist' / EDITION

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def check_count(result):
    value = result.get('checks_count', result.get('check_count', result.get('count', result.get('checks'))))
    return len(value) if isinstance(value, list) else value

def include(rel):
    if '__pycache__' in rel.parts or rel.suffix in {'.pyc', '.zip'}:
        return False
    first = rel.parts[0]
    if first == 'dist':
        return len(rel.parts) == 3 and rel.parts[1] == EDITION
    if first == 'build':
        return (len(rel.parts) == 4 and rel.parts[1] == EDITION
                and rel.name in {'book.tex','body.tex','body.md','indexes.tex','build_manifest.json'})
    if first in {'manuscript', 'figures', 'tools'}:
        return True
    if first == 'editorial':
        if rel.as_posix() == f'editorial/{EDITION}/archive_verification.json':
            return False
        if len(rel.parts) > 1 and re.fullmatch(r'revision[1-9][0-9]*',rel.parts[1]):
            return True
        # Keep editable evidence and original reading/disposition records;
        # V1 page images and complete scanned source books are not duplicated.
        return rel.suffix.lower() in {'.json','.csv','.md','.txt','.py'}
    return rel.as_posix() in {'README.md', 'CONTENT_REVIEW.md', 'PROJECT_STATE.json',
                             'build.sh', 'build_review.sh', 'requirements.txt'}

def main():
    global EDITION, OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--review-edition',default='revision3')
    args=parser.parse_args()
    if not re.fullmatch(r'revision[1-9][0-9]*',args.review_edition):
        raise ValueError('Invalid review edition')
    EDITION=args.review_edition;OUT=ROOT/'dist'/EDITION
    OUT.mkdir(parents=True, exist_ok=True)
    coverage = read(ROOT / 'editorial/full/coverage_validation.json')
    if coverage['located_groups'] != 243 or coverage['mistake_destinations'] != 457:
        raise ValueError('Coverage locations or read-mistake dispositions are incomplete')
    books = []
    for sub, title in NAMES.items():
        manifest = read(ROOT / f'build/{EDITION}/{sub}/build_manifest.json')
        if manifest.get('edition') != 'content_review' or manifest['partial'] or manifest.get('review_edition') != EDITION:
            raise ValueError(sub + ': not a full content-review build')
        pdf = ROOT / manifest['pdf']
        if digest(pdf) != manifest['sha256']:
            raise ValueError(sub + ': exported PDF differs from its build manifest')
        for item in manifest['sources']:
            if digest(ROOT / item['path']) != item['sha256']:
                raise ValueError(sub + ': manuscript changed after review export: ' + item['path'])
        records = read(ROOT / f'editorial/full/{sub}/chapter_records.json')
        for chapter in records['chapters']:
            if digest(ROOT / chapter['manuscript']) != chapter['sha256']:
                raise ValueError(sub + ': chapter ledger does not match the current text')
        result = read(ROOT / f'editorial/full/{sub}/results.json')
        if result['status'] != 'PASS':
            raise ValueError(sub + ': calculation/state checks unresolved')
        examples = [e for chapter in records['chapters'] for e in chapter.get('examples', [])]
        numbered = [q for q in manifest['questions'] if re.match(r'^例\s*[A-Z]*\s*\d',q['title'])]
        if not {q['anchor'] for q in numbered}.issubset({e['anchor'] for e in examples}):
            raise ValueError(sub + ': numbered question has no selection record')
        books.append(dict(subject=sub, title=title, pdf=manifest['pdf'], sha256=manifest['sha256'],
            chapters=len(manifest['sources']), manuscript_characters=sum(x['characters'] for x in manifest['sources']),
            numbered_examples=len(numbered),selected_source_records_including_selfchecks=len(examples),
            verification_check_records=check_count(result),
            verification_breakdown=result.get('verification_breakdown'),
            layout_checks='未执行：待用户正文审阅后进行', sources=manifest['sources']))
    figures = read(ROOT / 'editorial/full/figure_manifest.json')
    for figure in figures['items']:
        for asset in figure['formats'].values():
            if digest(ROOT / asset['path']) != asset['sha256']:
                raise ValueError('Figure changed after inventory: ' + asset['path'])
    os_extra = read(ROOT / 'editorial/revision2/OS_results.json')
    if os_extra['status'] != 'PASS':
        raise ValueError('Revised OS comparison-path checks unresolved')
    review = ROOT / f'editorial/{EDITION}/review/final_content_review.json'
    if not review.exists():
        raise ValueError('Final independent content review has not been recorded')
    independent = read(review)
    if independent.get('status') != 'PASS_CONTENT':
        raise ValueError('Independent content review has unresolved findings')
    for path, expected in independent['manuscript_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Text changed after independent content review: ' + path)
    for path, item in independent['unchanged_chapters_sha_only'].items():
        if digest(ROOT / path) != item['sha256'] or item['sha256'] != item['baseline_sha256']:
            raise ValueError('A chapter recorded as unchanged differs from its baseline: ' + path)
    for name, item in independent['mechanism_figures'].items():
        for ext in ['svg','png']:
            if digest(ROOT / 'figures' / (name + '.' + ext)) != item[ext + '_sha256']:
                raise ValueError('Mechanism figure changed after independent review: ' + name)
    conversion_path=ROOT/f'editorial/{EDITION}/conversion_results.json'
    conversion=read(conversion_path) if conversion_path.exists() else None
    if conversion is not None:
        if conversion['status']!='PASS':raise ValueError('Source conversion checks unresolved')
        for path,expected in conversion['source_sha256'].items():
            if digest(ROOT/path)!=expected:raise ValueError('Text changed after source conversion check: '+path)
    summary = dict(edition=EDITION+'_content_review', date=datetime.now(timezone.utc).date().isoformat(),
        books=books, chapters=sum(b['chapters'] for b in books),
        numbered_examples=sum(b['numbered_examples'] for b in books),
        referenced_figures=figures['referenced_figures'], stable_knowledge_groups_located=coverage['located_groups'],
        read_mistake_dispositions=coverage['mistake_destinations'],
        verification_check_records=sum(b['verification_check_records'] for b in books)+os_extra['check_count'],
        verification_count_note='综合检查记录包含数值/状态、图文数据及保全绑定；逐题计算见分科详细结果，不以此条数推断题库覆盖率。',
        source_conversion_checks=None if conversion is None else conversion['check_count'],
        independent_content_review=str(review.relative_to(ROOT)),
        pdf_layout_review=dict(status='NOT_PERFORMED',reason='遵照用户要求，先审正文，再做分页、裁切和逐页视觉检查'),
        limits=['正式2027大纲全文细目仍未取得，不宣称官方逐条核验完成。',
                '真题依据王道主书及社区二手复原卷交叉，未取得官方原卷/答案发布。',
                'V1版式与视觉记录属于旧PDF，不对本次正文审阅稿授予通过。',
                '未统计考试频率；本轮增补依据教学任务和已读资料。'])
    write(OUT / '交付清单.json', summary)
    edition_name={'revision2':'第二轮','revision3':'第三轮'}.get(EDITION,EDITION)
    archive = OUT / f'408讲义_{edition_name}正文审阅稿与源码.zip'
    members = []
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if not include(rel):
                continue
            z.write(path, '408_lecture_notes/' + rel.as_posix())
            members.append(dict(path=rel.as_posix(),bytes=path.stat().st_size,sha256=digest(path)))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise ValueError('ZIP CRC failed: ' + bad)
    write(ROOT / f'editorial/{EDITION}/archive_verification.json',
          dict(path=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=digest(archive),
               crc_check='PASS',files=len(members),members=members,pdf_layout_check_performed=False))
    print(json.dumps(dict(archive=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,
                          files=len(members),layout_checks='NOT_PERFORMED'),ensure_ascii=False))

if __name__ == '__main__':
    main()
