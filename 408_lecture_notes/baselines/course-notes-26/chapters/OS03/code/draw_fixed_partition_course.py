#!/usr/bin/env python3
from pathlib import Path
import subprocess
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="660" viewBox="0 0 1080 660">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#20343f">','<text x="25" y="35" font-size="25" font-weight="bold">王道课件：固定分区可等大，也可不等大</text>','<text x="25" y="65" font-size="19">各分区一次只装入一道作业；两列分别是独立内存示意，单位MB。</text>']
scale=10; top=130
for x,title,sizes in [(110,'等大：四个10 MB分区',[10,10,10,10]),(600,'不等大：2、2、4、6、8、12 MB',[2,2,4,6,8,12])]:
 svg.append(f'<text x="{x}" y="108" font-size="21" font-weight="bold">{title}</text>')
 y=top; addr=0
 for i,n in enumerate([8]+sizes):
  h=n*scale;label='操作系统 8 MB' if i==0 else f'分区{i}  {n} MB';color='#f5d7b4' if i==0 else '#dcefe0'
  svg.append(f'<rect x="{x}" y="{y}" width="330" height="{h}" fill="{color}" stroke="#7897a5"/>')
  svg.append(f'<text x="{x+165}" y="{y+h/2+6}" text-anchor="middle" font-size="18">{label}</text>')
  svg.append(f'<text x="{x-42}" y="{y+5}" font-size="16">{addr}</text>')
  y+=h;addr+=n
 svg.append(f'<text x="{x-42}" y="{y+5}" font-size="16">{addr}</text>')
svg+=['<text x="25" y="642" font-size="18">每个表项记录分区大小、起始地址和分配状态；分区内的未用空间为内部碎片。</text>','</g></svg>']
p=out/'OS03_fixed_partition_course.svg';p.write_text('\n'.join(svg))
for typ in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/(p.stem+'.'+typ))]
 if typ=='png':args+=['--export-dpi=180']
 else:args+=['--export-text-to-path']
 subprocess.run(args,check=True)
