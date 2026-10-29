from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parents[1]/'figures'
s=['''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="570" viewBox="0 0 1100 570"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#476b80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="22" fill="#243b49">''']
def txt(x,y,t,**kw):
 a=' '.join(f'{k.replace("_","-")}="{escape(str(v))}"' for k,v in kw.items());s.append(f'<text x="{x}" y="{y}" {a}>{escape(t)}</text>')
def box(x,y,w,h,t,color='#e4eef3'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#6c8c9d" stroke-width="2"/>');
 for i,line in enumerate(t.split('|')):txt(x+w/2,y+h/2+7+(i-(len(t.split('|'))-1)/2)*24,line,text_anchor='middle',font_size='19')
txt(20,32,'① 原始磁盘与物理格式化',font_weight='bold');box(30,48,1040,43,'磁盘原始空间','#f5f7f8')
txt(30,123,'物理格式化：划分扇区、检测坏扇区，并可用备用扇区替换（数量示意）。',font_size='20')
for i in range(20):box(30+52*i,137,52,45,('备用' if i>=17 else ('坏' if i in (12,13) else '扇区')),('#dcefe4' if i>=17 else ('#bac4ca' if i in (12,13) else '#f5f7f8')))
txt(20,220,'② 划分卷：主引导记录与三个分区',font_weight='bold')
for x,w,t,c in [(30,170,'主引导记录|MBR','#dfe5e8'),(200,260,'C:','#dcefe4'),(460,260,'D:','#dcefe4'),(720,350,'E:','#dcefe4')]:box(x,235,w,55,t,c)

txt(20,338,'③ 对C卷逻辑格式化：文件系统中的区域示例',font_weight='bold')
for x,w,t,c in [(30,120,'引导块','#e1e6e8'),(150,125,'超级块','#e1e6e8'),(275,190,'空闲空间管理|如位示图','#e1e6e8'),(465,150,'i结点区','#e1e6e8'),(615,115,'根目录','#e1e6e8'),(730,340,'其他文件、目录','#ffffff')]:box(x,350,w,70,t,c)
txt(30,460,'灰色表示初始化后已有管理数据；白色区域表示尚未存放相应数据。',font_size='20')
txt(30,510,'实际布局随文件系统和磁盘分区方式变化；MBR与卷内引导块职责不同。',font_size='20')
s.append('</g></svg>');p=out/'OS_filesystem_layout.svg';p.write_text('\n'.join(s))
for typ in ('png','pdf'):
 a=['inkscape',str(p),'--export-type='+typ,'--export-filename='+str(p.with_suffix('.'+typ))]
 a.insert(2,'--export-text-to-path' if typ=='pdf' else '--export-dpi=180');subprocess.run(a,check=True,stdout=subprocess.DEVNULL)
