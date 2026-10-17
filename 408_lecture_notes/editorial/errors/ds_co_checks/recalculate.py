"""数值与状态交叉核验。只给实际检查的题置位，不从文件存在推定正确。"""
from pathlib import Path
import json,math,heapq,collections,struct,csv
R=Path('/workspace/408_lecture_notes/editorial/errors');checks=[]
def ck(ids,label,observed,expected):
 assert observed==expected,(label,observed,expected)
 checks.append({'ids':['ERR-'+s for s in ids.split()],'calculation':label,'observed':observed,'expected':expected,'passed':True})
# Count iterations directly for nontrivial n, retaining values rather than testing an asymptotic label alone.
tri=[];sq=[];geo=[]
for n in [0,1,2,10,100,10000]:
 i=0;s=0
 while s<n:i+=1;s+=i
 tri.append([n,i,s]);assert (i==0 and n==0) or ((i-1)*i//2<n<=s)
 x=0
 while n>=(x+1)*(x+1):x+=1
 sq.append([n,x]);assert x==math.isqrt(n)
 i=1;c=0
 while i<n:c+=i;i*=2
 geo.append([n,c]);assert c==(0 if n<=1 else 2**((n-1).bit_length())-1)
ck('DS-1.2-015','循环实跑：n、次数、结束sum',tri,[[0,0,0],[1,1,1],[2,2,3],[10,4,10],[100,14,105],[10000,141,10011]])
ck('DS-1.2-016','平方条件循环实跑：n、次数',sq,[[0,0],[1,1],[2,1],[10,3],[100,10],[10000,100]])
ck('DS-1.2-017','内层总次数等比求和实跑',geo,[[0,0],[1,0],[2,1],[10,15],[100,127],[10000,16383]])
def stack_depth(target):
 inp=iter('abcdefg');st=[];depth=0;trace=[]
 for c in target:
  while not st or st[-1]!=c:
   x=next(inp,None)
   if x is None:return None
   st.append(x);depth=max(depth,len(st));trace.append(['push',x,''.join(st)])
  st.pop();trace.append(['pop',c,''.join(st)])
 return depth,trace
ck('DS-3.1-026','原做题本重复e序列不可由abcdefg各一次生成',stack_depth('bdefeag'),None)
maxdepth,tr=stack_depth('bdcfeag');ck('DS-3.1-026','原书恢复序列bdcfeag的最小容量',maxdepth,3);checks[-1]['trace']=tr
ck('DS-3.2-006','(3-8+21)%21',(3-8+21)%21,16)
def F(n):
 if n<=3:return 1,1
 a,c=F(n-2);b,d=F(n-4);return a+b+1,c+d+1
ck('DS-3.3-006','F(8)返回值与调用次数',list(F(8)),[9,9])
trace=[]
def func(x):
 trace.append(x)
 return 2 if x<=3 else func(x-2)+func(x-4)
func(func(5));ck('DS-3.3-007','调用进入顺序',trace,[5,3,1,4,2,0])
# Enumerated element positions validate the exact index conventions.
low=[(i,j) for i in range(9) for j in range(i+1)]
ck('DS-3.4-003','下三角0基对角下标',[low.index((i,i)) for i in range(9)],[i*(i+3)//2 for i in range(9)])
tri100=[(i,j) for i in range(1,101) for j in range(1,101) if abs(i-j)<=1]
ck('DS-3.4-006','三对角数组1基：A[66][65]',tri100.index((66,65))+1,195)
ck('DS-3.4-011','三对角数组0基：M[30][30]',tri100.index((30,30)),87)
up12=[(i,j) for i in range(1,13) for j in range(i,13)]
ck('DS-3.4-013','上三角12阶按行0基：m6,6',up12.index((6,6)),50)
up10=[(i,j) for j in range(1,11) for i in range(1,j+1)]
ck('DS-3.4-014','上三角10阶按列0基：m7,2=m2,7',up10.index((2,7)),22)
ck('DS-5.1-009','树叶数1+1+2×10+3×20',1+1+2*10+3*20,82)
h=[3,4,5,6,8,10];heapq.heapify(h);merges=[]
while len(h)>1:
 a=heapq.heappop(h);b=heapq.heappop(h);heapq.heappush(h,a+b);merges.append([a,b,a+b])
ck('DS-5.5-022','哈夫曼WPL/总权',sum(t[2] for t in merges)/36,2.5);checks[-1]['trace']=merges
ck('DS-6.1-011','21边集中于K7后连通分量',51-7+1,45)
ck('DS-6.1-016','最大不连通K6+孤立点再增1边',math.comb(6,2)+1,16)
# Enumerate all reachable directions for the inspected SCC figure.
ad={'A':['C'],'B':['A','D','E'],'C':['A','D'],'D':['A','E'],'E':['C']}
def reachable(a):
 seen={a};q=[a]
 while q:
  v=q.pop()
  for w in ad[v]:
   if w not in seen:seen.add(w);q.append(w)
 return seen
reach={v:reachable(v) for v in ad};groups=[];left=set(ad)
while left:
 v=min(left);g=sorted(w for w in left if w in reach[v] and v in reach[w]);groups.append(g);left-=set(g)
ck('DS-6.1-012','有向图强连通分量',groups,[['A','C','D','E'],['B']])
def dijk(edges,start,n,undirected=False):
 ad={i:[] for i in range(1,n+1)}
 for u,v,w in edges:
  ad[u].append((v,w))
  if undirected:ad[v].append((u,w))
 ds={i:math.inf for i in ad};ds[start]=0;prev={};done=set();states=[]
 while len(done)<n:
  u=min((i for i in ad if i not in done),key=lambda i:(ds[i],i));done.add(u)
  for v,w in ad[u]:
   if v not in done and ds[u]+w<ds[v]:ds[v]=ds[u]+w;prev[v]=u
  states.append({'u':u,'dist':[None if ds[i]==math.inf else ds[i] for i in ad]})
 return ds,prev,states
E=[(1,2,10),(1,3,2),(3,4,2),(3,6,11),(2,5,1),(4,5,4),(4,6,6),(5,7,7),(6,7,3)]
ds,p,st=dijk(E,1,7,True);path=[7]
while path[-1]!=1:path.append(p[path[-1]])
ck('DS-6.4-009','最短距离和路径',[ds[7],list(reversed(path))],[13,[1,3,4,6,7]])
E=[(1,5,6),(1,2,26),(1,3,3),(5,2,15),(5,3,6),(5,4,8),(4,2,1),(4,3,6),(3,2,22)]
ds,p,st=dijk(E,1,5);ck('DS-6.4-044','确定起点后第二个顶点时dist2..5',st[2]['dist'][1:],[21,3,14,6]);checks[-1]['trace']=st[:3]
E=[(1,2,'a',3),(1,3,'b',8),(2,4,'c',9),(3,2,'d',4),(2,5,'e',6),(3,5,'f',10),(4,6,'g',6),(5,6,'h',9)]
ad=collections.defaultdict(list)
for u,v,a,w in E:ad[u].append((v,a,w))
paths=[]
def walk(v,acts,t):
 if v==6:paths.append([acts,t]);return
 for z,a,w in ad[v]:walk(z,acts+a,t+w)
walk(1,'',0);mx=max(p[1] for p in paths);crit=sorted(a for a,t in paths if t==mx)
ck('DS-6.4-031','关键路径与工期',[crit,mx],[['bdcg','bdeh','bfh'],27]);checks[-1]['trace']=paths
ck('DS-6.4-031','选项活动集合覆盖全部关键路径',[all(set(p)&set(a) for p in crit) for a in ['ce','dc','fd','fh']],[False,False,True,False])
def binary_path(seq,target):
 lo=0;hi=len(seq)-1;tr=[]
 while lo<=hi:
  md=(lo+hi)//2;tr.append(md)
  if seq[md]==target:break
  if seq[md]<target:lo=md+1
  else:hi=md-1
 return tr
ck('DS-7.2-009','折半查找A11的1基比较下标',[i+1 for i in binary_path(list(range(1,12)),11)],[6,9,10,11])
s=list('bcdefgqrst');ck('DS-7.2-011','比较关键字',[s[i] for i in binary_path(s,'b')],['f','c','b'])
ck('DS-7.2-020','16项所有失败间隙的最多比较',max(len(binary_path(list(range(0,32,2)),v)) for v in range(-1,33,2)),5)
ck('DS-7.4-009','2047关键字3阶B树最大/最小层数',[math.floor(math.log2(2047+1)),math.ceil(math.log(2047+1,3))],[11,7])
ck('DS-7.5-014','线性探测49最终地址',next(a%14 for a in range(49%11,49%11+14) if a%14 not in [4,5,6,7]),8)
table=[None]*5
for k in [2022,12,25]:
 j=(k+4)%5
 while table[j] is not None:j=(j+1)%5
 table[j]=k
table[table.index(25)]='DEL';lens=[]
for s in range(5):
 c=1;j=s
 while table[j] is not None:c+=1;j=(j+1)%5
 lens.append(c)
ck('DS-7.5-023','删除标记后的各起点失败长度与ASL',[lens,sum(lens)/5],[[1,3,2,1,2],1.8])
a=[13,24,7,1,8,9,11,56,34,51,2,77,5];states=[]
for gap in [5,3]:
 for i in range(gap,len(a)):
  t=a[i];j=i
  while j>=gap and a[j-gap]>t:a[j]=a[j-gap];j-=gap
  a[j]=t
 states.append(a[:])
ck('DS-8.2-012','希尔排序5、3两趟结果',states[1],[1,7,5,2,8,9,24,11,34,51,13,77,56]);checks[-1]['trace']=states
def pop_count(h,small):
 a=h[:];a[0]=a.pop();cnt=0;i=0;trace=[]
 while 2*i+1<len(a):
  l=2*i+1;r=l+1;j=l
  if r<len(a):
   cnt+=1;trace.append([a[l],a[r]])
   if (a[r]<a[l]) if small else (a[r]>a[l]):j=r
  cnt+=1;trace.append([a[i],a[j]])
  if (a[i]<=a[j]) if small else (a[i]>=a[j]):break
  a[i],a[j]=a[j],a[i];i=j
 return cnt,a,trace
for name,h,small in [('DS-8.4-013',[62,34,53,12,8,46,22],False),('DS-8.4-017',[8,15,10,21,34,16,12],True)]:
 c,a,tr=pop_count(h,small);ck(name,'堆顶删除的关键字比较次数',c,3);checks[-1]['trace']=tr
# Composition: bit interpretation, memory and timing calculations.
ck('CO-1.3-014','局部加速90/1.5+10',90/1.5+10,70.0)
ck('CO-2.1-001','137.5转8进制的整数与小数位',[oct(137)[2:],int(.5*8)],['211',4])
ck('CO-2.1-027','65530零扩展后的32位十六进制',f'{65530:08X}','0000FFFA')
ck('CO-2.1-034','-32767转换为32位unsigned',(-32767)%(1<<32),(1<<32)-(1<<15)+1)
ck('CO-2.2-018','减法器A/B/Cin',[f'{69:08b}',f'{(~38)&255:08b}',1],['01000101','11011001',1])
ck('CO-2.2-029','-33-65的补码',f'{(-33-65)%(1<<32):08X}','FFFFFF9E')
for name,x,y,ex in [('CO-2.2-031',0xffffffff,0xfffffff0,[0,0]),('CO-2.2-032',10,(-20)%(1<<32),[1,0])]:
 signed=lambda z:z if z<1<<31 else z-(1<<32)
 z=signed(x)-signed(y);ck(name,'CF借位、OF有符号范围',[int(x<y),int(not -(1<<31)<=z<(1<<31))],ex)
u=0xf0000000;v={'浮':struct.unpack('>f',u.to_bytes(4,'big'))[0],'原':-(u&0x7fffffff),'补':u-(1<<32),'移':u-(1<<31)}
ck('CO-2.3-007','同位串四解释从大到小',''.join(sorted(v,key=v.get,reverse=True)),'移补原浮');checks[-1]['values']=v
ck('CO-2.3-021','b[1][2]地址及低字节',[0x8049820+(1*4+2)*2,(-6)%256],[0x804982c,0xfa])
ck('CO-2.3-030','record.a低字节和record.c地址',[273%256,hex(0xc008+6)],[0x11,'0xc00e'])
ck('CO-2.3-045','employee[1].id中56H地址',hex(0xa0b0+20+1),'0xa0c5')
ck('CO-3.2-001','SRAM地址/数据引脚',int(math.log2(1024))+8,18)
ck('CO-3.2-032','DRAM地址复用后的引脚',22//2+8,19)
ck('CO-3.3-001','字扩展/位扩展',[64//16,8//1],[4,8])
ck('CO-3.3-008','地址区间容量/单片容量',(0xcffff-0x90000+1)//(16*1024),16)
ck('CO-3.3-009','按字编址的片选111首末地址',[hex(7<<15),hex((8<<15)-1)],['0x38000','0x3ffff'])
ck('CO-3.3-012','64MB按字节编址MAR位数',(64*1024*1024).bit_length()-1,26)
ck('CO-3.4-011','磁盘平均存取时间ms四舍五入',round(8+(60/7200/2)*1000+(60/7200/1000)*1000,1),12.2)
ck('CO-3.5-023 CO-3.5-024','非突发/突发的缺失损失周期',[8*(1+8+1),1+8+8],[80,17])
seq=[0,4,8,2,0,6,8,6,4,8]
def lru(set_fn):
 groups=[[],[]];hits=0;trace=[]
 for b in seq:
  s=set_fn(b);g=groups[s];hit=b in g;hits+=hit
  if hit:g.remove(b)
  elif len(g)==2:g.pop(0)
  g.append(b);trace.append({'block':b,'set':s,'hit':hit,'groups':[v[:] for v in groups]})
 return hits,trace
h1,t1=lru(lambda b:b%2);h2,t2=lru(lambda b:b//2%2)
ck('CO-3.5-030','常见分组/原书分组的命中次数',[h1,h2],[1,3]);checks[-1]['standard_trace']=t1;checks[-1]['book_trace']=t2
ck('CO-3.5-031','含tag/valid/dirty的Cache总容量Kbit',(4*1024*32+1024*(18+1+1))//1024,148)
ck('CO-3.5-032','读写均计的缺失率',100*(1000//4)/(1000*2),12.5)
ck('CO-3.5-034','Cache每行总位数',32*8+(32-5-10)+1+1,275)
ck('CO-3.5-035','并行比较器个数/位数',[8,32-6-6],[8,20])
ck('CO-3.6-019','TLB标记位数',32-10-3,19)
ck('CO-4.1-012','分层扩展操作码指令总条数',15+15+16,46)
ck('CO-4.2-011','小端取16位字',hex(0x56+(0x78<<8)),'0x7856')
ck('CO-4.2-012','按字编址相对跳转PC',hex(0x4000+1+6),'0x4007')
ck('CO-4.2-015','指令剩余位移位数及范围',[16-math.ceil(math.log2(97))-math.ceil(math.log2(6)),-32,31],[6,-32,31])
ck('CO-4.2-019','补码位移+基址+LSB偏移',hex((0xc0000000-256+3)%(1<<32)),'0xbfffff03')
ck('CO-4.3-006','x86 jle下一条地址加位移',hex(0x804846e+0x0d),'0x804847b')
ck('CO-5.4-006','4个互斥微命令含不操作状态的字段位数',math.ceil(math.log2(4+1)),3)
ck('CO-6.1-016','总线MB/s',4*10/2,20.0)
ck('CO-6.1-022','3通道有效带宽GB/s四舍五入',round(3*1333*8/1000),32)
ck('CO-6.1-023','QPI双向有效带宽GB/s',2.4*2*2*2,19.2)
ck('CO-6.1-025','1333MT/s乘8B的GB/s四舍五入',round(1333*8/1000,2),10.66)
ck('CO-6.2-010','突发读块有效MB/s',round(32*50/(1+3+8),1),133.3)
ck('CO-6.2-011','每秒线路位数',480*(1+7+1+1),4800)
ck('CO-6.2-020','非突发读32B耗时ns',(32//8)*(1+6+1),32)
ck('CO-7.3-039','周期中断CPU实际占用比',100/400,.25)
(R/'ds_co_checks'/'recalculation_results.json').write_text(json.dumps({'method':'运行此脚本独立计算数值/状态；不覆盖未列题。','checks':checks,'distinct_question_count':len(set(z for c in checks for z in c['ids']))},ensure_ascii=False,indent=2))
d=json.load(open(R/'ds_co_errors.json'));by=collections.defaultdict(list)
for n,c in enumerate(checks,1):
 for rid in c['ids']:by[rid].append(n)
for x in d['records']:
 x['independent_calculation_checked']=x['id'] in by;x['independent_calculation_check_numbers']=by.get(x['id'],[]);x['independent_calculation_scope']='见ds_co_checks/recalculation_results.json指定数值或轨迹；不将数值检查扩写成整题来源或所有选项已核验。' if x['id'] in by else '未在本轮代码复算；原书答案字母目验单独登记。'
(R/'ds_co_errors.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('checks',len(checks),'distinct questions',len(by),'all passed')
