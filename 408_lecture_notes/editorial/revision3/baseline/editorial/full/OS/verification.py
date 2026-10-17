#!/usr/bin/env python3
"""Independent execution checks for scheduling, resources, addresses, files and I/O."""
from pathlib import Path
import itertools,json,math,re
ROOT=Path(__file__).resolve().parents[3]
D=json.loads((Path(__file__).with_name('model_data.json')).read_text())
RESULTS=[]

def record(name,actual,expected,scope):
    assert actual==expected,(name,actual,expected)
    RESULTS.append({'check':name,'actual':actual,'expected':expected,'status':'PASS','scope':scope})

def priority(arrival,burst,priority,high=True,names=None):
    left=burst[:];t=min(arrival);segments=[];finished={}
    while any(left):
        ready=[i for i in range(len(left)) if left[i] and arrival[i]<=t]
        if not ready:t=min(arrival[i] for i in range(len(left)) if left[i]);continue
        i=min(ready,key=lambda j:((-priority[j] if high else priority[j]),arrival[j],j))
        end=t+left[i]
        future=[a for a in arrival if a>t]
        if future:end=min(end,min(future))
        name=names[i] if names else f'P{i+1}'
        if segments and segments[-1][2]==name and segments[-1][1]==t:segments[-1][1]=end
        else:segments.append([t,end,name])
        left[i]-=end-t;t=end
        if not left[i]:finished[name]=t
    return segments,finished

def safety(allocation,need,available):
    work=available[:];done=[];states=[work[:]]
    while True:
        choices=[i for i in range(len(need)) if i not in done and all(x<=y for x,y in zip(need[i],work))]
        if not choices:break
        i=choices[0];done.append(i);work=[x+y for x,y in zip(work,allocation[i])];states.append(work[:])
    return len(done)==len(need),done,states

def lru(refs,n):
    order=[];faults=replacements=0;trace=[]
    for p in refs:
        hit=p in order;victim=None
        if hit:order.remove(p)
        else:
            faults+=1
            if len(order)==n: victim=order.pop(0);replacements+=1
        order.append(p);trace.append({'page':p,'order':order[:],'fault':not hit,'victim':victim})
    return faults,replacements,trace

def replace(refs,n,algorithm):
    pages=[];faults=0
    for at,p in enumerate(refs):
        if p in pages:
            if algorithm=='LRU':pages.remove(p);pages.append(p)
            continue
        faults+=1
        if len(pages)==n:
            if algorithm=='OPT':
                future=refs[at+1:]
                victim=max(pages,key=lambda x:(future.index(x) if x in future else math.inf))
                pages.remove(victim)
            else:pages.pop(0)
        pages.append(p)
    return faults

def buffers(n,T,M,C,double=False):
    timeline=[];device_free=cpu_free=0;slot_free=[0,0] if double else [0]
    for k in range(n):
        slot=k%len(slot_free)
        ins=max(device_free,slot_free[slot]);ine=ins+T
        cs=max(ine,cpu_free);ce=cs+M;done=ce+C
        device_free=ine;cpu_free=done;slot_free[slot]=ce
        timeline.append({'block':k+1,'buffer':slot,'input':[ins,ine],'copy':[cs,ce],'compute':[ce,done]})
    return cpu_free,timeline

