from pathlib import Path
import json,fitz,re,hashlib,datetime,collections
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/workspace/408_lecture_notes/editorial/errors');OUT=ROOT/'ds_co_checks';OUT.mkdir(exist_ok=True)
for d in ['question_anomalies','answer_labels','sheets']:(OUT/d).mkdir(exist_ok=True)
old=json.load(open('/workspace/study_analysis/v2/all_items.json'))['old'];old_index={(x['subject'],x['section'],x['题号']):x for x in old}
answers=json.load(open('/workspace/study_analysis/v2/book_answers.json'))
subjects={'DS':('数据结构','01_数据结构'),'CO':('计算机组成原理','02_计算机组成原理')};docs={};records=[];log=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for s,(name,folder) in subjects.items():
 src=Path('/workspace/Classroom')/folder/(name+'错题精简.json'); data=json.load(open(src))
 qp=next(src.parent.glob('*横版*pdf'));bp=Path('/workspace/study_analysis/v2/books')/('王道2027'+name+'_高清带书签版.pdf');qd=fitz.open(qp);bd=fitz.open(bp)
 docs[s]=(qd,bd)
 for ci,ch in enumerate(data):
  for si,sec in enumerate(ch['节列表']):
   for ei,e in enumerate(sec['错题列表']):
    no=e['题号'];section=sec['节号'];pg=e['PDF页码'];rid=f'ERR-{s}-{section}-{no:03}';oi=old_index[(s,section,no)];p=qd[pg-1];raw=p.get_text(sort=False)
    # Native source is re-read here; prior extracted strings are comparison only.
    text='\n'.join(l for l in raw.splitlines() if not any(k in l for k in ['公众号：','27王道','· 第','共641','共604']))
    text=text.strip();puas=sorted(set(c for c in text if 0xe000<=ord(c)<=0xf8ff));images=p.get_images();inside=[x for x in p.get_drawings() if 42<x['rect'].y0<420 and x['rect'].x0>40]
    options=sorted(set(re.findall(r'(?<![A-Za-z])([ABCD])[.．、]',text)))
    flags=[]
    if puas:flags.append('原生提取含私用区符号，括号/根式等需图核')
    if images:flags.append('原题含嵌入图，文字层不含完整图意')
    if inside:flags.append('题内存在矢量覆盖或线框，需检查是否遮蔽原文')
    if options!=list('ABCD'):flags.append('提取选项标记不完整或题型特殊')
    if any(k in text for k in ['下图','右图','图所示','图中','如下图']) and not images:flags.append('题干引用图示，需检查图文对应')
    # Small superscripts do not by themselves prove lost semantics, but are separately flagged.
    ss=p.get_text('dict')['blocks'];sup=any(sp.get('flags',0)&1 for b in ss if 'lines' in b for l in b['lines'] for sp in l['spans'] if 42<sp['bbox'][1]<420)
    if sup and not flags:flags.append('有上/下标或小字号数学排式，需图核符号层级')
    ak=f'{s}:{section}:{no}';a=answers.get(ak);aocr=[]
    if a:
     for c in a['crops']:
      fp=Path('/workspace/study_analysis/v2/ocr')/f'{s}_{c["page"]:03}.json';od=json.load(open(fp)) if fp.exists() else {'lines':[]};box=c['bbox']
      aocr.extend(l['text'] for l in od['lines'] if box[0]-3<=l['bbox'][0]<=box[2]+3 and box[1]-3<=l['bbox'][1]<box[3]-1)
     ac=a['crops'][0];box=fitz.Rect(ac['bbox']);box.y1=min(box.y0+60, max(box.y1,box.y0+28));pix=bd[ac['page']-1].get_pixmap(matrix=fitz.Matrix(2.4,2.4),clip=box,colorspace=fitz.csGRAY,alpha=False);ap=OUT/'answer_labels'/f'{rid}.png';pix.save(ap)
    years=re.findall(r'(20\d{2})\s*统考真题',text)
    rec={'id':rid,'legacy_id':oi['id'],'subject':s,'subject_name':name,'chapter':ch['章名'],'section':section,'section_name':sec['节名'],'question_number':no,'source_json':str(src),'json_pointer':f'/{ci}/节列表/{si}/错题列表/{ei}','question_pdf':str(qp),'question_pdf_page':pg,'question_raw_text':raw,'question_text':text,'options_detected':options,'question_source_reextracted':True,'previous_text_matches':raw==oi['text'],'original_wrong_choice':e['错选'],'original_grading':'原 JSON 将本条列为错题，并记录错选；未含批改文字、评分过程或作答推理。','original_reasoning':None,'confirmed_personal_cause':None,'personal_cause_status':'未提供作答推理，不能由错选反推个人错因。','pdf_annotation_count':len(list(p.annots() or [])),'source_identity':'王道做题本题目；原书题源与个人错题身份分别登记','personal_error':True,'book_claimed_exam_years':years,'official_exam_verified':False,'official_exam_verification':'仅能确认做题本是否印有统考真题标签；尚未对照官方完整卷核验原年份题号。','anomaly_flags':flags,'native_private_symbols':[f'U+{ord(c):04X}' for c in puas],'embedded_image_count':len(images),'interior_vector_count':len(inside),'superscript_detected':sup,'question_visual_checked':False,'answer_book':str(bp),'answer_key_index':ak,'answer_index_hint':a['answer'] if a else None,'answer_crops_hint':a['crops'] if a else [],'answer_explanation_ocr_unverified':'\n'.join(aocr),'answer_visual_checked':False,'answer_observed':None,'reading_level':'原题 PDF 原生文字已重提并登记；尚待逐题内容分类/必要图核；答案索引仅作线索。','unresolved':[]}
    if flags:
     blocks=p.get_text('blocks');bottom=max([b[3] for b in blocks if 42<=b[1]<420]+[200]);bb=fitz.Rect(58,42,540,min(424,bottom+8));qpix=p.get_pixmap(matrix=fitz.Matrix(2,2),clip=bb,alpha=False);ip=OUT/'question_anomalies'/f'{rid}.png';qpix.save(ip);rec['question_visual_image']=str(ip)
    records.append(rec);log.append({'id':rid,'event':'native_question_pdf_reread','path':str(qp),'pdf_page':pg,'text_sha256':hashlib.sha256(raw.encode()).hexdigest(),'comparison_prior_text_equal':raw==oi['text'],'annotation_count':rec['pdf_annotation_count']})

