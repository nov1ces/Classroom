from pathlib import Path
from xml.sax.saxutils import escape
import subprocess
root=Path(__file__).resolve().parents[1]; out=root/'figures'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="670" viewBox="0 0 1800 670">', '<defs><marker id="alloc" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#35896d"/></marker><marker id="request" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#486c91"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#203640" font-size="25">']
def txt(x,y,s,size=25):svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(s)}</text>')
def arrow(x1,y1,x2,y2,kind):
 col='#35896d' if kind=='alloc' else '#486c91';svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{col}" stroke-width="4" marker-end="url(#{kind})"/>')
def circle(x,y,label):svg.append(f'<circle cx="{x}" cy="{y}" r="39" fill="#dcecf5" stroke="#64879d" stroke-width="2"/>');txt(x,y+9,label,26)
def panel(offset,title,scenario):
 svg.append(f'<rect x="{offset+8}" y="65" width="875" height="520" rx="8" fill="#fcfdfd" stroke="#b3c5cc"/>');txt(offset+445,40,title,27)
 for x,lab in [(offset+100,'R1'),(offset+660,'R2')]:
  svg.append(f'<rect x="{x}" y="230" width="170" height="105" rx="4" fill="#e2efdc" stroke="#6c9982" stroke-width="2"/>');txt(x+85,224,lab,25)
 for x,y in [(offset+130,260),(offset+130,310),(offset+205,285),(offset+690,270),(offset+760,295)]:svg.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#f6ad69" stroke="#b66d3a"/>')
 # Resource instance to process = allocation; process to resource = current request.
 for a in [(offset+130,260,offset+408,137),(offset+130,310,offset+418,148),(offset+205,285,offset+405,408),(offset+690,270,offset+455,410)]:arrow(*a,'alloc')
 arrow(offset+455,132,offset+655,247,'request')
 if scenario==2:arrow(offset+466,146,offset+653,263,'request')
 svg.append(f'<path d="M{offset+401},430 Q{offset+270},485 {offset+225},340" fill="none" stroke="#486c91" stroke-width="4" marker-end="url(#request)"/>')
 if scenario==2:arrow(offset+760,280,offset+778,153,'alloc');circle(offset+780,112,'P3')
 circle(offset+435,108,'P1');circle(offset+435,445,'P2')
 if scenario==1:txt(offset+445,552,'空闲 (R1,R2)=(0,1)：P1 → P2，图可完全化简',22)
 else:txt(offset+445,552,'P3 可先释放；随后 P1 与 P2 仍互相等待',22)
panel(0,'① P1 请求一个 R2：可化简',1);panel(900,'② P1 请求两个 R2：不可完全化简',2)
txt(900,632,'绿色：分配边（资源实例 → 进程）；蓝色：请求边（进程 → 资源类型）',24)
svg.append('</g></svg>')
for n,x in [(1,0),(2,900)]:
    # Split panels for legible A4 labels; edge directions and instance positions
    # remain exactly as in the editable complete two-panel source.
    content='\n'.join(line for line in svg if not line.startswith('<text x="900" y="632"'))
    content=content.replace('width="1800" height="670" viewBox="0 0 1800 670"',
                            f'width="900" height="670" viewBox="{x} 0 900 670"',1)
    name=f'OS02_course_deadlock_{n}';p=out/(name+'.svg');p.write_text(content,encoding='utf8')
    for ext in ('png','pdf'):
        args=['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))]
        if ext=='pdf':args.insert(2,'--export-text-to-path')
        else:args.append('--export-dpi=180')
        subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
