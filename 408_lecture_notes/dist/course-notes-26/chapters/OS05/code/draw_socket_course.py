from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800" viewBox="0 0 1000 800"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#476b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC, sans-serif" font-size="22" fill="#243b49">''']
def text(x,y,t,**kw):
 a=' '.join(f'{k.replace("_","-")}="{escape(str(v))}"' for k,v in kw.items());svg.append(f'<text x="{x}" y="{y}" {a}>{escape(t)}</text>')
def box(x,y,w,h,label,fill='#f6f9fa'):
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="#7d9cab" stroke-width="2"/>');text(x+w/2,y+h/2+7,label,text_anchor='middle')
def arrow(x1,y1,x2,y2):svg.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#476b80" stroke-width="3" marker-end="url(#ar)"/>')
for off,phase in [(0,1),(395,2)]:
 text(20,off+30,'① 发送：P1写入套接字' if phase==1 else '② 接收：中断唤醒后，P3读取',font_weight='bold')
 for x,host,ip in [(30,'主机1','117.154.xxx.xxx'),(540,'主机2','168.98.xxx.xxx')]:
  svg.append(f'<rect x="{x}" y="{off+45}" width="430" height="267" fill="none" stroke="#839ca8" stroke-width="2"/>')
  text(x+8,off+70,host+'　'+ip,font_weight='bold')
  text(x+8,off+100,'用户空间')
  text(x+8,off+203,'内核空间')
  box(x+25,off+111,105,50,'P1 · fd' if host=='主机1' else 'P3 · fd','#dff0e6')
  if host=='主机1':box(x+285,off+111,105,50,'P2')
  box(x+135,off+214,190,52,'socket' if host=='主机1' else 'socket : 6666','#dff0e6')
  box(x+145,off+328,170,43,'网卡','#e6eff6')
  arrow(x+77,off+162,x+180,off+214)
  if host=='主机2':arrow(x+230,off+327,x+230,off+267)
  else:arrow(x+230,off+267,x+230,off+327)
 text(385,off+386,'TCP / IP 网络',font_size='20')
 arrow(345,off+349,655,off+349)
 if phase==1:
  box(185,off+111,105,50,'数据','#fff1c9');arrow(235,off+162,265,off+214)
  text(30,off+386,'write → 设备无关层 → 网卡驱动',font_size='18')
 else:
  box(700,off+111,105,50,'数据','#fff1c9');arrow(755,off+214,755,off+162)
  text(546,off+386,'网卡中断 → 驱动处理并唤醒 → read',font_size='18')
svg.append('</g></svg>')
p=out/'OS_socket_course.svg';p.write_text('\n'.join(svg))
for kind in ('png','pdf'):
 args=['inkscape',str(p),'--export-type='+kind,'--export-filename='+str(p.with_suffix('.'+kind))]
 if kind=='pdf':args.insert(2,'--export-text-to-path')
 else:args.insert(2,'--export-dpi=180')
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
