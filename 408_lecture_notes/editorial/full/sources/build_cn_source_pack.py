from pathlib import Path
import fitz,json,re,difflib
ROOT=Path('/workspace/408_lecture_notes');OUT=ROOT/'editorial/full/sources/cn_candidates';OUT.mkdir(exist_ok=True)
PICKS={2009:[33,34,35,37,38,40],2010:[36],2013:[38],2014:[37,38],2016:[40],2018:[34,39],2019:[37],2020:[34,36,38,40],2021:[36,37],2022:[33,34,39,40],2023:[33,36,37,39,40],2024:[36,39,40],2025:[34,36,38,40]}
answers=json.loads(Path('/workspace/study_analysis/v2/book_answers.json').read_text())
raw=Path('/workspace/study_analysis/04_计算机网络_book.txt').read_text()
wdp={}
section=None
for m in re.finditer(r'\[\[PDF_PAGE:(\d+)\]\]\n(.*?)(?=\[\[PDF_PAGE:|\Z)',raw,re.S):
 pg,t=int(m[1]),m[2]
 h=re.search(r'(?m)^(\d+\.\d+)(?=[^\d.\n])[^\n]+',t)
 if h:section=h[1]
 q=re.search(r'(?m)^(\d+)\.\s*【(20\d{2})\s*年?\s*统考真题】',t)
 if q:
  text=t[q.start():];text=re.sub(r'· 第\d+ 页，共\d+ 页·.*','',text,flags=re.S).strip()
  wdp[pg]={'book_question_number':int(q[1]),'year':int(q[2]),'section':section,'native_text':text,'horizontal_pdf_page':pg}
clean=lambda t:re.sub(r'[\W\d_]+','',re.sub(r'【.*?】','',t)).lower()
records=[];pdfs={}
for year,qs in PICKS.items():
 d=fitz.open(ROOT/f'editorial/sources/exams/exam_{year}_rebuild.pdf');texts=[p.get_text() for p in d]
 starts=[];want=1
 for pg,t in enumerate(texts):
  for m in re.finditer(r'(?m)^\s*(\d{1,2})\s*[.．、]\s*',t):
   if int(m[1])==want and want<=47:starts.append((want,pg,m.start()));want+=1
 for q in qs:
  _,pg,off=starts[q-1]
  if q<len(starts):_,epg,eoff=starts[q]
  else:epg,eoff=len(d)-1,len(texts[-1])
  chunks=[]
  for p in range(pg,epg+1):chunks.append(texts[p][off if p==pg else 0:eoff if p==epg else len(texts[p])])
  rebuild='\n'.join(chunks).strip()
  cand=[(difflib.SequenceMatcher(None,clean(rebuild),clean(x['native_text'])).ratio(),x) for x in wdp.values() if x['year']==year]
  score,best=max(cand,key=lambda x:x[0]);best=dict(best)
  ans=answers.get(f"CN:{best['section']}:{best['book_question_number']}")
  entry={'id':f'EX-CN-{year}-{q:02}','year':year,'question':q,'rebuild_pdf_pages':list(range(pg+1,epg+2)),'rebuild_question_text':rebuild,'wangdao_location':best,'matching_score':round(score,4),'answer_reference':ans,'status':'题文已提取；位置自动相似匹配待人工交叉，非逐题完成核验'}
  (OUT/f'{year}_{q:02}_text.txt').write_text(rebuild+'\n\n王道对应文本（待人工核对）：\n'+best['native_text'],encoding='utf8')
  imagepaths=[]
  for p in range(pg,epg+1):
   dst=OUT/f'{year}_{q:02}_rebuild_p{p+1}.png';d[p].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(dst);imagepaths.append(str(dst))
  entry['rebuild_images']=imagepaths
  if ans:
   book=fitz.open(ans['book']);crops=[]
   for j,c in enumerate(ans['crops'],1):
    dest=OUT/f'{year}_{q:02}_answer_{j}.png';book[c['page']-1].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(c['bbox'])).save(dest);crops.append(str(dest))
   entry['answer_crop_images']=crops
  records.append(entry)
(OUT/'candidate_sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('prepared',len(records),'CN candidate sources')
for x in records:print(x['id'],x['rebuild_pdf_pages'],x['wangdao_location']['section'],x['wangdao_location']['book_question_number'],x['matching_score'],x['answer_reference']['answer'] if x['answer_reference'] else 'NO_ANSWER')
