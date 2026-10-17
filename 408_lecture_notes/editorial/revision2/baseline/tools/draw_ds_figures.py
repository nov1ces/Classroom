#!/usr/bin/env python3
"""Generate editable DS teaching diagrams; needs only Python and Inkscape."""
from pathlib import Path
from html import escape
import math, json, subprocess, shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
MANIFEST=ROOT/'editorial/full/DS/figure_manifest.json'
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
def save(name,svg,title,data):
    p=OUT/f'{name}.svg';p.write_text(svg.content())
    exe=shutil.which('inkscape')
    if not exe: raise RuntimeError('Inkscape is required for SVG → PNG/PDF')
    for ext in ['png','pdf']:
        cmd=[exe,str(p),f'--export-type={ext}',f'--export-filename={OUT/(name+"."+ext)}']
        if ext=='png':cmd+=['--export-width=1800']
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    items.append({'id':name,'title':title,'svg':f'figures/{name}.svg','png':f'figures/{name}.png','pdf':f'figures/{name}.pdf','source':'tools/draw_ds_figures.py','data':data,'semantics':'实线为原有/已生效关系，虚线为待改关系、线索或冻结标记；文字标签在灰度打印中保留含义。'})

def tree(s,pos,edges,labels=None,fill=None):
    for a,b in edges:s.edge(pos[a],pos[b])
    for k,(x,y) in pos.items():s.circle(x,y,(labels or {}).get(k,k),fill=(fill or {}).get(k,'white'))

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

    s=SVG(h=530)
    for a,b in edges:s.edge(pos[a],pos[b])
    for a,b,route in [('D','B',[(160,360),(120,410),(280,410),(280,230)]),('E','B',[(400,360),(420,390),(315,250)]),('E','A',[(430,330),(530,330),(530,100)]),('C','A',[(690,200),(610,200),(520,95)]),('F','C',[(840,360),(900,400),(720,400),(720,230)])]:s.path(route)
    for k,p in pos.items():s.circle(*p,k)
    s.text(110,470,'D左：空前驱',22);s.text(810,470,'F右：空后继',22)
    s.text(500,515,'实线=孩子；虚线=中序线索；边界目标可改为头结点',22)
    save('DS_06_inorder_threads',s,'中序线索与孩子链接',{'inorder':'DBEACF','threads':{'D_left':None,'D_right':'B','E_left':'B','E_right':'A','C_left':'A','F_left':'C','F_right':None}})

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

    s=SVG(h=690)
    for col,(title,before,after) in enumerate([('LL：右旋','30(20(10,∅),∅)','20(10,30)'),('RR：左旋','10(∅,20(∅,30))','20(10,30)')]):
        cx=250+500*col;s.text(cx,35,title,25,bold=True)
        if col==0:p={'30':(cx+70,110),'20':(cx,220),'10':(cx-70,330)};es=[('30','20'),('20','10')]
        else:p={'10':(cx-70,110),'20':(cx,220),'30':(cx+70,330)};es=[('10','20'),('20','30')]
        tree(s,p,es);s.line(cx,375,cx,420,True)
        p={'20':(cx,470),'10':(cx-110,590),'30':(cx+110,590)};tree(s,p,[('20','10'),('20','30')])
    s.text(500,670,'LR：先左旋左孩子，再右旋根；RL按左右对称操作',23)
    save('DS_14_avl_rotations',s,'AVL单旋与双旋的方向',{'LL':[30,20,10],'RR':[10,20,30],'after':[20,10,30],'double_rotation':'LR: child-left then root-right; RL: child-right then root-left'})

    s=SVG(h=720)
    stages=[('插入50：第一次根分裂',[([30],500,110),([20],300,220),([50],700,220)],[(0,1),(0,2)]),('插入60：52从叶提升',[([30,52],500,350),([20],230,460),([50],500,460),([60],770,460)],[(0,1),(0,2),(0,3)]),('插入70：根再次分裂',[([52],500,580),([30],300,660),([68],700,660)],[(0,1),(0,2)])]
    for title,nodes,es in stages:
        s.text(30,nodes[0][2]-52,title,23,'start',True)
        for a,b in es:
            aa,xx,yy=nodes[a];bb,xxx,yyy=nodes[b];s.line(xx,yy+22,xxx,yyy-22,False)
        for keys,x,y in nodes:s.rect(x-65,y-23,130,46,' | '.join(map(str,keys)))
    # Last level expanded in its own following band to keep every label readable.
    s.h=850
    for x,l,parentx in [(170,20,300),(390,50,300),(610,60,700),(830,70,700)]:
        s.line(parentx,683,x,755);s.rect(x-55,755,110,46,str(l))
    save('DS_15_btree_split',s,'3阶B树插入时的提升与根分裂',{'order':3,'insert':[20,30,50,52,60,68,70],'final_root':[52],'final_internal':[[30],[68]],'leaves':[[20],[50],[60],[70]]})

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
    print(f'Generated {len(items)} DS figures in SVG, PNG, PDF')

if __name__=='__main__':main()
