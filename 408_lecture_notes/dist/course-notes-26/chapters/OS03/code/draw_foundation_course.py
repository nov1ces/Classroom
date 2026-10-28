#!/usr/bin/env python3
"""Redraw four OS memory-management teaching examples as editable SVG."""
from pathlib import Path
from html import escape
import subprocess

OUT=Path(__file__).resolve().parents[1]/'figures'
INK='#294958'; BLUE='#deedf5'; GREEN='#dfefe4'; ROSE='#f6e5ec'; YELLOW='#fff1ce'

def canvas(w,h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#547f96"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="white"/>',
            '<g font-family="Noto Sans CJK SC, sans-serif" font-size="21" fill="#294958">']

def box(out,x,y,w,h,lines,color=BLUE,size=21):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="#8da8b6"/>')
    for i,line in enumerate(lines):
        yy=y+h/2+(i-(len(lines)-1)/2)*27+7
        out.append(f'<text x="{x+w/2}" y="{yy}" text-anchor="middle" font-size="{size}">{escape(line)}</text>')

def text(out,x,y,s,size=21,anchor='start'):
    out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{escape(s)}</text>')

def line(out,x1,y1,x2,y2,arrow=False):
    out.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#547f96" stroke-width="2" fill="none"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

def save(name,out):
    out.append('</g></svg>');svg=OUT/(name+'.svg');svg.write_text('\n'.join(out))
    subprocess.run(['inkscape',str(svg),'--export-text-to-path','--export-type=pdf','--export-filename='+str(OUT/(name+'.pdf'))],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['inkscape',str(svg),'--export-type=png','--export-dpi=180','--export-filename='+str(OUT/(name+'.png'))],check=True,stdout=subprocess.DEVNULL)

out=canvas(1120,480)
for i,(heading,a,b,c) in enumerate([
    ('绝对装入','编译时知道装入位置','指令中已写物理地址179','直接访问物理地址179'),
    ('可重定位装入','装入前指令地址为79','装入时把地址改为179','运行时直接访问物理179'),
    ('动态运行时装入','装入前指令地址为79','装入后指令仍保持79','运行访存时 79＋100＝179')]):
    x=15+i*370;text(out,x+175,35,heading,23,'middle')
    box(out,x+20,55,310,70,[a]);box(out,x+20,175,310,70,[b],GREEN);box(out,x+20,295,310,75,[c],YELLOW)
    line(out,x+175,125,x+175,175,True);line(out,x+175,245,x+175,295,True)
text(out,560,435,'同一示例：起始物理地址100，变量在逻辑地址79',21,'middle')
save('OS03_loading_course',out)

out=canvas(1120,420)
text(out,280,32,'方法一：上、下限寄存器',23,'middle');text(out,840,32,'方法二：重定位与界地址寄存器',23,'middle')
box(out,25,65,210,75,['物理下限100','物理上限279']);box(out,305,65,210,75,['物理地址 180','100 ≤ 180 ≤ 279'],GREEN);line(out,235,102,305,102,True)
box(out,25,200,490,82,['合法物理空间 100～279','超出范围触发越界异常'],YELLOW)
box(out,600,65,210,75,['重定位寄存器100','最大逻辑地址179']);box(out,880,65,210,75,['逻辑地址80','80 ≤ 179'],GREEN);line(out,810,102,880,102,True)
box(out,600,200,490,82,['合法：100＋80＝物理地址180','越界：拒绝访问并触发异常'],YELLOW)
text(out,560,360,'若界地址字段保存长度180，则有效条件写为 0 ≤ 逻辑地址 < 180',20,'middle')
save('OS03_protection_course',out)

out=canvas(1120,600)
text(out,560,35,'32位进程虚拟映像（课件示意，具体布局随平台变化）',23,'middle')
text(out,85,90,'0xFFFFFFFF',20);text(out,85,190,'0xC0000000',20);text(out,85,347,'0x40000000',20);text(out,85,532,'0x08048000',20);text(out,85,565,'0x00000000',20)
box(out,250,65,330,110,['内核区：1 GiB','内核代码、数据与PCB'],BLUE)
box(out,250,175,330,90,['用户栈','局部变量、调用参数'],ROSE)
box(out,250,265,330,75,['共享库映射区','例如 printf 代码'],YELLOW)
box(out,250,340,330,75,['堆','malloc分配的数据'],GREEN)
box(out,250,415,330,55,['读写数据：全局／静态变量'],BLUE)
box(out,250,470,330,55,['只读代码／数据'],ROSE)
box(out,250,525,330,35,['低地址未使用区'],YELLOW,18)
text(out,650,135,'用户区与内核区通过地址边界区分',21)
text(out,650,200,'栈保存函数的运行现场与局部对象',21)
text(out,650,265,'库函数代码属于共享库映射区域',21)
text(out,650,330,'指针变量与它指向的堆对象须分开判断',21)
text(out,650,395,'全局及 static 变量属于静态存储期',21)
text(out,650,460,'宏在预处理阶段替换，不单独分配对象',21)
save('OS03_process_image_course',out)

out=canvas(1120,470)
text(out,310,38,'程序X的调用结构',23,'middle');text(out,840,38,'物理内存中的分区',23,'middle')
box(out,250,65,140,65,['A（main）','8 KB'])
box(out,105,190,140,65,['B','8 KB'],GREEN);box(out,395,190,140,65,['C','10 KB'],GREEN)
box(out,65,340,140,65,['D','12 KB'],ROSE);box(out,280,340,140,65,['E','4 KB'],ROSE);box(out,495,340,140,65,['F','10 KB'],ROSE)
line(out,320,130,175,190);line(out,320,130,465,190);line(out,175,255,135,340);line(out,465,255,350,340);line(out,465,255,565,340)
box(out,720,85,260,80,['固定区 A','8 KB'],BLUE);box(out,720,190,260,80,['覆盖区0：B 或 C','10 KB'],GREEN);box(out,720,295,260,80,['覆盖区1：D、E 或 F','12 KB'],ROSE)
text(out,850,430,'该安排共 8＋10＋12＝30 KB',22,'middle')
save('OS03_overlay_course',out)

out=canvas(1100,560)
text(out,550,35,'页0缺页：有空闲页框与需要置换',23,'middle')
box(out,300,65,500,72,['页0不驻留，后备位置为x','页1在框b；页2在框c且修改位为1'])
box(out,55,215,400,70,['存在空闲页框a'],GREEN)
box(out,645,215,400,70,['没有空闲页框'],ROSE)
line(out,420,137,255,215,True);line(out,680,137,845,215,True)
box(out,55,355,400,95,['页0从外存x调入页框a','页1、页2保持驻留'],YELLOW)
box(out,645,355,400,95,['页2写回外存z并撤销映射','页0从x调入页框c'],YELLOW)
line(out,255,285,255,355,True);line(out,845,285,845,355,True)
text(out,550,525,'I/O完成后更新页表，进程进入就绪，稍后重试原访存。',20,'middle')
save('OS03_fault_states_course',out)
