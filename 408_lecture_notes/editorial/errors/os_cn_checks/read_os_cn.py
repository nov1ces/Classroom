from pathlib import Path
import json,fitz,hashlib,re,datetime,collections
out=Path('/workspace/408_lecture_notes/editorial/errors/os_cn_checks'); idx=json.load(open('/workspace/study_analysis/v2/all_items.json'))['old']; answers=json.load(open('/workspace/study_analysis/v2/book_answers.json'));docs={}; rows=[]
for i in idx:
 if i['subject'] not in ['OS','CN']:continue
 s=i['subject'];p=Path(i['question_path']);docs.setdefault(str(p),fitz.open(p));pg=docs[str(p)][i['PDF页码']-1];text=pg.get_text();body=text.split('· 第')[0].strip();a=answers.get(f"{s}:{i['section']}:{i['题号']}")
 flags=[]
 if pg.get_images():flags.append('页面含嵌入图像')
 if len(pg.get_drawings())>2:flags.append('页面有额外矢量图/表线')
 if any(0xE000<=ord(c)<=0xF8FF or c=='\ufffd' for c in body):flags.append('公式或特殊字形文本异常')
 if re.search('如图|下图|图所示|如下表|下表|下图',body):flags.append('题干引用图/表')
 ocr=[]
 if a:
  for crop in a['crops']:
   op=Path(f"/workspace/study_analysis/v2/ocr/{s}_{crop['page']:03}.json")
   if op.exists():
    ol=json.load(open(op));y0,y1=crop['bbox'][1],crop['bbox'][3]
    ocr.append({'page':crop['page'],'text':'\n'.join(l['text'] for l in ol['lines'] if y0<=(l['bbox'][1]+l['bbox'][3])/2<y1),'notice':'既有OCR，仅作定位与辅助阅读，未等于原书核验'})
 r={'id':f"ERR-{s}-{i['section']}-{i['题号']:03}",'subject':s,'section':i['section'],'section_name':i['section_name'],'chapter':i['chapter'],'question_number':i['题号'],'question_source':str(p),'source_pdf_page':i['PDF页码'],'original_choice':i['错选'],'raw_question_text':body,'raw_page_text':text,'question_crops':i['question_crops'],'graphic_flags':flags,'image_count':len(pg.get_images()),'vector_path_count':len(pg.get_drawings()),'extracted_characters':len(text),'answer_index':a,'answer_ocr':ocr,'original_annotation':'JSON仅记录错选；本题PDF为做题本印刷题，未见个人推理或教师批注','reading_level':'原题PDF文本逐条重新提取；待逐条语义核读与图示抽查'}
 rows.append(r)
(out/'os_cn_raw_read.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
logs={'date':'2026-10-15','operation':'PyMuPDF逐条打开原做题本对应页并重新提取','count':len(rows),'subjects':dict(collections.Counter(r['subject'] for r in rows)),'sources':[],'items':[{'id':r['id'],'page':r['source_pdf_page'],'chars':r['extracted_characters'],'graphic_flags':r['graphic_flags']} for r in rows]}
for path,doc in docs.items():logs['sources'].append({'path':path,'pages':len(doc),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()})
(out/'os_cn_read_log.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
print('read',len(rows),'flagged',sum(bool(r['graphic_flags']) for r in rows))
for s in ['OS','CN']:
 print(s,[(r['section'],r['question_number'],r['graphic_flags']) for r in rows if r['subject']==s and r['graphic_flags']])
