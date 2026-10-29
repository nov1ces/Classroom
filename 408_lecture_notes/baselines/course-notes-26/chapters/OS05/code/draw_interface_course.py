from pathlib import Path
from html import escape
import subprocess

out=Path(__file__).resolve().parents[1]/'figures'
svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#476b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="25" fill="#243b49">''']
def text(x,y,value,**kw):
    props=' '.join(f'{k.replace("_","-")}="{escape(str(v))}"' for k,v in kw.items())
    svg.append(f'<text x="{x}" y="{y}" {props}>{escape(value)}</text>')
def rect(x,y,w,h,color='#eef4f7'):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" stroke="#7d9cab" stroke-width="2"/>')
def arrow(x1,y1,x2,y2):
    svg.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#476b80" stroke-width="2.5" marker-end="url(#arrow)"/>')
text(25,38,'应用程序接口与标准驱动接口',font_size='30',font_weight='bold')
text(25,85,'用户层 I/O 软件',font_weight='bold')
for x,title,details,color in [(25,'字符设备接口',['get / put','例：键盘、打印机','按字符处理'], '#e3f1e8'),(415,'块设备接口',['read / write','seek：改变读写位置','例：磁盘'], '#f6e8f0'),(805,'网络设备接口',['socket：指定协议','bind：绑定本地端口','connect / read / write'], '#fff1c9')]:
    rect(x,105,350,156,color);text(x+175,139,title,text_anchor='middle',font_weight='bold')
    for i,line in enumerate(details):text(x+18,177+32*i,line,font_size='22')
    arrow(x+175,264,600,310)
rect(305,315,590,68);text(600,358,'设备独立软件',text_anchor='middle',font_weight='bold')
arrow(600,383,600,420)
rect(305,425,590,67,'#e3f1e8');text(600,468,'统一的设备驱动程序接口',text_anchor='middle',font_weight='bold')
text(600,526,'例如：相同 read(p1, p2, p3) 接口约定',text_anchor='middle',font_size='22')
arrow(450,540,260,590);arrow(750,540,940,590)
rect(100,595,320,68);rect(780,595,320,68)
text(260,638,'设备驱动程序 A',text_anchor='middle');text(940,638,'设备驱动程序 B',text_anchor='middle')
arrow(260,665,260,713);arrow(940,665,940,713)
rect(100,717,320,70,'#fff1c9');rect(780,717,320,70,'#fff1c9')
text(260,759,'罗技设备（课件示例）',text_anchor='middle',font_size='22');text(940,759,'雷蛇设备（课件示例）',text_anchor='middle',font_size='22')
text(600,824,'中断处理程序响应设备完成或异常；厂商按接口实现对应驱动。',text_anchor='middle',font_size='22')
svg.append('</g></svg>');path=out/'OS_interface_layers.svg';path.write_text('\n'.join(svg))
for kind in ('pdf','png'):
    args=['inkscape',str(path),'--export-type='+kind,'--export-filename='+str(path.with_suffix('.'+kind))]
    args.insert(2,'--export-text-to-path' if kind=='pdf' else '--export-dpi=180')
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
