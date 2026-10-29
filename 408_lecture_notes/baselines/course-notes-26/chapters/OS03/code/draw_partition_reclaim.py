#!/usr/bin/env python3
from pathlib import Path
import html,subprocess
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
# kind,start,end,label. The textbook cases intentionally use different prior states.
cases=[('后方空闲',[(0,8,'sys','系统'),(8,28,'used','P1'),(28,32,'release','P4'),(32,42,'free','空10'),(42,60,'used','P3'),(60,64,'free','空4')],[(0,8,'sys','系统'),(8,28,'used','P1'),(28,42,'free','空14'),(42,60,'used','P3'),(60,64,'free','空4')],'[28,32)+[32,42) → [28,42)，14 MB'),('前方空闲',[(0,8,'sys','系统'),(8,28,'free','空20'),(28,32,'used','P4'),(32,42,'free','空10'),(42,60,'release','P3'),(60,64,'used','P5')],[(0,8,'sys','系统'),(8,28,'free','空20'),(28,32,'used','P4'),(32,60,'free','空28'),(60,64,'used','P5')],'[32,42)+[42,60) → [32,60)，28 MB'),('前后均空闲',[(0,8,'sys','系统'),(8,28,'free','空20'),(28,32,'release','P4'),(32,42,'free','空10'),(42,60,'used','P3'),(60,64,'free','空4')],[(0,8,'sys','系统'),(8,42,'free','空34'),(42,60,'used','P3'),(60,64,'free','空4')],'[8,28)+[28,32)+[32,42) → [8,42)，34 MB'),('前后均占用',[(0,8,'sys','系统'),(8,28,'used','P1'),(28,42,'release','P2'),(42,60,'used','P3'),(60,64,'free','空4')],[(0,8,'sys','系统'),(8,28,'used','P1'),(28,42,'free','空14'),(42,60,'used','P3'),(60,64,'free','空4')],'新增 [28,42) 空闲表项，14 MB')]
colors={'sys':'#f5d7b4','used':'#d8e8f1','release':'#f6dce8','free':'#dcefe0'}
w=1240;h=720;x0=205;scale=15.5;svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#20343f">','<text x="18" y="32" font-size="25" font-weight="bold">王道课件：动态分区回收的四种邻接情况</text>','<text x="18" y="60" font-size="18">每一行是独立状态；粉色区回收，绿色区为空闲，地址为半开区间，单位MB。</text>']
for i,(title,before,after,desc) in enumerate(cases):
 y=80+i*155;svg.append(f'<text x="18" y="{y+25}" font-size="21" font-weight="bold">{html.escape(title)}</text>')
 for j,(label,segments) in enumerate([('回收前',before),('回收后',after)]):
  yy=y+j*48;svg.append(f'<text x="138" y="{yy+24}" font-size="18">{label}</text>')
  for a,b,k,txt in segments:
   x=x0+a*scale;width=(b-a)*scale
   svg.append(f'<rect x="{x}" y="{yy}" width="{width}" height="31" fill="{colors[k]}" stroke="#7897a5"/>')
   svg.append(f'<text x="{x+width/2}" y="{yy+22}" text-anchor="middle" font-size="20">{html.escape(txt)}</text>')
   svg.append(f'<text x="{x}" y="{yy-3}" font-size="16">{a}</text>')
  svg.append(f'<text x="{x0+64*scale-12}" y="{yy-3}" font-size="16">64</text>')
 svg.append(f'<text x="{x0}" y="{y+115}" font-size="19">{html.escape(desc)}</text>')
 svg.append(f'<path d="M18 {y+130} H1215" stroke="#dce4e7"/>')
svg.append('</g></svg>');s=out/'OS03_partition_reclaim_course.svg';s.write_text('\n'.join(svg))
for typ in ['png','pdf']:
 args=['inkscape',str(s),'--export-type='+typ,'--export-filename='+str(out/('OS03_partition_reclaim_course.'+typ))]
 if typ=='png':args+=['--export-dpi=180']
 else:args+=['--export-text-to-path']
 subprocess.run(args,check=True)
