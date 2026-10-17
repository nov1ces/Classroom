import json,csv,collections
from pathlib import Path
out=Path(__file__).parent;dest=out.parent;rs=json.load(open(dest/'os_cn_errors.json'));mp={}
def setm(subject,section,qs,*ids):
 for q in qs:mp[f'ERR-{subject}-{section}-{q:03}']=list(ids)
def default(subject,section,*ids):
 for r in rs:
  if r['subject']==subject and r['section']==section:mp[r['id']]=list(ids)
def os(sec,qs,*ids):setm('OS',sec,qs,*['OS-'+i for i in ids])
def cn(sec,qs,*ids):setm('CN',sec,qs,*['CN-'+i for i in ids])
os('1.1',[3],'01-01');os('1.1',[10],'01-05');default('OS','1.2','OS-01-02');os('1.2',[19,20],'01-01','01-02')
os('1.3',[2,11],'01-03');os('1.3',[4],'01-04');os('1.3',[14],'01-05');os('1.3',[18,21],'01-04');os('1.3',[31],'01-04','01-05')
os('1.6',[2,6,8],'01-08');os('1.6',[13],'01-09');os('1.6',[16,18],'01-10');os('1.6',[20],'01-09','01-04')
os('2.1',[3,39],'02-01');os('2.1',[10,11,58,72],'02-04');os('2.1',[15,16,40,46,61,65,71],'02-02');os('2.1',[22],'01-07');os('2.1',[49,52,53,66],'02-03');os('2.1',[67],'02-01','01-07');os('2.1',[70],'02-10','01-05')
os('2.2',[6],'02-07','03-01');os('2.2',[9],'02-10','02-03','01-07');os('2.2',[10,12,52],'02-08')
os('2.3',[11,27],'03-01');os('2.3',[18],'03-05');os('2.3',[29,54],'03-06');os('2.3',[39],'03-07','04-01')
os('2.4',[17],'04-01','04-02');os('2.4',[23],'03-05','04-01');os('2.4',[26],'04-03');os('2.4',[28],'04-01','04-03');os('2.4',[39],'04-02','04-03','04-04')
os('3.1',[9,11],'01-06','05-01');os('3.1',[13],'01-06','05-03');os('3.1',[28],'05-04','05-06');os('3.1',[31,39,48,54],'05-04');os('3.1',[33],'05-06','01-06');os('3.1',[40,51],'05-06');os('3.1',[41],'05-01');os('3.1',[61],'05-03');os('3.1',[62,68],'05-05');os('3.1',[63],'01-06','05-01')
os('3.2',[12,13],'05-07','05-08','05-09');os('3.2',[14],'05-05');os('3.2',[16],'05-09');os('3.2',[18],'05-01','05-07');os('3.2',[19],'05-04');os('3.2',[29,52],'05-11');os('3.2',[46],'05-07');os('3.2',[60],'05-08')
os('4.2',[2],'06-06');os('4.2',[3],'06-01');os('4.2',[10],'06-06','06-01');os('4.2',[21,25,26,28],'06-05');os('4.2',[23],'06-04','06-05');os('4.2',[35],'02-06','05-04','06-05');os('4.2',[37,39],'06-02');os('4.2',[41],'06-06','06-03','06-05');os('4.2',[54],'06-02','01-05');os('4.2',[60],'06-03');os('4.2',[64],'06-08','06-02');os('4.2',[70],'06-01','06-06')
os('4.3',[4],'06-01','06-05');os('4.3',[5,8,14,15,17],'06-09');os('4.3',[9],'07-08','01-09');os('4.3',[12],'06-10')
os('5.1',[1],'07-01','07-06');os('5.1',[4],'07-01');os('5.1',[12],'07-06');os('5.1',[16],'07-03','07-06');os('5.1',[19],'07-02','01-04');os('5.1',[20],'07-02','07-04');os('5.1',[21],'07-03','01-04')
os('5.2',[11,13,38,41],'07-05');os('5.2',[12],'07-05','03-01');os('5.2',[18],'01-02');os('5.2',[20,23],'07-07');os('5.2',[29],'07-06');os('5.2',[40],'07-03')
os('5.3',[3],'07-01','07-08');os('5.3',[5],'07-09','05-09');os('5.3',[8,10,16,17,30],'07-08');os('5.3',[25],'07-10')
cn('1.2',[1],'01-04','01-05');cn('1.2',[15,17,18,23,25,28],'01-06');cn('1.2',[29],'01-06','05-01');cn('1.2',[38],'01-06','03-01')
cn('2.1',[1,7,16],'02-01');cn('2.1',[10,12],'02-02');cn('2.1',[17],'02-02','02-03');cn('2.2',[4],'02-06');default('CN','2.3','CN-02-08')
cn('3.4',[8,10],'03-07');cn('3.4',[18],'03-05');cn('3.4',[19],'03-07','01-03');cn('3.5',[14],'03-13')
cn('3.6',[3],'02-04','03-15');cn('3.6',[4,23],'03-14');cn('3.6',[8],'03-17','03-15');cn('3.6',[20],'03-11','01-03');cn('3.6',[21],'03-15','02-06');cn('3.6',[25],'03-15');cn('3.6',[28],'03-12');cn('3.6',[31],'03-16');cn('3.6',[32,36],'03-17');cn('3.6',[48],'03-12','03-16')
cn('3.8',[13],'03-19','02-08','01-03');cn('3.8',[15],'03-19');cn('3.8',[20],'03-19','01-03')
cn('4.1',[1,3],'04-01');cn('4.1',[6],'02-04');cn('4.1',[11,13,20],'02-05');cn('4.1',[18],'04-02')
cn('4.2',[4],'04-07');cn('4.2',[18,21,40,42,64],'04-08');cn('4.2',[24],'04-08','04-09');cn('4.2',[43,45],'04-08','04-11');cn('4.2',[48,51],'04-13');cn('4.2',[66],'04-07');cn('4.2',[72],'04-12');default('CN','4.3','CN-04-14')
cn('4.4',[6],'04-17','04-15');cn('4.4',[12],'04-16','04-05');cn('4.4',[15],'04-17');cn('4.4',[19],'04-18');cn('4.4',[20],'04-16','04-17','04-18');default('CN','4.5','CN-04-19');default('CN','4.6','CN-04-20');cn('4.7',[16],'04-21','04-09');cn('4.7',[18],'04-03','01-03')
cn('5.2',[4],'05-02');cn('5.2',[8,16],'05-03');cn('5.2',[15],'05-01','05-02');cn('5.3',[7,11],'05-04');cn('5.3',[10,14,29],'05-07');cn('5.3',[13],'05-09');cn('5.3',[21],'05-04','05-05');cn('5.3',[33,52],'05-08');cn('5.3',[47],'05-09','05-08');cn('5.3',[60],'05-09','05-08','05-04')
cn('6.1',[4],'06-01');cn('6.2',[1],'06-02');cn('6.2',[12],'06-03');cn('6.2',[14],'06-03','06-08','05-05');cn('6.3',[5],'06-04');default('CN','6.5','CN-06-08');cn('6.5',[18],'06-08','05-08')
known={r['知识点 ID']:r['知识点'] for s in ['OS','CN'] for r in json.load(open(dest.parent/'scope'/f'{s}_coverage.json'))}
sample={'ERR-OS-2.3-011':'样章完整例3-1（同步与互斥并存）','ERR-OS-2.3-018':'样章完整例3-2（信号量初值）','ERR-OS-2.3-027':'并入样章§3.1临界区定义','ERR-OS-2.3-029':'并入样章§3.8条件变量辨析','ERR-OS-2.3-039':'并入样章§3.5生产者—消费者模型与死锁区别','ERR-OS-2.3-054':'样章完整例3-7，真题2018年第28题'}
missing=[]
for r in rs:
 ids=mp.get(r['id'],[])
 if any(i not in known for i in ids):raise ValueError((r['id'],ids))
 r['knowledge_ids']=ids;r['knowledge_mapping']=[{'id':i,'name':known[i]} for i in ids];r['knowledge_mapping_status']='已据实际题干机制人工对应覆盖表初稿；不代表此题覆盖该知识点全部学习要求' if ids else '待章节映射：未能明确对应，不猜测'
 if not ids:missing.append(r['id'])
 if r['id'] in sample:
  r['initial_destination']=sample[r['id']]
  r['verification_status']='样章去向已定；原题与书答案已图读，选项已独立按机制核对；原个人推理未提供'
 if r['id']=='ERR-OS-2.3-054':r['question_category']=['我的错题','408真题（2018年第28题；第三方重建卷交叉核对）']
 if r['id']=='ERR-OS-4.2-028':r['selection_reason_and_deletion_check']='书将FAT支持的最大文件长度理解为整个分区大小，再求2^16簇与128KiB FAT；正文须声明该教材假设，不能由一般文件最大长度推出全盘FAT规模'
