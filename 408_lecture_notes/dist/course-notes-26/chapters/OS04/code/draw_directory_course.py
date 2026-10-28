from pathlib import Path
import html,subprocess
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="650" viewBox="0 0 1300 650">','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#547689"/></marker></defs>','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#243b46" font-size="25">']
def text(x,y,t,size=25,anchor='middle'):s.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{html.escape(t)}</text>')
def box(x,y,w,label,highlight=False):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="54" rx="6" fill="{ "#fff0cc" if highlight else "#e4eff4"}" stroke="#7194a4" stroke-width="2"/>');text(x+w/2,y+35,label,23)
def link(x1,y1,x2,y2):
 ym=(y1+y2)/2;s.append(f'<path d="M{x1},{y1} V{ym} H{x2} V{y2-4}" fill="none" stroke="#547689" stroke-width="2" marker-end="url(#a)"/>')
text(650,39,'课件目录结构：不同目录可以有同名文件',27)
link(650,124,220,190);link(650,124,650,190);link(650,124,1080,190)
link(220,244,110,315);link(220,244,320,315);link(650,244,550,315);link(650,244,750,315)
link(550,369,455,440);link(550,369,645,440)
box(550,70,200,'根目录',True);box(130,190,180,'qianlong');box(560,190,180,'照片',True);box(985,190,190,'对账单4')
box(20,315,180,'Test');box(230,315,180,'demo');box(460,315,180,'2015-08',True);box(670,315,180,'demo')
box(360,440,190,'自拍.jpg',True);box(560,440,190,'自拍2.png')
text(650,565,'从根出发：读根目录 → 照片目录 → 2015-08目录，课件模型下共3次目录读盘。',23)
text(650,608,'若照片目录已缓存且作为当前目录，只需再读取2015-08目录，课件模型下为1次。',23)
s.append('</g></svg>');p=out/'OS_directory_course.svg';p.write_text('\n'.join(s))
for typ,args in [('png',['--export-dpi=180']),('pdf',['--export-text-to-path'])]:subprocess.run(['inkscape',str(p),'--export-type='+typ,*args,'--export-filename='+str(p.with_suffix('.'+typ))],check=True,stdout=subprocess.DEVNULL)
