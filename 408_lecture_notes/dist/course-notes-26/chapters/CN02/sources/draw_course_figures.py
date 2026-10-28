from pathlib import Path
import html,subprocess
R=Path(__file__).resolve().parents[2]
def save(ch,stem,body,w=960,h=500):
 p=R/ch/'figures'/f'{stem}.svg'
 p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="#466c82"/></marker></defs><g font-family="Noto Sans CJK SC,sans-serif" font-size="18" fill="#243743">'+''.join(body)+'</g></svg>')
 for ext in ['png','pdf']:subprocess.run(['inkscape',str(p),f'--export-type={ext}',f'--export-filename={p.with_suffix("."+ext)}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def text(x,y,s,**kw):return f'<text x="{x}" y="{y}" '+''.join(f'{k}="{v}" ' for k,v in kw.items())+'>'+html.escape(s)+'</text>'
bits=[int(x) for x in '11010001']; body=[text(30,30,'11010001：位边界与半位电平（差分编码初始为高）')]
for i,b in enumerate(bits):body.append(text(205+i*85,60,str(b)))
prev=1;nrzi=[];dm=[]
for b in bits:
 if b==0:prev=1-prev
 nrzi.extend([prev,prev])
prev=1
for b in bits:
 if b==0:prev=1-prev
 dm.extend([prev,1-prev]);prev=1-prev
rows=[('NRZ',[a for b in bits for a in [b,b]]),('RZ',[a for b in bits for a in [b,0.5]]),('NRZI',nrzi),('曼彻斯特',[a for b in bits for a in ([0,1] if b==0 else [1,0])]),('差分曼彻斯特',dm)]
for row,(label,levels) in enumerate(rows):
 y=100+row*78;body.append(text(15,y+6,label))
 for i in range(9):body.append(f'<line x1="{180+i*85}" y1="{y-22}" x2="{180+i*85}" y2="{y+22}" stroke="#d7dde1" stroke-dasharray="4 3"/>')
 pts=[]
 for i,a in enumerate(levels):
  x=180+i*42.5;yy=y+(0.5-a)*32
  if pts:pts.append((x,yy))
  pts.extend([(x,yy),(x+42.5,yy)])
 body.append('<polyline points="'+' '.join(f'{x},{yy}' for x,yy in pts)+'" fill="none" stroke="#466c82" stroke-width="2.5"/>')
body.append(text(180,490,'曼彻斯特：上跳0、下跳1；差分曼彻斯特：起点跳0、不跳1'))
save('CN02','CN_course_five_codes',body,960,515)
body=[text(25,30,'四组数据经 A→B→C→D：发送2 ms，传播1 ms，中间处理0.5 ms')]
colors=['#c5dfec','#d4e5cf','#f2dfc4','#e5d0df']
for k,name in enumerate(['A→B','B→C','C→D']):
 y=100+k*105;body.append(text(15,y+28,name))
 body.append(f'<line x1="100" y1="{y+45}" x2="900" y2="{y+45}" stroke="#aaa"/>')
 for j in range(4):
  st=[0,3.5,7][k]+2*j;x=100+st*45
  body.append(f'<rect x="{x}" y="{y}" width="90" height="42" fill="{colors[j]}" stroke="#678294"/>');body.append(text(x+18,y+27,f'组{j+1}'))
for t in range(0,18,2):body.append(text(92+t*45,385,str(t)))
body += [text(785,410,'时间 / ms'),text(100,450,'D 收齐各组：10、12、14、16 ms（各发送结束后再传播1 ms）')]
save('CN01','CN_course_store_forward',body,960,475)
