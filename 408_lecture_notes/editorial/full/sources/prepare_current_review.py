from pathlib import Path
import json,re,difflib,fitz,hashlib
ROOT=Path('/workspace/408_lecture_notes');OUT=ROOT/'editorial/full/sources/current_review';OUT.mkdir(exist_ok=True)
INDEX=json.loads((ROOT/'editorial/full/sources/exam_question_index.json').read_text())
qs={}
for year in range(2009,2027):
 s=(ROOT/f'editorial/sources/exams/exam_{year}.txt').read_text();starts=[];want=1
 for m in re.finditer(r'(?m)^\s*(\d{1,2})\s*[.．、]\s*',s):
  if int(m[1])==want and want<=47:starts.append((want,m.start()));want+=1
 for i,(q,offset) in enumerate(starts):
  t=s[offset:starts[i+1][1] if i+1<len(starts) else len(s)]
  t=re.sub(r'\[\[PDF_PAGE:\d+\]\]','',t)
  t=re.sub(r'(?m)^20\d\d 年全国硕士研究生入学统一考试.*$','',t)
  t=re.sub(r'二、综合应用题.*','',t)
  qs[year,q]=t.strip()
clean=lambda t:re.sub(r'[\W\d_]+','',re.sub(r'\{#[^}]+\}|【.*?】|\\[A-Za-z]+','',t)).lower()
records=[]
for sub in ['CO','CN']:
 raw=(Path('/workspace/study_analysis')/f'{"02_计算机组成原理" if sub=="CO" else "04_计算机网络"}_book.txt').read_text();wd=[];section=None
 for m in re.finditer(r'\[\[PDF_PAGE:(\d+)\]\]\n(.*?)(?=\[\[PDF_PAGE:|\Z)',raw,re.S):
  pg,t=int(m[1]),m[2];h=re.search(r'(?m)^(\d+\.\d+)\s*(?=[\u4e00-\u9fff]|CISC|RISC|IPv4|IPv6|UDP|TCP)[^\n]+',t)
  if h:section=h[1]
  q=re.search(r'(?m)^(\d+)\.\s*【(20\d{2})\s*年?\s*统考真题】',t)
  if q:
   text=t[q.start():];text=re.sub(r'· 第\d+ 页，共\d+ 页·.*','',text,flags=re.S).strip()
   wd.append({'question_number':int(q[1]),'year':int(q[2]),'section':section,'native_text':text,'horizontal_page':pg})
 for path in sorted((ROOT/f'manuscript/{sub}').glob('*.md')):
  ch=int(path.name[:2])
  if not((sub=='CO' and ch>=2) or (sub=='CN' and ch>=3)):continue
  s=path.read_text();sha=hashlib.sha256(path.read_bytes()).hexdigest()
  for m in re.finditer(r'(?m)^### 例\s+([^\n]+)\n(.*?)(?=^### |^## |\Z)',s,re.S|re.M):
   yearmatch=re.search('【(20\\d\\d)】',m[0]);
   if not yearmatch:continue
   year=int(yearmatch[1]);stem=m[2].split('**解析')[0].strip();stem=re.sub(r'^【20\d\d】\s*','',stem)
   opts=[(difflib.SequenceMatcher(None,clean(stem),clean(qs[year,x['question']])).ratio(),x['question']) for x in INDEX if x['year']==year and x['subject']==sub]
   score,q=max(opts)
   wscore,w=max((difflib.SequenceMatcher(None,clean(qs[year,q]),clean(w['native_text'])).ratio(),w) for w in wd if w['year']==year)
   rec={'manuscript':str(path),'manuscript_sha256':sha,'heading':m[1],'year':year,'exam_question':q,'manuscript_stem':stem,'exam_text':qs[year,q],'exam_page':next(x['pdf_page'] for x in INDEX if x['year']==year and x['question']==q),'exam_match_score':score,'wangdao_match_score':wscore,'wangdao_location':w,'review_status':'待人工读题核验，不因匹配升级'}
   anchor=re.search(r'\{#([a-z]{2})-ex(\d+-\d+)\}',m[1]);rec['id']=(anchor[1].upper()+anchor[2]) if anchor else sub+re.match(r'(\S+)',m[1])[1]
   (OUT/f'{sub}{ch:02}_{rec["id"].replace("/","-")}.txt').write_text('稿件题干：\n'+stem+'\n\n复原卷：\n'+qs[year,q]+'\n\n王道题干：\n'+w['native_text'],encoding='utf8')
   records.append(rec)
   print(sub,ch,rec['id'],year,q,'match',round(score,3),w['section'],w['question_number'])
(OUT/'current_candidate_matches.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
