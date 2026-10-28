from pathlib import Path
from xml.sax.saxutils import escape
import subprocess
out=Path(__file__).resolve().parent.parent/'figures'
head='<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="720" viewBox="0 0 1500 720"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#506e80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="23" fill="#263943">'
def text(x,y,t,size=23):return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}">{escape(t)}</text>'
def box(x,y,w,h,t,color):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{color}" stroke="#859da9"/>'+text(x+w/2,y+h/2+7,t,20)
def line(x,y,xx,yy,label=''):return f'<path d="M{x},{y} L{xx},{yy}" stroke="#506e80" stroke-width="3" fill="none" marker-end="url(#a)"/>'+ (text((x+xx)/2+14,(y+yy)/2-18,label,21) if label else '')
def save(name,svg):
 p=out/(name+'.svg');p.write_text(svg+'</g></svg>')
 for ext in ['pdf','png']:
  cmd=['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))]
  if ext=='pdf':cmd.insert(2,'--export-text-to-path')
  else:cmd.append('--export-dpi=180')
  subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
svg=head
for col,(title,n) in enumerate([('一对一：3 个用户级线程映射 3 个内核级线程',3),('多对一：3 个用户级线程映射 1 个内核级线程',1),('多对多：3 个用户级线程映射 2 个内核级线程',2)]):
 x=20+col*495;svg+=text(x+230,38,title,20)
 svg+=box(x,60,465,260,'','\u0023f4f8fa')+box(x,370,465,260,'','\u0023f8f2ea')
 svg+=text(x+230,92,'应用程序 · 用户态',23)+text(x+230,668,'操作系统 · 内核态',23)
 for j in range(3):svg+=box(x+35+j*135,120,115,58,'用户线程'+str(j+1),'#e1efdb')
 if col>0:svg+=box(x+150,240,165,50,'线程库','#f6dfc5')
 for j in range(n):
  pos=x+65+j*140 if n==3 else x+165 if n==1 else x+95+j*165
  svg+=box(pos,445,115,58,'内核线程'+str(j+1),'#f9d5ae');svg+=line(pos+57,505,x+232,552)
 svg+=box(x+165,555,135,50,'所属进程','#dcecf5')
 if col==0:
  for j in range(3):svg+=line(x+92+j*135,180,x+122+j*140,440)
 else:
  for j in range(3):svg+=line(x+92+j*135,180,x+232,235)
  for j in range(n):
   pos=x+165 if n==1 else x+95+j*165
   svg+=line(x+232,292,pos+57,440)
 svg+=f'<path d="M{x},{345} H{x+465}" stroke="#7aa3b5" stroke-width="3" stroke-dasharray="9 7"/>'
footer=text(750,690,'虚线分隔用户态与内核态；线程库负责多对一、多对多模型中的用户线程管理。',24)
svg+=footer
save('OS02_course_thread_models',svg)
for i,x in enumerate((0,500,1000),1):
 panel=svg.replace(footer,'').replace('width="1500" height="720" viewBox="0 0 1500 720"',f'width="500" height="720" viewBox="{x} 0 500 720"',1)
 save(f'OS02_course_thread_models_{i}',panel)
svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="580" viewBox="0 0 900 580"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#506e80"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" font-size="23" fill="#263943">'
nodes={'S1':(450,80),'S2':(220,215),'S3':(680,215),'S4':(120,350),'S5':(350,350),'S6':(450,475)}
for a,b,label in [('S1','S2','a'),('S1','S3','b'),('S2','S4','c'),('S2','S5','d'),('S4','S6','e'),('S5','S6','f'),('S3','S6','g')]:
 x,y=nodes[a];xx,yy=nodes[b];dy=yy-y;dx=xx-x;length=(dx*dx+dy*dy)**0.5
 ux,uy=dx/length,dy/length;svg+=line(x+ux*35,y+uy*35,xx-ux*39,yy-uy*39,label)
for k,(x,y) in nodes.items():svg+=f'<circle cx="{x}" cy="{y}" r="36" fill="#dcecf5" stroke="#7c9eae" stroke-width="2"/>'+text(x,y+8,k,25)
svg+=text(450,560,'每条边各设一个初值为 0 的同步信号量',23)
save('OS02_course_precedence',svg)
