import heapq,json,math
from pathlib import Path
checks=[]
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append({'name':name,'actual':actual,'expected':expected,'passed':True})
# A local-child-only check misses an ancestor's range constraint.
tree=(10,(5,None,(12,None,None)),None)
def local(t):
 if not t:return True
 k,l,r=t
 return (not l or l[0]<k) and (not r or r[0]>k) and local(l) and local(r)
def ranged(t,lo=-math.inf,hi=math.inf):
 if not t:return True
 k,l,r=t;return lo<k<hi and ranged(l,lo,k) and ranged(r,k,hi)
check('BST直接孩子合法但祖先区间失败',[local(tree),ranged(tree)],[True,False])
N=[0,1]
for h in range(2,8):N.append(1+N[-1]+N[-2])
check('AVL最少结点数N(0..7)',N,[0,1,2,4,7,12,20,33])
check('5阶B树高3的最少/最多关键字',[2*3**2-1,5**3-1],[17,124])
check('3阶B树2047项的高度范围',[math.ceil(math.log(2048,3)),math.floor(math.log2(2048))],[7,11])
states=['empty',2022,12,'empty','deleted'];cost=[]
for start in range(5):
 for step in range(5):
  if states[(start+step)%5]=='empty':cost.append(step+1);break
check('含墓碑失败探查成本与ASL',[cost,sum(cost)/5],[[1,3,2,1,2],1.8])
table=[None]*11
for key in [20,3,11,18,9,14,7]:
 base=key*3%11
 for j in range(11):
  idx=(base+j*j)%11
  if table[idx] is None:table[idx]=key;break
path=[];base=8*3%11
for j in range(11):
 idx=(base+j*j)%11;path.append(idx)
 if table[idx] is None:break
check('二次探查8的失败路径',path,[2,3,6,0,7])
# Stable insertion versus a distant swap in selection.
records=[(2,'a'),(2,'b'),(1,'x')]
a=records.copy()
for i in range(len(a)-1):
 pick=min(range(i,len(a)),key=lambda j:a[j][0]);a[i],a[pick]=a[pick],a[i]
check('简单选择破坏相等记录次序',[x[1] for x in a],['x','b','a'])
a=[13,24,7,1,8,9,11,56,34,51,2,77,5]
for d in [5,3]:
 for i in range(d,len(a)):
  x=a[i];j=i-d
  while j>=0 and a[j]>x:a[j+d]=a[j];j-=d
  a[j+d]=x
check('两趟希尔排序',a,[1,7,5,2,8,9,24,11,34,51,13,77,56])
check('60块10段5路含初始生成I/O',2*60*(1+2),360)
def huffman(weights,k):
 weights=list(weights);padding=(-(len(weights)-1))%(k-1);weights.extend([0]*padding);heapq.heapify(weights);sums=[]
 while len(weights)>1:
  s=sum(heapq.heappop(weights) for _ in range(k));sums.append(s);heapq.heappush(weights,s)
 return padding,sums,sum(sums)
check('4路最佳归并补零、合并权和与WPL',huffman([30,44,8,6,3,20,60,18,9,62,68,85],4),[1,[17,64,196,413],690] if False else (1,[17,64,196,413],690))
check('二路最佳归并的最坏比较',huffman([10,35,40,50,60,200],2)[2]-5,825)
# Replacement selection, independent active/frozen heaps.
seq=[51,94,37,92,14,63,15,99,48,56,23,60,31,17,43,8,90,166,100];m=4
active=seq[:m];heapq.heapify(active);frozen=[];pos=m;runs=[];run=[]
while active or frozen:
 if not active:runs.append(run);run=[];active,frozen=frozen,[];heapq.heapify(active)
 x=heapq.heappop(active);run.append(x)
 if pos<len(seq):
  y=seq[pos];pos+=1
  heapq.heappush(active if y>=x else frozen,y)
if run:runs.append(run)
check('置换选择三段状态',runs,[[37,51,63,92,94,99],[14,15,23,31,48,56,60,90,166],[8,17,43,100]])
Path(__file__).with_name('DS-independent-numeric.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(len(checks),'independent DS numeric/record/state examples passed')
