#!/usr/bin/env python3
"""Record the current review edition from its real sources, without PDF QA."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, json, re, shutil

ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')
def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--edition',default='revision3');args=parser.parse_args()
    edition=args.edition
    if not re.fullmatch(r'revision[1-9][0-9]*',edition):raise ValueError('Invalid edition')
    here=ROOT/'editorial'/edition;out=ROOT/'dist'/edition
    review=load(here/'review/final_content_review.json')
    if review['status']!='PASS_CONTENT':raise ValueError('Independent content review unresolved')
    coverage=load(ROOT/'editorial/full/coverage_validation.json')
    inventory=load(ROOT/'editorial/full/figure_manifest.json')
    books=[];rows=[]
    for sub,title in NAMES.items():
        mf=load(ROOT/'build'/edition/sub/'build_manifest.json')
        record=load(ROOT/f'editorial/full/{sub}/chapter_records.json')
        if mf['review_edition']!=edition or mf['edition']!='content_review' or mf['partial']:
            raise ValueError('Not the complete current review edition: '+sub)
        if sha(ROOT/mf['pdf'])!=mf['sha256']:raise ValueError('Export changed: '+sub)
        numbered=[q for q in mf['questions'] if re.match(r'^例\s*\d',q['title'])]
        books.append(dict(subject=sub,title=title,pdf=mf['pdf'],sha256=mf['sha256'],
            chapters=len(mf['sources']),numbered_examples=len(numbered),sources=mf['sources']))
        for chapter in record['chapters']:
            path=ROOT/chapter['manuscript'];relative=str(path.relative_to(ROOT));current=sha(path)
            if current!=chapter['sha256']:raise ValueError('Stale chapter record: '+relative)
            baseline=here/'baseline'/relative;old=sha(baseline);changed=current!=old
            if changed:
                if review['manuscript_sha256'].get(relative)!=current:raise ValueError('Unreviewed change: '+relative)
                scope='本轮改动及所列题目已独立内容复读；实际再核范围见审校记录'
            else:
                unchanged=review['unchanged_chapters_sha_only'][relative]
                if unchanged['sha256']!=current or unchanged['baseline_sha256']!=old:raise ValueError('Unchanged-source mismatch: '+relative)
                scope='仅核与上轮同SHA；未冒充本轮重新精读'
            rows.append({'科目':sub,'章':chapter['chapter'],'标题':chapter['title'],'正文':relative,'SHA256':current,
                '本轮改动':'是' if changed else '否','内容核验':scope,
                '范围':'本地243稳定组定位；正式2027全文细目仍待核',
                '选题与来源':f'editorial/full/{sub}/chapter_records.json；新增题详见editorial/{edition}/{sub}_revision.md',
                '计算与机制':f'editorial/full/{sub}/results.json；源结构检查另列',
                'PDF状态':'仅导出正文审阅稿；本轮未做结构、分页、裁切或逐页视觉检查',
                '后续':'用户内容审阅及必要修订后，再统一检查讲义排版'})
    chapter_csv=here/'逐章状态.csv'
    with chapter_csv.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    out.mkdir(parents=True,exist_ok=True)
    for src,name in [(ROOT/'editorial/scope/coverage.csv','知识覆盖表.csv'),
        (ROOT/'editorial/full/入选题总台账.csv','入选题台账.csv'),(chapter_csv,'逐章状态.csv')]:
        shutil.copyfile(src,out/name)
    state_path=ROOT/'PROJECT_STATE.json';state=load(state_path)
    state['stage']='第三轮正文审阅稿已完成并导出；待用户反馈，本轮讲义排版检查未执行'
    state['current_edition']=edition+'_content_review';state['delivery_date']=datetime.now(timezone.utc).date().isoformat()
    state['books']=books;state.pop('completed_scope',None)
    state['completed']=dict(books=4,chapters=len(rows),numbered_full_examples=sum(b['numbered_examples'] for b in books),
        referenced_figures=inventory['referenced_figures'],stable_groups_located=coverage['located_groups'],
        read_error_records=coverage['mistake_destinations'],
        changed_chapters_independently_read=sum(r['本轮改动']=='是' for r in rows),
        unchanged_chapters_baseline_SHA_only=sum(r['本轮改动']=='否' for r in rows),pdf_layout_checks_performed=False)
    state.pop('archive',None)
    state['delivery_mode']='git_project_directory';state['project_entry']='README.md'
    state['build']='bash build_review.sh'
    state['active_revision'].update(stage='正文、图稿、综合题、来源与内容复核完成，审阅PDF已导出；待用户反馈',
        last_updated=datetime.now(timezone.utc).isoformat(),content_review=f'editorial/{edition}/review/final_content_review.json',
        change_log=f'dist/{edition}/本轮修改说明.md',chapter_status=f'editorial/{edition}/逐章状态.csv',
        layout_review_status='NOT_PERFORMED；按用户要求内容审阅后执行',
        pending=['用户本轮正文反馈','反馈后的必要内容修订','后续新版PDF结构、分页、裁切及全页视觉检查'])
    state['resumable_state']='以当前manuscript、分科台账、本轮独立内容SHA及build/'+edition+'指纹为准；旧版本PDF和旧视觉记录仅为历史。本轮未检查排版。'
    dump(state_path,state)
    print(json.dumps(state['completed'],ensure_ascii=False))
if __name__=='__main__':main()
