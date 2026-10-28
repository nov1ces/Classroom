from pathlib import Path
from html import escape
import subprocess,math
ROOT=Path(__file__).resolve().parents[2]
class Drawing:
 def __init__(self,w,h):
  self.w=w;self.h=h;self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466c82" stroke-width="1.2"/></marker></defs>','<rect width="100%" height="100%" fill="white"/>']
 def text(self,x,y,t,size=18,color='#223644',anchor='middle'):
  self.a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Noto Sans CJK SC,sans-serif" font-size="{size}" fill="{color}">{escape(str(t))}</text>')
 def line(self,x,y,u,v,dash=False,arrow=False):
  self.a.append(f'<path d="M{x},{y} L{u},{v}" fill="none" stroke="#466c82" stroke-width="2"'+(' stroke-dasharray="6,4"' if dash else '')+(' marker-end="url(#ar)"' if arrow else '')+'/>')
 def node(self,x,y,t,fill='#ddefe6',r=20):
  self.a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#6c8e9c" stroke-width="1.4"/>');self.text(x,y+6,t)
 def box(self,x,y,w,h,t,fill='#ddeff5',size=17):
  self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#8ba1ab"/>');self.text(x+w/2,y+h/2+6,t,size)
 def tree(self,nodes,edges,colors={}):
  for a,b in edges:
   x,y=nodes[a];u,v=nodes[b];dx=u-x;dy=v-y;l=math.hypot(dx,dy);self.line(x+20*dx/l,y+20*dy/l,u-20*dx/l,v-20*dy/l)
  for t,(x,y) in nodes.items():self.node(x,y,t,colors.get(t,'#ddefe6'))
 def save(self,ch,name):
  p=ROOT/ch/'figures'/name;p.with_suffix('.svg').write_text('\n'.join(self.a+['</svg>']))
  for ext in ['png','pdf']:
   cmd=['inkscape',str(p.with_suffix('.svg')),'--export-type='+ext,'--export-filename='+str(p.with_suffix('.'+ext))]
   if ext=='png':cmd+=['--export-dpi=160']
   else:cmd+=['--export-text-to-path']
   subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# 1. Expression DAG preserves two distinct operand inputs to multiplication.
d=Drawing(920,320);d.text(460,28,'共享子表达式：(a*b)*(a*b)*(a*b)*c',21)
pts={'t4: *':(460,75),'t3: *':(300,145),'t2: *':(210,220),'t1: *':(450,220),'a':(390,290),'b':(510,290),'c':(690,145)}
for a,b in [('t4: *','t3: *'),('t4: *','c'),('t3: *','t2: *'),('t3: *','t1: *'),('t1: *','a'),('t1: *','b')]:
 x,y=pts[a];u,v=pts[b];d.line(x,y+15,u,v-20,arrow=True)
d.line(245,214,415,214,arrow=True);d.line(245,228,415,228,arrow=True)
for t,(x,y) in pts.items():d.box(x-35,y-18,70,36,t)
d.save('DS06','DS06_expression_dag')
# 2. AVL deletion with zero child balance: all states are explicit.
d=Drawing(1020,310);d.text(510,28,'删除与旋转：孩子平衡因子为0',21)
for off,title,nodes,edges in [(0,'删除前',{4:(155,85),2:(80,165),5:(240,165),1:(35,245),3:(125,245)},[(4,2),(4,5),(2,1),(2,3)]),(340,'删除5后',{4:(155,85),2:(80,165),1:(35,245),3:(125,245)},[(4,2),(2,1),(2,3)]),(680,'右旋4后',{2:(155,85),1:(80,165),4:(240,165),3:(195,245)},[(2,1),(2,4),(4,3)])]:
 d.text(off+160,55,title);d.tree({k:(x+off,y) for k,(x,y) in nodes.items()},edges)
d.line(300,170,350,170,arrow=True);d.line(630,170,690,170,arrow=True);d.save('DS07','DS07_avl_delete_zero')
# 3. RBT course sequence.
d=Drawing(1040,400);d.text(520,28,'红黑插入：20,10,5,30,40',21)
black='#cbd5df';red='#f1cbd1'
rows=[(0,'插入20、10',{20:(125,110),10:(65,190)},[(20,10)],{20:black,10:red}),(250,'插入5，右旋20',{10:(125,110),5:(65,190),20:(185,190)},[(10,5),(10,20)],{10:black,5:red,20:red}),(500,'插入30，叔红变色',{10:(125,110),5:(65,190),20:(185,190),30:(220,270)},[(10,5),(10,20),(20,30)],{10:black,5:black,20:black,30:red}),(760,'插入40，左旋20',{10:(125,110),5:(65,190),30:(185,190),20:(145,270),40:(225,270)},[(10,5),(10,30),(30,20),(30,40)],{10:black,5:black,30:black,20:red,40:red})]
for off,title,nodes,edges,col in rows:d.text(off+125,65,title,16);d.tree({k:(x+off,y) for k,(x,y) in nodes.items()},edges,col)
d.text(520,360,'灰蓝为黑结点，粉色为红结点；省略的NIL均为黑色',18);d.save('DS07','DS07_rb_insert_course')
# 4. Hash table with intact tombstone.
d=Drawing(1080,275);d.text(540,28,'表长16，初始地址key mod 13，线性探测按模16',21)
vals=['空',14,1,68,27,55,19,20,84,79,23,11,10,'空','空','空']
for i,x in enumerate(vals):
 xx=20+i*65;d.text(xx+30,70,i,16);d.box(xx,85,60,47,x,fill='#ddeff5' if x!='空' else '#f5f5f5')
d.text(540,175,'删除20后：7号置为“已删”，跨过它仍继续查找',19)
for i in range(1,13):
 x=20+i*65;d.line(x+30,137,x+95,137,arrow=True)
d.text(540,230,'失败ASL按初始地址0～12平均，探测到13号空位停止',18);d.save('DS07','DS07_hash_course')
# 5. Course sort states, identity tags remain.
d=Drawing(1040,340);d.text(520,28,'同一输入的三种状态',21)
rows=[('初始',['49a',38,65,97,76,13,27,'49b']),('插入38后',[38,'49a',65,97,76,13,27,'49b']),('首次快速划分',[27,38,13,'49a',76,97,65,'49b'])]
for rr,(label,values) in enumerate(rows):
 y=70+rr*85;d.text(125,y+30,label,19)
 for i,v in enumerate(values):d.box(240+i*92,y,85,50,v,fill=('#dfefe6' if (rr==1 and i<2) or (rr==2 and i==3) else '#ddeff5'))
d.text(520,325,'插入维护有序前缀；快速划分确定一个枢轴及左右大小关系',18);d.save('DS08','DS08_sort_course')
# 6. Lecture tree showing three distinct traversal orders.
d=Drawing(1000,380);d.text(500,28,'同一棵树的三种深度优先次序',21)
nodes={'A':(230,80),'B':(135,160),'C':(330,160),'D':(70,240),'E':(195,240),'F':(290,240),'G':(100,320)}
edges=[('A','B'),('A','C'),('B','D'),('B','E'),('C','F'),('D','G')];d.tree(nodes,edges)
for y,text in [(100,'先序：A B D G E C F'),(170,'中序：D G B E A F C'),(240,'后序：G D E B F C A'),(310,'层序：A B C D E F G')]:d.text(690,y,text,21)
d.save('DS05','DS05_lecture_traversal')
print('6 course figures generated')
