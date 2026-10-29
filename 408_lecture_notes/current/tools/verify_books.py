#!/usr/bin/env python3
"""Verify folios, copied-page rendering, and all external PDF link destinations."""
import hashlib,json
from urllib.parse import unquote
from pathlib import Path
import fitz
from build_notes import ROOT,read,jwrite,sha
SUBJECTS={'DS':'数据结构','CO':'计算机组成原理','OS':'操作系统','CN':'计算机网络'}
def page_signature(page):
 w,h=page.rect.width,page.rect.height
 rects=[(0,0,w,27),(0,27,502,57),(538,27,w,57),(0,57,w,h)]
 return [hashlib.sha256(page.get_pixmap(matrix=fitz.Matrix(.8,.8),clip=fitz.Rect(r),alpha=False).samples).hexdigest() for r in rects]
def main():
 lengths={}
 for target in (ROOT/'books').glob('*.pdf'):
  with fitz.open(target) as d:lengths[target.name]=len(d)
 records=read(ROOT/'manifest.json')['chapters'];combined=fitz.open(ROOT/'books/408四科_强化笔记.pdf');errors=[];books=[]
 for path in sorted((ROOT/'books').glob('*.pdf')):
  doc=fitz.open(path);folios=[];external=0
  for i,p in enumerate(doc,1):
   value=''.join(p.get_textbox(fitz.Rect(502,27,538,57)).split())
   if value!=str(i):errors.append(f'{path.name} p{i}: folio {value}')
   folios.append(value)
   for link in p.get_links():
    if link['kind']==fitz.LINK_GOTOR:
     external+=1;target=path.parent/unquote(link['file'])
     if not target.exists():errors.append(f'{path.name}: missing PDF {link["file"]}')
     else:
      if not 0<=link.get('page',-1)<lengths[target.name]:errors.append(f'{path.name}: invalid destination {link}')
  books.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path),'pages':len(doc),'verified_folios':len(folios),'external_links':external})
  doc.close()
 equivalent=[]
 for subject,name in SUBJECTS.items():
  path=ROOT/'books'/(name+'_强化笔记.pdf');doc=fitz.open(path);matched=0
  for r in records:
   if not r['id'].startswith(subject):continue
   for i in range(r['pages']):
    a=doc[r['subject_start_page']-1+i];b=combined[r['combined_start_page']-1+i]
    if page_signature(a)!=page_signature(b):errors.append(f'{name} p{r["subject_start_page"]+i}: rendering differs from combined')
    else:matched+=1
  equivalent.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path),'matching_pages':matched,'total_pages':len(doc),'comparison':'All rendered page content except the separately verified folio rectangle','review_reference':'books/408四科_强化笔记.pdf'})
  doc.close()
 jwrite(ROOT/'sources/book_checks.json',{'errors':errors,'books':books,'page_equivalence':equivalent,'combined_sha256':sha(ROOT/'books/408四科_强化笔记.pdf')})
 print(json.dumps({'errors':errors,'verified_books':len(books),'equivalent_note_pages':sum(x['matching_pages'] for x in equivalent)},ensure_ascii=False))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
