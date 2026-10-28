#!/usr/bin/env python3
"""Editable vector reconstructions of two Wangdao OS address-translation examples."""
from pathlib import Path
import html, subprocess
out=Path(__file__).resolve().parent.parent/'figures'
def esc(s): return html.escape(str(s))
def text(x,y,s,size=22,color='#233840',anchor='middle',weight='normal'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>'
def box(x,y,w,h,label,fill='#e5f0f4',size=21):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="#648290" stroke-width="1.5"/>'+text(x+w/2,y+h/2+7,label,size)
def arrow(x1,y1,x2,y2): return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#436b80" stroke-width="2" marker-end="url(#arrow)"/>'
def create(name,parts,w=1000,h=480):
 pre=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#436b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC, sans-serif">'''
 (out/(name+'.svg')).write_text(pre+''.join(parts)+'</g></svg>',encoding='utf8')
 for ext in ['png','pdf']:
  command=['inkscape',str(out/(name+'.svg')),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))]
  if ext=='png':command.append('--export-dpi=180')
  if ext=='pdf':command.append('--export-text-to-path')
  subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

p=[]
p+=[text(500,30,'两级页表：逐级查表得到目标页框',26,weight='bold')]
p+=[box(45,58,250,48,'一级页号 0（10 位）'),box(295,58,250,48,'二级页号 1（10 位）'),box(545,58,330,48,'页内偏移 4095（12 位）','#fff1d4')]
p+=[text(125,157,'一级页表 / 页目录',21,weight='bold'),text(450,157,'页框 3：二级页表',21,weight='bold'),text(795,157,'物理内存',21,weight='bold')]
p+=[box(40,175,90,42,'页号','#dcece2'),box(130,175,155,42,'下级表页框','#dcece2'),box(40,217,90,42,'0'),box(130,217,155,42,'3'),box(40,259,90,42,'1'),box(130,259,155,42,'…')]
p+=[box(335,175,90,42,'页号','#dcece2'),box(425,175,145,42,'目标页框','#dcece2'),box(335,217,90,42,'0'),box(425,217,145,42,'2'),box(335,259,90,42,'1','#fff1d4'),box(425,259,145,42,'4','#fff1d4')]
p+=[box(690,175,95,42,'页框','#dcece2'),box(785,175,175,42,'内容','#dcece2'),box(690,217,95,42,'3'),box(785,217,175,42,'二级页表'),box(690,259,95,42,'4','#fff1d4'),box(785,259,175,42,'目标页','#fff1d4')]
p+=[arrow(285,238,330,196),arrow(570,280,685,280)]
p+=[text(500,361,'页框 3 的基址 = 3 × 4096 = 12288 B；二级页表项 1 地址 = 12288 + 1 × 4 = 12292 B',19),text(500,403,'查得目标页框 4：物理地址 = 4 × 4096 + 4095 = 20479 B',22,weight='bold'),text(500,444,'页表项地址与目标数据物理地址属于不同地址。',19)]
create('OS03_twolevel_course',p)

p=[];p+=[text(500,33,'分段：段表把各逻辑段映射到不连续的物理区域',26,weight='bold')]
p+=[text(145,90,'逻辑地址空间',22,weight='bold'),text(475,90,'段表',22,weight='bold'),text(795,90,'物理内存（KiB）',22,weight='bold')]
p+=[box(55,115,180,54,'段 0：MAIN / 7 KiB','#fbe4cc',18),box(55,169,180,54,'段 1：子程序 / 3 KiB','#e0efd9',18),box(55,223,180,54,'段 2：全局量 / 6 KiB','#e9def5',18)]
p+=[box(335,115,72,54,'段号','#dcece2'),box(407,115,110,54,'段长','#dcece2'),box(517,115,125,54,'基址','#dcece2'),box(335,169,72,54,'0'),box(407,169,110,54,'7 KiB'),box(517,169,125,54,'80 KiB'),box(335,223,72,54,'1'),box(407,223,110,54,'3 KiB'),box(517,223,125,54,'120 KiB'),box(335,277,72,54,'2','#fff1d4'),box(407,277,110,54,'6 KiB','#fff1d4'),box(517,277,125,54,'40 KiB','#fff1d4')]
p+=[box(725,115,210,40,'[0,40)：其他',size=18),box(725,155,210,55,'段 2：[40,46)','#e9def5',18),box(725,210,210,55,'段 0：[80,87)','#fbe4cc',18),box(725,265,210,55,'段 1：[120,123)','#e0efd9',18)]
p+=[arrow(235,142,330,196),arrow(235,196,330,250),arrow(235,250,330,304),arrow(642,196,720,236),arrow(642,250,720,292),arrow(642,304,720,182)]
p+=[text(500,382,'访问段 2、偏移 1024 B：先检查段长与权限',21,weight='bold'),text(500,420,'1024 < 6 × 1024；物理地址 = 40 × 1024 + 1024 = 41984 B',22),text(500,457,'图中省略不影响该例的其他内存区，不表示各段物理相邻。',19)]
create('OS03_segment_course',p)
print('两幅矢量图及PNG/PDF已重建')
