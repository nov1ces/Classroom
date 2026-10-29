#!/usr/bin/env python3
"""Assemble reinforcement PDFs and patch bidirectional example links."""
from pathlib import Path
import argparse,re,json,shutil,hashlib,zipfile
from urllib.parse import urlsplit,unquote
import fitz
from build_notes import ROOT,COMMON,read,jwrite,sha,build_input_fingerprint
SUBJECTS={'DS':('数据结构',8),'CO':('计算机组成原理',7),'OS':('操作系统',5),'CN':('计算机网络',6)}

def renumber(path):
 doc=fitz.open(path)
 for i,page in enumerate(doc,1):
  page.add_redact_annot(fitz.Rect(502,27,538,57),fill=(1,1,1))
  page.apply_redactions(images=0,graphics=0,text=0)
  page.insert_text(fitz.Point(506,44),str(i),fontname='folio',fontfile=str(COMMON/'fonts/NimbusRoman-Regular.otf'),fontsize=10,color=(0,0,0))
 tmp=path.with_suffix('.folio.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(path)

def assemble():
 all_doc=fitz.open();all_toc=[];records=[]
 for sub,(name,count) in SUBJECTS.items():
  d=fitz.open();toc=[];md=['# '+name+'强化笔记',''];all_toc.append([1,name,len(all_doc)+1])
  for n in range(1,count+1):
   ident=f'{sub}{n:02}';ch=ROOT/'chapters'/ident;pdf=fitz.open(ch/'notes.pdf');title=read(ch/'map.json')['title'];start=len(d);all_start=len(all_doc)
   d.insert_pdf(pdf);all_doc.insert_pdf(pdf);toc.append([1,title,start+1]);all_toc.append([2,title,all_start+1])
   for level,t,page in pdf.get_toc():
    if level>=2:toc.append([min(level,3),t,start+page]);all_toc.append([min(level+1,4),t,all_start+page])
   text=(ch/'notes.md').read_text();text=text.replace('](figures/',f'](../chapters/{ident}/figures/').replace('../../solutions/','../solutions/');md.append(text)
   records.append({'id':ident,'title':title,'pages':len(pdf),'combined_start_page':all_start+1,'subject_start_page':start+1,'pdf_sha256':sha(ch/'notes.pdf'),'content_sha256':sha(ch/'content.md')});pdf.close()
  d.set_toc(toc);d.set_metadata({'title':name+'强化笔记','creator':'XeLaTeX / PyMuPDF'})
  target=ROOT/'books'/(name+'_强化笔记.pdf');d.save(target,garbage=4,deflate=True);d.close();renumber(target)
  (ROOT/'books'/(name+'_强化笔记.md')).write_text('\n\n'.join(md))
 all_doc.set_toc(all_toc);all_doc.set_metadata({'title':'408四科强化笔记','creator':'XeLaTeX / PyMuPDF'})
 all_doc.save(ROOT/'books/408四科_强化笔记.pdf',garbage=4,deflate=True);all_doc.close();renumber(ROOT/'books/408四科_强化笔记.pdf')
 jwrite(ROOT/'manifest.json',{'chapters':records,'total_pages':sum(r['pages'] for r in records)})

def patch_links():
 nav=read(ROOT/'sources/navigation.json')['examples'];records=read(ROOT/'manifest.json')['chapters'];meta={r['id']:r for r in records}
 targets=[('408四科_强化笔记.pdf',None)]+[(name+'_强化笔记.pdf',s) for s,(name,_) in SUBJECTS.items()]
 counts={}
 for file,subject in targets:
  path=ROOT/'books'/file;doc=fitz.open(path);count=0
  for e in nav:
   if subject and e['subject']!=subject:continue
   page_number=e['note_page'] if subject is None else meta[e['chapter']]['subject_start_page']+e['note_local_page']-1
   page=doc[page_number-1]
   rects=page.search_for('例 '+e['number']) or page.search_for('例'+e['number'])
   for rect in rects:
    page.insert_link({'kind':fitz.LINK_GOTOR,'from':rect,'file':'408强化例题解析.pdf','page':e['solution_page']-1,'to':fitz.Point(0,0)})
    count+=1
  tmp=path.with_suffix('.tmp.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(path);counts[file]=count
 path=ROOT/'books/408强化例题解析.pdf';doc=fitz.open(path);count=0
 for e in nav:
  page=doc[e['solution_page']-1]
  rects=page.search_for('例 '+e['number']) or page.search_for('例'+e['number'])
  for rect in rects:
   page.insert_link({'kind':fitz.LINK_GOTOR,'from':rect,'file':'408四科_强化笔记.pdf','page':e['note_page']-1,'to':fitz.Point(0,0)})
   count+=1
 tmp=path.with_suffix('.tmp.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(path);counts[path.name]=count;renumber(path)
 jwrite(ROOT/'sources/link_checks.json',{'expected_examples':len(nav),'links_inserted':counts})
 print(json.dumps(counts,ensure_ascii=False))

def audit():
 errors=[];records=[]
 for ch in sorted((ROOT/'chapters').iterdir()):
  if read(ch/'sources/build-inputs.json')!=build_input_fingerprint(ch):errors.append(ch.name+': stale build')
  sync=read(ch/'sources/content-sync.json')
  if sync['canonical_sha256']!=sha(ch/'content.md'):errors.append(ch.name+': stale content')
  records.append({'id':ch.name,'pdf_sha256':sha(ch/'notes.pdf')})
 for r in read(ROOT/'manifest.json')['chapters']:
  if r['pdf_sha256']!=sha(ROOT/'chapters'/r['id']/'notes.pdf'):errors.append(r['id']+': stale assembly')
 for md in list((ROOT/'books').glob('*.md')):
  for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)',md.read_text()):
   u=urlsplit(target)
   if not u.scheme and u.path and not (md.parent/unquote(u.path)).exists():errors.append(md.name+': missing '+target)
 jwrite(ROOT/'sources/delivery_checks.json',{'errors':errors,'chapters':records,'visual_review':'separate_final_stage'})
 print(json.dumps({'errors':errors},ensure_ascii=False))
 if errors:raise SystemExit(1)

def package():
 target=ROOT.parent/'archive/packages/408强化笔记_源码素材.zip';target.parent.mkdir(exist_ok=True)
 excluded={'build','previews','__pycache__','build-logs','extracted'}
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file() and not p.is_symlink() and not any(s in excluded for s in p.relative_to(ROOT).parts):
    z.write(p,str(Path('current')/p.relative_to(ROOT)))
 with zipfile.ZipFile(target) as z:
  if z.testzip():raise RuntimeError('Archive CRC failure')
 print(target)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['assemble','links','audit','package']);a=ap.parse_args()
 {'assemble':assemble,'links':patch_links,'audit':audit,'package':package}[a.action]()
