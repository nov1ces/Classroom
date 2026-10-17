#!/usr/bin/env python3
"""Merge read ledgers and the accepted sample locations into the scope draft.

The base scope is an editable snapshot. It is intentionally kept separate from
the sample overlay so a rebuild cannot erase audited sample locations.
"""
from pathlib import Path
from collections import Counter
import csv,json,re,hashlib

ROOT=Path(__file__).resolve().parents[1]
EDIT=ROOT/'editorial'
SCOPE=EDIT/'scope'
NAMES={'DS':'数据结构','CO':'计算机组成原理','OS':'操作系统','CN':'计算机网络'}

def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2))

def csvwrite(path,rows,keys=None):
    if not rows:return
    keys=keys or list(rows[0])
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items() if k in keys})

def errors():
    left=json.loads((EDIT/'errors/ds_co_errors.json').read_text())['records']
    right=json.loads((EDIT/'errors/os_cn_errors.json').read_text())
    records=[]
    for x in left:
        r=dict(id=x['id'],subject=x['subject'],subject_name=x['subject_name'],knowledge_ids=x.get('knowledge_ids',[]),
          knowledge_point=x['knowledge_point'],core_method=x['core_method'],question_pdf=x['question_pdf'],
          question_pdf_page=x['question_pdf_page'],original_question_number=x['question_number'],
          question_text=x['question_text'],raw_question_text=x['question_raw_text'],
          chosen_option=x['original_wrong_choice'],provided_reasoning=x['original_reasoning'],
          provided_grading=x['original_grading'],book_answer=x['answer_observed'],
          book_answer_pdf=x['answer_book'],book_answer_pages=sorted({c['page'] for c in x['answer_crops_hint']}),
          confirmed_personal_cause=x['confirmed_personal_cause'],
          cause_limit=x['personal_cause_status'],destination=x['provisional_destination'],
          correction_or_task=x['selection_reason'],unresolved=x['unresolved'],
          missing_materials=x['missing_materials'],reading_level=x['reading_level'],
          question_visual_checked=x['question_visual_checked'],answer_line_visual_checked=x['answer_visual_checked'],
          source_category=x['question_category'],exam_identity_status=x['official_exam_verification'],
          book_claimed_exam_years=x['book_claimed_exam_years'],
          detail_ledger='editorial/errors/ds_co_errors.json',detail_id=x['id'])
        records.append(r)
    for x in right:
        s,a=x['source'],x['actual_answer_information']
        r=dict(id=x['id'],subject=x['subject'],subject_name=x['subject_name'],knowledge_ids=x.get('knowledge_ids',[]),
          knowledge_point=x['knowledge_point'],core_method=x['core_method'],question_pdf=s['question_pdf'],
          question_pdf_page=s['question_pdf_page'],original_question_number=s['error_json_question_number'],
          printed_question_number=s['printed_question_number'],question_text=x['question_text'],raw_question_text=x['raw_question_text'],
          chosen_option=a['chosen_option'],provided_reasoning=a['provided_reasoning'],
          provided_grading=a['provided_teacher_annotation'],book_answer=a['book_correct_answer'],
          book_answer_pdf=s['book_answer_pdf'],book_answer_pages=s['book_answer_pdf_pages'],
          confirmed_personal_cause=x['confirmed_personal_error_cause'],cause_limit=x['cause_limit'],
          destination=x['initial_destination'],correction_or_task=x['question_specific_correction'],
          unresolved=[z for z in x['unresolved_or_missing'] if '个人' not in z],
          missing_materials=x['unresolved_or_missing'],reading_level=x['reading_level'],
          question_visual_checked=bool(x['evidence'].get('original_question_image')),
          answer_line_visual_checked=True,source_category=x['question_category'],exam_identity_status=x['exam_identity'],
          independent_calculation=x['independent_calculation'],detail_ledger='editorial/errors/os_cn_errors.json',detail_id=x['id'])
        records.append(r)
    records.sort(key=lambda x:(list(NAMES).index(x['subject']),x['question_pdf_page']))
    assert len(records)==457 and len({r['id'] for r in records})==457
    assert Counter(r['subject'] for r in records)==Counter(DS=97,CO=130,OS=133,CN=97)
    assert all(r['question_text'] and r['chosen_option'] and r['knowledge_point'] and r['destination'] for r in records)
    payload=dict(date='2026-10-15',scope='457条实际错题的读取、分类与初拟去向；并非457题全部独立复算或官方真题核验。',
       records=records)
    dump(EDIT/'errors/错误题总台账.json',payload)
    keys=['id','subject_name','knowledge_ids','knowledge_point','core_method','question_pdf','question_pdf_page',
      'original_question_number','printed_question_number','chosen_option','provided_reasoning','provided_grading',
      'book_answer','book_answer_pdf','book_answer_pages','confirmed_personal_cause','cause_limit',
      'destination','correction_or_task','unresolved','reading_level','exam_identity_status','detail_ledger']
    csvwrite(EDIT/'errors/错误题总台账.csv',records,keys)
    summary=dict(total=457,subjects=dict(Counter(r['subject_name'] for r in records)),
        raw_question_text_read=457,book_answer_lines_visually_checked=457,
        original_question_pages_visually_checked=sum(r['question_visual_checked'] for r in records),
        stable_knowledge_mapping=sum(bool(r['knowledge_ids']) for r in records),
        pending_mapping=[r['id'] for r in records if not r['knowledge_ids']],
        confirmed_personal_psychological_causes=0,
        caveat='图读数字是原题页标记计数；不等于全书/全题解析图读。原作答推理未记录，不猜个人心理错因。')
    dump(EDIT/'errors/总读取统计.json',summary)
    return records


