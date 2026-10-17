#!/usr/bin/env python3
"""Join authored chapter records with stable scope IDs without guessing coverage.

The original scope and mistake-reading evidence stay available. This script
updates the current ledger only from explicit author mappings and real files.
It deliberately cannot certify the unavailable official 2027 syllabus text.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = dict(DS='数据结构', CO='计算机组成原理', OS='操作系统', CN='计算机网络')
KID = re.compile(r'^(?:DS|CO|OS|CN)-\d{2}-\d{2}$')

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def csvwrite(path, rows):
    if not rows: return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})

def mappings(records):
    found = {}
    def walk(value, context=None):
        if isinstance(value, dict):
            here = dict(context or {})
            for key in ['chapter','title','manuscript','file','path']:
                if key in value: here[key] = value[key]
            for key, entry in value.items():
                if KID.fullmatch(str(key)):
                    item = dict(entry) if isinstance(entry,dict) else {'location':entry}
                    found[key] = dict(context=here, **item)
            ident = value.get('id', value.get('knowledge_id', value.get('知识点 ID')))
            if isinstance(ident,str) and KID.fullmatch(ident):
                found[ident] = dict(context=here, **value)
            for child in value.values(): walk(child,here)
        elif isinstance(value,list):
            for child in value: walk(child,context)
    walk(records)
    return found

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-incomplete',action='store_true')
    parser.add_argument('--content-review',action='store_true',help='Record content-review scope; no PDF audit is performed')
    parser.add_argument('--review-edition',default='revision3')
    args = parser.parse_args()
    as_of = datetime.now(timezone.utc).date().isoformat()
    scope = ROOT / 'editorial/scope'
    base = json.loads((scope/'base_coverage.json').read_text())
    rows = base['rows']
    records = {}
    authored = {}
    selected = []
    decisions = {}
    by_knowledge = {}
    for sub in NAMES:
        p = ROOT/f'editorial/full/{sub}/chapter_records.json'
        if p.exists():
            records[sub] = json.loads(p.read_text())
            authored.update(mappings(records[sub]))
            for chapter in records[sub].get('chapters',[]):
                for example in chapter.get('examples',[]):
                    entry=dict(example)
                    entry['subject']=sub;entry['chapter']=chapter.get('chapter')
                    entry.setdefault('manuscript',chapter.get('manuscript'))
                    selected.append(entry)
                    for ident in entry.get('knowledge_ids',[]):
                        by_knowledge.setdefault(ident,[]).append(entry.get('id'))
            for decision in records[sub].get('errors',[]):
                if decision.get('id') in decisions:
                    raise ValueError('Duplicate mistake disposition: '+decision['id'])
                decisions[decision['id']]=decision
    error_path=ROOT/'editorial/errors/错误题总台账.json'
    error_payload=json.loads(error_path.read_text())
    for error in error_payload['records']:
        decision=decisions.get(error['id'])
        if not decision:continue
        if decision.get('knowledge_ids'):error['knowledge_ids']=decision['knowledge_ids']
        error.setdefault('initial_destination',error.get('destination'))
        error['destination']=decision.get('destination',error.get('destination'))
        error['full_book_handling']=decision
        loc={k:decision.get(k) for k in ['manuscript','anchor','location']}
        target=decision.get('target',decision.get('location',''))
        if isinstance(target,str) and '#' in target:
            path,anchor=target.split('#',1)
            if not loc['manuscript']:loc['manuscript']=path
            if not loc['anchor']:loc['anchor']=anchor
        loc['other_locations']=decision.get('locations',[])
        error['full_book_location']=loc
    dump(error_path,error_payload);csvwrite(error_path.with_suffix('.csv'),error_payload['records'])
    all_headings = {}
    for sub in NAMES:
        for p in sorted((ROOT/'manuscript'/sub).glob('[0-9][0-9]_*.md')):
            chapter = int(p.name[:2]); sec = 0
            for ln,line in enumerate(p.read_text().splitlines(),1):
                m = re.match(r'^(#{1,4})\s+(.+?)\s*\{#([^}\s]+)[^}]*\}\s*$',line)
                if not m: continue
                if len(m[1]) == 2: sec += 1
                h = dict(path=str(p.relative_to(ROOT)),line=ln,anchor=m[3],title=m[2],chapter=chapter,section=f'{chapter}.{sec}')
                all_headings[m[3]] = h
                if KID.fullmatch(m[3].upper()):
                    authored.setdefault(m[3].upper(),dict(anchor=m[3]))
    problems, completed = [], []
    for row in rows:
        ident = row['知识点 ID']
        item = authored.get(ident)
        if not item:
            problems.append(dict(id=ident,issue='作者台账/正文未提供明确的稳定ID位置映射'))
            continue
        anchor = str(item.get('anchor',item.get('锚点',''))).lstrip('#')
        if not anchor:
            candidate = ident.lower()
            if candidate in all_headings: anchor = candidate
        h = all_headings.get(anchor)
        if not h:
            problems.append(dict(id=ident,issue='映射锚点未在实际标题中找到',mapping=item))
            continue
        row['正文位置'] = f"{h['path']} §{h['section']}：{h['title']}（#{anchor}；第{h['line']}行）"
        row['实际正文锚点'] = anchor
        row['实际正文文件'] = h['path']
        row['例题 ID'] = item.get('examples') or item.get('example_ids') or item.get('例题 ID') or \
            list(dict.fromkeys(by_knowledge.get(ident,[]))) or '未另设完整编号题；解释、机制小例或边界辨析见本节，处理理由见分科考法台账'
        row['内容与题目来源'] = item.get('source',item.get('sources',f'WD27-{ident[:2]}；逐章选题、页码与复算见editorial/full/{ident[:2]}/chapter_records.json'))
        row['核验状态'] = item.get('status','已成稿并登记正文去向；知识/题源复核、计算与PDF检查见分立台账')
        row['核验状态'] = str(row['核验状态']) + '；正式2027大纲细目仍待逐条对照'
        row['相关个人错题 ID']=[e['id'] for e in error_payload['records'] if ident in e.get('knowledge_ids',[])]
        completed.append(ident)
    base['范围声明'] = '当前全稿沿用已读本地266条转录细目组织243个稳定知识组；正式2027大纲全文尚未取得，不宣称正式年度细目已完成逐条核验。'
    base['核验日期'] = as_of
    base['全稿回填依据'] = '实际作者台账明确ID/锚点映射与实际正文标题；定位核对不等于知识或题源自动审核。'
    dump(scope/'coverage.json',base); csvwrite(scope/'coverage.csv',rows)
    for sub in NAMES:
        subset = [r for r in rows if r['知识点 ID'].startswith(sub+'-')]
        dump(scope/f'{sub}_coverage.json',subset);csvwrite(scope/f'{sub}_coverage.csv',subset)
    validation = dict(date=as_of,stable_groups=len(rows),located_groups=len(completed),
        subjects=dict(Counter(x[:2] for x in completed)),unlocated=problems,
        official_2027_full_text_checked=False,
        separate_checks=['知识与条件审读','考法/选题与题源核验','实际计算和过程','PDF结构','人工逐页视觉'],
        status='全部稳定知识组已定位' if not problems else '仍有正文定位待核',
        selected_numbered_examples=sum(bool(re.match(r'^例\s*[A-Z]*\s*\d',
            all_headings.get(e.get('anchor',''),{}).get('title',''))) for e in selected),
        selected_source_records_including_selfchecks=len(selected),
        author_subject_records=list(records),missing_subject_records=[s for s in NAMES if s not in records],
        mistake_destinations=len(decisions),
        missing_mistake_destinations=[e['id'] for e in error_payload['records'] if e['id'] not in decisions],
        evidence='editorial/full/各科/chapter_records.json；正文文件；其他检查分别登记')
    if args.content_review:
        validation.update(edition=args.review_edition+'_content_review',pdf_checks='本轮未执行，待用户正文审阅后进行；历史检查不适用于当前修订正文')
    dump(ROOT/'editorial/full/coverage_validation.json',validation)
    dump(ROOT/'editorial/full/入选题总台账.json',dict(date=as_of,items=selected,
        source_limits='详细真题来源及核验按各科台账；社区复原不是官方原始发布；题目计数不是考试频率统计。'))
    csvwrite(ROOT/'editorial/full/入选题总台账.csv',selected)
    dump(ROOT/'editorial/full/错题最终去向.json',dict(date=as_of,decisions=list(decisions.values())))
    csvwrite(ROOT/'editorial/full/错题最终去向.csv',list(decisions.values()))
    methods=[]
    for r in rows:
        ident=r['知识点 ID'];entry=authored.get(ident,{})
        methods.append(dict(knowledge_id=ident,knowledge=r['知识点'],
            teaching_task=entry.get('methods') or r['核心考法'],learning_requirements=r['学习要求'],
            location=r['正文位置'],examples=r['例题 ID'],conditions=r['重要条件与边界'],
            handling='合并在相关代表题中，或以本节机制/辨析及自测承担；逐题新增价值和删除检查见入选题台账',
            priority_basis=r.get('教学优先级依据'),verification=r['核验状态']))
    dump(ROOT/'editorial/full/考法总表.json',dict(date=as_of,items=methods,
        caveat='按教学任务归组，不是对18年试卷的考频统计；真实独立计算与来源核验另记。'))
    csvwrite(ROOT/'editorial/full/考法总表.csv',methods)
    print(json.dumps(dict(located=len(completed),total=len(rows),problems=problems),ensure_ascii=False))
    if not args.allow_incomplete and (problems or validation['missing_subject_records'] or validation['missing_mistake_destinations']):
        raise SystemExit('Full editorial join is incomplete; inspect coverage_validation.json')

if __name__ == '__main__': main()
