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

def revision3_checks():
    """Execute the seven newly selected questions; retain the earlier 37 checks."""
    traces={}
    a=D['aging_2016'];k1,k2=a['coefficients']
    dynamic=lambda nice,cpu,wait:nice+k1*cpu-k2*wait
    record('2016动态优先数的运行与等待方向',
           [dynamic(10,1,0),dynamic(10,0,1)],[11,9],
           '例2-7；值小优先，原创代入仅检验公式方向，不证明任意到达流无饥饿')
    crossed=next(t for t in range(100) if dynamic(a['nice_waiter'],0,t)<a['nice_competitor'])
    record('2016老化代入首次严格超过',[crossed,dynamic(a['nice_waiter'],0,crossed)],[11,-1],
           '例2-7原创代入：nice差10，系数均为1，计时量按题设清零')

    a=D['paging_2009'];mapping=dict(a['initial_pages']);recent=list(mapping);tlb={};page_trace=[]
    for va in a['addresses']:
        page,offset=divmod(va,a['page_size']);elapsed=a['tlb_ns'];victim=None;fault=False
        if page not in tlb:
            elapsed+=a['memory_ns']
            if page not in mapping:
                fault=True;elapsed+=a['fault_ns']
                if len(mapping)==a['frames']:
                    victim=recent.pop(0);frame=mapping.pop(victim);tlb.pop(victim,None)
                else:raise AssertionError('Source scenario starts with a full resident set')
                mapping[page]=frame;tlb[page]=frame
                elapsed+=a['tlb_ns'] # restart the original instruction after fault handling
            else:tlb[page]=mapping[page]
        elapsed+=a['memory_ns']
        if page in recent:recent.remove(page)
        recent.append(page)
        page_trace.append({'VA':f'{va:X}H','page':page,'offset':offset,'fault':fault,'victim':victim,
                           'time_ns':elapsed,'PA':f'{mapping[page]*a["page_size"]+offset:X}H',
                           'resident':dict(mapping),'TLB':dict(tlb),'LRU_oldest_first':recent[:]})
    record('2009连续三次访问耗时ns',[r['time_ns'] for r in page_trace],[210,100000220,110],
           '例5-8；失败查询、含更新的缺页处理、原指令重试分开计时')
    record('2009局部LRU淘汰页',[r['victim'] for r in page_trace],[None,0,None],
           '例5-8；第一次使用页2后，页0为局部LRU，页2转换继续保留')
    record('2009虚地址1565H的物理地址',page_trace[1]['PA'],'101565H','例5-8；页1复用被淘汰页0的101H页框')
    record('2009连续驻留集合',[sorted(r['resident']) for r in page_trace],[[0,2],[1,2],[1,2]],'例5-8；每次访问承接前次状态')
    traces['paging_2009']=page_trace

    a=D['array_2020'];row,col=a['target'];page_bytes=2**a['offset_bits'];mask=2**a['table_index_bits']-1
    va=a['base_VA']+(row*a['columns']+col)*a['element_bytes']
    di=va>>(a['offset_bits']+a['table_index_bits']);ti=(va>>a['offset_bits'])&mask;off=va&(page_bytes-1)
    record('2020数组虚地址与字段',[f'{va:08X}H',di,ti,off],['10801008H',66,1,8],'例5-9；行优先下标与10+10+12位拆分')
    record('2020逐级页表项物理地址',
           [f'{a["directory_base_PA"]+di*a["entry_bytes"]:08X}H',f'{a["table_frame"]*page_bytes+ti*a["entry_bytes"]:08X}H'],
           ['00201108H','00301004H'],'例5-9；下级页框号先乘页大小，表项地址不是目标数据地址')
    record('2020行列访问的字节跨度与数组大小',
           [a['element_bytes'],a['columns']*a['element_bytes'],a['rows']*a['columns']*a['element_bytes']],
           [4,4096,4194304],'例5-9；访问模式核算，不从跨度擅推未给驻留集的缺页次数')

    a=D['directory_2022'];files={name:{'inode':ino,'block':block} for name,ino,block in a['records']}
    entries=[[name,files[name]['inode']] for name in a['children']['stu']]
    record('2022stu的全部给定目录项',entries,[['course',2],['doc',10]],'例6-7；只列stu直接包含的名字与inode号')
    same_inode_blocks=[r['block'] for name,r in files.items() if r['inode']==files['doc']['inode'] and name!='doc']
    record('2022同inode推得doc数据块',same_inode_blocks,[30],'例6-7；同一文件系统的inode10对应同一个文件对象')
    uncached_path=['course1 inode所在磁盘块',f'数据块{files["course1"]["block"]}']
    record('2022目录缓存后的读盘路径',uncached_path,['course1 inode所在磁盘块','数据块30'],
           '例6-7；course目录内容已缓存，未另给目标inode和数据缓存命中；共2块')
    fanout=a['block_bytes']//a['address_bytes'];blocks=math.ceil(a['course2_bytes']/a['block_bytes'])
    remain=max(0,blocks-a['direct_entries']);levels=[]
    for level in a['indirect_levels']:
        if remain:levels.append(level);remain=max(0,remain-fanout**level)
    record('2022文件扩展的块数与间接层级',[blocks,fanout,a['direct_entries']+fanout,levels],[1536,1024,1034,[1,2]],
           '例6-7第4问；完整跨页设问，一级覆盖后尚余502个数据块')
    record('2022扩展后实际间接索引块数',1+1+math.ceil((blocks-a['direct_entries']-fanout)/fanout),3,
           '例6-7题后路径说明；一级1块、二级根1块和一级叶1块，用户数据另计')

    a=D['inode_2018'];fanout=a['cluster_bytes']//a['address_bytes']
    maximum=(a['direct_entries']+sum(fanout**h for h in [1,2,3]))*a['cluster_bytes']
    record('2018混合索引最大文件字节数',[fanout,maximum],[1024,4402345705472],'例6-8第1问；数据覆盖，不含索引簇自身')
    inode_limit=a['inode_clusters']*(a['cluster_bytes']//a['inode_bytes']);per_file=math.ceil(a['image_bytes']/a['cluster_bytes'])
    data_limit=a['data_clusters']//per_file
    record('2018inode与数据簇的双重文件上限',[inode_limit,per_file,data_limit,min(inode_limit,data_limit)],
           [67108864,2,268435456,67108864],'例6-8第2问；5600B的两簇均用直接项，无间接索引簇')
    last=[math.ceil(size/a['cluster_bytes'])-1 for size in a['files_bytes']]
    index_reads=[0 if block<a['direct_entries'] else 1 for block in last]
    record('2018两文件末簇逻辑号',last,[1,9],'例6-8第3问；逻辑簇号从0开始，8直接项覆盖0至7')
    record('2018只取末簇号的额外索引读盘次数',index_reads,[0,1],
           '原问仅取簇号；共同起点inode已在内存、相关间接索引未缓存')
    record('2018另读末簇数据的完整路径读盘次数',[n+1 for n in index_reads],[1,2],
           '明确属于题后扩展，不冒充原问：索引读盘次数再加目标数据簇1次')

    # Event preconditions distinguish the waiting process from the current CPU owner.
    valid=[];keyboard_trace=[]
    for order in itertools.permutations(range(1,7)):
        state='running';input_ready=handler=buffered=False;trace=[];mode='kernel'
        for op in order:
            allowed={2:state=='running' and not input_ready,
                     6:state=='blocked' and not input_ready,
                     4:input_ready and not handler and state=='blocked',
                     3:handler and not buffered and state=='blocked',
                     1:buffered and state=='blocked',
                     5:state=='ready'}[op]
            if not allowed:break
            if op==2:state='blocked';mode='other process mode unspecified'
            elif op==6:input_ready=True
            elif op==4:handler=True;mode='kernel'
            elif op==3:buffered=True
            elif op==1:state='ready'
            elif op==5:state='running';mode='user' # dispatcher runs P before syscall return
            trace.append({'operation':op,'P_state_after':state,'CPU_mode_after':mode,'system_buffer_has_character':buffered})
        else:valid.append(list(order));keyboard_trace=trace
    record('2023键盘输入满足状态前提的六操作顺序',valid,[[2,6,4,3,1,5]],
           '例7-6；穷举720种顺序，依据等待、硬件事件、取字符、唤醒及返回前提筛选')
    order=valid[0];at=order.index(1)
    record('2023就绪前后和键盘输入后的题列操作',[order[at-1],order[at+1],order[order.index(6)+1]],[3,5,4],
           '例7-6第1问；题列相邻不代表机器指令紧邻')
    handler_start=next(r for r in keyboard_trace if r['operation']==4)
    record('2023中断入口的P状态与CPU模式',[handler_start['P_state_after'],handler_start['CPU_mode_after']],
           ['blocked','kernel'],'例7-6第4问；P仍阻塞，CPU可从另一进程进入中断处理')
    record('2023阻塞与可调度资格的分界',
           [next(r['operation'] for r in keyboard_trace if r['P_state_after']=='blocked'),next(r['operation'] for r in keyboard_trace if r['P_state_after']=='ready')],
           [2,1],'例7-6第2问；就绪后才有资格被选中，不保证立即执行')
    traces['keyboard_2023']=keyboard_trace

    a=D['disk_2019'];per_cyl=a['tracks_per_cylinder']*a['sectors_per_track']//a['sectors_per_cluster']
    capacity=a['cylinders']*a['tracks_per_cylinder']*a['sectors_per_track']*a['sector_bytes']
    record('2019磁盘总容量与每柱面簇数',[capacity,capacity//1024,per_cyl],[307200000,300000,1000],
           '例7-7第1问；簇含2扇区，不使物理磁盘总容量加倍')
    request_cylinders=[q//per_cyl for q in a['requests']]
    record('2019请求簇号转柱面号',request_cylinders,[100,60,101,110],'例7-7第2问；零基簇号每1000个跨一柱面')
    todo=a['requests'][:];head=a['head_cylinder'];order=[];disk_trace=[]
    while todo:
        choice=min(todo,key=lambda q:abs(q//per_cyl-head));cyl=choice//per_cyl
        disk_trace.append({'from_cylinder':head,'cluster':choice,'to_cylinder':cyl,'distance':abs(cyl-head)})
        order.append(choice);todo.remove(choice);head=cyl
    record('2019SSTF逐次重选顺序',order,[100260,101660,110560,60005],'例7-7；每次到达新柱面后重算剩余请求的距离')
    record('2019SSTF逐段移动与总量',[[r['distance'] for r in disk_trace],sum(r['distance'] for r in disk_trace)],
           [[15,1,9,50],75],'例7-7轨迹表；柱面移动不等于整个I/O耗时')
    first_sector=a['target_cluster']*a['sectors_per_cluster'];sectors_per_cyl=a['tracks_per_cylinder']*a['sectors_per_track']
    cylinder,remainder=divmod(first_sector,sectors_per_cyl);head,sector=divmod(remainder,a['sectors_per_track'])
    record('2019目标簇起始CHS与相邻扇区',[cylinder,head,sector,sector+1],[100,5,60,61],
           '例7-7第3问；簇100530覆盖同磁道的两个扇区，CHS为起始地址')
    record('2019CHS反算目标簇',(cylinder*sectors_per_cyl+head*a['sectors_per_track']+sector)//a['sectors_per_cluster'],
           a['target_cluster'],'例7-7地址双向复核，三个字段均用零基编号')
    traces['disk_2019']=disk_trace
    return traces

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
    r3=revision3_checks()
    checks={'priority_2022':seg,'banker_candidate_safe_sequence_counts':counts,'lru_2019':trace,'single_buffer':st,'double_buffer':dt,'revision3':r3}
    (Path(__file__).with_name('process_traces.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2))
    out={'status':'PASS','checks':RESULTS,'count':len(RESULTS),'revision3_added':len(RESULTS)-37,'limits':'断言核实际计算与轨迹；不认证题源、2027正式范围或讲义PDF版式。本轮未生成或检查讲义PDF；样章并发模型另见tools/verify_models.py及os_exam_checks。'}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({'status':'PASS','checks':len(RESULTS)},ensure_ascii=False))

if __name__=='__main__':run()
