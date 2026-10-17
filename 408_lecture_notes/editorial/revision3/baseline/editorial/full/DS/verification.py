#!/usr/bin/env python3
"""Independent executable checks for the DS manuscript, using delivered data only."""
from pathlib import Path
from collections import deque, Counter
from copy import deepcopy
from bisect import bisect_left
import itertools as it, math, heapq, json, random

HERE=Path(__file__).resolve().parent
RESULTS=[]
def record(id,task,actual,expected,scope):
    assert actual==expected,(id,actual,expected)
    RESULTS.append({'id':id,'task':task,'actual':actual,'expected':expected,'status':'PASS','scope':scope})

def min_stack_capacity(inp,out):
    stack=[];i=0;mx=0
    for x in out:
        while (not stack or stack[-1]!=x) and i<len(inp):
            stack.append(inp[i]);i+=1;mx=max(mx,len(stack))
        if not stack or stack.pop()!=x:return None
    return mx

def next_table(p):
    # Definition-based enumeration, independent of the linear preprocessing code.
    a=[-1]
    for j in range(1,len(p)):
        a.append(max(k for k in range(j) if p[:k]==p[j-k:j]))
    return a

def kmp(t,p):
    if not p:return 0
    nxt=next_table(p);i=j=0
    while i<len(t) and j<len(p):
        if j==-1 or t[i]==p[j]:i+=1;j+=1
        else:j=nxt[j]
    return i-len(p) if j==len(p) else -1

def nextval(p):
    nxt=next_table(p);v=[-1]*len(p)
    for j in range(1,len(p)):
        k=nxt[j];v[j]=v[k] if k>=0 and p[j]==p[k] else k
    return v

def majority(a):
    c=0;n=0
    for x in a:
        if n==0:c=x;n=1
        elif c==x:n+=1
        else:n-=1
    return c if a.count(c)>len(a)//2 else -1

class N:
    def __init__(self,x,l=None,r=None):self.x=x;self.l=l;self.r=r
def seq(t,mode):
    if not t:return []
    a=seq(t.l,mode);b=seq(t.r,mode)
    return [t.x]+a+b if mode=='pre' else a+[t.x]+b if mode=='in' else a+b+[t.x]
def post_iter(t):
    s=[];p=t;last=None;out=[]
    while p or s:
        if p:s.append(p);p=p.l
        else:
            q=s[-1]
            if q.r and last is not q.r:p=q.r
            else:out.append(q.x);last=s.pop()
    return out

def topo_orders(n,edges):
    return [p for p in it.permutations(range(n)) if all(p.index(a)<p.index(b) for a,b in edges)]
def unique_kahn(n,edges):
    deg=[0]*n;g=[[] for _ in range(n)]
    for u,v in edges:g[u].append(v);deg[v]+=1
    used=set()
    for _ in range(n):
        z=[v for v in range(n) if v not in used and deg[v]==0]
        if len(z)!=1:return False
        used.add(z[0])
        for v in g[z[0]]:deg[v]-=1
    return True

def dijkstra(n,edges,source):
    g=[[] for _ in range(n)];d=[math.inf]*n;d[source]=0;used=set();trace=[]
    for a,b,w in edges:g[a].append((b,w))
    for _ in range(n):
        remaining=[v for v in range(n) if v not in used]
        u=min(remaining,key=lambda v:d[v])
        if math.isinf(d[u]):break
        used.add(u)
        for v,w in g[u]:
            if v not in used:d[v]=min(d[v],d[u]+w)
        trace.append((u,list(d)))
    return d,trace

def all_path_dist(n,edges,s):
    g=[[] for _ in range(n)]
    for a,b,w in edges:g[a].append((b,w))
    best=[math.inf]*n
    def dfs(u,d,seen):
        best[u]=min(best[u],d)
        for v,w in g[u]:
            if v not in seen:dfs(v,d+w,seen|{v})
    dfs(s,0,{s});return best

def path_lengths(edges):
    g={i:[] for i in range(1,7)}
    for a,b,w,k in edges:g[a].append((b,w,k))
    result=[]
    def dfs(u,d,word):
        if u==6:result.append((word,d))
        for v,w,k in g[u]:dfs(v,d+w,word+k)
    dfs(1,0,'');return result

def height(t):return 0 if not t else 1+max(height(t.l),height(t.r))
def rotl(t):
    u=t.r;t.r=u.l;u.l=t;return u
def rotr(t):
    u=t.l;t.l=u.r;u.r=t;return u
def avl(t,x):
    if not t:return N(x)
    if x<t.x:t.l=avl(t.l,x)
    else:t.r=avl(t.r,x)
    b=height(t.l)-height(t.r)
    if b>1:
        if x>t.l.x:t.l=rotl(t.l)
        return rotr(t)
    if b< -1:
        if x<t.r.x:t.r=rotr(t.r)
        return rotl(t)
    return t
def shape(t):
    if not t:return None
    return [t.x,shape(t.l),shape(t.r)]
