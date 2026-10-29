#!/usr/bin/env python3
"""Draw the steady-state timeline cases from Wangdao buffering slides.

The integer values are deliberately chosen demonstrations, not values from
the slides. Initial states and the order/roles of T, M and C follow them.
"""
from pathlib import Path
from html import escape
import subprocess

OUT=Path(__file__).resolve().parents[1]/'figures'
OUT.mkdir(exist_ok=True)

def chart(name,title,panels):
    width=1200;height=650
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="1200" height="650" fill="white"/>',
         '<g fill="#253d4a" font-family="Noto Sans CJK SC, sans-serif" font-size="23">',
         f'<text x="40" y="34" font-size="25" font-weight="bold">{escape(title)}</text>']
    for n,case in enumerate(panels):
        base=60+n*285;start=230;unit=46;end=18
        svg.append(f'<text x="40" y="{base+25}" font-size="22" font-weight="bold">{escape(case["title"])}</text>')
        for row,(label,events) in enumerate(case['rows']):
            y=base+48+row*50
            svg.append(f'<text x="215" y="{y+25}" text-anchor="end" font-size="20">{escape(label)}</text>')
            svg.append(f'<line x1="{start}" y1="{y+32}" x2="{start+unit*end}" y2="{y+32}" stroke="#aab6bf" stroke-width="1"/>')
            for a,b,word,color in events:
                svg.append(f'<rect x="{start+a*unit}" y="{y}" width="{(b-a)*unit}" height="32" rx="3" fill="{color}" stroke="#536f7e"/>')
                svg.append(f'<text x="{start+(a+b)*unit/2}" y="{y+23}" text-anchor="middle" font-size="18">{escape(word)}</text>')
        for t in case['ticks']:
            x=start+t*unit
            svg.append(f'<line x1="{x}" y1="{base+195}" x2="{x}" y2="{base+203}" stroke="#536f7e"/>')
            svg.append(f'<text x="{x}" y="{base+226}" text-anchor="middle" font-size="20">{t}</text>')
        svg.append(f'<text x="40" y="{base+258}" font-size="19">{escape(case["note"])}</text>')
    svg.append('</g></svg>');path=OUT/(name+'.svg');path.write_text('\n'.join(svg),encoding='utf-8')
    for ext in ['png','pdf']:
        args=['inkscape',str(path),'--export-type='+ext,'--export-filename='+str(OUT/(name+'.'+ext))]
        if ext=='png':args.append('--export-dpi=180')
        else:args.append('--export-text-to-path')
        subprocess.run(args,check=True)

BLUE='#dcecf4';GREEN='#dcefe4';YELLOW='#fff1cd'
def events(pairs,prefix,color):return [(a,b,prefix,color) for a,b in pairs]

chart('OS05_single_steady','单缓冲：工作区初始已满，系统缓冲区初始为空',[
 {'title':'T > C：示意取 T=5，C=3，M=1；周期 T+M=6',
  'rows':[('设备 → 缓冲区',events([(0,5),(6,11),(12,17)],'T',BLUE)),
          ('缓冲区 → 工作区',events([(5,6),(11,12),(17,18)],'M',GREEN)),
          ('CPU处理工作区',events([(0,3),(6,9),(12,15)],'C',YELLOW))],
  'ticks':[0,6,12,18],'note':'CPU在3–5等待输入；复制结束后系统缓冲区才可重新填入。'},
 {'title':'T < C：示意取 T=3，C=5，M=1；周期 C+M=6',
  'rows':[('设备 → 缓冲区',events([(0,3),(6,9),(12,15)],'T',BLUE)),
          ('缓冲区 → 工作区',events([(5,6),(11,12),(17,18)],'M',GREEN)),
          ('CPU处理工作区',events([(0,5),(6,11),(12,17)],'C',YELLOW))],
  'ticks':[0,6,12,18],'note':'缓冲区在3–5保持已满；复制须等CPU释放工作区。'}])

chart('OS05_double_steady','双缓冲：工作区初始为空，缓冲区1满、缓冲区2空',[
 {'title':'T > M+C：示意取 T=5，M=1，C=3；周期 T=5',
  'rows':[('设备 → 缓冲区2',events([(0,5),(10,15)],'T',BLUE)),
          ('设备 → 缓冲区1',events([(5,10)],'T',BLUE)),
          ('复制M / CPU处理C',[(0,1,'M1',GREEN),(1,4,'C',YELLOW),(5,6,'M2',GREEN),(6,9,'C',YELLOW),(10,11,'M1',GREEN),(11,14,'C',YELLOW)])],
  'ticks':[0,5,10,15],'note':'M1、M2分别表示从缓冲区1、2复制；设备可连续填入。'},
 {'title':'T < M+C：示意取 T=2，M=1，C=3；周期 M+C=4',
  'rows':[('设备 → 缓冲区2',events([(0,2),(5,7),(13,15)],'T',BLUE)),
          ('设备 → 缓冲区1',events([(2,4),(9,11)],'T',BLUE)),
          ('复制M / CPU处理C',[(0,1,'M1',GREEN),(1,4,'C',YELLOW),(4,5,'M2',GREEN),(5,8,'C',YELLOW),(8,9,'M1',GREEN),(9,12,'C',YELLOW),(12,13,'M2',GREEN),(13,16,'C',YELLOW)])],
  'ticks':[0,4,8,12,16],'note':'设备在4–5和7–9等待空缓冲区；复制与CPU处理依次进行。'}])
