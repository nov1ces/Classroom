import fitz,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('/workspace/408_lecture_notes/editorial/errors/ds_co_checks');a=json.load(open(R/'native_records.json'));idx={x['id']:x for x in a};font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
ids=['ERR-DS-3.1-026','ERR-DS-3.2-009','ERR-DS-7.2-002','ERR-DS-6.4-019','ERR-CO-2.3-021','ERR-CO-3.5-030','ERR-CO-5.6-008','ERR-CO-6.1-025']
for j in range(0,len(ids),4):
 ims=[]
 for id in ids[j:j+4]:
  x=idx[id];p=fitz.open(x['question_pdf'])[x['question_pdf_page']-1];bot=max([b[3] for b in p.get_text('blocks') if 42<=b[1]<420]+[200]);pix=p.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(58,42,540,min(424,bot+8)),alpha=False);out=R/'question_anomalies'/f'{id}.png';pix.save(out);im=Image.open(out).convert('RGB');im=im.resize((840,round(im.height*840/im.width)));cell=Image.new('RGB',(840,im.height+30),'white');cell.paste(im,(0,30));ImageDraw.Draw(cell).text((0,0),id+' / native p'+str(x['question_pdf_page']),font=font,fill='black');ims.append(cell)
 rows=[]
 for n in range(0,len(ims),2):
  h=max(im.height for im in ims[n:n+2]);rr=Image.new('RGB',(1680,h),'#ddd')
  for k,im in enumerate(ims[n:n+2]):rr.paste(im,(k*840,0))
  rows.append(rr)
 out=Image.new('RGB',(1680,sum(im.height for im in rows)+10),'#aaa');y=0
 for im in rows:out.paste(im,(0,y));y+=im.height+5
 out.save(R/'sheets'/f'extra_question_{j//4+1:02}.jpg',quality=94)
# Full original book answer bands that have a condition or source wording issue.
for id in ['ERR-CO-3.5-030','ERR-CO-5.6-008','ERR-CO-3.6-005','ERR-DS-3.1-026']:
 x=idx[id];c=x['answer_crops_hint'][0];p=fitz.open(x['answer_book'])[c['page']-1];p.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(c['bbox']),alpha=False).save(R/'answer_labels'/f'{id}_full.png')
# Relevant original book question page 80 for the stack question.
b=fitz.open(idx['ERR-DS-3.1-026']['answer_book']);b[79].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(R/'question_anomalies'/'DS_book_p080.png')

# Additional manually examined opcode mismatch, restored against original textbook.
x=idx['ERR-CO-5.6-013'];p=fitz.open(x['question_pdf'])[x['question_pdf_page']-1]
p.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(58,42,540,240),alpha=False).save(R/'question_anomalies'/'ERR-CO-5.6-013.png')
b=fitz.open(x['answer_book']);b[267].get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False).save(R/'question_anomalies'/'CO_book_p268.png')
