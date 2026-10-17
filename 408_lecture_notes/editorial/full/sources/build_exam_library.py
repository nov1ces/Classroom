#!/usr/bin/env python3
"""Fetch community reconstructed papers; never claim official publication or answer verification."""
from pathlib import Path
import concurrent.futures,hashlib,json,shutil,urllib.request,fitz,re
ROOT=Path('/workspace/408_lecture_notes')
OUT=ROOT/'editorial/sources/exams'
REPORT=ROOT/'editorial/full/sources'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
existing={2009:ROOT/'editorial/sources/os_exam_checks/exam_2009_rebuild.pdf',2014:ROOT/'editorial/sources/os_exam_checks/exam_2014_rebuild.pdf',2018:ROOT/'editorial/errors/os_cn_checks/exam_2018_rebuild.pdf',2022:ROOT/'editorial/sources/os_exam_checks/exam_2022_rebuild.pdf',2024:ROOT/'editorial/sources/os_exam_checks/exam_2024_rebuild.pdf',2025:ROOT/'editorial/sources/os_exam_checks/exam_2025_rebuild.pdf'}
def subject(year,q):
 if q<=40:
  ds_end=10 if year==2009 else 11
  return 'DS' if q<=ds_end else 'CO' if q<=22 else 'OS' if q<=32 else 'CN'
 special={2014:{41:'DS',42:'DS',43:'CN',44:'CO',45:'CO',46:'OS',47:'OS'},2016:{41:'CN',42:'DS',43:'DS',44:'CO',45:'CO',46:'OS',47:'OS'},2019:{41:'DS',42:'DS',43:'OS',44:'OS',45:'CO',46:'CO',47:'CN'}}
 return special.get(year,{}).get(q,'DS' if q in (41,42) else 'CO' if q in (43,44) else 'OS' if q in (45,46) else 'CN')

def download(year):
 p=OUT/f'exam_{year}_rebuild.pdf'
 url=f'https://raw.githubusercontent.com/neville-studio/408-exam-paper/main/papers-rebuild/{year}.pdf'
 via='downloaded'
 if not p.exists():
  if year in existing and existing[year].exists(): shutil.copy2(existing[year],p);via='copied_previously_downloaded'
  else:
   with urllib.request.urlopen(url,timeout=40) as r: data=r.read()
   if not data.startswith(b'%PDF'): raise ValueError('not PDF')
   p.write_bytes(data)
 else:via='existing'
 doc=fitz.open(p)
 texts=[pg.get_text() for pg in doc]
 (OUT/f'exam_{year}.txt').write_text('\n'.join(f'\n[[PDF_PAGE:{i+1}]]\n'+t for i,t in enumerate(texts)),encoding='utf8')
 items=[]
 # Sequential q labels suppress incidental line-start numbers in code/data.
 want=1
 for pg,t in enumerate(texts,1):
  for m in re.finditer(r'(?m)^\s*(\d{1,2})\s*[.．、]\s*',t):
   q=int(m.group(1))
   if q!=want or q>47: continue
   tail=t[m.end():].strip().replace('\n',' ')
   items.append({'year':year,'question':q,'pdf_page':pg,'subject':subject(year,q),'text_start':tail[:160],'full_pdf':str(p),'verification_status':'定位索引；尚未逐题核对题干/选项/图示/答案'})
   want+=1
 row={'year':year,'source_kind':'社区二手复原卷，非官方原始发布','source_url':url,'local_pdf':str(p),'access':via,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(doc),'question_starts_detected':len(items),'index_complete':len(items)==47,'answers':'该卷未包含可据此认证的官方答案；选用时须与主书及独立解答交叉核验'}
 return row,items
rows=[];questions=[];failed=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 futures={pool.submit(download,y):y for y in range(2009,2027)}
 for f in concurrent.futures.as_completed(futures):
  y=futures[f]
  try:
   row,items=f.result();rows.append(row);questions+=items
   print(y,'OK',row['pages'],'pages',row['question_starts_detected'],'question positions',flush=True)
  except Exception as e: failed.append({'year':y,'error':repr(e)});print(y,'FAILED',repr(e),flush=True)
rows.sort(key=lambda r:r['year']);questions.sort(key=lambda r:(r['year'],r['question']))
(REPORT/'exam_library_manifest.json').write_text(json.dumps({'date':'2026-10-16','scope':'仅下载/读取文字与定位；不等于逐题核验，不作频率统计','papers':rows,'failures':failed},ensure_ascii=False,indent=2),encoding='utf8')
(REPORT/'exam_question_index.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf8')
import csv
with (REPORT/'exam_question_index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(questions[0]) if questions else []);w.writeheader();w.writerows(questions)
for row in rows:
 if not row['index_complete']: print('INDEX_INCOMPLETE',row['year'])
