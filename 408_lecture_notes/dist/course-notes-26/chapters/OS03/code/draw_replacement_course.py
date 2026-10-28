#!/usr/bin/env python3
"""Redraw the OS page-in source models and modified CLOCK source configurations."""
from pathlib import Path
from html import escape
import subprocess
R=Path(__file__).resolve().parents[1]/'figures'
H='<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#527b92"/></marker></defs>'
def text(x,y,s,size=30,anchor='middle',weight='normal'):
 return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'
def rect(x,y,w,h,lines,fill='#e5f1f7',fs=30):
 a=[f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#7598a8" stroke-width="2"/>']
 for k,l in enumerate(lines):a.append(text(x+w/2,y+h/2+(k-(len(lines)-1)/2)*36+10,l,fs))
 return ''.join(a)
def line(x,y,x2,y2,lab=None):
 a=f'<path d="M{x} {y} L{x2} {y2}" fill="none" stroke="#527b92" stroke-width="4" marker-end="url(#arrow)"/>'
 if lab:a+=text((x+x2)/2,(y+y2)/2-10,lab,25)
 return a
def save(name,w,h,body):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{H}<rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" fill="#203d4b">'+''.join(body)+'</g></svg>'
 src=R/(name+'.svg');src.write_text(svg,encoding='utf-8')
 for typ in ['pdf','png']:
  args=['inkscape',str(src),'--export-type='+typ,'--export-filename='+str(R/(name+'.'+typ))]
  if typ=='pdf':args.append('--export-text-to-path')
  else:args.append('--export-dpi=180')
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
# Three course models retain file/swap/backing distinctions and direction.
b=[]
for i,title in enumerate(['① 对换区充足','② 对换区不足','③ UNIX式']):
 x=18+i*535;b.append(f'<rect x="{x}" y="15" width="510" height="570" rx="14" fill="#f9fbfc" stroke="#b7cbd4"/>');b.append(text(x+255,60,title,34,weight='bold'))
 b.append(rect(x+15,190,140,90,['内存'],'#dcefdc',30));b.append(rect(x+340,110,150,85,['对换区'],'#ffebcc',30));b.append(rect(x+340,340,150,85,['文件区'],'#dcebf5',30))
 if i==0:
  b.append(line(x+340,382,x+265,382));b.append(line(x+265,382,x+265,152));b.append(line(x+265,152,x+340,152));b.append(text(x+260,435,'运行前复制',28))
  b.append(line(x+340,140,x+155,212));b.append(line(x+155,260,x+340,180));b.append(text(x+245,115,'调入 / 调出',26))
 elif i==1:
  b.append(line(x+340,385,x+155,258));b.append(text(x+255,470,'只读数据调入',28))
  b.append(line(x+340,145,x+155,210));b.append(line(x+155,260,x+340,180));b.append(text(x+260,112,'修改数据往返',25))
 else:
  b.append(line(x+340,385,x+155,258));b.append(text(x+255,470,'首次使用调入',28))
  b.append(line(x+155,210,x+340,145));b.append(line(x+340,180,x+155,260));b.append(text(x+260,112,'换出 / 再调入',25))
 b.append(text(x+255,508,['内容先复制至对换区','未修改 / 修改分别处理','换出后再从对换区调入'][i],26))
 b.append(text(x+255,550,'具体行为以题设模型为准',27))
save('OS03_page_backing_models_course',1608,605,b)
# Four separate source configurations: preserve position and outer arrow directions.
configs=[['0,1','1,1','1,0','0,0','0,1'],['0,1','0,1','1,0','1,1','0,1'],['0,1','0,0','0,0','0,1','0,0'],['0,1','0,1','0,1','0,1','0,1']]
b=[]
for i,states in enumerate(configs):
 x=20+(i%2)*770;y=18+(i//2)*365
 b.append(f'<rect x="{x}" y="{y}" width="750" height="345" rx="14" fill="#fafcfd" stroke="#b7cbd4"/>')
 b.append(text(x+375,y+39,f'候选状态 {i+1}',31,weight='bold'))
 coords=[(x+200,y+75),(x+490,y+75),(x+565,y+170),(x+345,y+255),(x+125,y+170)]
 centers=[(a+65,b0+28) for a,b0 in coords]
 for j in range(5):
  x1,y1=centers[j];x2,y2=centers[(j+1)%5]
  # clip connecting segments just outside node rectangles
  dx=x2-x1;dy=y2-y1
  import math
  t1=min(65/abs(dx) if dx else 10,28/abs(dy) if dy else 10);t2=t1
  b.append(line(round(x1+dx*t1),round(y1+dy*t1),round(x2-dx*t2),round(y2-dy*t2)))
 for (xx,yy),state in zip(coords,states):b.append(rect(xx,yy,130,56,['('+state+')'],'#dcecf6',30))
b.append(text(790,758,'每格依次为（访问位 A，修改位 M）；四图表示不同候选状态，不指定扫描起点。',27))
save('OS03_improved_clock_states_course',1580,780,b)
