#!/usr/bin/env python3
"""Structural PDF audit and full-page rendering; visual review is separate."""
from pathlib import Path
import json,re,hashlib
import fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'dist'/'操作系统_同步互斥与信号量_样章.pdf'
OUT=ROOT/'editorial'/'verification'
RENDER=ROOT/'build'/'rendered'


def main():
    OUT.mkdir(parents=True,exist_ok=True);RENDER.mkdir(parents=True,exist_ok=True)
    for old in RENDER.glob('*.png'):old.unlink()
    d=fitz.open(PDF)
    report={'pdf':str(PDF.relative_to(ROOT)),'sha256':hashlib.file_digest(PDF.open('rb'),'sha256').hexdigest(),
            'page_count':len(d),'page_labels':d.get_page_labels(),'bookmarks':d.get_toc(),
            'pages':[],'bad_internal_links':[],'internal_link_count':0,
            'scope':'Text bounds, glyph warnings, links and render artifacts only; not a semantic or visual pass.'}
    for i,page in enumerate(d):
        spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
        outside=[]
        for s in spans:
            r=fitz.Rect(s['bbox'])
            if r.x0 < -1 or r.y0 < -1 or r.x1>page.rect.width+1 or r.y1>page.rect.height+1:
                outside.append({'text':s['text'],'bbox':list(r)})
        text=page.get_text()
        row=dict(physical_page=i+1,label=page.get_label(),characters=len(text),
                 media_box=list(page.rect),outside=outside,replacement_glyphs=text.count('\ufffd'),
                 font_min=min((s['size'] for s in spans),default=None))
        report['pages'].append(row)
        for link in page.get_links():
            if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                report['internal_link_count']+=1
                if link.get('page',-1)<0 or link['page']>=len(d):
                    report['bad_internal_links'].append({'source_page':i+1,'link':str(link)})
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(RENDER/f'page_{i+1:03}.png')
    log=(ROOT/'build'/'os_sync.log').read_text(errors='replace')
    report['latex_missing_glyph_lines']=[s for s in log.splitlines() if 'Missing character:' in s]
    report['latex_overfull_lines']=[s for s in log.splitlines() if 'Overfull' in s]
    report['latex_undefined_lines']=[s for s in log.splitlines() if 'undefined' in s.lower()]
    report['latex_float_errors']=[s for s in log.splitlines() if 'Float too large' in s]
    report['embedded_font_names']=sorted({font[3] for page in d for font in page.get_fonts()})
    # Noto TTC faces share a CFF table whose PostScript name contains "jp".
    # The regional cmap is selected by the TTC face index; the shared CFF name
    # alone cannot identify the selected regional glyphs.
    report['font_face_manifest']=json.loads((OUT/'font_manifest.json').read_text())
    report['font_faces_verified']=all(
        report['font_face_manifest'][role]['normal']['index']==idx
        for role,idx in [('main',2),('sans',2),('mono',7)]) and '.ttc:2]' in log and '.ttc:7]' in log
    report['cff_name_note']='Noto SC faces share the collection CFF PostScript name containing jp; selected TTC indexes and cmap determine glyphs.'
    report['all_pages_rendered']=True
    contacts=[]
    for start in range(0,len(d),6):
        sheet=Image.new('RGB',(1180,2580),'#d5d5d5')
        draw=ImageDraw.Draw(sheet)
        for j,n in enumerate(range(start,min(start+6,len(d)))):
            im=Image.open(RENDER/f'page_{n+1:03}.png').convert('RGB')
            im.thumbnail((570,811))
            x=10+(j%2)*590;y=32+(j//2)*860
            draw.text((x,y-22),f'Physical {n+1} / label {d[n].get_label()}',fill='black')
            sheet.paste(im,(x,y))
        name=f'contact_{start//6+1:02}.png';sheet.save(RENDER/name);contacts.append('build/rendered/'+name)
    report['contact_sheets']=contacts
    report['structural_status']='PASS' if not any([
      report['bad_internal_links'],report['latex_missing_glyph_lines'],
      report['latex_overfull_lines'],report['latex_undefined_lines'],report['latex_float_errors'],
      not report['font_faces_verified'],
      any(p['outside'] or p['replacement_glyphs'] for p in report['pages'])]) else 'REVIEW'
    (OUT/'pdf_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (OUT/'pdf_text.txt').write_text('\n\f\n'.join(p.get_text() for p in d))
    print(json.dumps({k:report[k] for k in ['page_count','internal_link_count','structural_status','latex_overfull_lines']},ensure_ascii=False))


if __name__=='__main__':main()
