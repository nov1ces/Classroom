#!/usr/bin/env python3
"""王道OS 2.2.5_3和2.2.6课件队列图；可重建SVG/PNG/矢量PDF。"""
from pathlib import Path
import html, subprocess
O=Path(__file__).resolve().parents[1]/'figures';O.mkdir(exist_ok=True)
FONT='Noto Sans CJK SC, sans-serif'
def text(x,y,s,size=24,anchor='start',weight='normal',color='#243947'):
 return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>'
def rect(x,y,w,h,fill='#e3f1f4',stroke='#668da0',r=8):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
def arrow(x,y,u,v,color='#63879a',dash=''):return f'<path d="M{x},{y} L{u},{v}" fill="none" stroke="{color}" stroke-width="3" {dash} marker-end="url(#a)"/>'
def save(name,w,h,shapes):
 head=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#63879a"/></marker></defs><rect width="100%" height="100%" fill="white"/>'
 p=O/(name+'.svg');p.write_text(head+''.join(shapes)+'</svg>',encoding='utf8')
 for typ in ('pdf','png'):
  args=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(O/(name+'.'+typ))]
  if typ=='pdf':args+=['--export-text-to-path']
  else:args+=['--export-dpi=180']
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
# 不同类别分别入队，左右箭头为入队/调度方向。
s=[text(35,42,'按进程类型分别进入队列',27,weight='bold'),text(42,88,'最高优先级',21),text(42,357,'最低优先级',21)]
for y,label,example,method,share in [(100,'系统进程','如内存管理进程','优先级调度','50%'),(185,'交互式进程','如游戏、打字软件','RR','40%'),(270,'批处理进程','如模型训练、视频渲染','FCFS','10%')]:
 s += [arrow(45,y+30,210,y+30),rect(220,y,470,62),text(455,y+27,label,23,'middle','bold'),text(455,y+52,example,19,'middle'),arrow(700,y+30,780,y+30),rect(790,y,365,62,'#f1f4f5'),text(810,y+39,f'队内：{method}   示例时间：{share}',21)]
s += [text(35,385,'队列间另选一种规则：固定优先级，或按 50% / 40% / 10% 分配CPU时间。',22),text(35,420,'固定优先级：高优先级队列为空，低优先级队列才能被调度。',22)]
save('OS_multilevel_queue_course',1200,455,s)
# 公共就绪队列：按照课件 P1...P16 的蛇形次序完整表示。
s=[text(30,42,'公共就绪队列：四个CPU共享同一队列',27,weight='bold')]
for i in range(4):
 x=70+i*275;s+=[rect(x,70,195,74,'#e3f1f4'),text(x+98,102,f'CPU{i+1}',24,'middle','bold'),text(x+98,131,'Cache',19,'middle')]
s += [text(30,190,'公共队列（内核区，访问需互斥）',23),rect(30,205,1130,240,'#f7fbf8','#8eaa93')]
for row in range(4):
 for col in range(4):
  n=row*4+col+1; x=80+col*265;y=235+row*49
  s+=[rect(x,y,190,38,'#dceee4','#7fa291',19),text(x+95,y+27,'P'+str(n),21,'middle')]
  if col<3:s.append(arrow(x+190,y+19,x+255,y+19) if row%2==0 else arrow(x+265,y+19,x+200,y+19))
 if row<3:
  x=80+(3 if row%2==0 else 0)*265+95;s.append(arrow(x,y+38,x,y+48))
s += [text(35,492,'优点：队列共享便于负载均衡；进程迁移可能降低缓存亲和性。',23),text(35,528,'软亲和：调度器尽量保持；硬亲和：进程经系统调用限定CPU集合。',23)]
save('OS_common_ready_queue_course',1200,570,s)
# 课件4核示例：P16从CPU4队列迁到CPU1；保留迁移前后负载。
s=[text(30,42,'私有就绪队列：P16 从 CPU4 的队列迁至 CPU1',27,weight='bold')]
rows=[(80,'迁移前',[50,80,80,95],[['P1','P5','P9','P13'],['P2','P6','P10','P14'],['P3','P7','P11','P15'],['P4','P8','P12','P16']]),(400,'迁移后',[75,80,80,70],[['P1','P5','P9','P13','P16'],['P2','P6','P10','P14'],['P3','P7','P11','P15'],['P4','P8','P12']])]
for y,title,loads,queues in rows:
 s.append(text(32,y,title,24,weight='bold'))
 for i in range(4):
  x=30+i*290;s += [rect(x,y+20,260,75,'#e3f1f4'),text(x+130,y+52,f'CPU{i+1}   负载{loads[i]}%',23,'middle','bold'),text(x+130,y+82,'Cache',19,'middle'),arrow(x+130,y+98,x+130,y+118),rect(x,y+125,260,104,'#f4faf6','#82a18a'),text(x+130,y+157,'私有就绪队列',21,'middle'),text(x+130,y+192,' → '.join(queues[i]),20,'middle')]
 s.append(text(32,y+263,'P16 从 CPU4 队尾移出，插入 CPU1 队尾。' if title=='迁移后' else '四个就绪队列分别由对应处理器选择进程。',21))
s += [text(30,744,'Push：特定系统程序周期检查负载，把忙CPU就绪进程推向较空闲CPU。',22),text(30,780,'Pull：CPU调度程序发现本核负载低时，从忙CPU队列拉取就绪进程。',22),text(30,816,'两者的发起方不同，可在同一系统按实现需要共同使用。',22)]
save('OS_private_ready_queues_course',1200,850,s)
print('generated 3 SVG / PNG / PDF figures in',O)
