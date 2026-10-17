from pathlib import Path
import json,re,fitz
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
PDF=Path('/workspace/Classroom/02_计算机组成原理/【横版】27王道计算机组成原理选择题做题本.pdf')
book=fitz.open('/workspace/study_analysis/v2/books/王道2027计算机组成原理_高清带书签版.pdf')
answers=json.loads(Path('/workspace/study_analysis/v2/book_answers.json').read_text())
idx=json.loads((ROOT/'editorial/full/sources/exam_question_index.json').read_text())
coords={(r['year'],r['question']):r for r in idx}
doc=fitz.open(PDF);native=[];section='1.2'
for p in doc:
 t=p.get_text();m=re.search(r'(?:^|\n)(\d\.\d)\s+[^\n]+',t)
 if m:section=m.group(1)
 m=re.search(r'(?:^|\n)(\d{1,2})\.(?!\d)\s*(.*)',t)
 if m:
  n=int(m.group(1));year=re.search(r'【(20\d\d)',t)
  native.append({'section':section,'number':n,'year':int(year.group(1)) if year else None,'page':p.number+1,'text':t})
M={
'CO1-1':(2015,12),'CO1-2':(2022,12),'CO1-3':(2012,12),
'CO2-2':(2012,13),'CO2-3':(2025,12),'CO2-5':(2018,13),'CO2-6':(2023,16),'CO2-7':(2022,14),'CO2-8':(2014,14),'CO2-9':(2015,14),
'CO3-1':(2014,15),'CO3-2':(2011,15),'CO3-3':(2015,18),'CO3-4':(2009,15),'CO3-5':(2015,20),'CO3-6':(2016,13),'CO3-7':(2022,16),'CO3-8':(2015,15),'CO3-9':(2022,15),'CO3-10':(2024,17),
'CO4-1':(2022,19),'CO4-2':(2009,16),'CO4-3':(2012,15),'CO4-4':(2025,17),'CO4-5':(2022,20),
'CO5-1':(2023,18),'CO5-3':(2019,17),'CO5-4':(2012,18),'CO5-5':(2014,18),'CO5-6':(2021,21),
'CO6-1':(2009,18),'CO6-3':(2023,19),'CO6-4':(2022,22),
'CO7-1':(2009,20),'CO7-2':(2025,20),'CO7-3':(2023,20),'CO7-4':(2024,20),
'CO8-1':(2012,21),'CO8-2':(2011,22),'CO8-4':(2014,22),'CO8-5':(2020,22),'CO8-6':(2019,22),
'CO1-S1':(2014,12),'CO3-S3':(2024,18),'CO4-S1':(2025,15),'CO5-S1':(2009,19),'CO8-S1':(2024,21),'CO8-S2':(2024,22)
}
# Native words locate sources; PDF views and exact question comparison are separate human checks.
def norm(t):return re.sub(r'[^a-z0-9\u4e00-\u9fff]','',t.lower())
records=[]
for id,(year,qnum) in M.items():
 r=coords[(year,qnum)];text=(ROOT/f'editorial/sources/exams/exam_{year}.txt').read_text();m=re.search(r'(?:^|\n)\s*'+str(qnum)+r'[.．、]\s*',text)
 end=re.search(r'(?:^|\n)\s*'+str(qnum+1)+r'[.．、]\s*',text[m.end():])
 qt=text[m.start():m.end()+end.start()] if end else text[m.start():]
 cands=[n for n in native if n['year']==year]
 cands.sort(key=lambda n:SequenceMatcher(None,norm(qt),norm(n['text'])).ratio(),reverse=True)
 best=cands[0];key=f"CO:{best['section']}:{best['number']}";a=answers.get(key)
 rec={'id':id,'year':year,'exam_question':qnum,'paper_pdf_page':r['pdf_page'],'paper':'editorial/sources/exams/'+f'exam_{year}_rebuild.pdf','paper_kind':'社区二手复原；不代表官方原卷或官方答案发布','question_text_from_complete_paper':qt,'wangdao_section':best['section'],'wangdao_question_number':best['number'],'provided_native_pdf_page':best['page'],'main_book_answer':a,'match_score':round(SequenceMatcher(None,norm(qt),norm(best['text'])).ratio(),3),'provided_question_text':best['text'],'actual_views':[]}
 records.append(rec)
# Known non-exams in full examples/selfchecks.
for id,sec,n in [('CO2-1','2.1',1),('CO2-4','2.2',18),('CO6-2','5.6',13),('CO2-S3','2.3',24),('CO7-S1','6.2',10)]:
 best=next(r for r in native if r['section']==sec and r['number']==n);a=answers.get(f'CO:{sec}:{n}')
 records.append({'id':id,'year':None,'wangdao_section':sec,'wangdao_question_number':n,'provided_native_pdf_page':best['page'],'provided_question_text':best['text'],'main_book_answer':a,'actual_views':[]})
(HERE/'selected_source_locators.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('\n'.join(f"{r['id']} {r.get('year')}#{r.get('exam_question')} book {r['wangdao_section']}-{r['wangdao_question_number']} nativep{r['provided_native_pdf_page']} answerp{r['main_book_answer'].get('page') if r['main_book_answer'] else None} match{r.get('match_score')}" for r in records))