def validate_avl(t):
    if not t:return
    assert abs(height(t.l)-height(t.r))<=1
    a=seq(t,'in');assert a==sorted(a)
    validate_avl(t.l);validate_avl(t.r)

def btree_count(order,keys,height_):
    # Count shapes by root keys and ordered equal-height child compositions.
    t=math.ceil(order/2)
    def count(n,h,isroot):
        lo=1 if isroot else t-1;total=0
        if h==1:return int(lo<=n<=order-1)
        for k in range(lo,order):
            def compositions(s,c,prefix=()):
                if c==0:
                    if s==0:yield prefix
                    return
                for z in range(1,s+1):yield from compositions(s-z,c-1,prefix+(z,))
            for c in compositions(n-k,k+1):
                total+=math.prod(count(z,h-1,False) for z in c)
        return total
    return count(keys,height_,True)

def number_tree(t):
    return None if t is None else N(t[0],number_tree(t[1]),number_tree(t[2]))

def plain_bst_insert(t,x):
    if t is None:return N(x)
    if x<t.x:t.l=plain_bst_insert(t.l,x)
    else:t.r=plain_bst_insert(t.r,x)
    return t

def rotate_at(t,key,direction):
    if t.x==key:return rotl(t) if direction=='left' else rotr(t)
    if key<t.x:t.l=rotate_at(t.l,key,direction)
    else:t.r=rotate_at(t.r,key,direction)
    return t

def avl_state_audit(t):
    inorder=seq(t,'in');assert inorder==sorted(set(inorder))
    nodes=[]
    def walk(u):
        if u is None:return
        nodes.append({'key':u.x,'height':height(u),'balance':height(u.l)-height(u.r)})
        walk(u.l);walk(u.r)
    walk(t)
    return {'inorder':inorder,'height':height(t),'nodes':nodes}

def btree_keys(t):
    if not t['children']:return list(t['keys'])
    out=[]
    for i,key in enumerate(t['keys']):out+=btree_keys(t['children'][i])+[key]
    return out+btree_keys(t['children'][-1])

def audit_btree(t,order,temporary=()):
    """Strictly validate every bound; only explicitly named transient nodes may
    have the specified overflow/underflow. Child counts/order/depth never waive."""
    exceptions={tuple(v['path']):v['keys'] for v in temporary};seen=set();leaves=[];nodes=[]
    def walk(u,path=(),low=-math.inf,high=math.inf,depth=1):
        keys=u['keys'];children=u['children'];n=len(keys)
        assert keys==sorted(set(keys)) and all(low<key<high for key in keys),(path,keys,low,high)
        lower=1 if not path else math.ceil(order/2)-1
        if path in exceptions:
            assert n==exceptions[path] and not lower<=n<=order-1,(path,n)
            seen.add(path)
        else:assert lower<=n<=order-1,(path,n,lower,order-1)
        assert not children or len(children)==n+1,(path,n,len(children))
        if children:
            bounds=[low]+keys+[high]
            for i,c in enumerate(children):walk(c,path+(i,),bounds[i],bounds[i+1],depth+1)
        else:leaves.append(depth)
        nodes.append({'path':list(path),'keys':keys,'key_count':n,'child_count':len(children),'depth':depth})
    walk(t);assert seen==set(exceptions)
    assert len(set(leaves))==1,leaves
    inorder=btree_keys(t);assert inorder==sorted(set(inorder))
    return {'inorder':inorder,'key_count':len(inorder),'height':leaves[0],'nodes':nodes,'temporary_violations':list(temporary)}

def insert_btree_trace(initial,key,order):
    root=deepcopy(initial);trace=[]
    def insert(u):
        i=bisect_left(u['keys'],key)
        if u['children']:
            split=insert(u['children'][i])
            if split:
                promoted,right=split;u['keys'].insert(i,promoted);u['children'].insert(i+1,right)
        else:u['keys'].insert(i,key)
        if len(u['keys'])==order:
            trace.append(deepcopy(root));middle=order//2;promoted=u['keys'][middle]
            right={'keys':u['keys'][middle+1:],'children':u['children'][middle+1:] if u['children'] else []}
            u['keys']=u['keys'][:middle]
            if u['children']:u['children']=u['children'][:middle+1]
            return promoted,right
        return None
    split=insert(root)
    if split:
        promoted,right=split;root={'keys':[promoted],'children':[root,right]}
    trace.append(deepcopy(root));return trace

