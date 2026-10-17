#!/usr/bin/env python3
"""Package the four PDFs, editable text, diagrams and verifiable edit records.

Run after the separate semantic, calculation and final visual reviews. Merely
running this program never supplies a missing review or marks it as passed.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')

def included_in_release(rel):
    if rel.parts[0]=='build' or '__pycache__' in rel.parts or rel.suffix in {'.zip','.pyc'}:
        return False
    if rel.as_posix()=='editorial/full/archive_verification.json':
        return False
    if rel.parts[0]=='dist':
        current={f'{title}_讲义.pdf' for title in NAMES.values()}
        current.update({'四科目录.md','四科交付清单.json','验收与核验范围.md','知识覆盖表.csv','错题总台账.csv'})
        return rel.name in current
    return True

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def dump(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true',help='Write inventory, without packaging an unchecked release')
    args=parser.parse_args()
    books=[]
    for sub,title in NAMES.items():
        audit=load(ROOT/f'editorial/full/pdf/{sub}/audit.json')
        mf=load(ROOT/f'build/{sub}/build_manifest.json')
        pdf=ROOT/f'dist/{title}_讲义.pdf'
        if mf['partial']: raise ValueError(f'{sub}: preview build')
        if audit['sha256']!=digest(pdf) or mf['sha256']!=digest(pdf):
            raise ValueError(f'{sub}: audit refers to an older PDF')
        if audit['structural_status']!='PASS': raise ValueError(f'{sub}: structural checks unresolved')
        for source in mf['sources']:
            if digest(ROOT/source['path']) != source['sha256']:
                raise ValueError(f"{sub}: manuscript changed after build: {source['path']}")
        visual_path=ROOT/f'editorial/full/pdf/{sub}/visual_review.json'
        visual=load(visual_path) if visual_path.exists() else {}
        reviewed=sorted(set(visual.get('reviewed_pages',[])))
        visual_complete=(visual.get('status')=='PASS' and visual.get('sha256')==audit['sha256']
            and reviewed==list(range(1,audit['page_count']+1)))
        if not args.prepare_only and not visual_complete:
            raise ValueError(f'{sub}: final visual inspection is incomplete or stale')
        chapters=sorted((ROOT/f'manuscript/{sub}').glob('[0-9][0-9]_*.md'))
        books.append(dict(subject=sub,title=title,pdf=str(pdf.relative_to(ROOT)),sha256=digest(pdf),
            physical_pages=audit['page_count'],chapters=len(chapters),
            manuscript_characters=sum(len(p.read_text()) for p in chapters),
            bookmarks=len(audit['bookmarks']),internal_links=audit['internal_link_count'],
            visual_review_complete=visual_complete,visual_review=str(visual_path.relative_to(ROOT)),
            sources=mf['sources']))
    coverage=load(ROOT/'editorial/full/coverage_validation.json')
    figure_manifest=load(ROOT/'editorial/full/figure_manifest.json')
    for figure in figure_manifest['items']:
        for artifact in figure['formats'].values():
            if digest(ROOT/artifact['path']) != artifact['sha256']:
                raise ValueError(f"Diagram changed after inventory: {artifact['path']}")
    if not args.prepare_only and coverage['located_groups']!=243:
        raise ValueError('Knowledge positions are incomplete')
    if not args.prepare_only and coverage['mistake_destinations']!=457:
        raise ValueError('Mistake dispositions are incomplete')
    if not args.prepare_only:
        portable=load(ROOT/'editorial/full/portable_build_verification.json')
        if portable['status']!='PASS':raise ValueError('Isolated rebuild is incomplete')
        fingerprints={book['subject']:book['sha256'] for book in books}
        if {b['subject']:b['production_sha256'] for b in portable['books']}!=fingerprints:
            raise ValueError('Isolated rebuild refers to older production PDFs')
    counts=dict(books=len(books),chapters=sum(b['chapters'] for b in books),
        physical_pages=sum(b['physical_pages'] for b in books),
        manuscript_characters=sum(b['manuscript_characters'] for b in books),
        stable_groups_located=coverage['located_groups'],read_error_records=457)
    manifest=dict(date='2026-10-16',scope='四科全稿；正式2027细目对照仍待核',counts=counts,books=books,
        verification_types=['知识审读','考法/选题及题源','独立计算与过程','PDF结构','最终PDF人工逐页视觉'],
        limitations=['2027正式考试大纲的出版信息已核，全文细目尚未取得；不宣称官方逐条覆盖核验完成。',
        '真题题面依据王道主书与社区完整复原卷交叉核对，复原卷不是官方发布；未获得可认证的官方答案发布。',
        '未统计考试频率；教学重点不表示频率排名。'])
    dump(ROOT/'dist/四科交付清单.json',manifest)
    for src,name in [('editorial/scope/coverage.csv','知识覆盖表.csv'),
                     ('editorial/errors/错误题总台账.csv','错题总台账.csv')]:
        shutil.copyfile(ROOT/src,ROOT/'dist'/name)
    if args.prepare_only:
        print(json.dumps(counts,ensure_ascii=False));return
    archive=ROOT/'dist/408讲义_四科全稿_正文图稿与构建源码.zip'
    state=dict(schema='2.0',stage='四科全稿已成稿；剩余来源核验范围明确记录',delivery_date='2026-10-16',
        project_root=str(ROOT),completed=counts,books=books,
        accepted_feedback=load(ROOT/'PROJECT_STATE.json').get('accepted_feedback',{}),
        remaining={'official_2027_outline_full_text':'出版信息已核，全文细目尚未取得；沿用本地266条细目组织当前243组全稿',
                   'source_conditions':'editorial/未解决问题与后续任务.md；逐章台账记录保留、限条件处理或未选入的题目',
                   'exam_frequency_statistics':'未进行，不在正文声称频率与趋势'},
        build='bash build.sh',archive=str(archive.relative_to(ROOT)),
        resumable_state='以实际manuscript、editorial/full各科台账及最终PDF指纹为准；旧样章首轮材料保留为历史证据。')
    dump(ROOT/'PROJECT_STATE.json',state)
    for sub in NAMES:
        dest=ROOT/f'editorial/full/pdf/{sub}/contacts'
        dest.mkdir(parents=True,exist_ok=True)
        for image in (ROOT/f'build/{sub}/rendered').glob('contact_*.png'):
            shutil.copyfile(image,dest/image.name)
    included=[]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if not included_in_release(rel):continue
            name='408_lecture_notes/'+rel.as_posix()
            z.write(p,name); included.append(dict(path=rel.as_posix(),bytes=p.stat().st_size,sha256=digest(p)))
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad:raise ValueError('Corrupt ZIP member: '+bad)
    archive_report=dict(path=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=digest(archive),
        files=len(included),crc_check='PASS',members=included)
    dump(ROOT/'editorial/full/archive_verification.json',archive_report)
    print(json.dumps(dict(**counts,archive=str(archive.relative_to(ROOT)),archive_bytes=archive.stat().st_size),ensure_ascii=False))

if __name__=='__main__':main()
