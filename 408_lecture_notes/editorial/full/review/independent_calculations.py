#!/usr/bin/env python3
"""独立复算已实际读到的题解；按正文继续扩充，不以用例数代替覆盖。"""
from __future__ import annotations
from fractions import Fraction
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import struct
from itertools import product, permutations, combinations
from collections import Counter
import heapq
import ipaddress

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent

def file_identity(relative):
    p=ROOT/relative
    return {'path':relative,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    checks=[]
    # 按while原过程执行，不以讲义中的闭式重复代入。
    examples=[]
    for n in [0,1,2,3,4,5,6,7,10,100,999,10000]:
        i=total=0
        while total<n:
            i+=1;total+=i
        expected=math.ceil((math.sqrt(1+8*n)-1)/2)
        assert i==expected,(n,i,expected)
        assert (i==0 or (i-1)*i//2<n) and total>=n
        examples.append({'n':n,'rounds':i,'sum_at_stop':total})
    checks.append({'id':'RV-DS01-2017','source':file_identity('manuscript/DS/01_数据结构算法与复杂度.md'),'question':'例DS1-2','method':'直接执行累加循环并检查最小终止轮数','results':examples,'status':'passed'})
    examples=[]
    for n in [0,1,2,3,4,5,8,9,16,17,100,10000]:
        count=0;i=1
        while i<n:
            for j in range(i): count+=1
            i*=2
        assert count==i-1
        if n>1:assert n-1<=count<2*n
        examples.append({'n':n,'actual_inner_count':count,'first_unexecuted_i':i})
    checks.append({'id':'RV-DS01-2022','source':file_identity('manuscript/DS/01_数据结构算法与复杂度.md'),'question':'例DS1-3','method':'嵌套循环实际累计；检查几何级数边界','results':examples,'status':'passed'})
    cycles=8000+2000*10
    seconds=Fraction(cycles,10**9)
    assert cycles==28000 and seconds==Fraction(28,10**6)
    checks.append({'id':'RV-CO01-2022','source':file_identity('manuscript/CO/01_计算机系统与程序执行.md'),'question':'例CO1-2','method':'分开累计8000条/2000条指令周期，使用有理数单位换算','results':{'cycles':cycles,'average_CPI':str(Fraction(cycles,10000)),'seconds':str(seconds),'microseconds':str(seconds*10**6)},'status':'passed'})
    t=Fraction(90,1)/Fraction(3,2)+10
    optimized=20*Fraction(7,10)*Fraction(6,5)
    assert t==70 and optimized==Fraction(84,5)
    checks.append({'id':'RV-CO01-TIMES','source':file_identity('manuscript/CO/01_计算机系统与程序执行.md'),'question':'例CO1-3和2014自测','method':'速度比/指令比独立有理数计算','results':{'2012_seconds':str(t),'2014_seconds':str(optimized)},'status':'passed'})
    co2='manuscript/CO/02_数据表示与运算.md'
    values={
        '137.5_octal':'211.4' if 2*8**2+8+1+Fraction(4,8)==Fraction(275,2) else None,
        'unsigned_65530_hex':f'{65530:08X}',
        'signed_to_unsigned_hex':f'{(-32767)%(2**32):08X}',
        '69_minus_38':(69+((~38)&255)+1)&255,
        'negative_98_hex':f'{(-98)%(2**32):08X}',
        'negative_04375_hex':struct.pack('>f',-0.4375).hex().upper(),
        'CC900000_value':struct.unpack('>f',bytes.fromhex('CC900000'))[0],
        'B0C00000_value':struct.unpack('>f',bytes.fromhex('B0C00000'))[0],
    }
    assert values['137.5_octal']=='211.4'
    assert values['unsigned_65530_hex']=='0000FFFA'
    assert values['signed_to_unsigned_hex']=='FFFF8001'
    assert values['69_minus_38']==31
    assert values['negative_98_hex']=='FFFFFF9E'
    assert values['negative_04375_hex']=='BEE00000'
    assert values['CC900000_value']<values['B0C00000_value']<0
    checks.append({'id':'RV-CO02-NUMERIC','source':file_identity(co2),'question':'CO2-1、CO2-2、CO2-3、CO2-4、CO2-5、CO2-7、CO2-8','method':'进制值还原、模运算及Python binary32编码/解码独立检查','results':values,'status':'passed'})
    n=32;x=10;y=(-20)%(1<<n)
    sub=(x-y)%(1<<n)
    cf=int(x<y)
    sf=sub>>(n-1)
    of=int(bool(((x^y)&(x^sub))&(1<<(n-1))))
    assert sub==30 and cf==1 and sf==0 and of==0
    checks.append({'id':'RV-CO02-FLAGS','source':file_identity(co2),'question':'CO2-6','method':'32位按位减法结果、无符号借位及异号溢出逻辑独立求值','results':{'result':sub,'CF':cf,'SF':sf,'OF':of},'status':'passed'})
    def f32(x):return struct.unpack('>f',struct.pack('>f',x))[0]
    a=f32(2**25);b=-a;c=1.0
    left=f32(f32(a+b)+c);right=f32(a+f32(b+c))
    assert left==1 and right==0
    checks.append({'id':'RV-CO02-NONASSOC','source':file_identity(co2),'question':'浮点结合律反例','method':'每次加法后强制round-to-nearest binary32存储','results':{'left_grouped':left,'right_grouped':right},'status':'passed'})
    ds2='manuscript/DS/02_线性表下标结点与指针.md'
    rotations=0
    for n in range(2,31):
        for p in range(1,n):
            data=list(range(n))
            for l,r in [(0,p-1),(p,n-1),(0,n-1)]:
                while l<r:
                    data[l],data[r]=data[r],data[l];l+=1;r-=1
            assert data==list(range(p,n))+list(range(p))
            rotations+=1
    sequences=0
    for n in range(0,8):
        for arr in product(range(min(3,n)),repeat=n):
            candidate=count=0
            for value in arr:
                if count==0:candidate=value;count=1
                elif value==candidate:count+=1
                else:count-=1
            answer=candidate if arr.count(candidate)>n//2 else -1
            oracle=next((x for x,c in Counter(arr).items() if c>n/2),-1)
            assert answer==oracle
            sequences+=1
    checks.append({'id':'RV-DS02-ALGORITHMS','source':file_identity(ds2),'question':'DS2-4/DS2-6','method':'三次逆置按交换执行后与旋转规格比较；抵消算法与频次统计独立比较，含无主元素/空输入','results':{'rotations_checked':rotations,'majority_sequences_checked':sequences},'status':'passed'})
    cn1='manuscript/CN/01_网络层次服务与性能.md';cn2='manuscript/CN/02_物理层信号速率与交换.md'
    tx=Fraction(1500*8,10**8);prop=Fraction(200000,2*10**8)
    assert (tx+prop)*10**3==Fraction(28,25)
    old=min(2*10*5,10*math.log2(1001));new=min(2*20*5,20*math.log2(10001))
    assert abs(new/old-2.006577)<0.00001
    checks.append({'id':'RV-CN01-02-RATES','source':[file_identity(cn1),file_identity(cn2)],'question':'CN01小例/CN2-2','method':'统一SI单位和有理数；分别比较Nyquist/Shannon上界','results':{'CN01_arrival_ms':str((tx+prop)*10**3),'CN02_original_upper_Mbps':old,'CN02_new_upper_Mbps':new,'ratio':new/old},'status':'passed'})
    # 微秒为单位，逐分组、逐链路递推服务开始；不同跳可重叠。
    end=[[Fraction(0) for _ in range(1000)] for _ in range(2)]
    for packet in range(1000):
        for hop in range(2):
            arrival=Fraction(0) if hop==0 else end[hop-1][packet]+10
            free=Fraction(0) if packet==0 else end[hop][packet-1]
            end[hop][packet]=max(arrival,free)+80
    whole=end[-1][-1]+10
    assert whole==80100
    checks.append({'id':'RV-CN02-2023-PIPELINE','source':file_identity(cn2),'question':'CN2-3','method':'1000分组/2链路的实际事件递推，不直接套总时延闭式','results':{'last_bit_arrival_microseconds':str(whole),'first_packet_last_bit_arrival_microseconds':str(end[-1][0]+10),'last_three_second_link_send_ends':list(map(str,end[-1][-3:]))},'status':'passed'})
    cn3='manuscript/CN/03_链路层可靠传输与介质访问.md'
    def crc(value,g):
        while value.bit_length()>=g.bit_length():
            value^=g<<(value.bit_length()-g.bit_length())
        return value
    crc_r=[crc(int(s,2),0b10011) for s in ['101110000','101110100','101111000','101111100']]
    assert crc_r==[12,8,4,0]
    assert crc(0b101001<<3,0b1101)==1
    words=[int(s,2) for s in ['10011010','01011100','11110000','00001111']]
    distances=[(a^b).bit_count() for a,b in combinations(words,2)]
    assert min(distances)==4
    assert Fraction(1998*8,54)+2*28+2==354
    checks.append({'id':'RV-CN03-ERRORS-NAV','source':file_identity(cn3),'question':'CRC算例/2023/2025码距/2024NAV','method':'多项式逐位异或除法、码字两两异或计位及有理数时序','results':{'crc_remainders':[f'{r:04b}' for r in crc_r],'hamming_distances':distances,'NAV_microseconds':354},'status':'passed'})
    ds4='manuscript/DS/04_串与模式匹配.md'
    def nexts(p):
        if not p:return [],[]
        nxt=[-1]+[0]*(len(p)-1);i=0;k=-1
        while i<len(p)-1:
            if k==-1 or p[i]==p[k]:
                i+=1;k+=1;nxt[i]=k
            else:k=nxt[k]
        nv=[-1]*len(p)
        for j in range(1,len(p)):
            k=nxt[j];nv[j]=nv[k] if k>=0 and p[j]==p[k] else k
        return nxt,nv
    def match(t,p,nxt):
        if not p:return 0
        i=j=0
        while i<len(t) and j<len(p):
            if j==-1 or t[i]==p[j]:i+=1;j+=1
            else:j=nxt[j]
        return i-len(p) if j==len(p) else -1
    kn=0
    for nl in range(7):
        for ts in product('ab',repeat=nl):
            t=''.join(ts)
            for ml in range(5):
                for ps in product('ab',repeat=ml):
                    p=''.join(ps);nxt,nv=nexts(p)
                    assert match(t,p,nxt)==t.find(p)
                    assert match(t,p,nv)==t.find(p)
                    kn+=1
    assert nexts('aabaab')==([-1,0,1,0,1,2],[-1,-1,1,-1,-1,1])
    heap=[3,4,5,6,8,10];heapq.heapify(heap);merges=[]
    while len(heap)>1:
        v=heapq.heappop(heap)+heapq.heappop(heap);merges.append(v);heapq.heappush(heap,v)
    assert sum(merges)==90
    checks.append({'id':'RV-DS04-05-KMP-HUFFMAN','source':[file_identity(ds4),file_identity('manuscript/DS/05_树二叉树与应用.md')],'question':'KMP/nextval/DS5-5','method':'二元短串穷举与str.find规格比较；独立最小堆执行哈夫曼合并','results':{'kmp_text_pattern_pairs_checked':kn,'aabaab_next_and_nextval':nexts('aabaab'),'huffman_merge_weights':merges,'WPL':sum(merges)},'status':'passed'})
    def priority_schedule(jobs,larger=True):
        remaining={p:b for p,a,priority,b in jobs};t=0;segments=[];complete={}
        while any(remaining.values()):
            candidates=[x for x in jobs if x[1]<=t and remaining[x[0]]>0]
            if not candidates:t+=1;continue
            p,a,pri,b=(max if larger else min)(candidates,key=lambda x:x[2])
            if segments and segments[-1][0]==p:segments[-1][2]=t+1
            else:segments.append([p,t,t+1])
            remaining[p]-=1;t+=1
            if remaining[p]==0:complete[p]=t
        return segments,complete
    jobs=[('P1',0,1,60),('P2',20,10,42),('P3',30,100,13)]
    timeline,complete=priority_schedule(jobs)
    ta=[complete[p]-a for p,a,pri,b in jobs]
    assert ta==[115,55,13]
    jobs2=[('P0',0,15,100),('P1',10,20,60),('P2',10,10,20),('P3',15,6,10)]
    timeline2,complete2=priority_schedule(jobs2,False)
    assert len(timeline2)==6 and timeline2[-1][-1]==190
    checks.append({'id':'RV-OS02-PRIORITY','source':file_identity('manuscript/OS/02_进程线程调度与上下文切换.md'),'question':'OS2-3/OS2-4','method':'逐1ms选择当前已到达且最高优先级者并扣剩余服务量，非直接重抄完成时刻','results':{'2023_timeline':timeline,'2023_turnaround':ta,'2022_timeline':timeline2,'2022_dispatches':len(timeline2)},'status':'passed'})
    def safe_orders(available,alloc,need):
        orders=[]
        for order in permutations(range(len(alloc))):
            work=list(available)
            for i in order:
                if any(n>w for n,w in zip(need[i],work)):break
                work=[w+a for w,a in zip(work,alloc[i])]
            else:orders.append(order)
        return orders
    assert not safe_orders((0,2,1),[(2,0,0),(1,2,0),(0,1,1),(0,0,1)],[(0,0,1),(1,3,2),(1,3,1),(2,0,0)])
    alloc=[(0,0,3),(1,0,0),(1,3,5),(0,0,2),(0,0,1)]
    need=[(0,0,1),(0,7,5),(1,0,0),(0,6,2),(0,6,4)]
    counts=[len(safe_orders(a,alloc,need)) for a in [(1,4,0),(0,6,2),(1,1,1),(0,4,7)]]
    assert counts[0]>0 and counts[1:]==[0,0,0]
    checks.append({'id':'RV-OS04-BANKER','source':file_identity('manuscript/OS/04_死锁与资源分配.md'),'question':'OS4-2/OS4-3','method':'穷举全部进程序列，逐分量验证可完成性','results':{'2011_safe_order_count':0,'five_process_each_candidate_safe_order_count':counts},'status':'passed'})
    def buffer_events(n,T,M,C,slots):
        buffer_free=[0]*slots;device_free=worker_free=0;trace=[]
        for block in range(n):
            slot=block%slots
            input_start=max(device_free,buffer_free[slot]);input_end=input_start+T
            copy_start=max(input_end,worker_free);copy_end=copy_start+M
            compute_end=copy_end+C
            buffer_free[slot]=copy_end;device_free=input_end;worker_free=compute_end
            trace.append({'block':block+1,'slot':slot,'input':[input_start,input_end],'copy':[copy_start,copy_end],'compute':[copy_end,compute_end]})
        return worker_free,trace
    event_cases=0
    for n,T,M,C in product(range(1,7),[1,2,5,10],[1,3,7],[1,4,8]):
        single,unused=buffer_events(n,T,M,C,1)
        double,unused=buffer_events(n,T,M,C,2)
        assert single==T+M+(n-1)*(max(T,C)+M)+C
        assert double==T+(n-1)*max(T,M+C)+M+C
        event_cases+=1
    single,trace1=buffer_events(10,100,50,50,1);double,trace2=buffer_events(10,100,50,50,2)
    assert single==1550 and double==1100
    checks.append({'id':'RV-OS07-BUFFERS','source':file_identity('manuscript/OS/07_IO设备与外存调度.md'),'question':'单/双缓冲一般公式及OS7-2','method':'按设备可用/缓冲释放/单用户工作区三种资源独立推进事件，枚举不同阶段长短与n','results':{'parameter_combinations':event_cases,'2011_single_microseconds':single,'2011_double_microseconds':double,'single_first_three':trace1[:3],'double_first_three':trace2[:3]},'status':'passed'})
    idx=307400//1024;off=307400%1024
    assert (idx,off)==(300,200)
    assert divmod(409612,8192)==(50,12)
    assert 78*64+6*8+6==5046
    scan=(199-58)+(199-15)
    fcfs=sum(abs(a-b) for a,b in zip([58,130,42,180,15],[130,42,180,15,199]))
    assert scan==325 and fcfs==647
    checks.append({'id':'RV-OS06-07-ADDRESSES','source':[file_identity('manuscript/OS/06_文件目录与文件系统.md'),file_identity('manuscript/OS/07_IO设备与外存调度.md')],'question':'混合索引/位图/CHS/磁盘调度','method':'整数商余数与实际相邻磁道位移求和','results':{'logical_block':idx,'byte_offset':off,'bitmap_disk_block':32+409612//8192,'bitmap_byte':(409612%8192)//8,'CHS_record':5046,'SCAN_distance':scan,'FCFS_distance':fcfs},'status':'passed'})
    mtu=800;header=20;payload=1560;fragment_data=(mtu-header)//8*8
    pieces=[];remaining=payload;position=0
    while remaining:
        length=min(remaining,fragment_data)
        pieces.append({'total_length':length+header,'offset':position//8,'MF':int(remaining>length)})
        position+=length;remaining-=length
    assert pieces==[{'total_length':796,'offset':0,'MF':1},{'total_length':796,'offset':97,'MF':1},{'total_length':28,'offset':194,'MF':0}]
    subnet=ipaddress.ip_interface('168.16.84.24/20').network
    aggregate=list(ipaddress.collapse_addresses(ipaddress.ip_network(s) for s in ['35.230.32.0/21','35.230.40.0/21','35.230.48.0/21','35.230.56.0/21']))
    assert str(subnet)=='168.16.80.0/20' and list(map(str,aggregate))==['35.230.32.0/19']
    a=0xb9b6+0x65c5;folded=(a&0xffff)+(a>>16);checksum=(~folded)&0xffff
    assert checksum==0xe083
    checks.append({'id':'RV-CN04-05-FIELDS','source':[file_identity('manuscript/CN/04_网络层地址路由与转发.md'),file_identity('manuscript/CN/05_传输层可靠连接与窗口.md')],'question':'IPv4分片/子网/聚合/UDP反码和','method':'分片逐段扣原数据、标准库IP运算及16位回卷实际操作','results':{'fragments':pieces,'network':str(subnet),'aggregate':list(map(str,aggregate)),'UDP_checksum':f'{checksum:04X}','close_client_ms':50+1600,'close_server_ms':25*3},'status':'passed'})
    def quadratic_table():
        table=[None]*11
        for key in [20,3,11,18,9,14,7]:
            h=(key*3)%11
            for k in range(11):
                slot=(h+k*k)%11
                if table[slot] is None:table[slot]=key;break
            else:raise AssertionError('insertion failed')
        return table
    table=quadratic_table()
    assert table==[11,None,14,7,None,20,9,None,None,3,18]
    visits=[];key=8;h=key*3%11
    for k in range(11):
        slot=(h+k*k)%11;visits.append(slot)
        if table[slot] is None:break
    assert visits==[2,3,6,0,7]
    assert min((400/s+s)/2+1 for s in [8,10,20,25])==(400/20+20)/2+1
    checks.append({'id':'RV-DS07-SEARCH','source':file_identity('manuscript/DS/07_查找与索引结构.md'),'question':'2024二次探查/2025分块查找','method':'依次实际探查填槽，与完整表比较；失败逐步探查至首次空位','results':{'quadratic_table':table,'key8_probe_addresses':visits,'best_block_size':20},'status':'passed'})
    def cache_array(column_major,ways):
        sets=[[] for _ in range(64)];hits=misses=0
        pairs=((i,j) for j in range(64) for i in range(24)) if column_major else ((i,j) for i in range(24) for j in range(64))
        # 故意使用不连续物理页框，检验结果没有偷用虚页高位。
        ppns={0x422:0x1005,0x423:0x3020}
        for i,j in pairs:
            virtual=0x422000+(64*i+j)*4
            physical=ppns[virtual>>12]*4096+(virtual&4095)
            block=physical//32;group=block%64;tag=block//64
            lines=sets[group]
            if tag in lines:
                hits+=1;lines.remove(tag)
            else:
                misses+=1
                if len(lines)==ways:lines.pop(0)
            lines.append(tag)
        return {'hits':hits,'misses':misses,'accesses':hits+misses,'hit_rate':str(Fraction(hits,hits+misses))}
    matrix={(direction,ways):cache_array(direction=='column',ways) for direction,ways in [('row',4),('column',4),('row',2),('column',2)]}
    assert matrix[('row',4)]['misses']==matrix[('column',4)]['misses']==192
    assert matrix[('row',2)]['misses']==192 and matrix[('column',2)]['misses']==1536
    checks.append({'id':'RV-CO03-2023-INTEGRATED','source':file_identity('manuscript/CO/03_存储系统与地址.md'),'question':'CO3-11及2路原创变式','method':'逐次生成1536个元素字节地址，映射到不连续物理页框，再执行64组LRU/写分配访问','results':{'4way_row':matrix[('row',4)],'4way_column':matrix[('column',4)],'2way_row':matrix[('row',2)],'2way_column':matrix[('column',2)]},'status':'passed'})
    # 直接按A/Q/q-1拼接、补码解释、整串算术移位核Booth中间值。
    A=0;Q=5;qminus=0;M=-3;booth=[]
    for turn in range(4):
        pair=(Q&1)*2+qminus
        if pair==1:A+=M
        elif pair==2:A-=M
        combined=((A&31)<<5)|(Q<<1)|qminus
        signed=combined if combined<512 else combined-1024
        combined=(signed>>1)&1023
        A=(combined>>5)&31;A=A if A<16 else A-32
        Q=(combined>>1)&15;qminus=combined&1
        booth.append({'A':f'{A&31:05b}','Q':f'{Q:04b}','qminus':qminus})
    assert booth==[{'A':'00001','Q':'1010','qminus':1},{'A':'11111','Q':'0101','qminus':0},{'A':'00001','Q':'0010','qminus':1},{'A':'11111','Q':'0001','qminus':0}]
    assert (A<<4)+Q==-15
    checks.append({'id':'RV-CO02-BOOTH-TRACE','source':file_identity(co2),'question':'新增−3×5 Booth轨迹','method':'10位整串补码算术右移、逐轮拆回A/Q/q−1，与稿中四行完全比较','results':booth,'status':'passed'})
    # 把题中的符号位逻辑与有符号整数的真实越界条件比较，非重复代入答案。
    pairs=0
    for a_raw,b_raw in product(range(256),repeat=2):
        av=a_raw if a_raw<128 else a_raw-256
        bv=b_raw if b_raw<128 else b_raw-256
        a=a_raw>>7;b=b_raw>>7
        for subtract in [False,True]:
            value=av-bv if subtract else av+bv
            f=(value&255)>>7
            logic=(a and not b and not f) or (not a and b and f) if subtract else (a and b and not f) or (not a and not b and f)
            assert bool(logic)==(value < -128 or value > 127)
        pairs+=1
    samples16=[]
    for av,bv,subtract in [(32767,1,False),(-32768,1,True),(32767,-1,False),(-32768,-1,True)]:
        value=av-bv if subtract else av+bv
        samples16.append({'A':av,'B':bv,'operation':'subtract' if subtract else 'add','F_hex':f'{value&65535:04X}','OF':int(value < -32768 or value > 32767)})
    assert [r['OF'] for r in samples16]==[1,1,0,0]
    checks.append({'id':'RV-CO05-2022-INTEGRATED','source':file_identity('manuscript/CO/05_CPU与控制.md'),'question':'新增2022第43题（例5-2）','method':'穷举8位全部65536对输入，将加减OF符号位表达式与整数越界独立比较；另核16位边界例','results':{'eight_bit_operand_pairs':pairs,'operations_per_pair':2,'sixteen_bit_boundary_samples':samples16,'register_number_bits':4,'register_count':16,'fetch_control_sequence':['PCout,MARin','Read (5 cycles, includes MDR transfer)','MDRout,IRin'],'fetch_cycle_count':7},'status':'passed'})
    data={'generated_at':datetime.now(timezone.utc).isoformat(),'scope':'仅列实际复算的题目；未核验整书所有计算','checks':checks}
    (OUT/'independent_calculations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'status':'passed'},ensure_ascii=False))

if __name__=='__main__':main()
