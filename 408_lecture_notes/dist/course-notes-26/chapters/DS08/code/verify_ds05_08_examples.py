from pathlib import Path
from fractions import Fraction
from collections import deque
from functools import lru_cache
import heapq,json,math,hashlib
ROOT=Path(__file__).resolve().parents[3]
checks=[]
def check(ch,name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append({'chapter':ch,'name':name,'result':'passed','actual':str(actual),'expected':str(expected)})
def huffman(values,k=2):
 q=values[:];heapq.heapify(q);cost=0
 while len(q)>1:
  z=sum(heapq.heappop(q) for _ in range(k));cost+=z;heapq.heappush(q,z)
 return cost
check('DS05','nonleaf leaf count',1+3*20+2*10+1,82)
check('DS05','binary nodes with n2=8,n1=3',2*8+1+3,20)
check('DS05','3-ary min height 50',next(h for h in range(1,10) if (3**h-1)//2>=50),5)
check('DS05','binary min height 50',math.ceil(math.log2(51)),6)
for values,expected in [([3,4,5,6,8,10],90),([1,3,2,2,7],31),([80,10,8,2],130),([3,4,5],19)]:check('DS05','Huffman '+str(values),huffman(values),expected)
check('DS05','average answer code length',Fraction(130,100),Fraction(13,10))
check('DS05','remaining max-depth4 prefix slots',2**4-2**3-2**2,4)
def rebuild(pre,ino):
 if not pre:return None
 i=ino.index(pre[0]);return pre[0],rebuild(pre[1:1+i],ino[:i]),rebuild(pre[1+i:],ino[i+1:])
def order(t,kind):
 if t is None:return ''
 v,l,r=t
 return (v if kind=='pre' else '')+order(l,kind)+(v if kind=='in' else '')+order(r,kind)+(v if kind=='post' else '')
t=rebuild('DAEFBCHGI','EAFDHCBGI');check('DS05','pre/in rebuild middle',order(t,'in'),'EAFDHCBGI')
# BFS from the exact Wangdao 8-vertex lecture graph.
g={i:[] for i in range(1,9)}
for u,v in [(1,2),(1,5),(2,6),(3,4),(3,6),(3,7),(4,7),(4,8),(6,7),(7,8)]:g[u].append(v);g[v].append(u)
d={2:0};parent={2:-1};q=deque([2]);visit=[]
while q:
 u=q.popleft();visit.append(u)
 for v in sorted(g[u]):
  if v not in d:d[v]=d[u]+1;parent[v]=u;q.append(v)
check('DS06','BFS lecture visit',visit,[2,1,6,5,3,7,4,8])
check('DS06','BFS lecture d',[d[i] for i in range(1,9)],[1,0,2,3,2,1,2,3])
check('DS06','BFS lecture path',[parent[i] for i in range(1,9)],[2,-1,6,3,1,2,6,7])
I=10**9;A=[[0,6,13],[10,0,4],[5,I,0]];phases=[]
for k in range(3):
 for i in range(3):
  for j in range(3):A[i][j]=min(A[i][j],A[i][k]+A[k][j])
 phases.append([row[:] for row in A])
for i,e in enumerate([[[0,6,13],[10,0,4],[5,11,0]],[[0,6,10],[10,0,4],[5,11,0]],[[0,6,10],[9,0,4],[5,11,0]]]):check('DS06','Floyd phase '+str(i),phases[i],e)
edges=[(1,2,3),(1,3,8),(3,2,4),(2,4,9),(2,5,6),(3,5,10),(4,6,6),(5,6,9)];topo=[1,3,2,4,5,6];ve={i:0 for i in topo}
for u in topo:
 for a,b,w in edges:
  if a==u:ve[b]=max(ve[b],ve[a]+w)
vl={i:ve[6] for i in topo}
for u in topo[::-1]:
 for a,b,w in edges:
  if a==u:vl[a]=min(vl[a],vl[b]-w)
check('DS06','AOE ve',[ve[i] for i in range(1,7)],[0,12,8,21,18,27]);check('DS06','AOE vl',[vl[i] for i in range(1,7)],[0,12,8,21,18,27]);check('DS06','AOE activity margins',[vl[b]-w-ve[a] for a,b,w in edges],[9,0,0,0,0,0,0,0])
check('DS06','7 vertices ensure connected threshold',math.comb(6,2)+1,16)
check('DS06','51 vertices 21 edges max components',51-7+1,45)
probs=[Fraction(x,100) for x in [15,5,10,40,28,2]]
check('DS07','unequal probability ASL',sum((i+1)*p for i,p in enumerate(probs)),Fraction(367,100))
check('DS07','sorted probability ASL',sum((i+1)*p for i,p in enumerate(sorted(probs,reverse=True))),Fraction(218,100))
@lru_cache(None)
def bshapes(n,h,root=False):
 if h==1:return int(1<=n<=3)
 ways=0
 for keys in range(1,4):
  children=keys+1
  def distribute(remaining,k):
   if k==0:return int(remaining==0)
   return sum(bshapes(x,h-1)*distribute(remaining-x,k-1) for x in range(1,remaining+1))
  ways+=distribute(n-keys,children)
 return ways
check('DS07','4-order B-tree n=7 height2',bshapes(7,2,True),8);check('DS07','4-order B-tree n=7 height3',bshapes(7,3,True),1)
check('DS07','3-order B-tree max height 2047',max(h for h in range(1,15) if 2**h-1<=2047),11)
check('DS07','3-order B-tree min height 2047',next(h for h in range(1,15) if 3**h-1>=2047),7)
keys=[19,14,23,1,68,20,84,27,55,11,10,79];table=[None]*16;cost=[]
for key in keys:
 pos=key%13;c=1
 while table[pos] is not None:pos=(pos+1)%16;c+=1
 table[pos]=key;cost.append(c)
check('DS07','linear hash layout',table,[None,14,1,68,27,55,19,20,84,79,23,11,10,None,None,None])
check('DS07','linear success probes',cost,[1,1,1,2,1,1,3,4,3,1,3,9]);check('DS07','linear success ASL',Fraction(sum(cost),12),Fraction(5,2))
failure=[]
for start in range(13):
 pos=start;c=1
 while table[pos] is not None:c+=1;pos=(pos+1)%16
 failure.append(c)
check('DS07','failure by initial addresses',failure,[1,13,12,11,10,9,8,7,6,5,4,3,2]);check('DS07','failure ASL denominator13',Fraction(sum(failure),13),7)
a=[13,24,7,1,8,9,11,56,34,51,2,77,5]
for gap,e in [(5,[2,11,5,1,8,9,24,7,34,51,13,77,56]),(3,[1,7,5,2,8,9,24,11,34,51,13,77,56])]:
 for i in range(gap,len(a)):
  x=a[i];j=i-gap
  while j>=0 and a[j]>x:a[j+gap]=a[j];j-=gap
  a[j+gap]=x
 check('DS08','Shell gap '+str(gap),a[:],e)
a=[49,38,65,97,76,13,27,49];l=0;r=len(a)-1;p=a[l]
while l<r:
 while l<r and a[r]>=p:r-=1
 a[l]=a[r]
 while l<r and a[l]<=p:l+=1
 a[r]=a[l]
a[l]=p;check('DS08','first hole partition',a,[27,38,13,49,76,97,65,49])
check('DS08','two-way merge worst comparisons',huffman([10,35,40,50,60,200])-5,825)
check('DS08','4-way merge WPL',huffman([0,30,44,8,6,3,20,60,18,9,62,68,85],4),690)
check('DS08','16-block two-way external IO',32*(1+3),128);check('DS08','16-block four-way external IO',32*(1+2),96)
check('DS08','4500 records external IO',2*60*3,360)
seq=[51,94,37,92,14,63,15,99,48,56,23,60,31,17,43,8,90,166,100];active=seq[:4];heapq.heapify(active);frozen=[];idx=4;runs=[];run=[]
while active or frozen:
 if not active:runs.append(run);run=[];active=frozen;frozen=[];heapq.heapify(active)
 x=heapq.heappop(active);run.append(x)
 if idx<len(seq):
  y=seq[idx];idx+=1
  if y<x:frozen.append(y)
  else:heapq.heappush(active,y)
if run:runs.append(run)
check('DS08','replacement selection 19 records',runs,[[37,51,63,92,94,99],[14,15,23,31,48,56,60,90,166],[8,17,43,100]])
report={'checks':checks,'count':len(checks),'all_passed':True,'scope':'Independent recomputation of listed source/note examples; not a blanket proof of all content.','content_sha256':{c:hashlib.sha256((ROOT/'chapters'/c/'content.md').read_bytes()).hexdigest() for c in ['DS05','DS06','DS07','DS08']}}
path=ROOT/'sources/reviews/ds05-08-numerical.json';path.parent.mkdir(exist_ok=True,parents=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(str(len(checks))+' independent numerical/trace checks passed')
