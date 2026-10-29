#!/usr/bin/env python3
"""Render all margin strips and full diagram pages for fingerprint-bound review."""
from pathlib import Path
import hashlib
import json

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'sources/annotations'


def main():
    pdf = ROOT / 'books/408四科_强化笔记.pdf'
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    placement = json.loads((DATA / 'placement.json').read_text())
    out = DATA / 'previews'
    out.mkdir(exist_ok=True)
    doc = fitz.open(pdf)
    sheets=[]
    clip = fitz.Rect(383,74,536,777)
    font=ImageFont.truetype(str(ROOT/'common/fonts/DejaVuSansMono.ttf'),19)
    for start in range(0,len(doc),6):
        strips=[]
        for i in range(start,min(start+6,len(doc))):
            pm=doc[i].get_pixmap(matrix=fitz.Matrix(2.2,2.2),clip=clip,alpha=False)
            strips.append((i+1,Image.frombytes('RGB',[pm.width,pm.height],pm.samples)))
        width=max(im.width for _,im in strips)+12
        canvas=Image.new('RGB',(width*len(strips),max(im.height for _,im in strips)+35),'#e8ebed')
        draw=ImageDraw.Draw(canvas)
        for k,(number,im) in enumerate(strips):
            canvas.paste(im,(k*width+6,30))
            draw.text((k*width+10,5),'PDF page '+str(number),fill='#253c49',font=font)
        name=f'margins-{start+1:03}-{min(start+6,len(doc)):03}.png'
        canvas.save(out/name)
        sheets.append({'image':str((out/name).relative_to(ROOT)),'pages':[i for i,_ in strips]})
    full=[]
    figure_pages=sorted({p['page'] for p in placement['pieces'] if p['kind']=='figure'})
    for number in figure_pages:
        path=out/f'page-{number:03}.png'
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(path)
        full.append({'image':str(path.relative_to(ROOT)),'page':number})
    value={'pdf_sha256':digest,'pdf_pages':len(doc),'margin_sheets':sheets,'full_diagram_pages':full,
           'review_status':'pending_actual_view'}
    (DATA/'visual-review.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'margin_sheets':len(sheets),'full_diagram_pages':len(full),'pdf_sha256':digest}),flush=True)


if __name__=='__main__':
    main()
