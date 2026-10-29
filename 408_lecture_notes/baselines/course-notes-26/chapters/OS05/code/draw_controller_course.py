from pathlib import Path
from html import escape
import subprocess

out=Path(__file__).resolve().parents[1]/'figures'
s=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 Z" fill="#476b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="24" fill="#243b49">''']
def t(x,y,a,**kw):
 props=' '.join(f'{k.replace("_","-")}="{escape(str(v))}"' for k,v in kw.items());s.append(f'<text x="{x}" y="{y}" {props}>{escape(a)}</text>')
def box(x,y,w,h,label,color='#e3f1e8'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="#7d9cab" stroke-width="2"/>');t(x+w/2,y+h/2+8,label,text_anchor='middle')
def line(x1,y1,x2,y2,two=False):
 s.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#476b80" stroke-width="3" marker-end="url(#a)"'+(' marker-start="url(#a)"' if two else '')+'/>')
t(600,38,'I/O控制器的组成',text_anchor='middle',font_size='32',font_weight='bold')
s.append('<rect x="280" y="70" width="650" height="420" rx="8" fill="#eff5fa" stroke="#7d9cab" stroke-width="2"/>')
t(605,102,'I/O控制器',text_anchor='middle',font_weight='bold')
box(30,135,155,300,'CPU','#e7edf5')
for y,name in [(135,'数据寄存器'),(220,'控制寄存器'),(305,'状态寄存器')]:box(305,y,180,65,name,'#f9e6d7')
box(550,250,170,85,'I/O逻辑','#eee6f6')
box(760,145,140,72,'设备接口1');box(760,335,140,72,'设备接口 i')
line(185,165,305,165,True);t(215,151,'数据总线',font_size='20')
line(185,250,305,250);t(213,236,'控制信息',font_size='20')
line(305,335,185,335);t(213,321,'状态信息',font_size='20')
line(185,400,550,400);t(220,390,'地址线与控制线',font_size='20')
line(485,165,550,250,True);line(485,250,550,292);line(550,310,485,335)
line(720,270,760,181,True);line(720,320,760,371,True)
for y in (155,345):
 line(900,y+13,1060,y+13,True);t(1070,y+20,'数据',font_size='21')
 line(1060,y+38,900,y+38);t(1070,y+45,'状态',font_size='21')
 line(900,y+63,1060,y+63);t(1070,y+70,'控制',font_size='21')
t(30,540,'CPU—控制器接口：寄存器与总线',font_size='22');t(30,580,'I/O逻辑：识别命令、译码地址并控制设备接口',font_size='22');t(30,620,'控制器—设备接口：交换数据、接收状态并发送控制信号',font_size='22')
s.append('</g></svg>');p=out/'OS_controller_course.svg';p.write_text('\n'.join(s))
for kind in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+kind,'--export-filename='+str(p.with_suffix('.'+kind))];args.insert(2,'--export-text-to-path' if kind=='pdf' else '--export-dpi=180');subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
