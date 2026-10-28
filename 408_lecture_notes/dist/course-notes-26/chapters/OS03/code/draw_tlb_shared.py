#!/usr/bin/env python3
"""Redraw the Wangdao TLB timing and memory-mapped file examples."""
from pathlib import Path
import html, subprocess
out = Path(__file__).resolve().parents[1] / 'figures'
out.mkdir(exist_ok=True)
blue='#477793'; teal='#81a9b9'; green='#dcefe5'; yellow='#fff1c6'; rose='#f1deea'; ink='#253b47'
def start(width,height):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#608092"/></marker></defs>', f'<g font-family="Noto Sans CJK SC, sans-serif" fill="{ink}" font-size="20">']
def txt(x,y,s,size=20,anchor='start',fill=ink):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}">{html.escape(s)}</text>'
def line(x1,y1,x2,y2,stroke=blue,dash=''):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="2" {dash}/>'
def rect(x,y,w,h,fill,label=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="#7593a2" stroke-width="1.4"/>' + (txt(x+w/2,y+h*.69,label,19,'middle') if label else '')
def export(name,parts):
 parts.extend(['</g></svg>']); svg=out/(name+'.svg');svg.write_text('\n'.join(parts),encoding='utf8')
 for fmt in ['png','pdf']:
  args=['inkscape',str(svg),'--export-type='+fmt,'--export-filename='+str(out/(name+'.'+fmt))]
  if fmt=='png':args+=['--export-dpi=180']
  if fmt=='pdf':args+=['--export-text-to-path']
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

# Both cases concern a TLB miss. Horizontal positions use a common linear time scale.
p=start(1000,500);p.append(txt(25,33,'快表未命中：先后查询与并行查询',24))
scale=3.35;origin=188
for row,(title, starts, ends, ticks) in enumerate([
 ('先查快表，未命中后查慢表', [0,1,101],[1,101,201], [0,1,101,201]),
 ('快表与慢表同时查询', [0,0,100],[1,100,200], [0,1,100,200])]):
 top=78+row*205;p.append(txt(25,top,title,21));
 for j,(label,color,a,b) in enumerate(zip(['查快表','查慢表','访问内存'],[green,yellow,rose],starts,ends)):
  y=top+26+j*39;p.append(txt(25,y+18,label,18));p.append(rect(origin+scale*a,y,max(3.35,scale*(b-a)),14,color));
  if label=='查快表':p.append(txt(origin+scale*b+11,y+14,'1 μs',16))
 axis=top+151;p.append(line(origin,axis,origin+scale*210,axis,blue,'marker-end="url(#arrow)"'))
 # The 1-μs mark is called out above the axis because it lies 3.35 px after zero.
 for t in ticks:
  x=origin+scale*t;p.append(line(x,axis-5,x,axis+5));
  if t==1:p.append(line(x,axis-3,x+22,axis-20));p.append(txt(x+26,axis-21,'1',15))
  else:p.append(txt(x,axis+25,str(t),16,'middle'))
 p.append(txt(origin+scale*210+13,axis+7,'μs',18))
p.append(txt(25,485,'命中率 90%；快表 1 μs，内存 100 μs：平均分别为 111 μs、110.9 μs。',17));export('OS03_tlb_time',p)

# Dashed links denote mapping relationships; physical frames need not be contiguous.
p=start(1000,560);p.append(txt(25,32,'两个进程映射同一文件',24));
p.append(txt(24,74,'进程 2 虚拟地址空间',20));p.append(txt(637,74,'进程 1 虚拟地址空间',20));p.append(txt(369,74,'共享物理页框',20));
page_y={1:128,2:185,3:242}; frame_y={2:115,1:196,3:277};colors={1:'#c99652',2:'#68a892',3:'#8d7fa6'}
# Draw correspondences behind boxes for clarity.
for n in [1,2,3]:
 fy=frame_y[n]+19;py=page_y[n]+19
 p.append(line(199,py,385,fy,colors[n],'stroke-dasharray="6 4" marker-end="url(#arrow)"'))
 p.append(line(635,py,515,fy,colors[n],'stroke-dasharray="6 4" marker-end="url(#arrow)"'))
 # A separate lower lane represents correspondence to disk, not a synchronous write.
 path=f'M 385,{fy} C 300,{fy} 300,{380+n*18} {340+(n-1)*145},{380+n*18} L {340+(n-1)*145},474'
 p.append(f'<path d="{path}" fill="none" stroke="{colors[n]}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
for n in [1,2,3]:
 p.append(rect(50,page_y[n],150,38,yellow,f'虚拟页 {n}'))
 p.append(rect(635,page_y[n],150,38,yellow,f'虚拟页 {n}'))
 p.append(rect(385,frame_y[n],130,38,green,f'文件页 {n}'))
 p.append(rect(275+(n-1)*145,474,130,38,'#e0eef4',f'文件块 {n}'))
p.append(txt(95,332,'页表映射',18,fill=blue));p.append(txt(651,332,'页表映射',18,fill=blue));
p.append(txt(725,445,'同一磁盘文件',19));p.append(txt(28,544,'虚线表示对应关系；写入何时持久化取决于具体映射和同步方式。',17));export('OS03_mmap_shared',p)
print('created OS03_tlb_time and OS03_mmap_shared, SVG/PNG/PDF')

# Exact page-table and TLB snapshot used in 3.1.3_3, file page 4.
p=start(1100,550)
p.append(txt(25,32,'页号为 0 的三个逻辑地址：快表命中与未命中',24))
p.append(txt(25,66,'依次访问 (0,0)、(0,4)、(0,8)；页内偏移分别为 0、4、8。',19))
p.append(rect(30,135,190,78,'#e0eef4'))
p.append(txt(125,162,'逻辑地址',19,'middle'));p.append(txt(125,190,'页号 0 + 页内偏移',18,'middle'))
p.append(rect(305,95,250,150,green));p.append(txt(430,124,'快表（部分副本）',19,'middle'))
p.append(line(326,136,534,136));p.append(txt(360,164,'页号',18));p.append(txt(457,164,'页框号',18));p.append(txt(375,207,'0',21));p.append(txt(478,207,'600',21))
p.append(rect(305,294,250,161,yellow));p.append(txt(430,321,'内存页表（慢表）',19,'middle'))
p.append(line(326,332,534,332));p.append(txt(347,360,'页号',18));p.append(txt(457,360,'页框号',18))
for i,(pg,fr) in enumerate([(0,600),(1,500),(2,400)]):
 y=388+27*i;p.append(txt(365,y,str(pg),18));p.append(txt(478,y,str(fr),18))
p.append(rect(770,145,290,98,rose));p.append(txt(915,177,'构成物理地址',20,'middle'));p.append(txt(915,207,'600 × 页大小 + 页内偏移',18,'middle'))
p.append(rect(30,270,190,75,'#e0eef4'));p.append(txt(125,299,'页表寄存器 M、N',17,'middle'));p.append(txt(125,326,'0 ≤ 页号 < N',17,'middle'));p.append(line(125,213,125,270,blue,'marker-end="url(#arrow)"'));p.append(f'<path d="M220,307 H260 V173 H305" fill="none" stroke="{blue}" stroke-width="2" marker-end="url(#arrow)"/>');p.append(txt(225,295,'合法',16));p.append(line(125,345,125,394,blue,'marker-end="url(#arrow)"'));p.append(txt(125,419,'越界异常',17,'middle'))
p.append(line(555,173,770,173,blue,'marker-end="url(#arrow)"'));p.append(txt(612,159,'命中',18))
p.append(line(430,245,430,294,blue,'marker-end="url(#arrow)"'));p.append(txt(446,275,'未命中',18));p.append(line(510,294,510,245,blue,'stroke-dasharray="5 4" marker-end="url(#arrow)"'));p.append(txt(522,265,'回填（常见）',16))
p.append(line(555,386,690,386));p.append(line(690,386,690,224));p.append(line(690,224,770,224,blue,'marker-end="url(#arrow)"'));p.append(txt(600,370,'取得页框',17))
p.append(txt(305,480,'页表项地址 = M + 页号 × 页表项大小',16));p.append(txt(25,510,'快表中的 0→600 是课件显示的快照；首次访问是否命中取决于初始内容。',17));p.append(txt(25,535,'查到页框后回填快表是常见缓存行为，具体填充策略由实现决定。',17))
export('OS03_tlb_page_table',p)
print('created OS03_tlb_page_table, SVG/PNG/PDF')