def coverage(records):
    payload=json.loads((SCOPE/'base_coverage.json').read_text())
    rows=payload['rows']
    by_id={r['知识点 ID']:r for r in rows}
    sample={
      'OS-03-01':('§3.1；例3-1、例3-4','ERR-OS-2.3-011；ERR-OS-2.3-027（并入）；OS-EX-2024-46'),
      'OS-03-02':('§3.2 软件互斥与Peterson','TYP-OS-SW（典型算法与反例）'),
      'OS-03-03':('§3.2 TestAndSet、Swap及屏蔽中断','TYP-OS-HW（典型指令模型）'),
      'OS-03-04':('§3.2 自旋锁与阻塞锁','TYP-OS-HW（等待方式辨析）'),
      'OS-03-05':('§3.3；§3.4 例3-3','ERR-OS-2.3-018；MODEL-OS-SEM；OS-EX-2022-46'),
      'OS-03-06':('§3.8；例3-7','OS-EX-2018-28 / ERR-OS-2.3-054；ERR-OS-2.3-029（并入）；TYP-OS-CV'),
      'OS-03-07':('§3.5；例3-4至例3-6','OS-EX-2024-46；OS-EX-2009-45；OS-EX-2014-47；ERR-OS-2.3-039（并入）；TYP-OS-PC'),
      'OS-03-08':('§3.6 首末读者与公平条件','TYP-OS-RW（典型模型）'),
      'OS-03-09':('§3.7 申请人数限制与资源排序','TYP-OS-PHI（典型模型）'),
    }
    for kid,(where,qids) in sample.items():
        r=by_id[kid]
        r['正文位置']='操作系统第3章 '+where+'（样章已完成）'
        r['例题 ID']=qids
        r['内容与题目来源']='WD27-OS §2.3，PDF111–126理论；相关原题与答案见sample_selection.json、os_exam_candidates.json及个人错题台账；条件等待补参Oracle原始接口文档'
        r['核验状态']='样章正文、选题来源、过程复算和编辑修订已完成；PDF视觉检查另记；2027正式大纲细目仍待逐条核'
    for r in rows:
        r['相关个人错题 ID']=[x['id'] for x in records if r['知识点 ID'] in x['knowledge_ids']]
    payload['样章回填说明']='9个OS知识组回填实际正文位置；典型模型与完整编号例题分开登记；不变更官方细目待核状态。'
    dump(SCOPE/'coverage.json',payload)
    csvwrite(SCOPE/'coverage.csv',rows)
    for sub in NAMES:
        subset=[r for r in rows if r['知识点 ID'].startswith(sub+'-')]
        dump(SCOPE/f'{sub}_coverage.json',subset);csvwrite(SCOPE/f'{sub}_coverage.csv',subset)
    validation=json.loads((SCOPE/'coverage_validation.json').read_text())
    validation['范围']['OS']['正文完成组数']=9
    validation['范围']['OS']['已核验例题数']=7
    validation['范围']['OS']['题源口径']='5道真题（二手完整题页交叉核验，其中1道兼个人错题）+2道个人错题完整讲解；另3道错题并入辨析'
    validation['全部个人错题已登记']=len(records)
    validation['个人错题稳定ID已映射']=sum(bool(r['knowledge_ids']) for r in records)
    validation['各类验证分离']='知识正文、考法与选题、实际计算、PDF结构、PDF视觉检查分别见对应台账，不能互代。'
    dump(SCOPE/'coverage_validation.json',validation)
    p=SCOPE/'OS_目录.md';s=p.read_text()
    left,rest=s.split('## 第3章 同步、互斥与信号量',1)
    old,right=rest.split('## 第4章',1)
    chapter='''## 第3章 同步、互斥与信号量

状态：样章已完成；2027正式细目仍待核。稳定知识ID不因正文小节合并而改变。

前置：OS-01-01；OS-02-01；OS-02-02；OS-02-07。样章在3.1补定义并发交错、原子操作与运行/就绪/阻塞。

| 正文小节 | 实际任务 | 稳定ID |
| --- | --- | --- |
| 3.1 | 临界区、同步与互斥 | OS-03-01 |
| 3.2 | 软件互斥、硬件原子指令、自旋与阻塞 | OS-03-02；OS-03-03；OS-03-04 |
| 3.3 | 记录型信号量、P/V与初值 | OS-03-05 |
| 3.4 | 前驱图转线程代码 | OS-03-05 |
| 3.5 | 一次操作、有限缓冲、类别与整批约束 | OS-03-07；关联OS-03-01、OS-03-05 |
| 3.6 | 首末读者与公平条件 | OS-03-08 |
| 3.7 | 哲学家、人数限制与资源排序 | OS-03-09 |
| 3.8 | 管程、条件变量与等待语义 | OS-03-06 |
| 3.9—3.11 | 方法检查、回顾自测、题目与方法索引 | 回指上述组，不增造大纲条目 |

完整例题7道（真题5道，其中1道兼个人错题；另2道个人错题），3道个人错题并入辨析。经典模型另登记，见选题台账。原书§2.3为主资料，PDF111–126理论与相关习题、解析页已实际读。

'''
    p.write_text(left+chapter+'## 第4章'+right)
    return rows


