#!/usr/bin/env python3
"""按王道课件请求集绘制六种调度轨迹。"""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parent.parent/'figures'
traces=[('FCFS', [100,55,58,39,18,90,160,150,38,184],498),('SSTF',[100,90,58,55,39,38,18,150,160,184],248),('SCAN',[100,150,160,184,200,90,58,55,39,38,18],282),('LOOK',[100,150,160,184,90,58,55,39,38,18],250),('C-SCAN',[100,150,160,184,200,0,18,38,39,55,58,90],390),('C-LOOK',[100,150,160,184,18,38,39,55,58,90],322)]
for start in range(0,6,2):
 name='OS_disk_trace_'+str(start//2+1)+'_course'; svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="760" viewBox="0 0 1240 760">','<defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L6 3.5 L0 7 z" fill="#496b7f"/></marker></defs>','<rect width="1240" height="760" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#213845">']
 for k,(label,path,total) in enumerate(traces[start:start+2]):
  y=15+k*370;svg += [f'<rect x="12" y="{y}" width="1216" height="355" rx="8" fill="#f8fbfc" stroke="#a9bec8"/>',f'<text x="32" y="{y+36}" font-size="26">{label}　初始 100，移动 {total} 个磁道</text>']
  ox=80;span=1080; xx=lambda n:ox+span*n/200
  svg.append(f'<path d="M{ox} {y+100} H{ox+span}" stroke="#77919f" stroke-width="2"/>')
  for j,val in enumerate([0,18,38,39,55,58,90,100,150,160,184,200]):
   x=xx(val); offset=24 if val in [39,58,100,160,200] else 5
   svg.append(f'<path d="M{x} {y+95} V{y+105}" stroke="#77919f"/>');svg.append(f'<text x="{x}" y="{y+80-offset}" font-size="19" text-anchor="middle">{val}</text>')
  for j,(a,b) in enumerate(zip(path,path[1:])):
   yy=y+120+j*18;svg.append(f'<path d="M{xx(a)} {yy} H{xx(b)}" stroke="#496b7f" stroke-width="2.4" marker-end="url(#a)"/>')
  seq=' → '.join(map(str,path));svg.append(f'<text x="32" y="{y+337}" font-size="20">{escape(seq)}</text>')
 svg.append('</g></svg>');(out/(name+'.svg')).write_text('\n'.join(svg))
 for typ in ['png','pdf']:subprocess.run(['inkscape',str(out/(name+'.svg')),'--export-type='+typ,'--export-dpi=180','--export-filename='+str(out/(name+'.'+typ))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
