#!/usr/bin/env python3
"""Inventory diagrams actually referenced by the editable chapters."""
from pathlib import Path
from collections import defaultdict
import argparse, csv, hashlib, json, re
from datetime import datetime, timezone
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--content-only',action='store_true',help='Inventory sources and files without inspecting PDF geometry')
    args=parser.parse_args()
    refs=defaultdict(list)
    for p in sorted((ROOT/'manuscript').glob('*/[0-9][0-9]_*.md')):
        for ln,line in enumerate(p.read_text().splitlines(),1):
            for m in re.finditer(r'!\[([^\]]*)\]\(([^\s)]+\.png)',line):
                refs[Path(m[2]).stem].append(dict(path=str(p.relative_to(ROOT)),line=ln,caption=m[1]))
    entries=[]
    for name,locations in refs.items():
        formats={}
        for ext in ['svg','png','pdf']:
            p=ROOT/'figures'/(name+'.'+ext)
            if not p.exists():raise FileNotFoundError(p)
            formats[ext]=dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        png=Image.open(ROOT/formats['png']['path'])
        pdf=None if args.content_only else fitz.open(ROOT/formats['pdf']['path'])
        if pdf is not None and len(pdf)!=1:raise ValueError(name+': diagram PDF is not one page')
        spans=[] if pdf is None else [s for b in pdf[0].get_text('dict')['blocks'] if b['type']==0
               for ln in b['lines'] for s in ln['spans']]
        outside=[]
        for span in spans:
            box=fitz.Rect(span['bbox']);page=pdf[0].rect
            if box.x0 < -2 or box.y0 < -2 or box.x1>page.width+2 or box.y1>page.height+2:
                outside.append(dict(text=span['text'],bbox=list(box)))
        prefix=name[:2]
        script='tools/draw_figures.py' if re.match(r'^F\d',name) else f'tools/draw_{prefix.lower()}_figures.py'
        if not (ROOT/script).exists():raise FileNotFoundError(script)
        entries.append(dict(id=name,references=locations,formats=formats,source=script,
            png_pixels=list(png.size),pdf_points=None if pdf is None else list(pdf[0].rect),
            vector_text_outside=outside,vector_font_sizes=sorted({round(s['size'],2) for s in spans}),
            verification=('仅登记实际引用与三格式SHA；本次不读取PDF几何，不授予视觉或版式通过。' if args.content_only else
                '实际打开PNG/PDF且三格式存在；语义、数值与人工视觉检查见分科台账，不能由文件存在推出通过。'),
            geometry_check_performed=not args.content_only))
    out=ROOT/'editorial/full/figure_manifest.json'
    out.write_text(json.dumps(dict(date=datetime.now(timezone.utc).date().isoformat(),referenced_figures=len(entries),
        geometry_check_performed=not args.content_only,items=entries),ensure_ascii=False,indent=2)+'\n')
    with (out.with_suffix('.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['id','source','svg','png','pdf','references']);w.writeheader()
        for e in entries:
            w.writerow(dict(id=e['id'],source=e['source'],**{k:e['formats'][k]['path'] for k in ['svg','png','pdf']},references=json.dumps(e['references'],ensure_ascii=False)))
    print(json.dumps(dict(referenced_figures=len(entries),formats_per_figure=3,
        outside_findings={e['id']:e['vector_text_outside'] for e in entries if e['vector_text_outside']}),ensure_ascii=False))

if __name__=='__main__':main()
