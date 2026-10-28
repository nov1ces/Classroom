#!/usr/bin/env python3
"""Redraw disparate pre-VFS course interfaces, source 4.3.4 file p.3."""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="580" viewBox="0 0 1300 580">','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#466C82"/></marker></defs>','<rect width="1300" height="580" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#243947">']
def text(x,y,t,size=24):s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(t)}</text>')
def box(x,y,w,h,t,fill):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#7796a5" stroke-width="2"/>');text(x+w/2,y+h/2+8,t)
def arrow(path):s.append(f'<path d="{path}" fill="none" stroke="#466C82" stroke-width="3" marker-end="url(#a)"/>')
box(280,40,240,70,'用户进程 P1','#eaf3f6');box(800,40,240,70,'用户进程 P2','#eaf3f6')
for x,api,fs,dev in [(50,'open(a, b)','UFS 文件系统','磁盘'),(500,'fopen(x)','NTFS 文件系统','移动硬盘'),(950,'openf(p, q)','FAT 文件系统','U盘')]:
 box(x,190,300,60,api,'#eff6f1');box(x,300,300,70,fs,'#fff3dc');box(x,445,300,60,dev,'#f6f6f6');arrow(f'M400 110 V150 H{x+150} V190');arrow(f'M{x+150} 250 V300');arrow(f'M{x+150} 370 V445')
text(650,555,'课件示意：不同文件系统采用各自接口，用户需适配具体实现。',22)
s.append('</g></svg>');p=out/'OS_vfs_before_course.svg';p.write_text('\n'.join(s))
for typ in ['png','pdf']:
 cmd=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/('OS_vfs_before_course.'+typ))]
 if typ=='png':cmd.append('--export-dpi=180')
 else:cmd.append('--export-text-to-path')
 subprocess.run(cmd,check=True)
