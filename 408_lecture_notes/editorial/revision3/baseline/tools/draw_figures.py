#!/usr/bin/env python3
"""Editable SVG teaching figures. Inkscape exports the same sources to PNG/PDF."""
from pathlib import Path
from xml.sax.saxutils import escape
import json, math, subprocess

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures'
DATA=json.loads((FIG/'model_data.json').read_text())
INK='#243746'; ACCENT='#315f78'; WAIT='#79532e'; PALE='#f1f4f5'

class SVG:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9" fill="#243746"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="Noto Sans CJK SC, sans-serif" fill="#243746" font-size="22">']
    def text(self,x,y,s,size=22,anchor='middle',color=INK,weight='normal'):
        self.a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(s))}</text>')
    def line(self,x1,y1,x2,y2,dash=False,arrow=False):
        self.a.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def rect(self,x,y,w,h,fill=PALE,dash=False):
        self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{INK}" stroke-width="1.6"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def circle(self,x,y,r=32,fill=PALE):
        self.a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
    def save(self,name):
        self.a.extend(['</g>','</svg>'])
        p=FIG/f'{name}.svg';p.write_text('\n'.join(self.a))
        subprocess.run(['inkscape',str(p),'--export-type=png','--export-dpi=190',f'--export-filename={FIG/name}.png'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['inkscape',str(p),'--export-type=pdf',f'--export-filename={FIG/name}.pdf'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def lost():
    s=SVG(1000,415)
    for x,label in zip([65,300,615,870],['次序','进程 A','进程 B','共享 x']):s.text(x,36,label,23,weight='bold')
    rows=[('1','读 x：rA=0','',0),('2','','读 x：rB=0',0),('3','rA=rA+1=1','',0),('4','','rB=rB+1=1',0),('5','写 x=rA','',1),('6','','写 x=rB',1)]
    for i,row in enumerate(rows):
        y=88+i*54;s.line(25,y+15,970,y+15)
        for x,t in zip([65,300,615,870],row):s.text(x,y,t)
    s.save('F01_lost_update')

def trace():
    s=SVG(1000,405)
    for x,label in zip([155,365,595,850],['操作（初值 2）','操作后 S.value','等待队列','本次唤醒']):s.text(x,36,label,22,weight='bold')
    for i,row in enumerate(DATA['signed_trace']):
        y=90+i*51;s.line(30,y+14,970,y+14)
        actor,op=row['action'].split(':')
        for x,t in zip([155,365,595,850],[f'{actor} 执行 {op}',row['value'],' → '.join(row['queue']) or '空',row['wake'] or '无']):s.text(x,y,t)
    s.save('F02_signed_semaphore')

def dag():
    s=SVG(1000,355)
    pts={'A':(100,80),'B':(100,250),'C':(380,165),'D':(680,70),'E':(680,250),'F':(900,250)}
    for a,b in DATA['precedence']['edges']:
        x,y=pts[a];u,v=pts[b];dx,dy=u-x,v-y;n=math.hypot(dx,dy)
        s.line(x+dx/n*34,y+dy/n*34,u-dx/n*37,v-dy/n*37,arrow=True)
    for name,(x,y) in pts.items():s.circle(x,y);s.text(x,y+8,name,26,weight='bold')
    s.text(500,332,'T1：A、E、F 顺序执行；T2：B、C、D 顺序执行',21)
    s.save('F03_precedence_2022')

def buffer():
    s=SVG(1000,310)
    s.rect(35,92,235,125);s.text(152,130,'生产者',25,weight='bold');s.text(152,172,'P(empty) → 放入',20)
    s.rect(730,92,235,125);s.text(848,130,'消费者',25,weight='bold');s.text(848,172,'P(full) → 取出',20)
    for i in range(4):s.rect(350+i*74,111,65,65,fill='white');s.text(382+i*74,151,f'槽{i}',18)
    s.text(500,216,'单次缓冲操作由 mutex 保护',21)
    s.line(230,60,785,60,arrow=True);s.text(500,43,'放入完成后 V(full)：发布产品',21)
    s.line(785,263,230,263,arrow=True);s.text(500,294,'取出完成后 V(empty)：归还空槽',21)
    s.save('F04_buffer_permissions')

def deadlock():
    s=SVG(1000,290)
    s.rect(40,90,300,110);s.text(190,126,'消费者 C',25,weight='bold');s.text(190,165,'已持有 mutex；阻塞于 full',19)
    s.rect(660,90,300,110);s.text(810,126,'生产者 P',25,weight='bold');s.text(810,165,'阻塞于 mutex',21)
    s.line(340,105,655,105,dash=True,arrow=True);s.text(500,80,'C 等 P 放入产品',21)
    s.line(660,190,345,190,dash=True,arrow=True);s.text(500,231,'P 等 C 释放 mutex',21)
    s.text(500,275,'初始缓冲区为空；错误顺序：先 P(mutex)，再等待产品',20)
    s.save('F05_buffer_deadlock')

def readers():
    s=SVG(1000,340)
    xs=lambda t:150+t*105
    for t in range(8):s.line(xs(t),42,xs(t),250,dash=True);s.text(xs(t),282,str(t),18)
    for i,(name,a,b) in enumerate([('读者 R1',1,4),('读者 R2',2,5),('写者 W',5,7)]):
        y=65+i*75;s.text(18,y+21,name,22,anchor='start');s.rect(xs(a),y,xs(b)-xs(a),37,fill=PALE)
    s.line(xs(3),235,xs(5),235,dash=True,arrow=True);s.text(xs(4),221,'W 等待读者组退出',19)
    s.text(500,307,'第一个读者取得 rw；最后一个读者归还 rw',21)
    s.save('F06_readers_group')

def dining():
    s=SVG(1000,405);pts={}
    for i in range(5):
        a=-math.pi/2+i*2*math.pi/5;pts[i]=(350+150*math.cos(a),190+150*math.sin(a))
    for i in range(5):
        x,y=pts[i];u,v=pts[(i+1)%5];dx,dy=u-x,v-y;n=math.hypot(dx,dy)
        s.line(x+dx/n*40,y+dy/n*40,u-dx/n*45,v-dy/n*45,dash=True,arrow=True)
    for i,(x,y) in pts.items():s.circle(x,y,39);s.text(x,y+7,f'P{i}',24)
    s.text(740,110,'各 Pi 已拿到 Ci',24,weight='bold')
    s.text(740,157,'仍等待 C(i+1) mod 5',23)
    s.text(740,215,'虚线箭头：等待下一人',21)
    s.text(740,255,'环中无人能执行释放',21)
    s.text(500,385,'“最多 4 人申请”限制进入竞争的人数；并非同时吃饭的人数',21)
    s.save('F07_philosopher_wait_cycle')

def monitor():
    s=SVG(1000,365)
    s.text(200,35,'等待者 T1',24,weight='bold');s.text(760,35,'改变条件者 T2',24,weight='bold')
    left=[('持 m，检查条件为假',60),('wait(cv,m)：入队并释放 m',130),('重新取得 m，再检查条件',285)]
    right=[('取得 m，修改共享状态',160),('signal(cv)，随后释放 m',225)]
    for t,y in left:s.rect(25,y,380,48);s.text(215,y+31,t,20)
    for t,y in right:s.rect(590,y,380,48);s.text(780,y+31,t,20)
    s.line(405,155,585,183,arrow=True);s.text(505,124,'让出锁',19)
    s.line(590,250,410,306,dash=True,arrow=True);s.text(500,277,'通知后竞争锁',19)
    s.text(500,356,'本图采用 Mesa / POSIX 式通知语义：通知不把锁立即转交给等待者',20)
    s.save('F08_condition_wait')

if __name__=='__main__':
    FIG.mkdir(exist_ok=True)
    for draw in [lost,trace,dag,buffer,deadlock,readers,dining,monitor]:draw()
    print('8 SVG sources and matching PNG/PDF exports written')
