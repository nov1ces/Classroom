#!/usr/bin/env python3
"""Follow question-index links and check the example number on the target page."""
from pathlib import Path
import hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')

def main():
    for sub,title in NAMES.items():
        p=ROOT/'dist'/f'{title}_讲义.pdf';doc=fitz.open(p);toc=doc.get_toc()
        first=next(x[2] for x in toc if x[1]=='题目索引')-1
        last=next(x[2] for x in toc if x[1]=='方法索引')-1
        checked=[];bad=[]
        for pn in range(first,last):
            page=doc[pn]
            for link in page.get_links():
                if link.get('kind') not in (fitz.LINK_GOTO,fitz.LINK_NAMED):continue
                text=page.get_textbox(link['from']).strip()
                m=re.search(r'例\s*(\d+)[-‑－](\d+)',text)
                if not m:continue
                target=link.get('page',-1)
                pattern=r'例\s*'+m[1]+r'\s*[-‑－]\s*'+m[2]+r'(?=\D|$)'
                item=dict(index_page=pn+1,example=f'{m[1]}-{m[2]}',target_page=target+1)
                (checked if 0<=target<len(doc) and re.search(pattern,doc[target].get_text()) else bad).append(item)
        mf=json.loads((ROOT/f'build/{sub}/build_manifest.json').read_text())
        expected=sum(bool(re.match(r'^例\s*\d',q['title'])) for q in mf['questions'])
        if bad or len(checked)!=expected:raise AssertionError((sub,expected,len(checked),bad))
        result=dict(status='PASS',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            scope='实际读取全部编号例题的题目索引链接区域，并检查目标物理页出现同一例号；不以链接边界合法代替。',
            expected_examples=expected,checked=checked,unmatched=bad)
        (ROOT/f'editorial/full/pdf/{sub}/index_destination_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(dict(subject=sub,examples_checked=len(checked),status='PASS')))

if __name__=='__main__':main()
