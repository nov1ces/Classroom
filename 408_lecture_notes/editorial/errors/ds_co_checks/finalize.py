from pathlib import Path
import json,collections,csv,hashlib,os
ROOT=Path('/workspace/408_lecture_notes/editorial/errors');R=ROOT/'ds_co_checks';p=ROOT/'ds_co_errors.json';d=json.load(open(p));rs=d['records'];idx={x['id']:x for x in rs}
inputs=sorted(set(x[k] for x in rs for k in ['source_json','question_pdf','answer_book']))
sources=[]
for fn in inputs:
 fp=Path(fn);h=hashlib.sha256()
 with fp.open('rb') as f:
  while True:
   b=f.read(4*1024*1024)
   if not b:break
   h.update(b)
 sources.append({'path':fn,'bytes':fp.stat().st_size,'sha256':h.hexdigest(),'access':'原文件已读取；题目/答案读取层级分别登记。'})
(R/'source_fingerprints.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
visual_log=[]
for i in range(1,13):
 sh=R/'sheets'/f'answer_{i:02}.jpg';ids=json.load(open(sh.with_suffix('.json')))
 visual_log.append({'event':'answer_label_sheet_visually_read','sheet':str(sh),'ids':ids,'scope':'原书题号和答案字母已目验；只显示每条解析开头，不能宣称整段解析已逐字核。'})
for i in range(1,7):
 sh=R/'sheets'/f'question_{i:02}.jpg';ids=json.load(open(sh.with_suffix('.json')))
 visual_log.append({'event':'question_anomaly_sheet_visually_read','sheet':str(sh),'ids':ids,'scope':'原PDF题干、公式排式或题图；核对私用符号与位置信息。'})
extra=['ERR-DS-3.1-026','ERR-DS-3.2-009','ERR-DS-7.2-002','ERR-DS-6.4-019','ERR-CO-2.3-021','ERR-CO-3.5-030','ERR-CO-5.6-008','ERR-CO-6.1-025']
for i in range(2):visual_log.append({'event':'question_suspect_sheet_visually_read','sheet':str(R/'sheets'/f'extra_question_{i+1:02}.jpg'),'ids':extra[i*4:i*4+4],'scope':'原PDF正文疑点，含源题条件或转录问题。'})
for rid,img,bpg,note in [
 ('ERR-DS-3.1-026','DS_book_p080.png',80,'书中序列bdcfeag与做题本bdefeag不同。'),
 ('ERR-CO-2.2-022','CO_book_p057_q22.png',57,'原书else字符串计算机教育，做题本改成做题本集合地。'),
 ('ERR-CO-2.3-021','CO_book_p075_q21_q24.png',75,'原书数组第一行{2,9,-1,5}；做题本为{2,9,-1.5}。'),
 ('ERR-CO-5.6-013','CO_book_p268.png',268,'原书I2为load，做题本误排为add。')]:
 visual_log.append({'event':'original_book_question_visually_compared','id':rid,'source_book':idx[rid]['answer_book'],'source_book_pdf_page':bpg,'image':str(R/'question_anomalies'/img),'observation':note})
visual_log.append({'event':'additional_question_suspect_visually_read','id':'ERR-CO-5.6-013','image':str(R/'question_anomalies'/'ERR-CO-5.6-013.png'),'scope':'做题本操作码与访存注释不一致，已对照原书恢复load。'})
for rid in ['ERR-CO-3.5-030','ERR-CO-5.6-008','ERR-CO-3.6-005','ERR-DS-3.1-026']:
 visual_log.append({'event':'full_book_answer_band_visually_read','id':rid,'image':str(R/'answer_labels'/f'{rid}_full.png'),'source_crops':idx[rid]['answer_crops_hint']})
with (R/'read_events.jsonl').open('a') as f:
 for e in visual_log:f.write(json.dumps(e,ensure_ascii=False)+'\n')
(R/'visual_checks.json').write_text(json.dumps({'viewed_tool_images':visual_log,'question_check_count':sum(x['question_visual_checked'] for x in rs),'answer_label_check_count':227,'question_checks':[{'id':x['id'],'pdf':x['question_pdf'],'pdf_page':x['question_pdf_page'],'image':x['question_visual_image'],'notes':x['question_visual_read_notes']} for x in rs if x['question_visual_checked']]},ensure_ascii=False,indent=2))
for x in rs:
 x['student_work_availability']='只有所选选项；未见个人推理、手写步骤或批改文字。'
 x['official_exam_paper_question_number']=None
 x['question_elements_read']={'stem_and_options':'原题PDF原生文字逐条读取','formulas':'出现私用字符/上标异常者已目验，未将所有文字题标成整页视觉校对','diagram':'原题含嵌入图且已目验' if x['embedded_image_count'] else '未检测到嵌入题图；题目整页目验状态见question_visual_checked','personal_choice':'原JSON实读','grading':'原JSON错题标记已读；未含批改过程','book_answer':'原书扫描裁图中的题号和答案字母目验'}
 x['independent_exam_source_verification']='待原卷核对；书中真题标签不替代年份、原题号、全部图文和答案核验。'
 x['missing_problem_information_requiring_user']=[]
 x['difficulty']='待章节按前置知识和综合程度复核，不由题号或错选猜测难度。'
 x['incremental_teaching_task']=x['core_method']+'；需强调：'+x['conditions_and_boundaries']
 x['deletion_check_status']='待对应章节入选题定稿后比较解题模型、关键条件和真实错因；本轮仅作初拟去向。'
d['counts_by_destination']=dict(collections.Counter(x['provisional_destination'] for x in rs));d['verification_counts']={'native_question_reextract_and_read':227,'question_page_visual_checks':50,'embedded_figure_question_visual_checks':4,'book_answer_label_visual_checks':227,'independent_calculation_questions':sum(x['independent_calculation_checked'] for x in rs),'independent_calculation_checks':72,'official_exam_paper_verified':0,'knowledge_linked':226,'knowledge_link_pending':1,'confirmed_personal_reasoning_causes':0}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
cp=ROOT/'ds_co_errors.csv';cols=next(csv.reader(cp.open(encoding='utf-8-sig')))
for col in ['independent_calculation_checked','independent_calculation_check_numbers','answer_verification_scope','missing_problem_information_requiring_user']:
 if col not in cols:cols.append(col)
with cp.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader()
 for x in rs:
  y={k:x.get(k) for k in cols}
  for k,v in list(y.items()):
   if isinstance(v,(dict,list)):y[k]=json.dumps(v,ensure_ascii=False)
  w.writerow(y)
# Actual record-based checks, not merely title/file-existence checks.
assert len(rs)==227 and len({x['id'] for x in rs})==227
assert collections.Counter(x['subject'] for x in rs)=={'DS':97,'CO':130}
assert all(x['question_source_reextracted'] and x['question_text_read_by_editor'] for x in rs)
assert all(x['answer_visual_checked'] and x['answer_observed'] for x in rs)
assert all(x['confirmed_personal_cause'] is None and not x['official_exam_verified'] for x in rs)
assert all(not x['embedded_image_count'] or x['question_visual_checked'] for x in rs)
assert all(not x['anomaly_flags'] or x['question_visual_checked'] for x in rs)
assert all(x['original_wrong_choice'] for x in rs)
assert sum(x['independent_calculation_checked'] for x in rs)==71
csvrows=list(csv.DictReader(cp.open(encoding='utf-8-sig')));assert len(csvrows)==227
assert set(x['id'] for x in csvrows)==set(idx)
assert all(x['knowledge_point'] and x['core_method'] and x['conditions_and_boundaries'] for x in rs)
assert len([x for x in rs if not x['knowledge_ids']])==1
validation={'record_count':227,'unique_id_count':227,'source_item_counts':{'DS':97,'CO':130},'all_source_questions_reread':True,'all_book_answer_letters_visually_read':True,'all_detected_formula_or_image_anomalies_visually_read':True,'all_embedded_figure_questions_visually_read':True,'no_invented_personal_reasoning':True,'no_unverified_exam_promoted_to_verified':True,'independent_calculation_actual_questions':71,'csv_record_count':227,'knowledge_link_pending':['ERR-CO-3.2-026'],'status':'passed'}
(R/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
# Human-readable per-item issue list keeps unresolved cases recoverable.
issues=['# 数据结构、计组源题与条件检查\n','本表是编辑材料。源题答案字母目验不代表条件争议已解决。\n']
for x in rs:
 if x.get('source_correction') or x['unresolved']:
  issues.append('## '+x['id']+'\n')
  issues.append('原题：'+x['question_pdf']+'，PDF p'+str(x['question_pdf_page'])+'；答案书PDF p'+str(x['answer_crops_hint'][0]['page'])+'。\n')
  if x.get('source_correction'):
   c=x['source_correction'];issues.append(c['issue']+'\n恢复内容：'+c['restored']+'\n依据：'+c['basis']+'\n处理：'+c['action']+'\n')
  issues.extend(u+'\n' for u in x['unresolved'])
(R/'source_issues.md').write_text('\n'.join(issues))
print(json.dumps(d['verification_counts'],ensure_ascii=False))