def inventory():
    p=EDIT/'sources/file_inventory.json';rows=json.loads(p.read_text())
    for r in rows:
        if '错题精简.json' in r['filename']:
            r['content_status']='原始记录与对应题干选项已逐条读取；图核/答案行核读/独立复算层级见457条错题台账'
        if r['filename'].startswith('王道2027'):
            r['version_evidence']='版权页已图核：王道论坛组编，电子工业出版社，2026年1月第1版；各ISBN见scope/sources_verification.md'
            r['content_status']='版权页、目录与相关答案行已读；OS同步理论及题页另精读；未全书通读'
    dump(p,rows);csvwrite(EDIT/'sources/file_inventory.csv',rows)
    derived=[]
    for p in Path('/workspace/study_analysis').rglob('*'):
        if p.is_file():
            derived.append(dict(path=str(p),bytes=p.stat().st_size,status='既有派生产物；部分用作定位，非独立可信题源；实际使用见专项日志'))
    csvwrite(EDIT/'sources/derived_inventory.csv',derived)


def main():
    rs=errors();cr=coverage(rs);inventory()
    merged=['# 四科目录初稿\n\n本文件合并四科目录，OS第3章已经回填实际样章位置；其余为规划。正式2027大纲细目仍待核。\n']
    for s in NAMES:
        merged.append((SCOPE/f'{s}_目录.md').read_text())
    (EDIT/'四科目录初稿.md').write_text('\n\n---\n\n'.join(merged))
    print(json.dumps(dict(errors=len(rs),coverage=len(cr),sample_groups=9),ensure_ascii=False))

if __name__=='__main__':
    if (ROOT/'editorial/full/已确认的编写与标注规则.md').exists():
        raise SystemExit('此为历史样章同步器；全稿请运行 tools/sync_full_editorial.py，避免覆盖已完成章节。')
    main()