def delete_btree_trace(initial,key,order):
    root=deepcopy(initial);trace=[];minimum=math.ceil(order/2)-1
    def fix(parent,i):
        child=parent['children'][i]
        if len(child['keys'])>=minimum:return
        if i and len(parent['children'][i-1]['keys'])>minimum:
            donor=parent['children'][i-1]
            child['keys'].insert(0,parent['keys'][i-1]);parent['keys'][i-1]=donor['keys'].pop()
            if donor['children']:child['children'].insert(0,donor['children'].pop())
        elif i+1<len(parent['children']) and len(parent['children'][i+1]['keys'])>minimum:
            donor=parent['children'][i+1]
            child['keys'].append(parent['keys'][i]);parent['keys'][i]=donor['keys'].pop(0)
            if donor['children']:child['children'].append(donor['children'].pop(0))
        else:
            if i==len(parent['children'])-1:i-=1
            left=parent['children'][i];right=parent['children'].pop(i+1)
            left['keys']+=[parent['keys'].pop(i)]+right['keys'];left['children']+=right['children']
        trace.append(deepcopy(root))
    def delete(u,x):
        i=bisect_left(u['keys'],x)
        if i<len(u['keys']) and u['keys'][i]==x:
            if not u['children']:
                u['keys'].pop(i);trace.append(deepcopy(root));return
            pred=u['children'][i]
            while pred['children']:pred=pred['children'][-1]
            replacement=pred['keys'][-1];u['keys'][i]=replacement
            delete(u['children'][i],replacement);fix(u,i)
        else:
            assert u['children'],x
            delete(u['children'][i],x);fix(u,i)
    delete(root,key)
    if not root['keys'] and root['children']:
        root=root['children'][0];trace.append(deepcopy(root))
    return trace

def stable_counting(records,range_size):
    counts=[0]*range_size
    for key,identity in records:counts[key]+=1
    frequencies=counts[:]
    for i in range(1,range_size):counts[i]+=counts[i-1]
    prefixes=counts[:];out=[None]*len(records)
    for item in reversed(records):
        counts[item[0]]-=1;out[counts[item[0]]]=item
    return frequencies,prefixes,out

def linear_table(vals,m,h):
    a=[None]*m;probes=[]
    for x in vals:
        j=h(x);p=[]
        while a[j] is not None:p.append(j);j=(j+1)%m
        p.append(j);a[j]=x;probes.append(p)
    return a,probes

def shell(a,gaps):
    a=list(a);trace=[]
    for d in gaps:
        for i in range(d,len(a)):
            x=a[i];j=i
            while j>=d and a[j-d]>x:a[j]=a[j-d];j-=d
            a[j]=x
        trace.append(list(a))
    return trace

def partition(a,l,r):
    x=a[l]
    while l<r:
        while l<r and a[r]>=x:r-=1
        a[l]=a[r]
        while l<r and a[l]<=x:l+=1
        a[r]=a[l]
    a[l]=x;return l
def quick(a,l,r):
    if l<r:
        p=partition(a,l,r);quick(a,l,p-1);quick(a,p+1,r)

def replace_select(a,m):
    it_=iter(a);active=list(it.islice(it_,m));heapq.heapify(active);frozen=[];runs=[];cur=[];events=[]
    while active:
        x=heapq.heappop(active);cur.append(x)
        try:y=next(it_)
        except StopIteration:y=None
        if y is not None:
            heapq.heappush(active if y>=x else frozen,y)
        events.append({'out':x,'new':y,'active':sorted(active),'frozen':sorted(frozen)})
        if not active:
            runs.append(cur);cur=[];active=frozen;frozen=[];heapq.heapify(active)
    return runs,events

def merge_cost(weights,k=2):
    a=list(weights);heapq.heapify(a);steps=[]
    extra=(-((len(a)-1)))%(k-1)
    for _ in range(extra):heapq.heappush(a,0)
    while len(a)>1:
        b=[heapq.heappop(a) for _ in range(k)];w=sum(b);steps.append((b,w));heapq.heappush(a,w)
    return sum(w for b,w in steps),steps

