#!/usr/bin/env python3
from pathlib import Path
import subprocess
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
initial=[(0,8,'sys','系统'),(8,28,'free','空20'),(28,32,'used','P4'),(32,42,'free','空10'),(42,60,'used','P3'),(60,64,'free','空4')]
cases=[('部分分配',[(0,8,'sys','系统'),(8,12,'alloc','P5'),(12,28,'free','空16'),(28,32,'used','P4'),(32,42,'free','空10'),(42,60,'used','P3'),(60,64,'free','空4')],'由[8,28)分配[8,12)，将原表项改为起始12、大小16'),('整块分配',[(0,8,'sys','系统'),(8,28,'free','空20'),(28,32,'used','P4'),(32,42,'free','空10'),(42,60,'used','P3'),(60,64,'alloc','P5')],'由[60,64)完整分配4 MB，删除原空闲表项')]
colors={'sys':'#f5d7b4','used':'#d8e8f1','alloc':'#f6dce8','free':'#dcefe0'};w=1240;h=395;x0=205;scale=15.5
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#20343f">','<text x="18" y="32" font-size="25" font-weight="bold">王道课件：空闲分区表的两种分配更新</text>','<text x="18" y="59" font-size="18">两行各从同一空闲状态开始；粉色为分给P5的4 MB，地址按半开区间表示。</text>']
for i,(title,after,desc) in enumerate(cases):
 y=92+i*150;svg.append(f'<text x="18" y="{y+22}" font-size="20" font-weight="bold">{title}</text>')
 for j,(lab,items) in enumerate([('分配前',initial),('分配后',after)]):
  yy=y+j*47;svg.append(f'<text x="135" y="{yy+23}" font-size="18">{lab}</text>')
  for a,b,k,txt in items:
   x=x0+a*scale;width=(b-a)*scale;svg.append(f'<rect x="{x}" y="{yy}" width="{width}" height="30" fill="{colors[k]}" stroke="#7897a5"/>');svg.append(f'<text x="{x+width/2}" y="{yy+21}" text-anchor="middle" font-size="20">{txt}</text>');svg.append(f'<text x="{x}" y="{yy-3}" font-size="16">{a}</text>')
  svg.append(f'<text x="{x0+64*scale-13}" y="{yy-3}" font-size="16">64</text>')
 svg.append(f'<text x="{x0}" y="{y+112}" font-size="19">{desc}</text>');svg.append(f'<path d="M18 {y+130} H1215" stroke="#dce4e7"/>')
svg.append('</g></svg>');p=out/'OS03_partition_allocation_course.svg';p.write_text('\n'.join(svg))
for typ in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(out/(p.stem+'.'+typ))]
 args+=['--export-dpi=180'] if typ=='png' else ['--export-text-to-path'];subprocess.run(args,check=True)
