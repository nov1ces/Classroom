from pathlib import Path
from html import escape
import subprocess,math
out=Path(__file__).resolve().parents[1]/'figures'/'DS05_huffman_course'
a=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500">','<rect width="100%" height="100%" fill="white"/>']
def text(x,y,s,size=20):a.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Noto Sans CJK SC,sans-serif" font-size="{size}" fill="#223644">{escape(str(s))}</text>')
def tree(nodes,edges):
 for u,v,digit in edges:
  x,y=nodes[u][:2];xx,yy=nodes[v][:2];dx=xx-x;dy=yy-y;length=math.hypot(dx,dy)
  a.append(f'<path d="M{x+22*dx/length},{y+22*dy/length} L{xx-22*dx/length},{yy-22*dy/length}" fill="none" stroke="#6a8794" stroke-width="2"/>')
  if digit is not None:text((x+xx)/2+(10 if dx<0 else -10),(y+yy)/2,digit,17)
 for k,(x,y,label,leaf) in nodes.items():
  a.append(f'<circle cx="{x}" cy="{y}" r="24" fill="'+('#dfefe6' if leaf else '#ddeff5')+'" stroke="#6a8794"/>');text(x,y+7,label)
text(280,30,'权值1、3、2、2、7：WPL＝31',22)
ns={'r':(250,78,15,False),'d':(75,165,'d:7',True),'n8':(340,165,8,False),'b':(445,250,'b:3',True),'n5':(275,250,5,False),'e':(345,335,'e:2',True),'n3':(220,335,3,False),'a':(165,420,'a:1',True),'c':(275,420,'c:2',True)}
tree(ns,[(u,v,None) for u,v in [('r','d'),('r','n8'),('n8','b'),('n8','n5'),('n5','e'),('n5','n3'),('n3','a'),('n3','c')]])
text(280,480,'合并权值：3＋5＋8＋15＝31',20)
text(825,30,'100题答案编码：WPL＝130 bit',22)
ns={'r':(780,78,100,False),'c':(650,165,'C:80',True),'n20':(900,165,20,False),'a':(805,270,'A:10',True),'n10':(990,270,10,False),'d':(935,385,'D:2',True),'b':(1050,385,'B:8',True)}
tree(ns,[('r','c',0),('r','n20',1),('n20','a',0),('n20','n10',1),('n10','d',0),('n10','b',1)])
text(825,445,'C＝0；A＝10；D＝110；B＝111',20)
text(825,480,'固定2位：200 bit；平均码长：1.3 bit',19)
a.append('</svg>');out.with_suffix('.svg').write_text('\n'.join(a))
for ext in ['png','pdf']:
 cmd=['inkscape',str(out.with_suffix('.svg')),'--export-type='+ext,'--export-filename='+str(out.with_suffix('.'+ext))]
 cmd+=['--export-dpi=180'] if ext=='png' else ['--export-text-to-path']
 subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
