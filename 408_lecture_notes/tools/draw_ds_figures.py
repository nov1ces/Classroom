#!/usr/bin/env python3
"""Generate editable DS teaching diagrams; needs only Python and Inkscape."""
from pathlib import Path
from html import escape
import math, json, subprocess, shutil, argparse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
MANIFEST=ROOT/'build/DS/figure_manifest.json'
OUT.mkdir(exist_ok=True,parents=True)

class SVG:
    def __init__(self,w=1000,h=500):
        self.w,self.h=w,h; self.a=[]
    def text(self,x,y,s,size=23,anchor='middle',bold=False):
        self.a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{"bold" if bold else "normal"}">{escape(str(s))}</text>')
    def line(self,x1,y1,x2,y2,arrow=False,dash=False,width=2.4):
        self.a.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222" stroke-width="{width}"'+(' marker-end="url(#arr)"' if arrow else '')+(' stroke-dasharray="9 6"' if dash else '')+'/>')
    def rect(self,x,y,w,h,label='',dash=False,fill='white',size=23):
        self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" stroke="#222" stroke-width="2.2" fill="{fill}"'+(' stroke-dasharray="9 6"' if dash else '')+'/>')
        if label: self.text(x+w/2,y+h/2+size*.34,label,size)
    def circle(self,x,y,label,r=27,fill='white',size=23):
        self.a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#222" stroke-width="2.2"/>')
        self.text(x,y+size*.34,label,size)
    def edge(self,p,q,arrow=False,label=None,offset=(0,-10),dash=False,r=28):
        x1,y1=p;x2,y2=q;d=math.hypot(x2-x1,y2-y1);dx=(x2-x1)/d;dy=(y2-y1)/d
        self.line(x1+r*dx,y1+r*dy,x2-r*dx,y2-r*dy,arrow,dash)
        if label is not None:
            x=(x1+x2)/2+offset[0]; y=(y1+y2)/2+offset[1]
            self.rect(x-23,y-20,46,30,'',fill='white')
            self.text(x,y+3,label,21)
    def path(self,points,arrow=True,dash=True):
        ss=' '.join(f'{x},{y}' for x,y in points)
        self.a.append(f'<polyline points="{ss}" fill="none" stroke="#222" stroke-width="2.1"'+(' stroke-dasharray="8 5"' if dash else '')+(' marker-end="url(#arr)"' if arrow else '')+'/>')
    def content(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L10,4 L0,8 Z" fill="#222"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC" fill="#111">'+''.join(self.a)+'</g></svg>'

items=[]
ONLY=set()
def save(name,svg,title,data):
    item={'id':name,'title':title,'svg':f'figures/{name}.svg','png':f'figures/{name}.png','pdf':f'figures/{name}.pdf','source':'tools/draw_ds_figures.py','data':data,'semantics':'实线为原有/已生效关系，虚线为待改关系、线索或冻结标记；文字标签在灰度打印中保留含义。'}
    items.append(item)
    if ONLY and name not in ONLY:return
    p=OUT/f'{name}.svg';p.write_text(svg.content())
    exe=shutil.which('inkscape')
    if not exe: raise RuntimeError('Inkscape is required for SVG → PNG/PDF')
    for ext in ['png','pdf']:
        cmd=[exe,str(p),f'--export-type={ext}',f'--export-filename={OUT/(name+"."+ext)}']
        if ext=='png':cmd+=['--export-width=1800']
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def tree(s,pos,edges,labels=None,fill=None):
    for a,b in edges:s.edge(pos[a],pos[b])
    for k,(x,y) in pos.items():s.circle(x,y,(labels or {}).get(k,k),fill=(fill or {}).get(k,'white'))

def avl_node(x,l=None,r=None):return [x,l,r]
def avl_height(t):return 0 if t is None else 1+max(avl_height(t[1]),avl_height(t[2]))

# Original numerical teaching examples, following the source's four rotation
# rules. These are not changed versions of any source examination question.
AVL_CASES=[
    {'type':'LL','insert':10,'pre_insert':avl_node(50,avl_node(30,avl_node(20),avl_node(40)),avl_node(70)),
     'states':[avl_node(50,avl_node(30,avl_node(20,avl_node(10)),avl_node(40)),avl_node(70)),avl_node(30,avl_node(20,avl_node(10)),avl_node(50,avl_node(40),avl_node(70)))],
     'operations':[{'direction':'right','at':50}], 'transfer':'40：由30的右子树转接为50的左子树'},
    {'type':'RR','insert':70,'pre_insert':avl_node(30,avl_node(10),avl_node(50,avl_node(40),avl_node(60))),
     'states':[avl_node(30,avl_node(10),avl_node(50,avl_node(40),avl_node(60,None,avl_node(70)))),avl_node(50,avl_node(30,avl_node(10),avl_node(40)),avl_node(60,None,avl_node(70)))],
     'operations':[{'direction':'left','at':30}], 'transfer':'40：由50的左子树转接为30的右子树'},
    {'type':'LR','insert':40,'pre_insert':avl_node(70,avl_node(30,avl_node(20),avl_node(50)),avl_node(90)),
     'states':[avl_node(70,avl_node(30,avl_node(20),avl_node(50,avl_node(40))),avl_node(90)),avl_node(70,avl_node(50,avl_node(30,avl_node(20),avl_node(40))),avl_node(90)),avl_node(50,avl_node(30,avl_node(20),avl_node(40)),avl_node(70,None,avl_node(90)))],
     'operations':[{'direction':'left','at':30},{'direction':'right','at':70}], 'transfer':'40：第一步由50的左子树转接为30的右子树'},
    {'type':'RL','insert':80,'pre_insert':avl_node(50,avl_node(30),avl_node(90,avl_node(70),avl_node(100))),
     'states':[avl_node(50,avl_node(30),avl_node(90,avl_node(70,None,avl_node(80)),avl_node(100))),avl_node(50,avl_node(30),avl_node(70,None,avl_node(90,avl_node(80),avl_node(100)))),avl_node(70,avl_node(50,avl_node(30)),avl_node(90,avl_node(80),avl_node(100)))],
     'operations':[{'direction':'right','at':90},{'direction':'left','at':50}], 'transfer':'80：第一步由70的右子树转接为90的左子树'},
]

def draw_avl_state(s,t,cx,y,insert,span=230):
    order=[];positions={}
    def walk(u,depth):
        if u is None:return
        walk(u[1],depth+1);order.append((u,depth));walk(u[2],depth+1)
    walk(t,0)
    for i,(u,depth) in enumerate(order):positions[u[0]]=(cx-span/2+(i+.5)*span/len(order),y+43*depth)
    for u,depth in order:
        for ch in u[1:]:
            if ch is not None:s.edge(positions[u[0]],positions[ch[0]],r=17)
    for u,depth in order:
        x,yy=positions[u[0]];bf=avl_height(u[1])-avl_height(u[2])
        s.circle(x,yy,u[0],r=17,size=19,fill='#dedede' if u[0]==insert else 'white')
        bf_label=f'{bf:+d}' if bf else '0'
        s.a.append(f'<text x="{x+22}" y="{yy-12}" font-size="14" text-anchor="start" paint-order="stroke" stroke="white" stroke-width="3" stroke-linejoin="round">{bf_label}</text>')

def draw_avl_cases(cases):
    s=SVG(h=505)
    for row,case in enumerate(cases):
        dy=row*235;s.text(16,dy+26,case['type'],23,'start',True)
        centers=[220,780] if len(case['states'])==2 else [160,500,840]
        for i,(t,cx) in enumerate(zip(case['states'],centers)):
            action='插入后' if i==0 else ('右旋' if case['operations'][i-1]['direction']=='right' else '左旋')+str(case['operations'][i-1]['at'])
            s.text(cx,dy+27,f'{action}，h={avl_height(t)}',20,bold=True)
            draw_avl_state(s,t,cx,dy+62,case['insert'])
        for a,b in zip(centers,centers[1:]):s.line(a+142,dy+110,b-142,dy+110,True)
        s.text(500,dy+226,case['transfer'],19)
    s.text(500,496,'灰底为新插入结点；结点旁小字为平衡因子（左高−右高）；空树高0',18)
    return s

def bnode(keys,children=None):return {'keys':list(keys),'children':children or []}

def draw_btree(s,t,x,y,width,level_gap=74,font=21,marks=()):
    gap=11;bh=34
    # The CJK box-drawing separator has a full-em advance, while digits use
    # roughly .56 em. Measuring them alike lets labels escape their node boxes.
    def node_width(u):
        label='│'.join(map(str,u['keys']))
        return max(40,sum(font if ch=='│' else font*.56 for ch in label)+20)
    def measure(u):
        return max(node_width(u),sum(measure(c) for c in u['children'])+gap*max(0,len(u['children'])-1))
    tw=measure(t)
    if tw>width:raise ValueError(f'B-tree diagram needs {tw:g}px, only {width:g}px available')
    def place(u,left,cy,path=()):
        w=measure(u);cx=left+w/2;nw=node_width(u)
        if u['children']:
            cw=sum(measure(c) for c in u['children'])+gap*(len(u['children'])-1);cl=cx-cw/2
            for i,c in enumerate(u['children']):
                cc=cl+measure(c)/2;s.line(cx,cy+bh/2,cc,cy+level_gap-bh/2)
                place(c,cl,cy+level_gap,path+(i,));cl+=measure(c)+gap
        s.rect(cx-nw/2,cy-bh/2,nw,bh,'│'.join(map(str,u['keys'])) or '空',dash=path in marks,fill='#eeeeee' if path in marks else 'white',size=font)
    place(t,x+(width-tw)/2,y)

BTREE_INSERT_INITIAL=bnode([5,10,15,20],[bnode([1,3]),bnode([6,8]),bnode([11,13]),bnode([16,18]),bnode([21,23,25,27])])
BTREE_INSERT_STATES=[
    bnode([5,10,15,20],[bnode([1,3]),bnode([6,8]),bnode([11,13]),bnode([16,18]),bnode([21,23,25,27,29])]),
    bnode([5,10,15,20,25],[bnode([1,3]),bnode([6,8]),bnode([11,13]),bnode([16,18]),bnode([21,23]),bnode([27,29])]),
    bnode([15],[bnode([5,10],[bnode([1,3]),bnode([6,8]),bnode([11,13])]),bnode([20,25],[bnode([16,18]),bnode([21,23]),bnode([27,29])])]),
]
BTREE_BORROW_INITIAL=bnode([10],[bnode([2,5]),bnode([12,15,18])])
BTREE_BORROW_STATES=[bnode([10],[bnode([5]),bnode([12,15,18])]),bnode([12],[bnode([5,10]),bnode([15,18])])]
BTREE_DELETE_STATES=[
    bnode([15],[bnode([5,10],[bnode([3]),bnode([6,8]),bnode([11,13])]),bnode([20,25],[bnode([16,18]),bnode([21,23]),bnode([27,29])])]),
    bnode([15],[bnode([10],[bnode([3,5,6,8]),bnode([11,13])]),bnode([20,25],[bnode([16,18]),bnode([21,23]),bnode([27,29])])]),
    bnode([], [bnode([10,15,20,25],[bnode([3,5,6,8]),bnode([11,13]),bnode([16,18]),bnode([21,23]),bnode([27,29])])]),
    bnode([10,15,20,25],[bnode([3,5,6,8]),bnode([11,13]),bnode([16,18]),bnode([21,23]),bnode([27,29])]),
]

def main():
    s=SVG(h=610)
    for row,lab in enumerate(['① 原链：s尚未接入','② 先保存旧后继','③ 再改p的后继']):
        y=85+row*190;s.text(25,y-40,lab,23,'start',True)
        if row<2:
            for x,name in [(200,'p:A'),(560,'r:B'),(830,'C')]:s.rect(x-65,y-20,130,48,name)
            s.line(265,y+4,495,y+4,True);s.line(625,y+4,765,y+4,True)
            s.rect(360,y+60,130,48,'s:X')
            if row==1:s.path([(490,y+84),(560,y+84),(560,y+30)],True,False)
        else:
            for x,name in [(160,'p:A'),(390,'s:X'),(620,'r:B'),(850,'C')]:s.rect(x-65,y-20,130,48,name)
            for x in [225,455,685]:s.line(x,y+4,x+100,y+4,True)
    save('DS_01_list_insert',s,'单链表插入的两次链接更新',{'before':['A','B','C'],'insert':'X','after':['A','X','B','C'],'operations':['s.next=p.next','p.next=s']})

    s=SVG(h=410)
    nodes={'l':(180,100),'o':(300,100),'a':(420,100),'d':(540,100),'b':(420,300),'e':(540,300),'i':(680,200),'n':(800,200),'g':(920,200)}
    for a,b in [('l','o'),('o','a'),('a','d'),('d','i'),('b','e'),('e','i'),('i','n'),('n','g')]:s.edge(nodes[a],nodes[b],True)
    for k,p in nodes.items():s.circle(*p,k)
    s.circle(60,100,'头1');s.edge((60,100),nodes['l'],True)
    s.text(60,35,'str1',23);s.line(60,45,60,70,True)
    s.circle(300,300,'头2');s.edge((300,300),nodes['b'],True)
    s.text(300,230,'str2',23);s.line(300,240,300,270,True)
    s.text(770,345,'共享同一组 i → n → g 结点',23)
    save('DS_02_shared_suffix',s,'两个单链表共享后缀',{'words':['loading','being'],'shared':'ing','lengths':[7,5],'head_nodes':['头1','头2'],'head_pointer_targets':['头1','头2']})

    s=SVG(h=560);pos={i:(500+185*math.sin(i*math.pi/4),250-185*math.cos(i*math.pi/4)) for i in range(8)}
    for i in range(8):s.edge(pos[i],pos[(i+1)%8],True,r=40)
    val={6:'A',7:'B',0:'C',1:'D'}
    for i,(x,y) in pos.items():s.circle(x,y,f'{i}:{val.get(i,"空")}',r=38,size=23,fill='#eeeeee' if i in val else 'white')
    s.text(500,245,'M=8，容量7',24, bold=True);s.text(500,285,'有效队列 A B C D',23)
    s.text(190,430,'front=6',23);s.line(270,415,*[pos[6][0]-5,pos[6][1]+40],True)
    s.text(810,430,'rear=2（下个入队位）',22);s.line(770,400,pos[2][0],pos[2][1]+40,True)
    s.text(500,530,'长度 (2−6+8) mod 8 = 4；还可入队3个',23)
    save('DS_03_circular_queue',s,'循环队列下标环绕',{'M':8,'front':6,'rear':2,'values':val,'length':4,'spare':3})

    s=SVG(h=410);chars=list('abaabac');x0=260;cw=75
    s.text(40,92,'主串',23,'start')
    for j,c in enumerate(chars):s.rect(x0+j*cw,60,cw,50,c,fill='#eeeeee' if j<5 else 'white')
    s.text(x0+5*cw+cw/2,40,'i=5',23)
    s.text(40,182,'原对齐',23,'start')
    for j,c in enumerate('abaabc'):s.rect(x0+j*cw,150,cw,50,c)
    s.text(x0+5*cw+cw/2,232,'j=5，失配',22)
    s.text(40,302,'移动后',23,'start')
    for j,c in enumerate('abaabc'):s.rect(x0+(j+3)*cw,270,cw,50,c)
    s.text(500,380,'保留后缀 ab；i不动，j=2，模式右移3位',23)
    save('DS_04_kmp_shift',s,'KMP失配保留最长相等前后缀',{'pattern':'abaabc','matched':'abaab','i':5,'j_before':5,'j_after':2,'shift':3})

    pos={'A':(500,70),'B':(280,200),'C':(720,200),'D':(160,330),'E':(400,330),'F':(840,330)};edges=[('A','B'),('A','C'),('B','D'),('B','E'),('C','F')]
    s=SVG(h=530);tree(s,pos,edges)
    for y,line in [(410,'先序 A B D E C F     中序 D B E A C F'),(460,'后序 D E B F C A     层序 A B C D E F')]:s.text(500,y,line,23)
    save('DS_05_binary_traversal',s,'同一二叉树的四种遍历',{'children':{'A':['B','C'],'B':['D','E'],'C':[None,'F']},'preorder':'ABDECF','inorder':'DBEACF','postorder':'DEBFCA','levelorder':'ABCDEF'})

    # Keep the same six-node example as DS_05. Each L/R field has its own
    # outgoing port, so the boundary threads cannot be mistaken for D.right
    # or F.left. Incoming threads land on separate parts of the data cell.
    s=SVG(h=710)
    thread_pos={'A':(500,105),'B':(260,260),'C':(750,260),
                'D':(110,445),'E':(405,445),'F':(885,445)}
    children={'A':['B','C'],'B':['D','E'],'C':[None,'F'],
              'D':[None,None],'E':[None,None],'F':[None,None]}
    tags={k:[int(v is None) for v in pair] for k,pair in children.items()}
    thread_routes=[
        ('D','left',None,[(62,475),(62,560)]),
        ('D','right','B',[(158,475),(158,515),(242,515),(242,290)]),
        ('E','left','B',[(357,475),(357,495),(278,495),(278,290)]),
        ('E','right','A',[(453,475),(453,500),(485,500),(485,135)]),
        ('C','left','A',[(702,290),(702,320),(650,320),(530,165),(515,135)]),
        ('F','left','C',[(837,475),(837,515),(750,515),(750,290)]),
        ('F','right',None,[(933,475),(933,560)])]
    s.text(500,30,'实线：孩子链接　　虚线箭头：中序线索',23,bold=True)
    for a,pair in children.items():
        for side,b in zip(['left','right'],pair):
            if b is None:continue
            x,y=thread_pos[a];tx,ty=thread_pos[b]
            s.a.append(f'<g id="child-{a}-{side}" data-from="{a}" data-side="{side}" data-target="{b}" data-kind="child">')
            s.line(x+(-48 if side=='left' else 48),y+30,tx,ty-30)
            s.a.append('</g>')
    for a,side,b,route in thread_routes:
        target=b if b is not None else f'null-{a}-{side}'
        s.a.append(f'<g id="thread-{a}-{side}" data-from="{a}" data-side="{side}" data-target="{target}" data-kind="thread">')
        s.path(route)
        s.a.append('</g>')
    for k,(x,y) in thread_pos.items():
        ltag,rtag=tags[k]
        s.a.append(f'<g id="node-{k}" data-node="{k}" data-ltag="{ltag}" data-rtag="{rtag}">')
        s.rect(x-72,y-30,144,60)
        s.line(x-24,y-30,x-24,y+30);s.line(x+24,y-30,x+24,y+30)
        s.text(x-48,y+8,f'L{ltag}',23)
        s.text(x,y+9,k,26,bold=True)
        s.text(x+48,y+8,f'R{rtag}',23)
        s.a.append('</g>')
    for a,side,x in [('D','left',62),('F','right',933)]:
        s.a.append(f'<g id="null-{a}-{side}" data-boundary="{a}_{side}">')
        s.rect(x-26,560,52,42,'∅',size=25)
        s.a.append('</g>')
    s.text(155,588,'空前驱',22);s.text(840,588,'空后继',22)
    s.text(500,643,'中序：D → B → E → A → C → F',24,bold=True)
    s.text(500,685,'L / R 为左 / 右指针域；0 = 孩子，1 = 线索；本图首尾取 ∅',22)
    save('DS_06_inorder_threads',s,'中序线索与孩子链接',{
        'root':'A','children':children,'inorder':'DBEACF',
        'tags':tags,'tag_convention':{'child':0,'thread':1},
        'threads':{'D_left':None,'D_right':'B','E_left':'B','E_right':'A',
                   'C_left':'A','F_left':'C','F_right':None},
        'predecessors':{'D':None,'B':'D','E':'B','A':'E','C':'A','F':'C'},
        'successors':{'D':'B','B':'E','E':'A','A':'C','C':'F','F':None},
        'boundary_convention':'无头结点，D.left 与 F.right 均为 ∅；二者的 tag 仍为1',
        'node_centres':thread_pos,
        'thread_routes':[{'from':a,'side':side,'target':b,'points':route}
                         for a,side,b,route in thread_routes],
        'source_refs':{'book_pdf_pages':[156,157],'book_print_pages':[144,145],
                       'slides':{'5.3.2_1 线索二叉树的概念.pdf':[4,5],
                                 '5.3.2_2 二叉树的线索化.pdf':[4,5],
                                 '5.3.2_3 在线索二叉树中找前驱后继.pdf':[3,5]}}})

    s=SVG(h=540);s.text(240,40,'森林：A有孩子B、C；D独立',23);s.text(740,40,'二叉树：左孩子、右兄弟',23)
    p={'A':(200,110),'B':(110,260),'C':(290,260),'D':(420,110)};tree(s,p,[('A','B'),('A','C')])
    p={'A':(660,110),'B':(560,260),'C':(650,405),'D':(840,260)}
    for a,b in [('A','B'),('B','C'),('A','D')]:s.edge(p[a],p[b],True)
    for k,v in p.items():s.circle(*v,k)
    s.text(585,172,'左',22);s.text(625,345,'右',22);s.text(790,172,'右',22)
    s.text(500,505,'A的左子树只表示第一棵树除根外的结点',23)
    save('DS_07_forest_conversion',s,'森林的孩子兄弟转换',{'forest':[{'A':['B','C']},{'D':[]}],'binary_edges':[['A','B','left'],['B','C','right'],['A','D','right']]})

    s=SVG(h=590);p={'36':(500,60),'15':(260,180),'21':(740,180),'7':(130,310),'8':(390,310),'10':(610,310),'11':(870,310),'3':(65,450),'4':(195,450),'5':(805,450),'6':(935,450)}
    e=[('36','15'),('36','21'),('15','7'),('15','8'),('21','10'),('21','11'),('7','3'),('7','4'),('11','5'),('11','6')];tree(s,p,e)
    for a,b in e:
        x=(p[a][0]+p[b][0])/2;y=(p[a][1]+p[b][1])/2;s.text(x+(-18 if p[b][0]<p[a][0] else 18),y,'0' if p[b][0]<p[a][0] else '1',21)
    s.text(500,555,'WPL = 7+11+15+21+36 = 90；平均码长 90/36 = 2.5',23)
    save('DS_08_huffman',s,'六字符哈夫曼合并树',{'weights':[3,4,5,6,8,10],'merge_weights':[7,11,15,21,36],'WPL':90,'average':2.5})

    s=SVG(h=470)
    states=[[12,15,10,21,34,16],[10,15,12,21,34,16]]
    for col,a in enumerate(states):
        base=250+col*500;p={i+1:(base+[0,-115,115,-175,-55,55][i],70+[0,120,120,240,240,240][i]) for i in range(6)}
        for k in range(2,7):s.edge(p[k//2],p[k])
        for k,v in p.items():s.circle(*v,a[k-1])
        s.text(base,385,'12填根' if col==0 else '10上移，12留在16上方',23)
    s.text(500,445,'比较：15与10；12与10；12与16，共3次',23)
    save('DS_09_heap_delete',s,'小根堆删除堆顶后的下滤',{'initial':[8,15,10,21,34,16,12],'states':states,'comparisons':[[15,10],[12,10],[12,16]],'comparison_count':3})

    s=SVG(h=570);p={'a':(230,90),'b':(80,240),'c':(380,240),'e':(130,410),'f':(380,410),'d':(250,510)}
    e=[('a','b'),('a','c'),('a','e'),('b','e'),('c','f'),('f','d'),('e','d')];tree(s,p,e)
    for j,k in enumerate('abcdef'):
        ns=sorted(b if a==k else a for a,b in e if k in [a,b]);s.rect(550,55+j*77,380,58,f'{k}: '+', '.join(ns))
    save('DS_10_graph_storage',s,'同一无向图及其邻接表',{'vertices':list('abcdef'),'edges':e,'DFS':'abedfc','BFS':'abcefd'})

    s=SVG(h=510);p={'V1':(270,80),'V2':(730,80),'V3':(270,380),'V4':(730,380)}
    e=[('V1','V2',10),('V1','V3',8),('V1','V4',5),('V2','V3',8),('V2','V4',11),('V3','V4',8)]
    for a,b,w in e:s.edge(p[a],p[b],label=w,offset=((-45 if (a,b)==('V1','V4') else 45) if (a,b) in [('V1','V4'),('V2','V3')] else 0,-12))
    for k,v in p.items():s.circle(*v,k,r=34)
    s.text(500,475,'Prim从V4开始：选(V1,V4)后，下一条须跨出{V1,V4}',23)
    save('DS_11_mst_2015',s,'2015最小生成树原图重绘',{'year':2015,'question':6,'edges':e,'MST_weight':21})

    s=SVG(h=570);p={'1':(500,65),'5':(170,240),'2':(830,240),'4':(270,455),'3':(730,455)}
    e=[('1','5',6),('1','2',26),('1','3',3),('5','2',15),('5','4',8),('5','3',6),('4','2',1),('4','3',6),('3','2',22)]
    offs={('1','3'):(-23,-80),('5','3'):(-40,12),('4','2'):(40,-18),('5','2'):(0,-12)}
    for a,b,w in e:s.edge(p[a],p[b],True,w,offs.get((a,b),(0,-10)))
    for k,v in p.items():s.circle(*v,k)
    s.text(500,545,'确定3、5后：dist[2,3,4,5] = [21,3,14,6]',23)
    save('DS_12_dijkstra_2021',s,'2021Dijkstra原图重绘',{'year':2021,'question':8,'edges':e,'after_two':[21,3,14,6],'final':[15,3,14,6]})

    s=SVG(h=490);p={'1':(90,245),'2':(340,100),'3':(340,390),'4':(650,100),'5':(650,390),'6':(910,245)}
    e=[('1','2','a=3'),('1','3','b=8'),('3','2','d=4'),('2','4','c=9'),('2','5','e=6'),('3','5','f=10'),('4','6','g=6'),('5','6','h=9')]
    for a,b,w in e:s.edge(p[a],p[b],True,w,offset=((-50 if w=='d=4' else 0),-10))
    for k,v in p.items():s.circle(*v,k)
    save('DS_13_aoe_2013',s,'2013AOE原图重绘',{'year':2013,'question':9,'edges':e,'ve':[0,12,8,21,18,27],'vl':[0,12,8,21,18,27],'critical_paths':['bdcg','bdeh','bfh']})

    avl_sources={'purpose':'原创数值机制例，显示非空中间子树的转接；不属于例7-3原题数据',
                 'sources':[{'path':'/workspace/Classroom/01_数据结构/【课件】数据结构基础考点讲解/第七章 查找/7.3.2_1 平衡二叉树.pdf','pdf_pages':[7,8,9,10,11,12,13,14,15]},
                            {'path':'/workspace/study_analysis/v2/books/王道2027数据结构_高清带书签版.pdf','pdf_pages':[294,295,296,297],'printed_pages':[282,283,284,285]}]}
    save('DS_14_avl_rotations',draw_avl_cases(AVL_CASES[:2]),'AVL的LL/RR单旋与中间子树转接',{'cases':AVL_CASES[:2],**avl_sources})
    save('DS_21_avl_double_rotations',draw_avl_cases(AVL_CASES[2:]),'AVL的LR/RL两步状态与中间子树转接',{'cases':AVL_CASES[2:],**avl_sources})

    btree_sources={'purpose':'原创5阶B树机制例；沿用来源定义与调整规则，数值快照为教学构造，未改任何真题阶数',
                   'sources':[{'path':'/workspace/Classroom/01_数据结构/【课件】数据结构基础考点讲解/第七章 查找/7.4.1_1 B树.pdf','pdf_pages':[12,13,14,15,16,17,18]},
                              {'path':'/workspace/Classroom/01_数据结构/【课件】数据结构基础考点讲解/第七章 查找/7.4.1_2 B树的插入删除.pdf','pdf_pages':[2,7,8,12,13,24,25,26,27,30,34,36,39,41,44,45,53]},
                              {'path':'/workspace/study_analysis/v2/books/王道2027数据结构_高清带书签版.pdf','pdf_pages':[317,318,319,320],'printed_pages':[305,306,307,308]}]}
    s=SVG(w=1200,h=510)
    s.text(300,30,'① 插入29：最右叶暂有5项',23,bold=True)
    draw_btree(s,BTREE_INSERT_STATES[0],10,85,580,marks=((4,),))
    s.text(900,30,'② 提升25：根暂有5项',23,bold=True)
    draw_btree(s,BTREE_INSERT_STATES[1],610,85,580,marks=((),))
    s.text(600,265,'③ 根再分裂，提升15建立新根；原6个孩子按区间分到两侧',23,bold=True)
    draw_btree(s,BTREE_INSERT_STATES[2],100,315,1000,level_gap=68)
    s.text(600,495,'5阶：非根2～4项；溢出5项 → 左2项 + 提升1项 + 右2项',22)
    save('DS_15_btree_split',s,'5阶B树叶分裂向根传播',{'order':5,'insert':29,'initial':BTREE_INSERT_INITIAL,'states':BTREE_INSERT_STATES,'temporary_violations':[[{'path':[4],'keys':5}],[{'path':[],'keys':5}],[]],**btree_sources})

    s=SVG(w=1200,h=535)
    for cx,t,label,marks in [(200,BTREE_BORROW_INITIAL,'借位前',()),(600,BTREE_BORROW_STATES[0],'删2：左叶仅1项',((0,),)),(1000,BTREE_BORROW_STATES[1],'10下移，12上移',())]:
        s.text(cx,30,label,22,bold=True);draw_btree(s,t,cx-190,85,380,level_gap=70,font=21,marks=marks)
    s.line(380,95,420,95,True);s.line(780,95,820,95,True)
    s.text(300,267,'从插入图末态删1：叶合并后，左双亲仅1项',21,bold=True)
    draw_btree(s,BTREE_DELETE_STATES[1],10,320,580,level_gap=70,font=21,marks=((0,),))
    s.text(900,267,'再与右兄弟及根15合并，空根降高',21,bold=True)
    draw_btree(s,BTREE_DELETE_STATES[3],610,320,580,level_gap=70,font=21)
    s.line(580,345,620,345,True)
    s.text(600,524,'虚框只标临时下溢；所有完成态均满足非根下限、孩子数与叶等深',20)
    save('DS_20_btree_delete',s,'5阶B树借位、合并向上传播与根降高',{'order':5,'borrow':{'initial':BTREE_BORROW_INITIAL,'delete':2,'states':BTREE_BORROW_STATES,'temporary_violations':[[{'path':[0],'keys':1}],[]]},'cascade':{'initial':BTREE_INSERT_STATES[2],'delete':1,'states':BTREE_DELETE_STATES,'temporary_violations':[[{'path':[0,0],'keys':1}],[{'path':[0],'keys':1}],[{'path':[],'keys':0}],[]]},**btree_sources})

    s=SVG(h=410);s.rect(350,65,300,55,'20 | 40 | 60',fill='#eeeeee')
    leaves=[([10,20],170),([30,40],500),([50,60],830)]
    for i,(ks,x) in enumerate(leaves):s.line(400+i*100,120,x,240);s.rect(x-105,240,210,60,' | '.join(map(str,ks)))
    s.line(275,270,395,270,True);s.line(605,270,725,270,True)
    s.text(500,370,'图中内部关键字取对应子树最大值；记录都在叶层',23)
    save('DS_16_bplus',s,'B+树索引与叶链',{'convention':'每个内部关键字为对应孩子子树最大值','index':[20,40,60],'leaves':[[10,20],[30,40],[50,60]]})

    s=SVG(h=490);levels=[[[7],[3],[5],[1],[6],[2],[4],[8]],[[3,7],[1,5],[2,6],[4,8]],[[1,3,5,7],[2,4,6,8]],[[1,2,3,4,5,6,7,8]]]
    for i,level in enumerate(levels):
        s.text(30,70+i*125,f'{i}层',23,'start');total=sum(len(z) for z in level);slot=95;start=150
        for seg in level:
            w=len(seg)*slot;s.rect(start,35+i*125,w-10,58,' '.join(map(str,seg)),fill='#eeeeee' if i==3 else 'white');start+=w
    save('DS_17_merge_trace',s,'二路归并的逐层有序段',{'input':[7,3,5,1,6,2,4,8],'levels':levels})

    s=SVG(h=470);steps=[('初装','37 51 92 94','无'),('输出37、51、63','92 94 99','14 15'),('第一段即将结束','99','14 15 48'),('输出99后换段','无','14 15 48 56')]
    for i,(title,a,f) in enumerate(steps):
        y=35+100*i;s.text(25,y+38,title,22,'start');s.rect(300,y,300,65,a);s.rect(650,y,310,65,f,dash=True)
    s.text(450,450,'当前段候选',22);s.text(800,450,'冻结区：下一段再参加',22)
    save('DS_18_replacement_selection',s,'置换选择的冻结与换段',{'input':[51,94,37,92,14,63,15,99,48,56,23,60,31,17,43,8,90,166,100],'m':4,'first_run':[37,51,63,92,94,99],'frozen_after_first':[14,15,48,56]})

    s=SVG(h=560)
    for side,heads,losers,champ in [(0,[3,5,2,7],[5,7,3],'C:2'),(1,[3,5,6,7],[5,7,6],'A:3')]:
        base=250+side*500;s.text(base,35,'原首记录' if side==0 else 'C换入6后',23,bold=True)
        s.rect(base-70,65,140,45,'冠军 '+champ,size=22)
        nodes=[(base,180,('A:3' if side==0 else 'C:6')),(base-125,300,'B:5'),(base+125,300,'D:7')]
        s.line(base,205,base-125,275);s.line(base,205,base+125,275)
        for x,y,v in nodes:s.rect(x-50,y-25,100,50,str(v))
        for i,v in enumerate(heads):
            x=base-195+i*130;py=325;s.line(base+(-125 if i<2 else 125),py,x,435);s.rect(x-48,435,96,50,f'{"ABCD"[i]}:{v}',size=22)
    s.text(500,540,'内部保存败者；只重赛换入记录所在叶到根的路径',23)
    save('DS_19_loser_tree',s,'四路归并败者树两轮状态',{'heads_before':[3,5,2,7],'heads_after':[3,5,6,7],'champions':['C','A'],'losers_before':[5,7,3],'losers_after':[5,7,6]})

    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps({'subject':'DS','count':len(items),'figures':items},ensure_ascii=False,indent=2))
    print(f'Generated {len(ONLY) if ONLY else len(items)} DS figures in SVG, PNG, PDF; manifest has {len(items)} figures')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',nargs='+',default=[],help='Regenerate only these figure IDs; still refresh the complete manifest')
    ONLY.update(parser.parse_args().only)
    main()
