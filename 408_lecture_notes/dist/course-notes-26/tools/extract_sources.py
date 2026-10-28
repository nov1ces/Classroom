#!/usr/bin/env python3
"""Inventory and extract all project lecture slides and maps; extraction is not content review."""
from pathlib import Path
import argparse,collections,datetime,hashlib,json,re,subprocess,concurrent.futures
import fitz,os
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[2]
CN={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8}
SUBJECTS={'01_数据结构':'DS','02_计算机组成原理':'CO','03_操作系统':'OS','04_计算机网络':'CN'}
def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(2**20),b''):h.update(chunk)
 return h.hexdigest()
def chapter_id(p,subject):
 for part in p.parts:
  m=re.search(r'第([一二三四五六七八])章',part)
  if m:return subject+str(CN[m[1]]).zfill(2)
 return 'maps'
def extract():
 files=[];page_files=[];subject_counts=collections.defaultdict(collections.Counter)
 for dirname,subject in SUBJECTS.items():
  directory=PROJECT/dirname
  for group in sorted(directory.iterdir()):
   if not group.is_dir() or not (group.name.startswith('【课件】') or group.name.startswith('【导图】')):continue
   kind='lecture' if group.name.startswith('【课件】') else 'mindmap'
   for path in sorted(group.rglob('*.pdf')):
    ident=chapter_id(path.relative_to(group),subject)
    target=ROOT/'sources'/'extracted'/subject/ident/(path.stem+'.txt')
    target.parent.mkdir(parents=True,exist_ok=True)
    pdf=fitz.open(path);pages=[];text_chunks=[];hash_groups=collections.defaultdict(list)
    for i,page in enumerate(pdf):
     s=page.get_text('text',sort=True)
     norm=re.sub(r'\s+','',s)
     txt_hash=hashlib.sha256(norm.encode()).hexdigest()
     residual=re.sub(r'[王道计算机考研]','',norm)
     entry={'file_page':i+1,'text_chars':len(s),'nonspace_chars':len(norm),'watermark_residual_chars':len(residual),'image_objects':len(page.get_images(full=True)),'text_sha256':txt_hash,'needs_visual_or_ocr':len(residual)<40}
     pages.append(entry)
     if norm:hash_groups[txt_hash].append(i+1)
     text_chunks.append(f'\n===== 文件页 {i+1} / {len(pdf)} =====\n'+s)
    rel=str(path.relative_to(PROJECT))
    target.write_text(f'来源：{rel}\n科目：{subject}\n章节：{ident}\n状态：自动文本提取，未授予人工核验结论\n'+''.join(text_chunks),encoding='utf-8')
    stat={'id':subject+'-'+kind+'-'+path.stem,'subject':subject,'chapter':ident,'kind':kind,'path':rel,'bytes':path.stat().st_size,'sha256':sha_file(path),'pdf_pages':len(pdf),'extracted_text':str(target.relative_to(ROOT)),'pages_requiring_visual_or_ocr':[x['file_page'] for x in pages if x['needs_visual_or_ocr']],'same_normalized_text_page_groups':[v for v in hash_groups.values() if len(v)>1],'extraction_status':'all_pages_extracted','content_review_status':'pending','duplicate_policy':'equal nonempty normalized text is a candidate only; figure/animation/state equivalence requires review'}
    files.append(stat);page_files.append({'path':rel,'subject':subject,'chapter':ident,'kind':kind,'pages':pages})
    subject_counts[subject][kind+'_files']+=1;subject_counts[subject][kind+'_pages']+=len(pdf)
    subject_counts[subject][kind+'_low_text_pages']+=len(stat['pages_requiring_visual_or_ocr'])
    pdf.close()
  print(subject,dict(subject_counts[subject]),flush=True)
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 write_json(ROOT/'sources'/'source_inventory.json',{'created_utc':now,'policy':'Extraction and inventory only; coverage/review must be established per knowledge item.','project_root':str(PROJECT),'summary':dict(subject_counts),'files':files})
 write_json(ROOT/'sources'/'page_inventory.json',{'created_utc':now,'files':page_files})
 return files

def ocr_map(record):
 path=PROJECT/record['path'];out=ROOT/'sources'/'extracted'/record['subject']/record['chapter']/(path.stem+'.ocr.txt')
 if out.exists() and out.stat().st_size>50:return str(out.relative_to(ROOT))
 doc=fitz.open(path);chunks=[]
 for i,page in enumerate(doc):
  scale=min(2.3,4000/max(page.rect.width,page.rect.height))
  png=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).tobytes('png')
  p=subprocess.run(['tesseract','stdin','stdout','--tessdata-dir','/workspace/study_analysis/v2/tessdata','-l','chi_sim+eng','--psm','11'],input=png,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
  if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-300:])
  chunks.append(f'\n===== 文件页 {i+1} =====\n'+p.stdout.decode('utf8',errors='replace'))
 out.write_text('来源：'+record['path']+'\n状态：自动OCR初稿；需对照原图核验\n'+''.join(chunks),encoding='utf8')
 return str(out.relative_to(ROOT))
def maps_ocr(files):
 records=[r for r in files if r['kind']=='mindmap'];results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  jobs={pool.submit(ocr_map,r):r for r in records}
  for future in concurrent.futures.as_completed(jobs):
   r=jobs[future]
   try:results.append({'path':r['path'],'ocr_file':future.result(),'status':'ocr_draft','visual_review':'pending'})
   except Exception as e:results.append({'path':r['path'],'status':'failed','error':str(e)})
   if len(results)%10==0:print('map OCR',len(results),'/',len(records),flush=True)
 write_json(ROOT/'sources'/'mindmap_ocr_inventory.json',{'engine':'tesseract','languages':['chi_sim','eng'],'psm':11,'review_status':'draft_requires_visual_confirmation','files':results})

def scans_ocr(files):
 records=[r for r in files if r['kind']=='lecture' and len(r['pages_requiring_visual_or_ocr'])/r['pdf_pages']>.7]
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  jobs={pool.submit(ocr_map,r):r for r in records}
  for future in concurrent.futures.as_completed(jobs):
   r=jobs[future]
   try:
    results.append({'path':r['path'],'ocr_file':future.result(),'status':'ocr_draft','visual_review':'pending'})
    print('scan OCR done',r['chapter'],Path(r['path']).name,flush=True)
   except Exception as e:
    results.append({'path':r['path'],'status':'failed','error':str(e)})
    print('scan OCR failed',r['path'],str(e),flush=True)
   write_json(ROOT/'sources'/'lecture_scan_ocr_inventory.json',{'engine':'tesseract','languages':['chi_sim','eng'],'review_status':'draft_requires_visual_confirmation','files':results,'total_candidates':len(records)})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ocr-maps',action='store_true');ap.add_argument('--reuse-inventory',action='store_true');ap.add_argument('--ocr-scans',action='store_true');a=ap.parse_args()
 files=json.loads((ROOT/'sources'/'source_inventory.json').read_text())['files'] if a.reuse_inventory else extract()
 if a.ocr_maps:maps_ocr(files)

 if a.ocr_scans:scans_ocr(files)
