#!/usr/bin/env python3
"""Redraw the course shared open-file table example, 4.1.7 p.7."""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1350" height="580" viewBox="0 0 1350 580">','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#466C82"/></marker></defs>','<rect width="1350" height="580" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#243947">']
def txt(x,y,t,size=25,weight='normal'):
 s.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="{weight}">{escape(str(t))}</text>')
def rect(x,y,w,h,fill='#fff'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#7796a5" stroke-width="2"/>')
def line(path):s.append(f'<path d="{path}" fill="none" stroke="#466C82" stroke-width="3" marker-end="url(#a)"/>')
def process(y,name,idx,access):
 rect(40,y,620,180,'#f5f9fb');txt(350,y+35,name+'的进程打开文件表',27,'bold')
 for i,(k,v) in enumerate([('编号',idx),('文件名','test.txt'),('读写指针','各自记录'),('访问权限',access),('系统表索引','k')]):
  x=48+i*120;rect(x,y+65,120,44,'#dcecf3');txt(x+60,y+95,k,22);rect(x,y+109,120,52);txt(x+60,y+143,v,22)
process(20,'进程 A','2','只读');process(300,'进程 B','1','读和写')
rect(790,130,510,270,'#f5f9fb');txt(1045,169,'系统打开文件表（课件示意）',27,'bold')
for i,(k,v) in enumerate([('编号','k'),('文件名','test.txt'),('外存地址','…'),('打开计数器','2')]):
 x=802+i*122;rect(x,200,122,48,'#dcecf3');txt(x+61,232,k,22);rect(x,248,122,58,'#e3f0f3');txt(x+61,285,v,22)
line('M660 165 H 740 V277 H790');line('M660 445 H 740 V277 H790')
txt(675,548,'课件模型：两进程记录各自权限和读写指针，系统表记录文件及打开计数。',22)
s.append('</g></svg>');p=out/'OS_shared_open_course.svg';p.write_text('\n'.join(s))
for typ in ['png','pdf']:
 cmd=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/('OS_shared_open_course.'+typ))]
 if typ=='png':cmd.append('--export-dpi=180')
 else:cmd.append('--export-text-to-path')
 subprocess.run(cmd,check=True)
