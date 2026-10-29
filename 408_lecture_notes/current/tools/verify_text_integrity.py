#!/usr/bin/env python3
"""Verify running titles, placed sidebar text, and figure/section reading order."""
import re
import fitz
from build_notes import ROOT,read,jwrite,sha

def compact(text):return re.sub(r'\s+','',text)

def event(doc,text):
    needle=compact(text)
    for page_no,page in enumerate(doc,1):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                if needle in compact(''.join(s['text'] for s in line['spans'])):
                    return page_no,line['bbox'][1]
    raise ValueError('PDF text not found: '+text)

def main():
    errors=[];inputs=[];headers=0;sidebars=0;orders=[]
    for chapter in sorted((ROOT/'chapters').iterdir()):
        path=chapter/'notes.pdf';doc=fitz.open(path);inputs.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path)})
        title=compact(read(chapter/'map.json')['title'])
        for number,page in enumerate(doc,1):
            region=fitz.Rect(0,60,595,125) if number==1 else fitz.Rect(0,0,500,65)
            if title not in compact(page.get_textbox(region)):errors.append(f'{chapter.name} p{number}: incomplete chapter title')
            headers+=1
        items=read(chapter/'sidebars.json')
        for record in read(chapter/'sources/sidebar-placement.json'):
            text=compact(doc[record['page']-1].get_text())
            for placed in record['sidebars']:
                item=items[placed['index']];sidebars+=1
                for key in ['title','body']:
                    expected=item.get(key,'')
                    if expected and not re.search(r'[$`\\*_]',expected) and compact(expected) not in text:
                        errors.append(f'{chapter.name} p{record["page"]}: incomplete sidebar {key}')
        if chapter.name=='CO02':
            try:
                heading=event(doc,'恢复余数法的寄存器轨迹');figure=event(doc,'15除以2的试减')
                if figure<=heading:errors.append('CO02: division figure precedes its section')
                orders.append({'chapter':'CO02','heading_position':heading,'figure_position':figure})
            except ValueError as error:errors.append(str(error))
        if chapter.name=='CN04':
            try:
                table_end=event(doc,'AS4、AS10、AS19');figure=event(doc,'销售部已分配')
                if figure<=table_end:errors.append('CN04: subnet figure interrupts routing table')
                orders.append({'chapter':'CN04','table_end_position':table_end,'next_figure_position':figure})
            except ValueError as error:errors.append(str(error))
        doc.close()
    result={'errors':errors,'inputs':inputs,'verified_chapter_titles':headers,'verified_placed_sidebars':sidebars,'reading_order_checks':orders}
    jwrite(ROOT/'sources/text_integrity_checks.json',result)
    print({key:result[key] for key in ['errors','verified_chapter_titles','verified_placed_sidebars','reading_order_checks']})
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
