from pathlib import Path
import html,subprocess
root=Path(__file__).resolve().parents[1];out=root/'figures'
def export(name,w,h,parts):
 text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466C82"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC, sans-serif" font-size="19" fill="#20343F">'+''.join(parts)+'</g></svg>'
 p=out/(name+'.svg');p.write_text(text)
 for ext in ['png','pdf']:subprocess.run(['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def text(x,y,s,size=19):return f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>'
def grid(x,y,s,first=1,highlight=()):
 a=[]
 for i,c in enumerate(s):
  xx=x+43*i;a.append(f'<rect x="{xx}" y="{y}" width="43" height="38" fill="'+('#FDEAC9' if i+first in highlight else '#E1EEF3')+'" stroke="#86A4B4"/>');a.append(text(xx+15,y+26,c));a.append(text(xx+15,y-8,str(i+first),15))
 return a
parts=[text(24,29,'顺序串：length = 7，ch[0]弃用'),*grid(140,78,' wangdao',0),text(24,108,'位置'),text(24,168,'块链串：每结点保存4字符，另存总长度')]
for x,s in [(90,'wang'),(340,'dao#')]:
 parts+=grid(x,195,s);parts.append(f'<rect x="{x+172}" y="195" width="45" height="38" fill="#F1E7ED" stroke="#86A4B4"/>')
parts+=[f'<path d="M307,214 H340" stroke="#466C82" stroke-width="2" marker-end="url(#a)"/>',text(580,221,'NULL'),text(24,285,'#表示末块填充；由length区分有效字符与填充')]
export('DS04_string_layout',750,310,parts)
parts=[text(24,30,'T = abaabc：第6个字符失配，next[6] = 3'),text(24,108,'主串S'),*grid(155,78,'abaab?',1,highlight=(6,)),text(24,172,'原模式'),*grid(155,142,'abaabc',1,highlight=(6,)),text(24,254,'右移后'),*grid(284,224,'abaabc',1,highlight=(3,)),text(24,325,'保留已匹配后缀ab：位置4、5与模式位置1、2对齐'),text(24,365,'主串i不变；模式j由6退到3；位移 = 6 − 3 = 3')]
parts.append('<path d="M391,189 V215" fill="none" stroke="#B67F99" stroke-width="2" marker-end="url(#a)"/>')
export('DS04_kmp_1based',740,395,parts)