def sheets(kind,selected,per=20,cols=2,width=600):
 for start in range(0,len(selected),per):
  chunk=selected[start:start+per];rows=[]
  for rr in range(0,len(chunk),cols):
   cells=[]
   for r in chunk[rr:rr+cols]:
    path=Path(r['question_visual_image']) if kind=='question' else OUT/'answer_labels'/f'{r["id"]}.png';im=Image.open(path).convert('RGB');im=im.resize((width,int(im.height*width/im.width)));cell=Image.new('RGB',(width,im.height+29),'white');cell.paste(im,(0,29));ImageDraw.Draw(cell).text((3,3),r['id']+' / p'+str(r['question_pdf_page'] if kind=='question' else r['answer_crops_hint'][0]['page']),(0,0,0),font=font);cells.append(cell)
   h=max(x.height for x in cells);row=Image.new('RGB',(width*cols,h),'#dddddd')
   for i,cell in enumerate(cells):row.paste(cell,(i*width,0))
   rows.append(row)
  sheet=Image.new('RGB',(width*cols,sum(x.height for x in rows)+len(rows)*5),'#bbbbbb');y=0
  for row in rows:sheet.paste(row,(0,y));y+=row.height+5
  out=OUT/'sheets'/f'{kind}_{start//per+1:02}.jpg';sheet.save(out,quality=94);(out.with_suffix('.json')).write_text(json.dumps([x['id'] for x in chunk],ensure_ascii=False,indent=2))
sheets('answer',records,20,2,660)
sheets('question',[x for x in records if x['anomaly_flags']],8,2,840)
(OUT/'native_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(OUT/'read_events.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in log))
print('records',len(records),'DS',sum(r['subject']=='DS' for r in records),'CO',sum(r['subject']=='CO' for r in records),'anomalies',sum(bool(x['anomaly_flags']) for x in records),'answer hints missing',sum(x['answer_index_hint'] is None for x in records),'prior text differs',sum(not x['previous_text_matches'] for x in records))
print(collections.Counter(f for x in records for f in x['anomaly_flags']))
