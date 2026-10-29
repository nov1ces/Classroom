from pathlib import Path
import html, subprocess
ROOT=Path(__file__).resolve().parents[3]
def txt(x,y,s,size=18):return f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>'
def box(x,y,w,h,s,fill='#DDEFF5'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#7D9BAA"/>'+txt(x+9,y+h/2+6,s)
def edge(x,y,a,b,rev=False):return f'<path d="M{x},{y} L{a},{b}" fill="none" stroke="#466C82" stroke-width="1.8" marker-end="url(#a)"'+(' marker-start="url(#b)"' if rev else '')+'/>'
def path(d,reverse=False):return f'<path d="{d}" fill="none" stroke="#466C82" stroke-width="1.8" marker-end="url(#a)"'+(' marker-start="url(#b)"' if reverse else '')+'/>'
def save(ch,name,w,h,p):
 out=ROOT/'chapters'/ch/'figures';out.mkdir(exist_ok=True)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466C82"/></marker><marker id="b" markerWidth="8" markerHeight="8" refX="0" refY="3" orient="auto"><path d="M7,0 L0,3 L7,6" fill="none" stroke="#466C82"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC,sans-serif" fill="#223C49">'+''.join(p)+'</g></svg>'
 f=out/(name+'.svg');f.write_text(svg)
 for ext in ['png','pdf']:subprocess.run(['inkscape',str(f),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# Four logical relationships, same node labels for comparison.
p=[txt(20,28,'集合：只表示同属一个集合'),txt(415,28,'线性：一对一的前后关系')]
for x,y,label in [(45,80,'a'),(160,55,'b'),(255,110,'c'),(110,150,'d')]:p.append(box(x,y,45,32,label))
for i,label in enumerate('abcd'):
 x=420+i*85;p.append(box(x,100,45,32,label))
 if i<3:p.append(edge(x+45,116,x+84,116))
p +=[txt(20,242,'树：一个父结点可联系多个孩子'),txt(415,242,'图：一般的多对多关系')]
for x,y,label in [(160,270,'a'),(65,345,'b'),(255,345,'c'),(65,420,'d')]:p.append(box(x,y,45,32,label))
p +=[edge(180,302,90,345),edge(183,302,275,345),edge(88,377,88,420)]
for x,y,label in [(450,290,'a'),(620,290,'b'),(450,415,'c'),(620,415,'d')]:p.append(box(x,y,45,32,label))
p +=[edge(495,305,620,305,True),edge(473,322,473,415,True),edge(642,322,642,415,True),edge(495,430,620,430,True),edge(490,320,620,420,True)]
save('DS01','DS01_logical_structures',760,490,p)
p=[txt(20,28,'同一逻辑序列：a → b → d → e → f')]
p +=[txt(20,73,'顺序存储')]
for i,l in enumerate(['a','b','d','e','f']):p +=[box(230+i*85,55,85,38,l),txt(235+i*85,118,str(100+i*4),15)]
p +=[txt(20,175,'链式存储')]
loc={'a':230,'b':485,'d':315,'e':570,'f':400}
for i,l in enumerate(['a','d','f','b','e']):p +=[box(230+i*85,155,75,38,l),txt(235+i*85,218,str(100+i*4),15)]
seq=['a','b','d','e','f']
for j,(a,b) in enumerate(zip(seq,seq[1:])):
 y=235+j*18;p.append(path(f'M{loc[a]+37},194 V{y} H{loc[b]+37} V194'))
p +=[txt(20,340,'索引存储')]
for i,l in enumerate(seq):p.append(box(230+i*85,318,85,64,l+' / '+str(100+['a','d','f','b','e'].index(l)*4),'#E3EFE5'))
p +=[txt(20,445,'散列存储'),box(230,414,130,48,'关键字 k'),edge(360,438,435,438),box(435,414,110,48,'h(k)'),edge(545,438,610,438),box(610,414,120,48,'存储位置')]
p +=[txt(20,510,'逻辑关系保持相同，表示关系的方式和操作代价不同。')]
save('DS01','DS01_storage_models',780,540,p)
# Doubly linked insertion and circular empty states.
p=[txt(20,30,'双链表：p之后插入s，旧后继为q'),txt(20,82,'插入前')]
p +=[box(155,58,85,42,'p'),box(410,58,85,42,'q'),edge(240,79,410,79,True)]
p +=[txt(20,172,'插入后'),box(155,146,85,42,'p'),box(285,146,85,42,'s','#F6E4EB'),box(410,146,85,42,'q'),edge(240,167,285,167,True),edge(370,167,410,167,True)]
p +=[txt(20,235,'s->next=q；q->prior=s；s->prior=p；p->next=s',17),txt(20,295,'循环单链表空表：L->next=L'),box(420,265,110,42,'头结点'),path('M530,286 H605 V330 H475 V307')]
p +=[txt(20,390,'循环双链表空表：next和prior都指回L'),box(420,365,110,42,'头结点'),path('M530,380 H640 V445 H475 V407'),path('M420,390 H355 V460 H455 V407')]
save('DS02','DS02_double_and_cycles',760,490,p)
# Lecture's exact Fib(4) call tree, 9 calls.
p=[txt(20,30,'Fib(4)调用树：9次调用，最大4层同时活跃')]
nodes=[(370,60,'Fib(4)'),(230,150,'Fib(3)'),(510,150,'Fib(2)'),(135,245,'Fib(2)'),(315,245,'Fib(1)'),(470,245,'Fib(1)'),(590,245,'Fib(0)'),(65,340,'Fib(1)'),(205,340,'Fib(0)')]
for x,y,l in nodes:p.append(box(x,y,104,42,l,'#E3EFE5' if l=='Fib(2)' else '#DDEFF5'))
for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),(3,7),(3,8)]:
 x,y,_=nodes[a];xx,yy,_=nodes[b];p.append(edge(x+52,y+42,xx+52,yy))
p +=[txt(20,435,'Fib(0)=0，Fib(1)=1；两个Fib(2)是相同子问题的重复计算。',17)]
save('DS03','DS03_fib_tree',760,470,p)
