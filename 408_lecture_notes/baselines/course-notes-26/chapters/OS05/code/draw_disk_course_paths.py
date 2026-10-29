#!/usr/bin/env python3
"""Reconstruct the six disk-scheduling paths from the Wangdao slide example."""
from pathlib import Path
from html import escape
import subprocess

OUT=Path(__file__).resolve().parents[1]/'figures';OUT.mkdir(exist_ok=True)

# Parenthesised positions in the notes are non-service turning/jump positions.
CASES=[
 ('FCFS',[(100,False),(55,True),(58,True),(39,True),(18,True),(90,True),(160,True),(150,True),(38,True),(184,True)],498),
 ('SSTF',[(100,False),(90,True),(58,True),(55,True),(39,True),(38,True),(18,True),(150,True),(160,True),(184,True)],248),
 ('SCAN',[(100,False),(150,True),(160,True),(184,True),(200,False),(90,True),(58,True),(55,True),(39,True),(38,True),(18,True)],282),
 ('LOOK',[(100,False),(150,True),(160,True),(184,True),(90,True),(58,True),(55,True),(39,True),(38,True),(18,True)],250),
 ('C-SCAN',[(100,False),(150,True),(160,True),(184,True),(200,False),(0,False),(18,True),(38,True),(39,True),(55,True),(58,True),(90,True)],390),
 ('C-LOOK',[(100,False),(150,True),(160,True),(184,True),(18,True),(38,True),(39,True),(55,True),(58,True),(90,True)],322),
]
for title,points,total in CASES:
    assert sum(abs(points[i][0]-points[i-1][0]) for i in range(1,len(points)))==total,title

for group in range(3):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="860" viewBox="0 0 1200 860">',
         '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#51778c"/></marker></defs>',
         '<rect width="1200" height="860" fill="white"/>',
         '<g fill="#233e4c" font-family="Noto Sans CJK SC, sans-serif" font-size="22">']
    for n,(title,points,total) in enumerate(CASES[2*group:2*group+2]):
        top=25+n*415; left=95; step=3.9; y0=top+80; dy=27
        svg.append(f'<text x="35" y="{top+25}" font-size="25" font-weight="bold">{escape(title)}：总移动 {total} 道，平均 {total}/9 道</text>')
        for t in [0,50,100,150,200]:
            x=left+t*step
            svg.append(f'<line x1="{x}" y1="{y0-18}" x2="{x}" y2="{y0+310}" stroke="#dbe4e8" stroke-width="1"/>')
            svg.append(f'<text x="{x}" y="{y0-25}" text-anchor="middle" font-size="20">{t}</text>')
        for i,(position,served) in enumerate(points):
            x=left+position*step;y=y0+i*dy
            if i:
                px=left+points[i-1][0]*step;py=y0+(i-1)*dy
                svg.append(f'<line x1="{px}" y1="{py}" x2="{x}" y2="{y}" stroke="#51778c" stroke-width="1.6" marker-end="url(#a)"/>')
            color='#577e95' if served else 'white'
            svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}" stroke="#577e95" stroke-width="1.5"/>')
            svg.append(f'<text x="1160" y="{y+6}" text-anchor="end" font-size="18">{i:02}　{position}'+(' 服务' if served else (' 初始' if i==0 else ' 经过'))+'</text>')
        svg.append(f'<text x="35" y="{top+403}" font-size="19">竖向为先后次序；实心点服务请求，空心点为初始或非服务折返点。</text>')
    svg.append('</g></svg>');name=f'OS05_disk_course_paths_{group+1:02}'
    path=OUT/(name+'.svg');path.write_text('\n'.join(svg),encoding='utf8')
    for ext in ['png','pdf']:
        args=['inkscape',str(path),'--export-type='+ext,'--export-filename='+str(OUT/(name+'.'+ext))]
        args.append('--export-dpi=180' if ext=='png' else '--export-text-to-path')
        subprocess.run(args,check=True)
