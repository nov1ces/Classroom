#!/usr/bin/env python3
"""Redraw the two file-system in-memory structures from course 4.3.2 pp.8–9."""
from pathlib import Path
from html import escape
import subprocess
root=Path(__file__).resolve().parents[1]; out=root/'figures'; out.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="970" viewBox="0 0 1300 970">', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#466C82"/></marker></defs>', '<rect width="1300" height="970" fill="white"/>', '<g font-family="Noto Sans CJK SC,sans-serif" fill="#243947">']
def rect(x,y,w,h,fill='#ffffff',stroke='#7c9aaa',rx=4): s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
def txt(x,y,t,size=21,weight='normal',align='middle',fill='#243947'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{align}" font-weight="{weight}" fill="{fill}">{escape(str(t))}</text>')
def line(path,color='#466C82',dash=False):s.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.2" '+('stroke-dasharray="6 5" ' if dash else '')+'marker-end="url(#arrow)"/>')
def panel(base,title,marked):
 rect(10,base,1280,460,'#fff','#aabcc6',8);txt(35,base+35,title,25,'bold','start')
 # Column titles + the exact table values of the course diagram.
 txt(110,base+73,'用户区',20,'bold');txt(622,base+73,'内核区',20,'bold');txt(1150,base+73,'外存',20,'bold')
 rect(35,base+105,150,105,'#eff6f5');txt(110,base+140,'文件描述符',19);txt(110,base+178,'fd = 1',23,'bold')
 rect(215,base+95,330,200,'#f7fafc');txt(380,base+122,'进程打开文件表',20,'bold')
 txt(238,base+153,'索引','20','normal','start');txt(294,base+153,'打开方式',20,'normal','start');txt(420,base+153,'系统表索引',20,'normal','start')
 rect(224,base+166,312,42,'#fff');txt(242,base+193,'0',20,'normal','start');txt(294,base+193,'读／写',20,'normal','start');txt(449,base+193,'0',17)
 rect(224,base+211,312,42,'#e1f1f5');txt(242,base+238,'1',20,'normal','start');txt(294,base+238,'只读',20,'normal','start');txt(449,base+238,'2',17)
 rect(575,base+95,335,200,'#f7fafc');txt(742,base+122,'系统打开文件表',20,'bold')
 txt(592,base+153,'索引',20,'normal','start');txt(650,base+153,'目录项',20,'normal','start');txt(795,base+153,'打开计数',20,'normal','start')
 for i,(label,num) in enumerate([('FCB_F',1),('FCB_B',2),('FCB_A',1)]):
  y=base+165+i*38;rect(584,y,317,35,'#e1f1f5' if i==2 else '#fff');txt(598,y+24,str(i),20,'normal','start');txt(652,y+24,label,20,'normal','start');txt(832,y+24,str(num),17)
 rect(950,base+95,300,200,'#f5f9fb');txt(1100,base+122,'外存目录 M 与文件',20,'bold');rect(965,base+138,120,125,'#fff');txt(1025,base+162,'目录 M',20,'bold')
 for i,c in enumerate('ABCD'):txt(1025,base+181+i*22,'FCB_'+c,19)
 rect(1100,base+150,135,44,'#e2ebf1');txt(1167,base+179,'文件 A',20);rect(1100,base+207,135,44,'#fff');txt(1167,base+236,'文件 B',20)
 rect(575,base+325,335,95,'#f5f9fb');txt(742,base+353,'内存中的目录 M 缓存',18,'bold');txt(742,base+388,'FCB_A   FCB_B   FCB_C   FCB_D',18)
 if marked:
  line(f'M 185 {base+169} H 208');line(f'M 545 {base+232} H 565 V {base+258} H 575');line(f'M 950 {base+202} H 930 V {base+375} H 915');line(f'M 880 {base+325} V {base+297}');line(f'M 910 {base+258} H 930 V {base+285} H 1243 V {base+172} H 1236')
  txt(220,base+320,'③ 在进程表建立表项并返回fd',20,'normal','start');txt(960,base+320,'① 路径逐级读入目录',20,'normal','start');txt(575,base+317,'② 复制FCB_A至系统表',20,'normal','start')
 else:
  line(f'M 185 {base+169} H 208');line(f'M 545 {base+232} H 565 V {base+258} H 575');line(f'M 910 {base+258} H 930 V {base+285} H 1243 V {base+172} H 1236')
  txt(35,base+337,'进程项1 → 系统项2 → 文件A',18,'normal','start');txt(35,base+372,'目录项缓存加速后续路径查找',18,'normal','start')
panel(0,'① 文件系统内存结构示意',False);panel(480,'② open(…/M/A，只读) 的课件示例',True)
s.append('</g></svg>'); p=out/'OS_open_course.svg';p.write_text('\n'.join(s))
for typ in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/('OS_open_course.'+typ))]
 if typ=='png':args.append('--export-dpi=180')
 if typ=='pdf':args.append('--export-text-to-path')
 subprocess.run(args,check=True)
