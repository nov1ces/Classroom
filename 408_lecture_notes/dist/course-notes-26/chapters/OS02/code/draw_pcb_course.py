#!/usr/bin/env python3
"""王道OS 2.1.3课件PCB组织示例，生成三张可编辑图。"""
from pathlib import Path
import html,subprocess
O=Path(__file__).resolve().parents[1]/'figures';O.mkdir(exist_ok=True)
def label(x,y,s,size=27,anchor='middle',weight='normal'):
 return f'<text x="{x}" y="{y}" font-family="Noto Sans CJK SC,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#243947">{html.escape(s)}</text>'
def box(x,y,w,h,fill='#e3f1f4',stroke='#668da0'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def arrow(x,y,u,v):return f'<path d="M{x},{y} L{u},{v}" fill="none" stroke="#63879a" stroke-width="3" marker-end="url(#arrow)"/>'
def save(name,w,h,parts):
 head=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#63879a"/></marker></defs><rect width="100%" height="100%" fill="white"/>'
 svg=O/(name+'.svg');svg.write_text(head+''.join(parts)+'</svg>')
 for fmt in ('pdf','png'):
  a=['inkscape',str(svg),'--export-type='+fmt,'--export-filename='+str(O/(name+'.'+fmt))]+(['--export-text-to-path'] if fmt=='pdf' else ['--export-dpi=180'])
  subprocess.run(a,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def chain_row(y,title,labels):
 r=[box(35,y,250,65,'#dceef4'),label(160,y+42,title,25),arrow(290,y+33,390,y+33)]
 for j,v in enumerate(labels):
  x=405+230*j;r += [box(x,y,160,65),label(x+80,y+42,v,26)]
  if j+1<len(labels):r.append(arrow(x+165,y+33,x+215,y+33))
 return r
s=[label(35,45,'链式组织：同一状态的 PCB 链接成队列',28,'start','bold')]
s+=chain_row(90,'执行指针',['PCB2']);s+=chain_row(195,'就绪队列指针',['PCB5','PCB1','PCB4']);s+=chain_row(300,'阻塞队列指针',['PCB3','PCB7','PCB6']);s += [label(35,420,'单CPU在同一时刻最多一个进程运行；就绪队列顺序由调度规则决定。',22,'start'),label(35,456,'阻塞进程可按等待事件分别组织为多个队列。',22,'start')]
save('OS_pcb_chains_course',1200,495,s)
s=[label(35,45,'多核及按事件区分的等待队列',28,'start','bold')]
s+=chain_row(80,'运行队列',['PCB2','PCB8']);s+=chain_row(165,'就绪队列',['PCB5','PCB1','PCB4']);s+=chain_row(250,'等待事件 A',['PCB3','PCB7']);s+=chain_row(335,'等待事件 B',['PCB6']);s += [label(35,455,'多核CPU可以有多个进程同时处于运行态。',23,'start')]
save('OS_pcb_event_queues_course',1200,495,s)
s=[label(35,42,'索引组织：索引表保存各PCB的定位信息',28,'start','bold')]
s+=chain_row(75,'执行指针',['PCB2'])
for y,ptr,table,vals in [(195,'就绪表指针','就绪索引表',['PCB5','PCB1','PCB4']),(425,'阻塞表指针','阻塞索引表',['PCB6','PCB7','PCB3'])]:
 s += [box(30,y+60,245,65,'#dceef4'),label(152,y+102,ptr,25),arrow(280,y+92,370,y+92),box(385,y,220,60,'#d5e8ef'),label(495,y+39,table,24,'middle','bold')]
 for j,v in enumerate(vals):
  yy=y+60+j*50;s += [box(385,yy,220,50,'#f1f6f7'),label(495,yy+34,f'索引项 {j+1}',22),arrow(610,yy+25,765,yy+25),box(780,yy,180,50),label(870,yy+34,v,23)]
s += [label(35,665,'链式图和索引图的阻塞项顺序各依课件示例，并不要求相同。',21,'start')]
save('OS_pcb_index_course',1200,705,s)
print('generated three PCB figures')
