#!/usr/bin/env python3
"""Redraw course VFS interface and vnode dispatch; sources: VFS pages 3–9."""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1100" viewBox="0 0 1400 1100">','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#466C82"/></marker></defs>','<rect width="1400" height="1100" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#243947">']
def box(x,y,w,h,t,fill='#eaf3f6',size=26):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="#7796a5" stroke-width="2"/>');text(x+w/2,y+h/2+size*.35,t,size)
def text(x,y,t,size=25,weight='normal'):
 s.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="{weight}">{escape(t)}</text>')
def line(path):s.append(f'<path d="{path}" fill="none" stroke="#466C82" stroke-width="3" marker-end="url(#a)"/>')
text(700,44,'统一接口分派到不同文件系统',31,'bold')
box(130,75,260,60,'用户进程 P1');box(1010,75,260,60,'用户进程 P2');box(470,180,460,70,'POSIX 接口：open(x, y, z)','#edf6f1')
line('M260 135 V 160 H 570 V180');line('M1140 135 V 160 H 830 V180')
box(500,290,400,75,'虚拟文件系统 VFS','#e3edf7',28);line('M700 250 V290')
for x,kind,medium in [(110,'UFS','磁盘'),(555,'NTFS','移动硬盘'),(1000,'FAT','U盘')]:
 box(x,430,290,70,kind+' 文件系统','#fff3dc');line(f'M700 365 V 395 H {x+145} V 430');box(x,535,290,60,medium,'#f6f6f6');line(f'M{x+145} 500 V535')
text(700,658,'打开文件：内存 vnode 分别指向对应的具体操作',27,'bold')
for x,kind in [(80,'UFS'),(750,'FAT')]:
 box(x,705,250,300,'','white');text(x+125,742,'vnode（内存）',23,'bold')
 for i,label in enumerate(['文件名','文件大小','创建者','文件格式','函数功能指针']):text(x+125,782+i*43,label,24)
 box(x+295,760,250,185,'','white',22);text(x+420,790,kind+' 操作表',22,'bold')
 for i,label in enumerate(['open','read','write']):text(x+420,830+i*43,label,24)
 line(f'M{x+250} 932 H{x+295}')
text(700,1060,'挂载：登记文件系统信息和操作入口，将文件系统根关联到挂载点。',23)
s.append('</g></svg>');p=out/'OS_vfs_course.svg';p.write_text('\n'.join(s))
for typ in ['png','pdf']:
 cmd=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/('OS_vfs_course.'+typ))]
 if typ=='png':cmd.append('--export-dpi=180')
 else:cmd.append('--export-text-to-path')
 subprocess.run(cmd,check=True)
