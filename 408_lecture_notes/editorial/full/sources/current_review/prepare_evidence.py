from pathlib import Path
import json,fitz
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/workspace/408_lecture_notes');OUT=Path(__file__).parent
rec=json.loads((OUT/'current_candidate_matches.json').read_text());ans=json.loads(Path('/workspace/study_analysis/v2/book_answers.json').read_text());font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
selected=[r for r in rec if r['id'].startswith(('CO3','CN3','CO2-7','CO2-8','CO2-9','CN4','CN5','CN6','CO6','CO7'))]
for r in selected:
 sub=r['id'][:2];w=r['wangdao_location'];a=ans.get(f'{sub}:{w["section"]}:{w["question_number"]}');r['book_answer']=a;r['answer_images']=[]
 if a:
  d=fitz.open(a['book'])
  for i,c in enumerate(a['crops'],1):
   dest=OUT/f'{r["id"]}_book_answer_{i}.png';d[c['page']-1].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(c['bbox'])).save(dest);r['answer_images'].append(str(dest))
 d=fitz.open(ROOT/f'editorial/sources/exams/exam_{r["year"]}_rebuild.pdf');pg=r['exam_page'];dest=OUT/f'{r["id"]}_exam_p{pg}.png';d[pg-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(dest);r['exam_image']=str(dest)
for i in range(0,len(selected),4):
 batch=selected[i:i+4];cells=[]
 for r in batch:
  imgs=[Image.open(x).convert('RGB') for x in r['answer_images']];h=sum(im.height for im in imgs);w=max([im.width for im in imgs] or [900]);canvas=Image.new('RGB',(max(w,1000),h+45),'white');draw=ImageDraw.Draw(canvas);draw.text((10,10),f'{r["id"]} [{r["year"]} q{r["exam_question"]}] WD {r["wangdao_location"]["section"]}-{r["wangdao_location"]["question_number"]}  ans={r["book_answer"]["answer"] if r["book_answer"] else "NONE"}',font=font,fill='black');y=45
  for im in imgs:canvas.paste(im,(0,y));y+=im.height
  cells.append(canvas)
 total=Image.new('RGB',(max(x.width for x in cells),sum(x.height for x in cells)+20*(len(cells)-1)),'white');y=0
 for c in cells:total.paste(c,(0,y));y+=c.height+20
 total.save(OUT/f'answers_contact_{i//4+1:02}.png')
(OUT/'selected_evidence.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
print(len(selected),'questions,',len(list(OUT.glob('answers_contact_*.png'))),'contacts')
