import json,math,ipaddress,heapq
from pathlib import Path
out=Path(__file__).parent;logs=[]
def add(id,calculation,result,answer,assumptions=None,status='独立复算通过'):
 logs.append(dict(id=id,calculation=calculation,result=result,answer=answer,assumptions=assumptions or [],status=status))
# 抢占调度：事件到达、优先级和剩余执行量独立模拟。
jobs=[('P0',0,15,100),('P1',10,20,60),('P2',10,10,20),('P3',15,6,10)]
remaining={n:t for n,a,p,t in jobs};timeline=[];t=0;done=set()
while len(done)<len(jobs):
 ready=[j for j in jobs if j[1]<=t and j[0] not in done]
 if not ready:t=min(j[1] for j in jobs if j[0] not in done);continue
 n,a,p,tot=min(ready,key=lambda j:j[2]);future=[j[1] for j in jobs if j[1]>t];end=min(t+remaining[n],min(future,default=math.inf));
 if timeline and timeline[-1][0]==n and timeline[-1][2]==t:timeline[-1][2]=end
 else:timeline.append([n,t,end])
 remaining[n]-=end-t;t=end
 if not remaining[n]:done.add(n)
add('ERR-OS-2.2-052','逐到达事件优先级抢占模拟',{'timeline':timeline,'dispatches':len(timeline)},'C')
alloc=[[0,0,3],[1,0,0],[1,3,5],[0,0,2],[0,0,1]];maxi=[[0,0,4],[1,7,5],[2,3,5],[0,6,4],[0,6,5]];need=[[m-a for m,a in zip(mm,aa)] for mm,aa in zip(maxi,alloc)];bank=[]
for av in [[1,4,0],[0,6,2],[1,1,1],[0,4,7]]:
 work=av[:];seq=[]
 while True:
  cand=next((p for p in range(5) if p not in seq and all(a<=b for a,b in zip(need[p],work))),None)
  if cand is None:break
  seq.append(cand);work=[a+b for a,b in zip(work,alloc[cand])]
 bank.append({'available':av,'safe':len(seq)==5,'completed_sequence':seq,'remaining_work':work})
