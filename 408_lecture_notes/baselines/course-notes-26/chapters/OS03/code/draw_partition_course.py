#!/usr/bin/env python3
from pathlib import Path
import html, subprocess
p=Path(__file__).resolve().parents[1]/'figures';p.mkdir(exist_ok=True)
rows=[
 ('首次适应', ['20 @ 8','10 @ 32','4 @ 60'], 'P5：15 MB', ['5 @ 23','10 @ 32','4 @ 60'], 'P6：8 MB', ['5 @ 23','2 @ 40','4 @ 60']),
 ('最佳适应', ['4 @ 60','10 @ 32','20 @ 8'], 'P5：3 MB', ['1 @ 63','10 @ 32','20 @ 8'], 'P6：9 MB', ['1 @ 63','1 @ 41','20 @ 8']),
 ('最坏适应', ['20 @ 8','10 @ 32','4 @ 60'], 'P5：3 MB', ['17 @ 11','10 @ 32','4 @ 60'], 'P6：9 MB', ['10 @ 32','8 @ 20','4 @ 60']),
 ('邻近适应', ['4','6','10','4'], 'P5：5 MB', ['4','1','10','4'], 'P6：5 MB', ['4','1','5','4'])]
w=1200;h=540;svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#20343f">','<text x="20" y="31" font-size="24" font-weight="bold">王道课件：按空闲链选择分区并依次分配</text>','<text x="20" y="59" font-size="18">前三行方框为“大小 @ 起始地址”，单位MB；末行只标课件给出的空闲区大小。</text>']
for i,(name,a,action1,b,action2,c) in enumerate(rows):
 y=87+105*i;svg.append(f'<text x="20" y="{y+24}" font-size="20" font-weight="bold">{html.escape(name)}</text>')
 for col,states in enumerate([a,b,c]):
  x0=145+col*350
  label=['初始空闲链','分配P5后','分配P6后'][col]
  svg.append(f'<text x="{x0}" y="{y+19}" font-size="17">{label}</text>')
  boxwidth=78 if len(states)==3 else 58
  for j,v in enumerate(states):
   x=x0+j*(boxwidth+4)
   svg.append(f'<rect x="{x}" y="{y+30}" width="{boxwidth}" height="32" rx="3" fill="#DFEDF3" stroke="#6C94A8"/>')
   svg.append(f'<text x="{x+boxwidth/2}" y="{y+51}" text-anchor="middle" font-size="16">{html.escape(v)}</text>')
  if col<2:
   lbl=action1 if col==0 else action2
   svg.append(f'<text x="{x0+255}" y="{y+20}" font-size="16">{html.escape(lbl)}</text>')
   svg.append(f'<path d="M{x0+255} {y+45} h65 m-10 -7 l10 7 l-10 7" fill="none" stroke="#466C82" stroke-width="2"/>')
 svg.append(f'<path d="M20 {y+80} H1180" stroke="#e0e8eb"/>')
svg.append('</g></svg>');(p/'OS03_partition_algorithms_course.svg').write_text('\n'.join(svg))
subprocess.run(['inkscape',str(p/'OS03_partition_algorithms_course.svg'),'--export-type=png','--export-dpi=180','--export-filename='+str(p/'OS03_partition_algorithms_course.png')],check=True)
subprocess.run(['inkscape',str(p/'OS03_partition_algorithms_course.svg'),'--export-text-to-path','--export-type=pdf','--export-filename='+str(p/'OS03_partition_algorithms_course.pdf')],check=True)
