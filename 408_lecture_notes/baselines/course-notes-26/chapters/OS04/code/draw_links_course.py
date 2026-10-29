#!/usr/bin/env python3
"""Course hard/symbolic-link example, 4.1.8 pp.5 and 8."""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="880" viewBox="0 0 1300 880">','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#466C82"/></marker></defs>','<rect width="1300" height="880" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#243947">']
def text(x,y,t,size=23,weight='normal'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" font-weight="{weight}">{escape(t)}</text>')
def box(x,y,w,h,t,fill='#eaf3f6',size=23):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#7796a5" stroke-width="2"/>');text(x+w/2,y+h/2+size*.35,t,size)
def arrow(path,dashed=False):s.append(f'<path d="{path}" fill="none" stroke="#466C82" stroke-width="2.5" '+('stroke-dasharray="7 5" ' if dashed else '')+'marker-end="url(#a)"/>')
def panel(base,deleted):
 text(650,base+35,'② 两个硬链接删除后的课件状态' if deleted else '① 原始状态：两条硬链接与一条软链接',26,'bold')
 for i,(user,name) in enumerate([('User1','aaa'),('User2','bbb'),('User3','ccc')]):
  y=base+75+i*95;box(25,y,180,60,user+' 的目录','#eff6f1');box(240,y,130,60,name+(' 已删除' if deleted and i<2 else ''),'#f7e8eb' if deleted and i<2 else '#eaf3f6',22)
 if not deleted:
  box(650,base+110,245,70,'inode 1 · count=2','#eaf3f6');box(1050,base+110,200,70,'文件 1','#eff6f1');arrow(f'M370 {base+105} H470 V{base+130} H650');arrow(f'M370 {base+200} H470 V{base+160} H650');arrow(f'M895 {base+145} H1050')
 else:
  box(650,base+110,245,70,'inode 1 · count=0','#f7e8eb');box(1050,base+110,200,70,'文件 1 已回收','#f7e8eb');text(770,base+210,'两项已删，路径失效',21)
 box(650,base+275,245,70,'inode 2 · count=1','#eaf3f6');box(1005,base+275,245,70,'文件 2：符号链接','#fff3dc',21);arrow(f'M370 {base+295} H650');arrow(f'M895 {base+310} H1005')
 box(405,base+365,490,52,'文件 2 内容：C:/User1/aaa','#fff3dc',23);arrow(f'M1060 {base+345} V{base+391} H900',True)
 text(1060,base+430,'链接仍在；路径已失效' if deleted else '访问 ccc 时再解析目标路径',21)
panel(0,False);panel(440,True)
s.append('</g></svg>');p=out/'OS_links_course.svg';p.write_text('\n'.join(s))
for typ in ['png','pdf']:
 cmd=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/('OS_links_course.'+typ))]
 if typ=='png':cmd.append('--export-dpi=180')
 else:cmd.append('--export-text-to-path')
 subprocess.run(cmd,check=True)
