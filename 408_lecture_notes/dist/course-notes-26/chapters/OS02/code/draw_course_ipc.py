from pathlib import Path
from xml.sax.saxutils import escape
import subprocess
out=Path(__file__).resolve().parent.parent/'figures';out.mkdir(exist_ok=True)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="900" viewBox="0 0 1500 900">','<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#526f80"/></marker></defs>','<rect width="1500" height="900" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#203640" font-size="23">']
def txt(x,y,t,size=23):svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(t)}</text>')
def box(x,y,w,h,label,fill):
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#8ca2ae" stroke-width="2"/>');txt(x+w/2,y+h/2+8,label)
def arrow(x1,y1,x2,y2):svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#526f80" stroke-width="3" fill="none" marker-end="url(#arr)"/>')
def panel(x,y,indirect,stage):
 svg.append(f'<rect x="{x}" y="{y}" width="460" height="350" rx="12" fill="#fafcfd" stroke="#bac9d0"/>')
 title=['① 发送前','② 消息进入中间实体','③ 接收后'][stage];txt(x+230,y+37,title,26)
 top='P地址空间：msg'
 bottom='Q地址空间'+('：msg' if stage==2 else '')
 middle=('信箱 A'+('：msg' if stage==1 else '') if indirect else 'Q 的消息队列'+('：msg' if stage==1 else ''))
 box(x+55,y+65,350,57,top,'#dcecf5');box(x+55,y+155,350,57,middle,'#fff0dc');box(x+55,y+245,350,57,bottom,'#e3efdb')
 if stage==1:arrow(x+230,y+124,x+230,y+150)
 if stage==2:arrow(x+230,y+214,x+230,y+240)
 txt(x+230,y+332,('send(A,msg) / receive(A,&msg)' if indirect else 'send(Q,msg) / receive(P,&msg)'),20)
txt(750,40,'直接通信：进程 P 向进程 Q 发送；Q 从自己的消息队列接收',28)
for i in range(3):panel(35+i*480,55,False,i)
txt(750,470,'间接通信：进程 P 向信箱 A 发送；Q 从信箱 A 接收',28)
for i in range(3):panel(35+i*480,485,True,i)
txt(750,875,'msg 随发送进入消息队列或信箱，接收后交给 Q；空队列的等待语义取决于接口。',23)
svg.append('</g></svg>');p=out/'OS02_course_ipc.svg';p.write_text('\n'.join(svg),encoding='utf8')
for ext in ('png','pdf'):
 args=['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/('OS02_course_ipc.'+ext))]
 if ext=='pdf':args.insert(2,'--export-text-to-path')
 else:args.append('--export-dpi=180')
 subprocess.run(args,check=True)