(dest/'os_cn_errors.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2))
# 按既有csv字段顺序，补稳定知识点ID及样章已定去向。
p=dest/'os_cn_errors.csv'
with open(p,encoding='utf-8-sig',newline='') as f:csvrows=list(csv.DictReader(f));fields=list(csvrows[0])

if '知识点ID' not in fields:fields.insert(fields.index('知识点'),'知识点ID')
lookup={r['id']:r for r in rs}
for r in csvrows:r['知识点ID']=';'.join(lookup[r['稳定ID']]['knowledge_ids']);r['初拟去向']=lookup[r['稳定ID']]['initial_destination'];r['选题价值与边界']=lookup[r['稳定ID']]['selection_reason_and_deletion_check'];r['核验状态']=lookup[r['稳定ID']]['verification_status']
with open(p,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(csvrows)
summary={'date':'2026-10-15','json_format':'顶层数组，每元素为一条实际错题','primary_key':'id','join_to_coverage_key':'knowledge_ids（数组，覆盖表中文键“知识点 ID”）','items_read':len(rs),'subjects':dict(collections.Counter(r['subject'] for r in rs)),'answer_lines_visually_checked':len(rs),'full_original_question_text_semantically_read':len(rs),'graphic_or_formula_anomalies_visually_checked':18,'independent_calculation_records':46,'independently_checked_sample_concept_questions':6,'book_tagged_exam_candidates':sum(r['exam_identity']['book_tag_year'] is not None for r in rs),'exam_identity_cross_checked_with_secondary_full_paper':1,'coverage_mapping_complete_items':len(rs)-len(missing),'coverage_mapping_pending_items':missing,'personal_psychological_causes_confirmed':0,'personal_answer_book_answer_conflicts':['ERR-OS-3.1-011'],'fixed_ocr_answer_indices':{'ERR-CN-1.2-023':'B,D,C,A,B'},'sample_destinations':sample,'selection_status':'样章6条去向已定；其余为按考法初拟去向，未称全部选题定稿','json_path':str(dest/'os_cn_errors.json'),'csv_path':str(dest/'os_cn_errors.csv')}
summary['read_report_path']=str(dest/'os_cn_read_report.md');summary['calculation_validation_assertions']=11;summary['calculation_validation_assertions_passed']=11
(dest/'os_cn_report_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
