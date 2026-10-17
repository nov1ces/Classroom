#!/usr/bin/env python3
"""Check source labels in actual PDF text, separately from human page review."""
from pathlib import Path
import argparse,hashlib,json,re
import fitz

ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--subjects',nargs='+',choices=list(NAMES),default=list(NAMES))
    args=parser.parse_args();items=[]
    for sub in args.subjects:
        manifest=json.loads((ROOT/f'build/{sub}/build_manifest.json').read_text())
        p=ROOT/manifest['pdf'];d=fitz.open(p)
        count=0;bad=[];alone=[];diagram_labels=[];trailing_citations=[]
        for n,page in enumerate(d,1):
            blocks=page.get_text('dict')['blocks']
            all_lines=[line for b in blocks if b['type']==0 for line in b['lines']]
            for block in blocks:
                if block['type']!=0:continue
                for line_number,line in enumerate(block['lines']):
                    text=''.join(s['text'] for s in line['spans']).strip()
                    if not re.match(r'^(【\d{4}】|〖[^〗]+〗)',text):continue
                    # Bold sans-serif labels inside vector figures are captions,
                    # not ordinary question paragraphs; keep a separate record.
                    if 'NotoSerif' not in line['spans'][0]['font']:
                        diagram_labels.append(dict(page=n,text=text));continue
                    if line_number and re.fullmatch(r'〖[^〗]+〗',text):
                        trailing_citations.append(dict(page=n,text=text,
                            scope='说明段末的短例题源回指，不是题干首行'))
                        continue
                    count+=1;x=line['bbox'][0]
                    if abs(x-24*72/25.4)>1.0:bad.append(dict(page=n,text=text[:70],x=x))
                    # A PDF can split the same printed baseline into two text
                    # lines around a stretchable space; combine its neighbours.
                    baseline=''.join(''.join(s['text'] for s in other['spans'])
                        for other in sorted(all_lines,key=lambda z:z['bbox'][0])
                        if abs(other['bbox'][1]-line['bbox'][1])<.2)
                    if re.fullmatch(r'【\d{4}】(?:改编)?|〖[^〗]+〗',baseline.strip()):alone.append(n)
        item=dict(subject=sub,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),question_source_lines=count,
            nonflush_lines=bad,standalone_source_lines=alone,diagram_labels_outside_question_scope=diagram_labels,
            trailing_reference_notes_outside_question_scope=trailing_citations)
        items.append(item)
        if bad or alone:raise AssertionError(item)
        print(json.dumps(dict(subject=sub,question_source_lines=count,status='PASS'),ensure_ascii=False))
    out=ROOT/'editorial/final/chinese_format_scan.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(dict(status='PASS',scope='实际PDF普通题干源标行不单独占行，首行x坐标等于正文左边界；图内标题单列。普通段落缩进另由人工逐页检查。',books=items),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
