#!/usr/bin/env python3
"""Package an actually reviewed first-round delivery, preserving raw ledgers."""
from pathlib import Path
from datetime import datetime, timezone
import csv,json,hashlib,shutil,zipfile
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
PDF=DIST/'操作系统_同步互斥与信号量_样章.pdf'

def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def dump(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2))

def figures():
    defs=[
      ('F01_lost_update','两次更新的六步交错','OS-03-01','机制示例，非真题原图','verify_models.py:lost_update'),
      ('F02_signed_semaphore','初值2的记录型P/V队列','OS-03-05','课件与主书机制重绘','model_results.json:signed_trace'),
      ('F03_precedence_2022','2022年第46题前驱图','OS-03-05','原题五条边重绘；底部线程归属为讲解标注','model_results.json:precedence；原题图证'),
      ('F04_buffer_permissions','空位与产品许可的相反流向','OS-03-07','经典模型讲解图，四槽仅示意','缓冲模型守恒检查；正文容量参数n'),
      ('F05_buffer_deadlock','消费者持锁等产品的等待环','OS-03-07','错误代码的过程讲解图','model_results.json:buffer_wrong_order'),
      ('F06_readers_group','两读者重叠与写者等待','OS-03-08','示意时间线，不是原真题数据','R1:[1,4)，R2:[2,5)，W:[5,7)；首末读者机制'),
      ('F07_philosopher_wait_cycle','五人各持一根的等待环','OS-03-09','经典模型的等待关系图','model_results.json:philosophers'),
      ('F08_condition_wait','等待释放锁与通知后重取锁','OS-03-06','Mesa/POSIX式机制图','Oracle接口语义；正文while过程'),
    ]
    out=[]
    for fid,title,kid,origin,calc in defs:
        svg,png,pdf=[ROOT/'figures'/f'{fid}.{ext}' for ext in ['svg','png','pdf']]
        assert svg.exists() and png.exists() and pdf.exists()
        xml=svg.read_text();assert '<svg ' in xml and '<text ' in xml and '<image ' not in xml
        with Image.open(png) as im:
            assert im.width>=1000 and im.height>=250
            size=list(im.size)
        out.append(dict(id=fid,title=title,knowledge_id=kid,source_type=origin,
            svg=str(svg.relative_to(ROOT)),png=str(png.relative_to(ROOT)),pdf=str(pdf.relative_to(ROOT)),
            drawing_source='tools/draw_figures.py',png_pixels=size,verification=calc,
            svg_sha256=sha(svg),png_sha256=sha(png),status='已重绘、导出并在样章阅图'))
    # Independently verify the illustrative reader intervals: half-open endpoints
    # let the last reader release before the writer begins at time 5.
    read_intervals=[(1,4),(2,5)];writer=(5,7)
    assert all(max(a,writer[0])>=min(b,writer[1]) for a,b in read_intervals)
    events=sorted([(a,1) for a,b in read_intervals]+[(b,-1) for a,b in read_intervals])
    count=0;counts=[]
    for t,delta in events:
        count+=delta;assert count>=0;counts.append([t,count])
    assert counts==[[1,1],[2,2],[4,1],[5,0]]
    dump(ROOT/'editorial/figures/figure_manifest.json',out)
    dump(ROOT/'editorial/figures/reader_timeline_check.json',dict(status='PASS',events=counts,writer=writer,scope='illustrative half-open time intervals'))
    with (ROOT/'editorial/figures/figure_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    return out

def validate():
    audit=read('editorial/verification/pdf_audit.json')
    visual=read('editorial/verification/final_visual_check.json')
    assert audit['structural_status']=='PASS'
    assert visual['status']=='PASS' and visual['pdf_sha256']==sha(PDF)==audit['sha256']
    assert audit['page_count']==20 and audit['internal_link_count']==48
    assert len(audit['bookmarks'])==36
    errors=read('editorial/errors/错误题总台账.json')['records']
    coverage=read('editorial/scope/coverage.json')['rows']
    ids={r['知识点 ID'] for r in coverage}
    assert len(errors)==457 and len({r['id'] for r in errors})==457
    assert len(coverage)==243 and len(ids)==243
    assert all(set(r['knowledge_ids'])<=ids for r in errors)
    assert [r['id'] for r in errors if not r['knowledge_ids']]==['ERR-CO-3.2-026']
    assert all(r['question_text'] and r['chosen_option'] and r['destination'] for r in errors)
    model=read('editorial/verification/model_results.json')
    assert model['status']=='PASS' and model['precedence']['count']==6
    assert model['buffer_wrong_order']['deadlocks']>0
    assert all(x['deadlocks']==0 for x in model['philosophers'] if x['mode']!='naive')
    with fitz.open(PDF) as doc:
        assert sum(len(page.search_for('P(empty)')) for page in doc)>0
        assert sum(len(page.search_for('signal(S_AC)')) for page in doc)>0
        assert sum(len(page.search_for('信号量')) for page in doc)>5
    return audit

def main():
    DIST.mkdir(exist_ok=True)
    audit=validate();figs=figures()
    state=dict(schema='1.0',stage='首轮可评阅；等待样章反馈后统一标准并逐章推进',
        source_read_date='2026-10-15',delivery_date='2026-10-16',
        project_root=str(ROOT),sample_pdf=str(PDF.relative_to(ROOT)),pdf_sha256=sha(PDF),
        manuscript='manuscript/OS/03_同步互斥与信号量.md',
        completed=dict(reference_analysis=True,error_records_read=457,error_knowledge_mapping=456,
                       provisional_knowledge_groups=243,local_outline_items=266,
                       sample_knowledge_groups=9,numbered_examples=7,selected_verified_past_exam_questions=5,
                       personal_error_items_used=6,figures=8,pdf_physical_pages=20),
        remaining=dict(official_2027_outline_full_text='未取得；出版书目信息已核，不称未发布',
             full_books='四科29章规划，已完成1章，其余28章待逐章编写',
             pending_error_mapping=['ERR-CO-3.2-026'],
             source_conditions='editorial/未解决问题与后续任务.md',
             question_verification='样章之外多数书标真题尚未完成原卷身份核验；未统计全题库考频'),
        next_actions=['先读取本状态及实际文件，保留已完成内容与稳定ID',
                      '依据样章反馈校准深度、密度、选题与版式，不逐节重复请求确认',
                      '取得正式2027细目并逐条对照；已有错题不因该缺项停读',
                      '逐章维护覆盖、考法、题源、图稿、复算、未解决问题，知识核验后连续阅读编辑'],
        build='bash build.sh',
        verification_files=['editorial/verification/model_results.json',
          'editorial/sources/os_exam_checks/verification_results.json',
          'editorial/verification/technical_review_checks.json',
          'editorial/verification/pdf_audit.json','editorial/verification/final_visual_check.json'])
    dump(ROOT/'PROJECT_STATE.json',state)
    for source,name in [
       ('editorial/四科目录初稿.md','四科目录初稿.md'),
       ('editorial/scope/coverage.csv','知识覆盖表初稿.csv'),
       ('editorial/errors/错误题总台账.csv','错题总台账.csv'),
       ('editorial/首轮验收与样章自评.md','首轮验收与样章自评.md')]:
        shutil.copy2(ROOT/source,DIST/name)
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if '__pycache__' in rel.parts or p.suffix in ['.pyc','.zip']:continue
        if rel.parts[0]=='build' and (len(rel.parts)<2 or rel.parts[1] not in ['rendered','os_sync_body.tex','fonts.tex','os_sync.log','release_build.log']):continue
        if p.name in ['交付文件清单.json','archive_verification.json']:continue
        files.append(p)
    manifest=dict(delivery_date='2026-10-16',pdf_sha256=sha(PDF),
                  files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
    dump(DIST/'交付文件清单.json',manifest)
    files.append(DIST/'交付文件清单.json')
    archive=DIST/'408讲义_首轮交付_含源码与编辑材料.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,Path('408讲义首轮')/p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert '408讲义首轮/dist/操作系统_同步互斥与信号量_样章.pdf' in z.namelist()
    result=dict(status='PASS',archive=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,
       sha256=sha(archive),entries=len(files),pdf_sha256=sha(PDF),visual_pdf_sha256=read('editorial/verification/final_visual_check.json')['pdf_sha256'],
       frozen_visual_review_matches_pdf=True,searchable_text_checks='P(empty)、signal(S_AC)、信号量均实查可搜索')
    dump(ROOT/'editorial/verification/archive_verification.json',result)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    if (ROOT/'editorial/full/已确认的编写与标注规则.md').exists():
        raise SystemExit('此为首轮历史打包器；四科全稿请运行 tools/bundle_release.py。')
    main()