add('ERR-OS-2.4-026','Need矩阵与逐步Work安全性模拟',{'need':need,'cases':bank},'C')
add('ERR-OS-3.1-054','按11位偏移计算',{'page_size':2**11,'total_KiB':2**18//1024,'frames':2**7,'instruction_physical':2*2048+1500,'operand_frame':[2,3,7][2500//2048]},'B',['按字节编址，物理容量按18位地址模型'])
free=[(0,55)];used={}
for op,size in [('alloc',15),('alloc',30),('free',15),('alloc',8),('alloc',6)]:
 if op=='alloc':
  p,n=min((q for q in free if q[1]>=size),key=lambda q:q[1]);free.remove((p,n));used[size]=(p,size)
  if n>size:free.append((p+size,n-size))
 else:free.append(used.pop(size))
add('ERR-OS-3.1-061','最佳适配空闲分区模拟',{'free':sorted(free),'max_free_MB':max(n for p,n in free)},'B')
add('ERR-OS-3.1-062','每页页表项=2^10/2，目录项=2^16/512',{'entries_per_page':512,'directory_entries':128},'B')
v=int('20501225',16);add('ERR-OS-3.1-068','按10/10/12位掩码提取',{'directory_hex':hex(v>>22),'page_hex':hex((v>>12)&1023),'offset_hex':hex(v&4095)},'A')
def faults(seq,frames,algo):
 cache=[];n=0
 for pos,p in enumerate(seq):
  if p in cache:
   if algo=='LRU':cache.remove(p);cache.append(p)
   continue
  n+=1
  if len(cache)==frames:
   if algo in ['FIFO','LRU']:cache.pop(0)
   else:
    def nxt(q):
     try:return seq.index(q,pos+1)
     except ValueError:return math.inf
    cache.remove(max(cache,key=nxt))
  cache.append(p)
 return n
seq=[(j*128+i)*4//512 for i in range(128) for j in range(128)];add('ERR-OS-3.2-012','实际生成16384次数组访问页号并模拟1页框',{'faults_int4B':faults(seq,1,'FIFO')},'D',['int占4B；数据初始不在内存'])
seq=[(i*64+j)//128 for j in range(64) for i in range(64)];vals={a:faults(seq,3,a) for a in ['FIFO','LRU','OPT']};add('ERR-OS-3.2-013','生成4096次数组访问的页号，用3数据页框分别模拟置换',vals,'C',['书答案2048对应FIFO/LRU；若允许OPT，结果不同'],'条件不足：置换算法影响结果')
add('ERR-OS-3.2-014','0.75×1+0.25×(2+1)',1.5,'B',['忽略TLB查找，无缺页'])
add('ERR-OS-3.2-018','32位按字节地址空间',{'bytes':2**32,'GiB':4},'D')
add('ERR-OS-3.2-019','2^32字节/512字节每页',{'entries':2**32//512,'power':23},'C')
add('ERR-OS-3.2-052','从图t位置向前取6次再去重',{'last_six':[6,0,3,2,3,2],'working_set':sorted(set([6,0,3,2,3,2]))},'A',['范围归属待大纲核验'])
add('ERR-OS-4.2-010','3200×16/1024=50块；独立区分两种平均口径',{'book_approximation':50/2+1,'uniform_exact_expectation':(50+1)/2+1},'B',['书采用N/2近似，精确等概率期望26.5不在选项'],'答案口径需注明近似')
add('ERR-OS-4.2-025','每块floor(512/100)=5条记录；顺链读5块后写1块',{'records_per_block':5,'read_blocks':5,'write_blocks':1,'total_IO':6},'D',['隐式链接且目录已在内存'])
add('ERR-OS-4.2-026','偏移1569//512=3，取链第4块',{'zero_based_index':1569//512,'disk_block':[50,121,75,80,63][1569//512]},'B')
clusters=512*2**20//(2*4*1024);add('ERR-OS-4.2-028','按题源把最大文件长度视为整个分区，计算簇数及最少簇号位数',{'clusters':clusters,'bits':math.ceil(math.log2(clusters)),'FAT_KiB':clusters*2//1024},'B',['最大文件=可管理分区容量的教材假设；忽略保留簇和特殊标志'])
add('ERR-OS-4.2-060','4类别×5独立权限位',20,'D')
block=409612//(1024*8);byte=(409612%(1024*8))//8;add('ERR-OS-4.3-014','以每位图块8192位定位，再除8定位字节',{'bitmap_disk_block':32+block,'byte':byte,'bit':409612%8},'C')
def buffers(double):
 # 磁盘读完成后，传送操作占CPU；传送和分析在用户区顺序执行。
 disk=0;cpu=0;last_release=[0,0];trace=[]
 for i in range(10):
  b=i%2 if double else 0;start=max(disk,last_release[b]);read_end=start+100;disk=read_end
  copy_start=max(cpu,read_end);copy_end=copy_start+50;last_release[b]=copy_end;cpu=copy_end+50
  trace.append({'block':i+1,'read':[start,read_end],'copy':[copy_start,copy_end],'analyse':[copy_end,cpu]})
 return {'finish_us':cpu,'trace':trace}
add('ERR-OS-5.2-038','按缓冲释放、磁盘及CPU资源约束逐块排程',{'single':buffers(False),'double':buffers(True)},'B')
add('ERR-OS-5.3-016','78×8×8+6×8+6',78*64+6*8+6,'B',['全部从0编号'])
add('ERR-CN-2.1-007','2^(4000/1000)',16,'D')
add('ERR-CN-2.1-010','2×8000×log2(8)',48000,'C',['独立码元率受2B限制'])
add('ERR-CN-2.1-012','min(2×4000×log2(2),4000×log2(128))',{'nyquist':8000,'shannon':28000,'max_bps':8000},'B')
add('ERR-CN-2.1-016','(1/(1/8))×log2(16)',32,'B')
old=min(2*10e6*5,10e6*math.log2(1+10**3));new=min(2*20e6*5,20e6*math.log2(1+10**4));add('ERR-CN-2.1-017','原/新信道各取Nyquist和Shannon较小值',{'old_bps':old,'new_bps':new,'ratio':new/old},'A')
add('ERR-CN-2.3-007','10Mb/s÷5台',2,'A',['均分理想平均值'])
add('ERR-CN-3.4-010','累计ACK4覆盖0..4，已发送0..6',{'retransmit':[5,6],'count':2},'B',['ACK表示刚收到的帧号'])
Tf=128*8/16000;cycle=Tf+.5+Tf;W=math.ceil(cycle/Tf);add('ERR-CN-3.4-019','GBN完整回环含ACK发送，W=ceil((Tf+2Tp+Ta)/Tf)，2^k−1≥W',{'Tf_s':Tf,'ACK_s':Tf,'cycle_s':cycle,'W_min':W,'k_min':math.ceil(math.log2(W+1))},'C')
add('ERR-CN-3.6-008','64−(6+6+4+2+4)−40',2,'A',['802.1Q帧不含前导码，最小帧64B'])
add('ERR-CN-3.6-020','往返2×(100+100)m/(2×10^8m/s)',{'us':2*200/(2e8)*1e6},'A')
data_us=1998*8/54;add('ERR-CN-3.6-048','CTS结束后SIFS+数据+SIFS+ACK',{'data_us':data_us,'NAV_us':28+data_us+28+2},'B')
add('ERR-CN-3.8-020','目的MAC6B×8/100Mb/s',{'us':6*8/100},'B')
net=ipaddress.ip_network('211.71.136.23/20',strict=False);add('ERR-CN-4.2-043','对源和目的分别应用/20掩码',{'network':str(net),'same_subnet':ipaddress.ip_address('211.71.130.25') in net},'B')
add('ERR-CN-4.2-064','5叶子完整二叉子网划分最深20+4=/24',{'prefix':24,'usable':2**(32-24)-2},'B',['覆盖整个/20的恰5子网划分'])
payload=1580-20;cap=(800-20)//8*8;parts=[];off=0
while payload:
 n=min(cap,payload);payload-=n;parts.append({'total':20+n,'data':n,'offset_8B':off//8,'MF':int(payload>0)});off+=n
add('ERR-CN-4.2-066','按8B对齐逐片切分1560B负载',parts,'B')
s=int('1011100110110110',2)+int('0110010111000101',2);fold=(s&0xffff)+(s>>16);check=(~fold)&0xffff;add('ERR-CN-5.2-016','二进制求和并端回卷，最后取反',{'raw_sum':hex(s),'folded':hex(fold),'checksum_hex':hex(check),'checksum_bits':f'{check:016b}'},'C')
add('ERR-CN-5.3-021','末次ACK序号−初始SYN序号−SYN占号−FIN占号',985-211-2,'B')
cw=1;threshold=8;traj=[]
for r in range(1,14):
 traj.append(cw)
 if r==8:threshold=cw/2;cw=1
 elif cw<threshold:cw=min(2*cw,threshold)
 else:cw+=1
add('ERR-CN-5.3-033','逐发送轮次更新cwnd，12超时后门限6',traj,'C',['第1轮cwnd=1，发生超时的12算第8轮'])
cw=1;threshold=4;traj=[]
for r in range(10):cw=min(cw*2,threshold) if cw<threshold else cw+1;traj.append(cw)
add('ERR-CN-5.3-047','超时后cwnd逐RTT增长，再取min(rwnd,cwnd)',{'cwnd_KiB':traj,'rwnd_KiB':10,'send_window':min(10,cw)},'A')
add('ERR-CN-5.3-052','最长按拥塞避免每RTT增1MSS',(32-8)*2,'D',['单位ms；慢开始只会更快'])
cw=2000+1000;rw=4000;outstanding=1000;add('ERR-CN-5.3-060','ACK3001只确认第一个1000B段；慢开始更新cwnd后扣在途量',{'cwnd':cw,'rwnd':rw,'outstanding':outstanding,'can_send_bytes':min(cw,rw)-outstanding,'segments':(min(cw,rw)-outstanding)//1000},'A')
add('ERR-CN-6.2-012','缓存命中0次；无缓存沿root/com/xyz.com/abc.xyz.com共4次',{'min_queries':0,'max_queries':4},'C')
add('ERR-CN-6.2-014','DNS缓存命中0，最坏3个远程RTT；TCP+HTML2RTT',{'min_ms':2*10,'max_ms':(3+2)*10},'D',['忽略局域网其他时延'])
add('ERR-CN-6.5-012','HTML1RTT后3图片流水线共1RTT',2,'A',['已发出HTTP请求；不再加TCP握手'])
add('ERR-CN-6.5-018','TCP握手1RTT+HTML1RTT+图像2RTT',{'RTTs':4,'ms':40},'B',['题源初始拥塞窗口1MSS；现代窗口较大时结论会改变'])
add('ERR-CN-6.5-019','HTML及7图各新连接握手+请求响应2RTT',(1+7)*2,'D',['不并行，非持久HTTP'])
records={r['id']:r for r in logs}
validation_checks={
 'priority_dispatches':records['ERR-OS-2.2-052']['result']['dispatches']==6,
 'banker_four_cases':[r['safe'] for r in records['ERR-OS-2.4-026']['result']['cases']]==[True,False,False,False],
 'single_buffer_finish':records['ERR-OS-5.2-038']['result']['single']['finish_us']==1550,
 'double_buffer_finish':records['ERR-OS-5.2-038']['result']['double']['finish_us']==1100,
 'array_replacement_counterexample':records['ERR-OS-3.2-013']['result']=={'FIFO':2048,'LRU':2048,'OPT':1917},
 'address_field_directory':records['ERR-OS-3.1-068']['result']['directory_hex']=='0x81',
 'address_field_page':records['ERR-OS-3.1-068']['result']['page_hex']=='0x101',
 'fragment_lengths':[r['total'] for r in records['ERR-CN-4.2-066']['result']]==[796,796,28],
 'fragment_MF':[r['MF'] for r in records['ERR-CN-4.2-066']['result']]==[1,1,0],
 'ones_complement_checksum':records['ERR-CN-5.2-016']['result']['checksum_hex']=='0xe083',
 'TCP_outstanding_allowance':records['ERR-CN-5.3-060']['result']['segments']==2,
}
assert all(validation_checks.values()),validation_checks
(out/'os_cn_calculation_log.json').write_text(json.dumps({'date':'2026-10-15','records':logs,'validation_checks':validation_checks},ensure_ascii=False,indent=2))
for r in logs:
 if r['status']!='独立复算通过':print(r['id'],r['status'],r['result'])
print('computed',len(logs))
