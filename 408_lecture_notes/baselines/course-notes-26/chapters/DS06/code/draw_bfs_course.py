from pathlib import Path
from html import escape
import subprocess,math
out=Path(__file__).resolve().parents[1]/'figures'/'DS06_bfs_course'
a=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="410" viewBox="0 0 1100 410">','<rect width="100%" height="100%" fill="white"/>']
def text(x,y,s,size=20):a.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Noto Sans CJK SC,sans-serif" font-size="{size}" fill="#223644">{escape(str(s))}</text>')
def draw(nodes,edges,tree):
 for u,v in edges:
  x,y=nodes[u];xx,yy=nodes[v];dx=xx-x;dy=yy-y;l=math.hypot(dx,dy);col='#b67f99' if tuple(sorted((u,v))) in tree else '#8ca2ae'
  a.append(f'<path d="M{x+22*dx/l},{y+22*dy/l} L{xx-22*dx/l},{yy-22*dy/l}" fill="none" stroke="{col}" stroke-width="3"/>')
 for k,(x,y) in nodes.items():
  a.append(f'<circle cx="{x}" cy="{y}" r="23" fill="'+('#fff1b4' if k==2 else '#ddeff5')+'" stroke="#6a8794"/>');text(x,y+7,k)
text(270,30,'原无向图：以2为源点',22)
ns={1:(65,145),2:(195,145),3:(325,145),4:(455,145),5:(65,295),6:(195,295),7:(325,295),8:(455,295)}
tree={tuple(sorted(x)) for x in [(2,1),(2,6),(1,5),(6,3),(6,7),(3,4),(7,8)]}
draw(ns,[(1,2),(1,5),(2,6),(3,4),(3,6),(3,7),(4,7),(4,8),(6,7),(7,8)],tree)
text(270,380,'粉色边为首次发现各结点的树边',19)
text(820,30,'BFS生成树：同层按编号访问',22)
ns={2:(815,85),1:(665,170),6:(895,170),5:(665,255),3:(815,255),7:(995,255),4:(815,340),8:(995,340)}
draw(ns,[(2,1),(2,6),(1,5),(6,3),(6,7),(3,4),(7,8)],tree)
text(820,395,'2到8：2 → 6 → 7 → 8，长度3',19)
a.append('</svg>');out.with_suffix('.svg').write_text('\n'.join(a))
for ext in ['png','pdf']:
 cmd=['inkscape',str(out.with_suffix('.svg')),'--export-type='+ext,'--export-filename='+str(out.with_suffix('.'+ext))]
 cmd+=['--export-dpi=180'] if ext=='png' else ['--export-text-to-path'];subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
