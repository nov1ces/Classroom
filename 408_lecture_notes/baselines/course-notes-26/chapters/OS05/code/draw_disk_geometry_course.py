from pathlib import Path
from html import escape
from math import cos,sin,pi
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 Z" fill="#476b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="24" fill="#243b49">''']
def t(x,y,a,**kw):
 props=' '.join(f'{k.replace("_","-")}="{escape(str(v))}"' for k,v in kw.items());s.append(f'<text x="{x}" y="{y}" {props}>{escape(a)}</text>')
t(600,36,'盘面、磁头与柱面（王道课件示例）',text_anchor='middle',font_size='30',font_weight='bold')
x=390; ys=[165,275,385,495]
for n,y in enumerate(ys):
 s.append(f'<ellipse cx="{x}" cy="{y}" rx="240" ry="44" fill="{["#dcecf4","#f8e8da"][n%2]}" stroke="#6694a8" stroke-width="2"/>')
 for radius in [100,130,160,190,220]:
  ry=radius*44/240;color='#d49b35' if radius==160 else '#76a395';width=4 if radius==160 else 1.6
  s.append(f'<ellipse cx="{x}" cy="{y}" rx="{radius}" ry="{ry:.2f}" fill="none" stroke="{color}" stroke-width="{width}"/>')
 for k in range(8):
  angle=2*pi*k/8;xx=x+240*cos(angle);yy=y+44*sin(angle)
  s.append(f'<path d="M{x},{y} L{xx:.2f},{yy:.2f}" stroke="#abc3c8" stroke-width="1.2"/>')
 s.append(f'<ellipse cx="{x}" cy="{y}" rx="70" ry="13" fill="white" stroke="#6694a8"/>')
 t(30,y+8,f'{n}号盘面')
 s.append(f'<path d="M785,{y-22} H544" stroke="#344b59" stroke-width="5"/><rect x="538" y="{y-32}" width="22" height="25" fill="#344b59"/>')
 s.append(f'<path d="M549,{y-6} L549,{y+3}" stroke="#344b59" stroke-width="3" marker-end="url(#a)"/>')
s.append('<path d="M785,130 V510" stroke="#344b59" stroke-width="5"/>')
s.append('<path d="M230,134 V520 M550,134 V520" stroke="#d49b35" stroke-width="2" stroke-dasharray="7 6"/>')
s.append('<path d="M610,105 H770" stroke="#bb5160" stroke-width="3" marker-start="url(#a)" marker-end="url(#a)"/>')
t(610,86,'磁臂共同移动方向',font_size='20')
t(815,160,'每个盘面对应一个磁头',font_size='22');t(815,200,'磁头连接同一磁臂',font_size='22');t(815,238,'因而共同进退',font_size='22')
t(815,345,'同半径磁道形成柱面',font_size='22');t(815,382,'金色磁道标出一个柱面',font_size='22')
t(50,585,'一个盘片可以有两个盘面；图中示出0～3号四个盘面。',font_size='22')
t(50,620,'按柱面号移动磁臂，选择盘面对应磁头，等待目标扇区转至磁头下。',font_size='22')
t(50,655,'教学模型按（柱面号，盘面号，扇区号）定位；具体设备可能对外提供LBA。',font_size='22')
s.append('</g></svg>');p=out/'OS_disk_geometry_course.svg';p.write_text('\n'.join(s))
for kind in ('png','pdf'):
 args=['inkscape',str(p),'--export-type='+kind,'--export-filename='+str(p.with_suffix('.'+kind))];args.insert(2,'--export-text-to-path' if kind=='pdf' else '--export-dpi=180');subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
