#!/usr/bin/env python3
"""Rebuild Wangdao slide 2.2.1 page 7 as an editable seven-state diagram."""
from pathlib import Path
import subprocess, re
p=Path(__file__).resolve().parent.parent/'figures'; p.mkdir(exist_ok=True)
dot=r'''digraph SevenStates {
 graph [rankdir=LR, bgcolor="white", pad="0.3", nodesep="0.7", ranksep="1.0", splines=polyline, outputorder=edgesfirst];
 node [shape=box, style="rounded,filled", fontname="Noto Sans CJK SC", fontsize=20, width=1.4, height=.58, color="#6B91A7", fillcolor="#E0EFF4"];
 edge [fontname="Noto Sans CJK SC", fontsize=14, color="#547E93", arrowsize=.8];
 create [label="创建态", fillcolor="#FFF0DC"]; ready [label="就绪态"]; run [label="运行态"]; term [label="终止态", fillcolor="#FFF0DC"];
 rs [label="就绪挂起", fillcolor="#EDE9F2"]; bs [label="阻塞挂起", fillcolor="#EDE9F2"]; block [label="阻塞态"];
 {rank=same; create;} {rank=same; ready; rs;} {rank=same; run; block; bs;} {rank=same; term;}
 create -> ready [label="接纳"];
 ready -> run [label="调度"];
 run -> ready [label="时间片到/抢占", constraint=false];
 run -> term [label="退出"];
 run -> block [label="等待事件", constraint=false];
 block -> ready [label="事件发生", constraint=false];
 create -> rs [label="创建后挂起"];
 ready -> rs [label="挂起", constraint=false];
 rs -> ready [label="激活", constraint=false];
 block -> bs [label="挂起", constraint=false];
 bs -> block [label="激活", constraint=false];
 bs -> rs [label="事件发生", constraint=false];
 run -> rs [label="挂起", constraint=false];
}'''
(p/'OS07_seven_states.dot').write_text(dot,encoding='utf8')
subprocess.run(['dot','-Tsvg',str(p/'OS07_seven_states.dot'),'-o',str(p/'OS07_seven_states.svg')],check=True)
# Separate the labels on the paired up/down arrows while preserving geometry.
svg_path=p/'OS07_seven_states.svg'
svg=svg_path.read_text(encoding='utf8')
for edge,offset in [('ready&#45;&gt;rs',-15),('rs&#45;&gt;ready',15),('block&#45;&gt;bs',-15),('bs&#45;&gt;block',15)]:
    pattern=r'(<g id="edge\d+" class="edge">\s*<title>'+edge+r'</title>.*?</g>)'
    def shift(match):
        return re.sub(r'(<text text-anchor="middle" x=")([-\d.]+)',lambda m:m[1]+str(float(m[2])+offset),match[0],count=1)
    svg,n=re.subn(pattern,shift,svg,flags=re.S)
    if n!=1:raise RuntimeError('Cannot locate edge '+edge)
svg_path.write_text(svg,encoding='utf8')
for fmt in ['png','pdf']:
 subprocess.run(['inkscape',str(p/'OS07_seven_states.svg'),'--export-type='+fmt,'--export-dpi=200','--export-filename='+str(p/('OS07_seven_states.'+fmt))],check=True,stdout=subprocess.DEVNULL)
print('generated')