def main():
    counts=[]
    for n in range(1001):
        i=0;s=0
        while s<n:i+=1;s+=i
        assert s>=n and (i==0 or (i-1)*i//2<n)
        counts.append(i)
    record('DS-C01','2017累计和停止次数，n=0..1000',counts[100],14,'实际循环与最小三角数不等式逐项互证')
    sums=[]
    for n in range(2,1001):
        a=[];i=1
        while i<n:a.append(i);i*=2
        s=sum(a);assert n-1<=s<2*n;sums.append(s)
    record('DS-C02','2022倍增嵌套循环n=1000',sums[-1],1023,'逐轮次数之和；验证线性上下界，不只看层数')
    for n in range(2,30):
        for p in range(1,n):
            a=list(range(n));a[:p]=reversed(a[:p]);a[p:]=reversed(a[p:]);a.reverse()
            assert a==list(range(p,n))+list(range(p))
    record('DS-C03','三次逆置循环左移',True,True,'穷举n=2..29全部合法p，含p=1、p=n−1')
    for n in range(1,9):
        for a in it.product(range(3),repeat=n):
            c=Counter(a);expected=next((x for x,v in c.items() if v>n/2),-1)
            assert majority(list(a))==expected
    record('DS-C04','主元素候选加复核',True,True,'穷举长度1..8、值域0..2，与直接计数对照')
    record('DS-C05','2009栈最小容量',min_stack_capacity('abcdefg','bdcfeag'),3,'逐次压入弹出；原材料错误字符不进入计算')
    record('DS-C06','栈以cd开头的序列',[ ''.join(p) for p in it.permutations('abcd') if ''.join(p).startswith('cd') and min_stack_capacity('abcd',p) is not None],['cdba'],'枚举全部4!输出并模拟栈')
    record('DS-C07','循环队列A[21]长度',(3-8+21)%21,16,'直接按有效下标9..20、0..3另计16')
    record('DS-C08','共享栈相邻余量',4-2-1,1,'已用左0..2右4..7，剩单元3')
    def calls(n):return 1 if n<=3 else 1+calls(n-2)+calls(n-4)
    record('DS-C09','递归F(8)调用次数',calls(8),9,'数调用树结点，不以返回值代替次数')
    tri=[(i,j) for i in range(1,101) for j in range(1,101) if abs(i-j)<=1]
    record('DS-C10','2016三对角(30,30)位置',tri.index((30,30)),87,'枚举按行压缩坐标，与公式独立交叉')
    up=[(i,j) for j in range(1,11) for i in range(1,j+1)]
    record('DS-C11','2020对称上三角列优先',up.index((2,7)),22,'先对称转换(7,2)→(2,7)，再坐标枚举')
    up12=[(i,j) for i in range(1,13) for j in range(i,13)]
    record('DS-C12','2018上三角行优先',up12.index((6,6)),50,'正文方法变式去向的独立位置校验')
    record('DS-C13','多维数组地址',1000+((4-2)*4+(1+1))*4,1040,'单位字节；行宽4而非3')
    for n in range(2,10):
        coords=[(i,j) for j in range(1,n+1) for i in range(j,n+1)]
        for index,(i,j) in enumerate(coords):assert (j-1)*(2*n-j+2)//2+i-j+1==index+1
    record('DS-C14','下三角按列压缩公式',True,True,'n=2..9全部坐标，数组从1开始')
    s=[5,8,3,2]
    for op in ['+','-','*']:
        a=s.pop();b=s.pop();s.append(b+a if op=='+' else b-a if op=='-' else b*a)
    record('DS-C15','2018双栈表达式',s,[15],'按b op a实际弹栈')
    record('DS-C16','abaabc普通next',next_table('abaabc'),[-1,0,0,1,1,2],'定义枚举真前后缀，而非复制正文线性建表程序')
    record('DS-C17','aabaab普通next',next_table('aabaab'),[-1,0,1,0,1,2],'逐前缀枚举')
    nv=nextval('aabaab');record('DS-C18','aabaab修正next',nv,[-1,-1,1,-1,-1,1],'相同失配字符连续跳过')
    record('DS-C19','2024最大模式位移',max(j-x for j,x in enumerate(nv)),5,'所有失配位置完整比较')
    cases=0
    words=[''.join(p) for n in range(7) for p in it.product('ab',repeat=n)]
    pats=[''.join(p) for n in range(5) for p in it.product('ab',repeat=n)]
    for t in words:
        for p in pats:assert kmp(t,p)==t.find(p);cases+=1
    record('DS-C20','KMP与独立字符串查找一致',cases,3937,'穷举主串长度0..6、模式0..4，含空串与重叠边界')
    record('DS-C21','树度数求叶',1+3*20+2*10+1,82,'总度数=总节点数−1')
    record('DS-C22','3叉50结点最小高',next(h for h in range(1,10) if (3**h-1)//2>=50),5,'按每层最大容量枚举')
    selected={1,3,7,15,31,2,4,5,6,8}
    assert all(i==1 or i//2 in selected for i in selected)
    record('DS-C23','2020最坏顺序位置见证',[len(selected),max(selected),max(i.bit_length() for i in selected)],[10,31,5],'显式合法10节点形态，证明31位置可能被使用')
    t=N('A',N('B',N('D'),N('E')),N('C',None,N('F')))
    record('DS-C24','二叉树四序前三种',[''.join(seq(t,m)) for m in ['pre','in','post']],['ABDECF','DBEACF','DEBFCA'],'递归实际遍历')
    record('DS-C25','非递归后序与递归互证',post_iter(t),seq(t,'post'),'显式栈与last机制独立运行')
    record('DS-C26','4结点先序形态数',math.comb(8,4)//5,14,'卡特兰计数')
    w,steps=merge_cost([3,4,5,6,8,10]);record('DS-C27','2023哈夫曼WPL',[w,w/36],[90,2.5],'优先队列每轮重新取两个最小值')
    record('DS-C28','前缀编码剩余容量',len([x for x in it.product('01',repeat=4) if not ''.join(x).startswith(('1','01'))]),4,'枚举长度4全部码位，扣除被占子树')
    edges=[('a','b'),('a','c'),('a','e'),('b','e'),('c','f'),('f','d'),('e','d')];g={x:[] for x in 'abcdef'}
    for a,b in edges:g[a].append(b);g[b].append(a)
    for a in g:g[a].sort()
    seen=set();order=[]
    def dfs(u):
        seen.add(u);order.append(u)
        for v in g[u]:
            if v not in seen:dfs(v)
    dfs('a');record('DS-C29','固定邻接次序DFS',''.join(order),'abedfc','按字母顺序实际递归')
    q=deque(['a']);seen={'a'};order=[];dist={'a':0}
    while q:
        u=q.popleft();order.append(u)
        for v in g[u]:
            if v not in seen:seen.add(v);dist[v]=dist[u]+1;q.append(v)
    record('DS-C30','BFS轨迹与距离',[''.join(order),dist['d'],dist['f']],['abcefd',2,2],'入队时标记')
    mst=[(0,1,10),(0,2,8),(0,3,5),(1,2,8),(1,3,11),(2,3,8)];weights=[]
    for es in it.combinations(mst,3):
        reached={0}
        for _ in range(4):
            for a,b,w in es:
                if a in reached:reached.add(b)
                if b in reached:reached.add(a)
        if len(reached)==4:weights.append(sum(w for a,b,w in es))
    record('DS-C31','2015MST总权',min(weights),21,'枚举6选3并独立检查连通')
    de=[(0,4,6),(0,1,26),(0,2,3),(4,1,15),(4,3,8),(4,2,6),(3,1,1),(3,2,6),(2,1,22)]
    d,tr=dijkstra(5,de,0)
    record('DS-C32','2021Dijkstra第二次路径确定',tr[2][1][1:],[21,3,14,6],'记录起点之后确定3、5时的真实距离数组')
    record('DS-C33','2021Dijkstra最终距离',d,all_path_dist(5,de,0),'枚举全部简单路径的独立交叉核验')
    rng=random.Random(408);tests=0
    for _ in range(100):
        e=[(u,v,rng.randrange(6)) for u in range(5) for v in range(5) if u!=v and rng.random()<.3]
        assert dijkstra(5,e,0)[0]==all_path_dist(5,e,0);tests+=1
    record('DS-C34','非负最短路通用测试',tests,100,'含零权、不可达，与枚举路径比较')
    base=[(a,b) for a in range(4) for b in range(a+1,4)];tests=0
    for mask in range(1<<len(base)):
        es=[e for i,e in enumerate(base) if mask>>i&1]
        assert unique_kahn(4,es)==(len(topo_orders(4,es))==1);tests+=1
    assert not unique_kahn(4,[(0,1),(1,0)])
    record('DS-C35','唯一拓扑序与排列枚举',tests,64,'4顶点全部按编号定向DAG；另查含环情况')
    aoe=[(1,2,3,'a'),(1,3,8,'b'),(3,2,4,'d'),(2,4,9,'c'),(2,5,6,'e'),(3,5,10,'f'),(4,6,6,'g'),(5,6,9,'h')]
    paths=path_lengths(aoe);critical=sorted(p for p,w in paths if w==max(w for p,w in paths))
    record('DS-C36','2013AOE三关键路径',critical,['bdcg','bdeh','bfh'],'枚举源到汇全部有向路径')
    outcomes=[]
    for change in ['ce','dc','fd','fh']:
        e=[(a,b,w-int(k in change),k) for a,b,w,k in aoe];outcomes.append(max(w for p,w in path_lengths(e)))
    record('DS-C37','2013四个选项分别缩短1后的工期',outcomes,[27,27,26,27],'改变实际持续时间重算全部路径，不只检查标题')
    a=list(range(1,17));low=0;high=15;comp=[]
    while low<=high:mid=(low+high)//2;comp.append(mid+1);low=mid+1
    record('DS-C38','2010折半失败比较位序',comp,[8,12,14,15,16],'目标大于最大关键字，闭区间向下取中点')
    t=None
    for x in [34,23,15,98,115,28,107]:t=avl(t,x);validate_avl(t)
    record('DS-C39','AVL七次插入最终树',shape(t),[34,[23,[15,None,None],[28,None,None]],[107,[98,None,None],[115,None,None]]],'每一步同时检查平衡与中序，不只检查最终根')
    record('DS-C40','3阶B树高度区间',[int(math.log2(2048)),next(h for h in range(1,20) if 3**h-1>=2047)],[11,7],'最小/最大容量两端分别计算')
    ns=[btree_count(4,7,h) for h in range(1,4)]
    record('DS-C41','2025B树按高度计形态',ns,[0,8,1],'递归枚举合法有序子树项数分配，包含非根下限与等高约束')
    table,ps=linear_table([2022,12,25],5,lambda k:(k+4)%5);table[4]='deleted';lens=[]
    for start in range(5):
        j=start;c=1
        while table[j] is not None:j=(j+1)%5;c+=1
        lens.append(c)
    record('DS-C42','2023删除标记失败ASL',[lens,sum(lens)/5],[[1,3,2,1,2],1.8],'按五个初始地址实际探查到从未用空槽')
    a=[None]*11
    for x in [20,3,11,18,9,14,7]:
        h=x*3%11;k=0
        while a[(h+k*k)%11] is not None:k+=1
        a[(h+k*k)%11]=x
    record('DS-C43','2024二次探查散列表',a,[11,None,14,7,None,20,9,None,None,3,18],'每个增量从H0计算')
    probes=[];k=0;h=8*3%11
    while True:
        j=(h+k*k)%11;probes.append(j)
        if a[j] is None:break
        k+=1
    record('DS-C44','2024查8失败地址序列',probes,[2,3,6,0,7],'实际探查并确认最后空槽7')
    trace=shell([13,24,7,1,8,9,11,56,34,51,2,77,5],[5,3,1])
    record('DS-C45','希尔前两趟',trace[:2],[[2,11,5,1,8,9,24,7,34,51,13,77,56],[1,7,5,2,8,9,24,11,34,51,13,77,56]],'对所有余数分组进行真实间隔插入')
    for p in it.permutations(range(6)):
        a=list(p);quick(a,0,len(a)-1);assert a==sorted(p)
    for p in it.product(range(3),repeat=6):
        a=list(p);quick(a,0,len(a)-1);assert a==sorted(p)
    record('DS-C46','双向划分排序正确',True,True,'全部6!不同键排列及3^6重复值输入，含全相等')
    choices=[[5,2,16,12,28,60,32,72],[2,16,5,28,12,60,32,72],[2,12,16,5,28,32,72,60],[5,2,12,28,16,32,72,60]]
    pivots=[[i for i,x in enumerate(a) if all(v<=x for v in a[:i]) and all(v>=x for v in a[i+1:])] for a in choices]
    record('DS-C47','2019各选项分隔位置',pivots,[[4,7],[0,7],[0,4,5],[2,5]],'同时检查全左/全右关系，非只看与最终排名相同')
    a=[None,12,15,10,21,34,16];i=1;count=0;x=a[1]
    while 2*i<len(a):
        c=2*i
        if c+1<len(a):count+=1;c=c+1 if a[c+1]<a[c] else c
        count+=1
        if x<=a[c]:break
        a[i]=a[c];i=c
    a[i]=x
    record('DS-C48','2015删堆顶实际比较',[count,a[1:]],[3,[10,15,12,21,34,16]],'数孩子间及候选间比较，不计边界判断')
    def merge(a,b):
        out=[];i=j=c=0
        while i<len(a) and j<len(b):
            c+=1
            if a[i]<=b[j]:out.append(a[i]);i+=1
            else:out.append(b[j]);j+=1
        return out+a[i:]+b[j:],c
    a,c1=merge([3,5],[7,9]);b,c2=merge(a,[6]);record('DS-C49','2024两次归并比较',[c1,c2,c1+c2,b],[2,3,5,[3,5,6,7,9]],'真实合并到一侧耗尽，剩余直接复制')
    a=[5,46,13,55,94,17,42];a=sorted(a,key=lambda x:x%10)
    record('DS-C50','LSD第一趟',a,[42,13,94,5,55,46,17],'稳定个位分配；05以数值5记录，正文保留两位显示')
    inp=[51,94,37,92,14,63,15,99,48,56,23,60,31,17,43,8,90,166,100];runs,events=replace_select(inp,4)
    expected=[[37,51,63,92,94,99],[14,15,23,31,48,56,60,90,166],[8,17,43,100]]
    record('DS-C51','2023置换选择全部三段',runs,expected,'真实工作区输出/换入/冻结，全部19条记录一次输出')
    assert Counter(sum(runs,[]))==Counter(inp)
    for p in [list(range(20)),list(range(19,-1,-1))]:
        r,_=replace_select(p,4)
        assert len(r[0])==(20 if p[0]<p[-1] else 4)
    record('DS-C52','置换选择首段两端长度',[20,4],[20,4],'递增/递减20记录，m=4，实际过程验证')
    w,steps=merge_cost([10,35,40,50,60,200]);record('DS-C53','2012最优二路归并',[w,w-5],[830,825],'每次重新取最短两段，比较成本减五个−1')
    w,steps4=merge_cost([30,44,8,6,3,20,60,18,9,62,68,85],4);record('DS-C54','四路归并补零后WPL',[w,[x[1] for x in steps4]],[690,[17,64,196,413]],'自动补1个零权叶，再逐次选4个最小值')
    record('DS-C55','外存60块与两趟归并I/O',2*60*(1+2),360,'明确包含初始段生成、读写各一遍')
    for _ in range(100):
        n=rng.randrange(10,101);original=[rng.randrange(30) for _ in range(n)];a=list(original);l=0;r=n-1
        while l<=r:
            # Random pivot, converted to the manuscript's in-place partition.
            j=rng.randrange(l,r+1);a[l],a[j]=a[j],a[l]
            p=partition(a,l,r)
            if p==9:break
            if p<9:l=p+1
            else:r=p-1
        assert sorted(a[:10])==sorted(original)[:10]
    record('DS-C57','2022最小10个数的迭代选择',100,100,'随机且含重复值输入，与完整排序的前10项独立对照；不要求保留的10项自身已序')
    # Verify all diagram numerical payloads against the checked examples.
    mf=HERE/'figure_manifest.json'
    if mf.exists():
        figs=json.loads(mf.read_text())['figures'];fd={f['id']:f['data'] for f in figs}
        assert fd['DS_08_huffman']['WPL']==90
        assert fd['DS_12_dijkstra_2021']['after_two']==tr[2][1][1:]
        assert fd['DS_18_replacement_selection']['first_run']==runs[0]
        assert fd['DS_13_aoe_2013']['critical_paths']==critical
        record('DS-C56','图文共用数值一致',True,True,'读实际图稿manifest，与本脚本实际结果对照')
    # Revision 2: audit the actual numerical trees drawn, including transient
    # states. Rotations and B-tree operations below are independent of SVG code.
    avl_audits=[];avl_summary=[]
    for figure_id in ['DS_14_avl_rotations','DS_21_avl_double_rotations']:
        for case in fd[figure_id]['cases']:
            before=number_tree(case['pre_insert']);validate_avl(before);assert height(before)==3
            inserted=plain_bst_insert(before,case['insert']);assert shape(inserted)==case['states'][0]
            audits=[]
            for i,state in enumerate(case['states']):
                t=number_tree(state);audit=avl_state_audit(t)
                assert audit['inorder']==sorted(avl_state_audit(inserted)['inorder'])
                if i:
                    operation=case['operations'][i-1]
                    rotated=rotate_at(number_tree(case['states'][i-1]),operation['at'],operation['direction'])
                    assert shape(rotated)==state,(case['type'],i)
                audits.append(audit)
            validate_avl(number_tree(case['states'][-1]))
            avl_audits.append({'type':case['type'],'insert':case['insert'],'operations':case['operations'],'states':audits})
            avl_summary.append([case['type'],[a['height'] for a in audits]])
    record('DS-C58','AVL四型逐状态BST、节点高度/平衡因子与实际旋转',avl_summary,[['LL',[4,3]],['RR',[4,3]],['LR',[4,4,3]],['RL',[4,4,3]]],'读取数值图数据；每状态中序、每节点高度/BF、插入前合法AVL、每一次旋转与最后平衡均核验，双旋中间态允许尚未平衡')
    split=fd['DS_15_btree_split'];order=split['order'];assert order==5
    assert insert_btree_trace(split['initial'],split['insert'],order)==split['states']
    insertion_audits=[audit_btree(split['initial'],order)]+[audit_btree(t,order,bad) for t,bad in zip(split['states'],split['temporary_violations'])]
    initial_keys=btree_keys(split['initial'])
    for a in insertion_audits[1:]:assert a['inorder']==sorted(initial_keys+[29])
    record('DS-C59','5阶插入：叶5项分裂、根5项分裂及6孩子分接',[[a['key_count'],a['height']] for a in insertion_audits],[[16,2],[17,2],[17,2],[17,3]],'独立自底向上插入重现图中全部3步；非根2..4、根1..4、结点内有序、孩子区间/数量、叶等深逐状态断言；仅指定节点临时5项')
    deletion=fd['DS_20_btree_delete'];borrow=deletion['borrow'];cascade=deletion['cascade']
    assert delete_btree_trace(borrow['initial'],borrow['delete'],5)==borrow['states']
    borrow_audits=[audit_btree(borrow['initial'],5)]+[audit_btree(t,5,bad) for t,bad in zip(borrow['states'],borrow['temporary_violations'])]
    for a in borrow_audits[1:]:assert a['inorder']==[5,10,12,15,18]
    record('DS-C60','5阶删除经父借位：10下移、12上移',[[a['key_count'],a['height']] for a in borrow_audits],[[6,2],[5,2],[5,2]],'实际删除2后叶仅1项，再经父分隔项向3项兄弟借；完成态两叶各2项，不直接搬兄弟项跳过父')
    assert cascade['initial']==split['states'][-1]
    assert delete_btree_trace(cascade['initial'],cascade['delete'],5)==cascade['states']
    cascade_audits=[audit_btree(cascade['initial'],5)]+[audit_btree(t,5,bad) for t,bad in zip(cascade['states'],cascade['temporary_violations'])]
    expected_keys=[x for x in btree_keys(cascade['initial']) if x!=1]
    for a in cascade_audits[1:]:assert a['inorder']==expected_keys
    record('DS-C61','5阶删除合并传播：叶下溢、双亲下溢、空根降高',[[a['key_count'],a['height']] for a in cascade_audits],[[17,3],[16,3],[16,3],[16,3],[16,2]],'每层1+1+2合并成4项，内结点合并按原顺序接5个孩子；空根暂只有1孩子，压缩后全叶同时升一层')
    bn=lambda keys,children=None:{'keys':keys,'children':children or []}
    internal_initial=bn([15],[bn([5,10],[bn([1,3]),bn([6,8]),bn([11,13])]),bn([20,25,30],[bn([16,18]),bn([21,23]),bn([26,28]),bn([31,33])])])
    internal_expected=bn([20],[bn([10,15],[bn([3,5,6,8]),bn([11,13]),bn([16,18])]),bn([25,30],[bn([21,23]),bn([26,28]),bn([31,33])])])
    def mirror_btree(t):return bn([34-x for x in reversed(t['keys'])],[mirror_btree(c) for c in reversed(t['children'])])
    internal_checks=[]
    for initial,key,expected in [(internal_initial,1,internal_expected),(mirror_btree(internal_initial),33,mirror_btree(internal_expected))]:
        audit_btree(initial,5);trace=delete_btree_trace(initial,key,5);assert trace[-1]==expected
        internal_checks.append(audit_btree(trace[-1],5)['key_count'])
    record('DS-C62','5阶内部层左右借位的孩子转接',internal_checks,[19,19],'先在底层合并造成内结点下溢；右借时把右兄弟最左孩子[16,18]接到左结点，左借作镜像核验，保持3孩子和全树区间')
    illegal_premerge=bn([1,3,5,6,8]);rejected=False
    try:audit_btree(illegal_premerge,5)
    except AssertionError:rejected=True
    record('DS-C63','5阶禁止合法2键兄弟的提前合并',[2+1+2,1+1+2,rejected],[5,4,True],'m=5上限4，不把CLRS最小度t=3的最大5键套来；合法合并发生在一侧下溢到1键之后')
    def binary_insertion_work(inp):
        a=list(inp);comparisons=shifts=0
        for i in range(1,len(a)):
            x=a[i];low=0;high=i-1
            while low<=high:
                comparisons+=1;mid=(low+high)//2
                if a[mid]>x:high=mid-1
                else:low=mid+1
            for j in range(i,low,-1):a[j]=a[j-1];shifts+=1
            a[low]=x
        return a,comparisons,shifts
    for n in range(2,129):
        sorted_out,c,m=binary_insertion_work(range(n));assert sorted_out==list(range(n)) and m==0
        assert c==sum(i.bit_length() for i in range(1,n))
        reverse_out,rc,rm=binary_insertion_work(range(n-1,-1,-1));assert reverse_out==list(range(n))
        assert rm==n*(n-1)//2
    record('DS-C64','每趟照常折半：有序仍需对数定位、逆序仍需二次移动',[c,m,rm],[769,0,8128],'n=2..128逐一计比较与右移；n=128给出实际计数，不以零移动推断最好线性总时间')
    def equal_heap_comparisons(n):
        a=[7]*n;comparisons=0
        def sift(i,size):
            nonlocal comparisons
            x=a[i]
            while i*2+1<size:
                child=i*2+1
                if child+1<size:
                    comparisons+=1
                    if a[child]<a[child+1]:child+=1
                comparisons+=1
                if x>=a[child]:break
                a[i]=a[child];i=child
            a[i]=x
        for i in range(n//2-1,-1,-1):sift(i,n)
        for size in range(n-1,0,-1):a[0],a[size]=a[size],a[0];sift(0,size)
        return comparisons
    equal_counts=[equal_heap_comparisons(n) for n in [64,128,256]]
    record('DS-C65','允许相等即停的堆排序全等输入',equal_counts,[186,378,762],'含自底向上建堆与n−1次输出，下滤每次至多两比即停，计数3n−6；说明线性特例，不反推一般最坏界')
    counting_input=[[2,'a'],[4,'x'],[3,'a'],[0,'x'],[2,'b'],[3,'b']]
    frequencies,prefixes,counted=stable_counting(counting_input,5)
    enumerated=0
    for n in range(7):
        for values in it.product(range(3),repeat=n):
            records=[[x,i] for i,x in enumerate(values)]
            _,_,out_records=stable_counting(records,3)
            assert out_records==sorted(records,key=lambda item:item[0]);enumerated+=1
    record('DS-C66','计数排序频次、前缀与相等记录身份', [frequencies,prefixes,counted,enumerated],[[1,0,2,2,1],[1,1,3,5,6],[[0,'x'],[2,'a'],[2,'b'],[3,'a'],[3,'b'],[4,'x']],1093],'复算正文6条带身份记录；再枚举长度0..6、值域0..2的1093序列，与稳定参考排序对照')
    out={'subject':'DS','status':'PASS','checks_count':len(RESULTS),'checks':RESULTS,'notes':['程序结果核验不替代题源图文核验或PDF视觉检查。','图数值检查读取图源manifest，并非仅检查文件和标题。','有限穷举范围与各项记录一致，不据此声称所有算法性质已形式证明。','第二轮仅进行正文与图机制复核，未生成、分页或视觉检查成稿PDF。'],'replacement_events':events,'optimal_merge_steps':steps,'four_way_steps':steps4,'revision2':{'avl_states':avl_audits,'btree_insertion':insertion_audits,'btree_borrow':borrow_audits,'btree_merge_cascade':cascade_audits,'internal_borrow_final':[internal_expected,mirror_btree(internal_expected)]}}
    (HERE/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(f'DS: {len(RESULTS)} calculation/process checks PASS')

if __name__=='__main__':main()
