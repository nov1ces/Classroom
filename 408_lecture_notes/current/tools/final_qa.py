#!/usr/bin/env python3
"""Final-stage PDF checks and page rendering, gated on a verified GitHub push."""
from pathlib import Path
import argparse,json,re,hashlib
import fitz
from PIL import Image,ImageDraw
from build_notes import ROOT,read,jwrite,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');a=ap.parse_args()
 gate=ROOT/'sources/github_pre_layout.json'
 if not gate.exists():raise SystemExit('Push the complete build to GitHub and record the remote commit before layout QA.')
 reports=[]
 for path in sorted((ROOT/'books').glob('*.pdf')):
  doc=fitz.open(path);issues=[];fonts=set()
  for i,p in enumerate(doc,1):
   if abs(p.rect.width-595.276)>1 or abs(p.rect.height-841.89)>1:issues.append({'page':i,'issue':'not A4'})
   for f in p.get_fonts():
    if f[0] not in fonts:
     fonts.add(f[0])
     if not doc.extract_font(f[0])[3]:issues.append({'page':i,'issue':'unembedded font '+f[3]})
   for w in p.get_text('words'):
    if w[0]<0 or w[1]<0 or w[2]>596 or w[3]>843:issues.append({'page':i,'issue':'out of page '+w[4]})
  reports.append({'file':str(path.relative_to(ROOT)),'pdf_sha256':sha(path),'pages':len(doc),'issues':issues})
  if a.render and path.name in ['408四科_强化笔记.pdf','408强化例题解析.pdf']:
   out=ROOT/'previews'/('notes' if path.name.startswith('408四科') else 'solutions');out.mkdir(parents=True,exist_ok=True)
   for stale in list(out.glob('page-*.png'))+list(out.glob('contact-*.png')):stale.unlink()
   for i,p in enumerate(doc,1):p.get_pixmap(matrix=fitz.Matrix(1.45,1.45),alpha=False).save(out/f'page-{i:03}.png')
   for start in range(1,len(doc)+1,9):
    tiles=[]
    for i in range(start,min(len(doc)+1,start+9)):
     im=Image.open(out/f'page-{i:03}.png');im.thumbnail((298,421));tile=Image.new('RGB',(320,450),'#eee');tile.paste(im,((320-im.width)//2,5));ImageDraw.Draw(tile).text((12,430),str(i),fill='#222');tiles.append(tile)
    contact=Image.new('RGB',(960,450*((len(tiles)+2)//3)),'#ddd')
    for i,t in enumerate(tiles):contact.paste(t,((i%3)*320,(i//3)*450))
    contact.save(out/f'contact-{start:03}.png')
 warnings=[]
 for log in list((ROOT/'chapters').glob('*/build/main.log'))+[ROOT/'solutions/build/main.log']:
  if not log.exists():continue
  text=log.read_text(errors='replace')
  for pattern in ['Missing character:','Overfull \\hbox','Overfull \\vbox','undefined references','Label(s) may have changed']:
   if pattern in text:warnings.append({'log':str(log.relative_to(ROOT)),'pattern':pattern,'count':text.count(pattern)})
 jwrite(ROOT/'sources/final_layout_checks.json',{'github_pre_layout':read(gate),'books':reports,'compile_warnings':warnings,'visual_review':'pending_independent_page_review'})
 print(json.dumps({'books':len(reports),'pages':sum(r['pages'] for r in reports),'issues':sum(len(r['issues']) for r in reports),'compile_warnings':warnings},ensure_ascii=False))
if __name__=='__main__':main()