def run():
    # Trusted typical exercise adds the SRTF remaining-time and RR queue tasks.
    arrivals=[0,1,2,3];bursts=[8,4,9,5];left=bursts[:];t=0;ends={};timeline=[]
    while any(left):
        ready=[i for i in range(4) if arrivals[i]<=t and left[i]]
        i=min(ready,key=lambda i:(left[i],arrivals[i],i))
        if timeline and timeline[-1][2]==i:timeline[-1][1]=t+1
        else:timeline.append([t,t+1,i])
        left[i]-=1;t+=1
        if not left[i]:ends[i]=t
    record('2.2综合6 SRTF轨迹',timeline,[[0,1,0],[1,5,1],[5,10,3],[10,17,0],[17,26,2]],'例2-6，逐时间单位独立模拟')
    record('2.2综合6 SRTF平均周转',sum(ends[i]-arrivals[i] for i in range(4))/4,13.0,'与主书扫描108核对')
    left=bursts[:];t=0;queue=[];admitted=set();ends={};timeline=[]
    while any(left):
        for i in range(4):
            if i not in admitted and arrivals[i]<=t:queue.append(i);admitted.add(i)
        i=queue.pop(0);end=t+min(2,left[i]);timeline.append([t,end,i]);left[i]-=end-t;t=end
        for j in range(4):
            if j not in admitted and arrivals[j]<=t:queue.append(j);admitted.add(j)
        if left[i]:queue.append(i)
        else:ends[i]=t
    record('2.2综合6 RR完成时刻',[ends[i] for i in range(4)],[22,12,26,23],'同刻新到先入队再放回过期者')
    record('2.2综合6 RR平均周转',sum(ends[i]-arrivals[i] for i in range(4))/4,19.25,'例2-6，与主书109轨迹核对')
    a=D['priority_2023'];seg,end=priority(a['arrival'],a['burst'],a['priority'])
    record('2023优先级运行段',seg,a['segments'],'例2-3、OS_priority_timeline图共用数据')
    record('2023平均周转ms',sum(end[f'P{i+1}']-a['arrival'][i] for i in range(3))/3,61.0,'含到达时刻扣除')
    a=D['priority_2022'];seg,end=priority(a['arrival'],a['burst'],a['priority'],False,['P0','P1','P2','P3'])
    record('2022优先级运行段',seg,a['segments'],'例2-4；值小为高')
    record('2022调度次数',len(seg),6,'含首次、不计最后空闲，实际更换为5')
    record('2019反馈平均等待ms',((50-30)+(30-20))/2,15.0,'例2-5两者初始到达0')
    b=D['banker_2011'];safe,seq,states=safety(b['allocation'],b['need'],b['available'])
    record('2011安全检查',[safe,seq,states],[False,[0,3],[[0,2,1],[2,2,1],[2,2,2]]],'例4-2；不安全不自动当已死锁')
    b=D['banker_2_4_026'];need=[[m-a for m,a in zip(mx,al)] for mx,al in zip(b['max'],b['allocation'])]
    got=[safety(b['allocation'],need,av)[0] for av in b['candidates']]
    record('2.4-026四候选安全性',got,[True,False,False,False],'例4-3；各候选独立初态')
    # Exhaust every process ordering; independently cross-check greedy safety.
    counts=[]
    for av in b['candidates']:
        total=0
        for seq in itertools.permutations(range(5)):
            w=av[:]
            for i in seq:
                if any(x>y for x,y in zip(need[i],w)):break
                w=[x+y for x,y in zip(w,b['allocation'][i])]
            else:total+=1
        counts.append(total)
    record('2.4-026排列核对',[n>0 for n in counts],got,'穷举120种完成次序/每候选')
    before=safety([[1],[1]],[[3],[2]],[2])[0];after=safety([[2],[1]],[[2],[2]],[1])[0]
    record('请求有现存量但破坏安全',[before,after],[True,False],'章4原创最小机制示例')
    # Best-fit dynamic partitions, with allocation at each chosen hole's start.
    holes=[(0,55)];allocated=[];tr=[]
    for size in [15,30]:
        i=min((i for i,x in enumerate(holes) if x[1]>=size),key=lambda i:holes[i][1]);base,n=holes.pop(i);allocated.append((base,size));holes.append((base+size,n-size));tr.append(sorted(n for _,n in holes if n))
    holes.append(allocated[0]);tr.append(sorted(n for _,n in holes if n))
    for size in [8,6]:
        i=min((i for i,x in enumerate(holes) if x[1]>=size),key=lambda i:holes[i][1]);base,n=holes.pop(i);holes.append((base+size,n-size));tr.append(sorted(n for _,n in holes if n))
    record('2010最佳适应每步洞大小',tr,[[40],[10],[10,15],[2,15],[2,9]],'例5-2；单位沿原题MB')
    record('2010页目录项数',2**16//(2**10//2),128,'例5-3，逻辑空间按页计')
    addr=0x20501225
    record('2019三级字段',[addr>>22,(addr>>12)&1023,addr&4095],[0x81,0x101,0x225],'例5-4与地址字段图')
    record('3.2典型地址转换',11*1024+(0xA6F%1024),0x2E6F,'1KB页，页2映射页框11')
    record('TLB平均访存次数',0.75+0.25*3,1.5,'二级页表全驻留，无缺页，忽略TLB时间')
    a=D['lru_2019'];faults,reps,trace=lru(a['references'],a['frames'])
    record('2019LRU缺页置换',[faults,reps],[9,5],'例5-5，空框初态')
    record('2019LRU逐步次序',[r['order'] for r in trace],[[0],[0,1],[0,1,2],[0,1,2,7],[1,2,7,0],[2,7,0,5],[7,0,5,3],[7,0,3,5],[7,3,5,0],[3,5,0,2],[5,0,2,7],[0,2,7,6]],'核查正文完整12行表')
    record('2021调页后物理地址',0x60*4096+(0x2A01%4096),0x60A01,'例5-6；先淘汰干净页3')
    a=D['workset_2016'];record('2016工作集',sorted(set(a['past'][-a['window']:])),[0,2,3,6],'例5-7，窗口按引用次数')
    column=[(j*128+i)*4//512 for i in range(128) for j in range(128)]
    row=[(i*128+j)*4//512 for i in range(128) for j in range(128)]
    record('3.2-012行列访存缺页',[replace(column,1,'FIFO'),replace(row,1,'FIFO')],[16384,128],'4B整数、页对齐、数据空初态；只有一数据框')
    ref=[1,2,3,4,1,2,5,1,2,3,4,5]
    record('FIFO异常核验',[replace(ref,3,'FIFO'),replace(ref,4,'FIFO')],[9,10],'解释Belady边界的独立交叉计算')
    record('单级页表容量',[2**(32-12),2**(32-12)*4],[1048576,4194304],'章5自测1')
    record('混合索引偏移与范围',[1234//1024,307400//1024,(307400//1024)-266,(10+256+256**2)*1024],[1,300,34,67381248],'例6-3：64MB+266KB')
    record('隐式链接改第22记录I/O',math.ceil(22/5)+1,6,'例6-4，读5块后写回1块')
    record('目录精确期望',sum(range(1,51))/50+1,26.5,'每个目录块64项，目标等概率，再读inode')
    bit=409612;rel,remain=divmod(bit,8192);byte,within=divmod(remain,8)
    record('2015位图位置',[32+rel,byte,within],[82,1,4],'例6-6，起点只加到位图相对块号')
    record('2017权限位',4*5,20,'例6-2，20个独立真假组合位')
    a=D['buffer_2011'];single,st=buffers(a['n'],a['input'],a['copy'],a['compute']);double,dt=buffers(a['n'],a['input'],a['copy'],a['compute'],True)
    record('2011单双缓冲总时间',[single,double],[1550,1100],'事件资源占用独立推演，微秒')
    record('单块无流水收益',[buffers(1,100,50,50)[0],buffers(1,100,50,50,True)[0]],[200,200],'章7自测2')
    record('2011前三块单缓冲轨迹',st[:3],[{'block':1,'buffer':0,'input':[0,100],'copy':[100,150],'compute':[150,200]},{'block':2,'buffer':0,'input':[150,250],'copy':[250,300],'compute':[300,350]},{'block':3,'buffer':0,'input':[300,400],'copy':[400,450],'compute':[450,500]}],'正文与时间线图')
    record('CHS逻辑记录号',78*64+6*8+6,5046,'例7-3，零基编号')
    a=D['scan_2015'];head=a['head'];req=a['requests'];scan=sorted(x for x in req if x>=head)+sorted((x for x in req if x<head),reverse=True)
    dist=lambda seq:sum(abs(b-a) for a,b in zip([head]+seq,seq))
    todo=req[:];s=[];p=head
    while todo:
        q=min(todo,key=lambda q:abs(q-p));todo.remove(q);s.append(q);p=q
    record('2015SCAN顺序和距离',[scan,dist(scan)],[[130,180,199,42,15],325],'请求已含物理端点199')
    record('同数据FCFS与SSTF',[dist(req),dist(s),s],[647,227,[42,15,130,180,199]],'题后方法比较')
    record('7200rpm平均旋转ms',round(1000/(7200/60)/2,6),4.166667,'章7单位示例')
    # This does not replace technical/source or visual checks.
    checks={'priority_2022':seg,'banker_candidate_safe_sequence_counts':counts,'lru_2019':trace,'single_buffer':st,'double_buffer':dt}
    (Path(__file__).with_name('process_traces.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2))
    out={'status':'PASS','checks':RESULTS,'count':len(RESULTS),'limits':'断言核实际计算与轨迹；不认证题源、2027正式范围或全部PDF视觉。样章并发模型另见tools/verify_models.py及os_exam_checks。'}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({'status':'PASS','checks':len(RESULTS)},ensure_ascii=False))

if __name__=='__main__':run()
