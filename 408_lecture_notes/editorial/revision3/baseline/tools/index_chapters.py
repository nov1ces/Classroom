#!/usr/bin/env python3
"""Generate the current table of contents from real, editable chapters."""
from pathlib import Path
import argparse,json,re

ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--review',action='store_true',help='Keep the review directory separate from the V1 delivery')
    args=parser.parse_args()
    rows=[];text=['# 四科实际目录\n\n以下由实际分章正文生成；各条目的核验状态另见覆盖及审校台账。正式2027细目对照不在本目录中自动认证。\n']
    for sub,name in NAMES.items():
        text.append('\n## '+name+'\n')
        for p in sorted((ROOT/'manuscript'/sub).glob('[0-9][0-9]_*.md')):
            number=int(p.name[:2]);section=0
            for line in p.read_text().splitlines():
                m=re.match(r'^(#{1,2})\s+(.+?)\s*$',line)
                if not m:continue
                title=re.sub(r'\s*\{#[^}]+\}\s*$','',m[2])
                if len(m[1])==1:
                    text.append(f'\n### 第{number}章 {title}\n')
                    text.append(f'\n正文：[{p.name}](../../{p.relative_to(ROOT).as_posix()})\n')
                else:
                    section+=1;text.append(f'\n- {number}.{section}　{title}')
                rows.append(dict(subject=sub,chapter=number,level=len(m[1]),
                    section=f'{number}.{section}' if len(m[1])==2 else str(number),
                    title=title,manuscript=str(p.relative_to(ROOT))))
            text.append('\n')
    out=ROOT/'editorial/full/四科实际目录.md'
    out.write_text('\n'.join(text)+'\n')
    (out.with_suffix('.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    target=ROOT/'dist/revision2/四科目录.md' if args.review else ROOT/'dist/四科目录.md'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(out.read_text() if args.review else out.read_text().replace('(../../manuscript/','(../manuscript/'))
    print(json.dumps({'chapters':sum(r['level']==1 for r in rows),'sections':sum(r['level']==2 for r in rows)},ensure_ascii=False))

if __name__=='__main__':main()
