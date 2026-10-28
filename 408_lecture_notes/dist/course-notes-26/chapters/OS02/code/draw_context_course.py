#!/usr/bin/env python3
"""Four exact states of Wangdao process-control slide's x++ example."""
from pathlib import Path
from html import escape
import subprocess
p=Path(__file__).resolve().parent.parent/'figures';p.mkdir(exist_ok=True)
w,h=1200,860
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#53798D"/></marker></defs>',
'<rect width="100%" height="100%" fill="white"/>',
'<g font-family="Noto Sans CJK SC, sans-serif" fill="#253B49">',
'<text x="600" y="40" text-anchor="middle" font-size="27" font-weight="bold">x++ 执行过程中保存和恢复现场</text>']
cards=[(30,75,'① P1 执行完指令3',['PC：指令4地址（下一条）','IR：指令3；CPU 通用寄存器 R = 2','P1 的内存：x = 1（尚未写回）']),
(635,75,'② 切出 P1',['PCB(P1) 保存 PC、PSW 和寄存器','其中 PC = 指令4地址，R = 2','P1 的内存仍为 x = 1']),
(30,455,'③ 另一个进程 P2 运行',['P2 使用自己的运行现场','CPU 通用寄存器可被 P2 改为 250','PCB(P1) 里保存的 R 仍为 2']),
(635,455,'④ 恢复 P1 并执行指令4',['从 PCB(P1) 恢复 PC、PSW、R','恢复时 PC = 指令4地址，R = 2','指令4将 R 写回：P1 内存 x = 2'])]
for x,y,title,lines in cards:
 svg += [f'<rect x="{x}" y="{y}" width="535" height="300" rx="16" fill="#F4F8FA" stroke="#8EAAB8" stroke-width="2"/>',f'<rect x="{x}" y="{y}" width="535" height="58" rx="16" fill="#DDEFF4"/>',f'<text x="{x+20}" y="{y+39}" font-size="25" font-weight="bold">{escape(title)}</text>']
 for i,line in enumerate(lines):svg.append(f'<text x="{x+25}" y="{y+118+i*57}" font-size="22">{escape(line)}</text>')
svg += ['<path d="M570,225 H625" stroke="#53798D" stroke-width="4" fill="none" marker-end="url(#arr)"/>',
'<path d="M900,382 V410 H300 V445" stroke="#53798D" stroke-width="4" fill="none" marker-end="url(#arr)"/>',
'<path d="M570,605 H625" stroke="#53798D" stroke-width="4" fill="none" marker-end="url(#arr)"/>',
'<text x="600" y="823" text-anchor="middle" font-size="20">PC 指向下一条指令；保存现场不等于把 P2 的寄存器值写入 P1</text>', '</g></svg>']
(p/'OS_context_switch_course.svg').write_text('\n'.join(svg),encoding='utf8')
for fmt in ['png','pdf']:
 subprocess.run(['inkscape',str(p/'OS_context_switch_course.svg'),'--export-type='+fmt,'--export-dpi=180','--export-filename='+str(p/('OS_context_switch_course.'+fmt))],check=True,stdout=subprocess.DEVNULL)
