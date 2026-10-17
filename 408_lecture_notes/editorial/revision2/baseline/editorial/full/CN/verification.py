#!/usr/bin/env python3
"""Portable arithmetic/state cross-checks for the CN manuscript (stdlib only)."""
from pathlib import Path
from itertools import combinations,product
import ipaddress, math, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
checks=[]
def record(id,description,actual,expected,assumptions=()):
    assert actual==expected,(id,actual,expected)
    checks.append({'id':id,'description':description,'actual':actual,'expected':expected,'assumptions':list(assumptions),'status':'PASS'})
def close(id,description,actual,expected,tol=1e-9,assumptions=()):
    assert abs(actual-expected)<=tol,(id,actual,expected)
    checks.append({'id':id,'description':description,'actual':actual,'expected':expected,'tolerance':tol,'assumptions':list(assumptions),'status':'PASS'})
# Time and rates, checked in SI units.
close('CN-CAL-001','1500B@100Mb/s sends in120us',1500*8/100e6,120e-6)
close('CN-CAL-002','200km propagation is1ms',200e3/2e8,.001)
close('CN-CAL-003','last bit arrives1.12ms',1500*8/100e6+200e3/2e8,.00112)
record('CN-CAL-004','single-way BDP is100000bit',int(100e6*.001),100000)
record('CN-CAL-005','4kb/s at1000Baud needs16states',2**(4000//1000),16)
record('CN-CAL-006','one16-state symbol each1/8s gives32bit/s',int(1/(1/8)*math.log2(16)),32)
record('CN-CAL-007','200kHz 4ASK Nyquist gives800kb/s',int(2*200000*math.log2(4)),800000)
record('CN-CAL-008','8kHz 8-state upper bound remains48kb/s',int(2*8000*math.log2(8)),48000)
record('CN-CAL-009','binary4kHz SNR127 tighter8kb/s bound',int(min(2*4000,4000*math.log2(128))),8000)
old=min(2*10e6*5,10e6*math.log2(1001));new=min(2*20e6*5,20e6*math.log2(10001))
record('CN-CAL-010','QAM32 changed conditions nearest gain is2',min([2,2.2,2.4,2.6],key=lambda x:abs(new/old-x)),2)
# Store-and-forward event recurrence; does not use closed-form pipeline formula.
def pipeline(n,tx,prop):
    free=[0.]*len(tx); arrivals=[]
    for _ in range(n):
        t=0
        for i in range(len(tx)):
            t=max(t,free[i])+tx[i];free[i]=t;t+=prop[i]
        arrivals.append(t)
    return arrivals
close('CN-CAL-011','2023q33 independent hop event simulation',pipeline(1000,[80e-6]*2,[10e-6]*2)[-1],.08010,tol=1e-12)
record('CN-CAL-012','3packets2hops no propagation completes4slots',pipeline(3,[1,1],[0,0]),[2.,3.,4.])
close('CN-CAL-013','chapter2 review10packets3hops',pipeline(10,[.001]*3,[.002]*3)[-1],.018)
# Framing and CRC bitwise long division.
def stuff(bits):
    out=[];run=0
    for b in bits:
        out.append(b);run=run+1 if b=='1' else 0
        if run==5:out.append('0');run=0
    return ''.join(out)
def unstuff(bits):
    out=[];run=0;i=0
    while i<len(bits):
        b=bits[i];out.append(b);run=run+1 if b=='1' else 0;i+=1
        if run==5:assert bits[i]=='0';i+=1;run=0
    return ''.join(out)
record('CN-CAL-014','2013q37 exact18-bit stuffed stream',stuff('0111110001111110'),'011111000011111010')
record('CN-CAL-015','stuffed111110 restores original without deleting data0',unstuff('1111100'),'111110')
def pmod(value,g):
    trace=[value]
    while value.bit_length()>=g.bit_length():
        value^=g<<(value.bit_length()-g.bit_length());trace.append(value)
    return value,trace
rem,trace=pmod(int('101001000',2),int('1101',2))
record('CN-CAL-016','CRC complete division intermediate values',trace,[328,232,56,12,1])
record('CN-CAL-017','CRC appended frame has zero remainder',pmod(int('101001001',2),0b1101)[0],0)
record('CN-CAL-018','2023q37 A/B/C/D remainders', [pmod(int(s,2),0b10011)[0] for s in ['101110000','101110100','101111000','101111100']],[12,8,4,0])
# Demonstrate zero remainder is not a no-error proof: XOR a nonzero generator multiple.
valid=int('101111100',2);corrupt=valid^0b10011
record('CN-CAL-019','nonzero corruption can remain divisible by generator', [valid!=corrupt,pmod(corrupt,0b10011)[0]==0],[True,True])
words=[int(s,2) for s in ['10011010','01011100','11110000','00001111']]
dists=[(a^b).bit_count() for a,b in combinations(words,2)]
record('CN-CAL-020','2025q34 all six Hamming distances',dists,[4,4,4,4,4,8])
record('CN-CAL-021','min distance4 detects3 corrects1',[min(dists)-1,(min(dists)-1)//2],[3,1])
def syndrome(bits):
    res=0
    for i,v in enumerate(bits,1):
        if v:res^=i
    return res
h=[int(c) for c in '1011010'];record('CN-CAL-022','Hamming encoded word syndrome0',syndrome(h),0)
h[5]^=1;record('CN-CAL-023','Hamming flipped position6 gives syndrome6',syndrome(h),6)
h[syndrome(h)-1]^=1;record('CN-CAL-024','Hamming actual correction restores word',''.join(map(str,h)),'1011010')
# Reliable transmission event state checks.
close('CN-CAL-025','2020q36 SW with long ACK gives40percent',.8/(.8+.4+.8),.4)
def gbn_starts(n,w,td=64,tau=250,ta=64):
    starts=[];ack_end=0;acks=[]
    for i in range(n):
        start=starts[-1]+td if starts else 0
        if i>=w:start=max(start,acks[i-w])
        starts.append(start)
        ack_end=max(ack_end,start+td+tau)+ta
        acks.append(ack_end+tau)
    return starts,acks
record('CN-CAL-026','GBN window10 has no idle through40frames',gbn_starts(40,10)[0],list(range(0,40*64,64)))
record('CN-CAL-027','GBN window9 incurs first52ms idle',gbn_starts(12,9)[0][9]-9*64,52)
record('CN-CAL-028','GBN capacity requires4 sequence bits',next(k for k in range(1,8) if 2**k-1>=10),4)
record('CN-CAL-029','2009q35 cumulative ACK3 leaves4..7',list(range(max([0,2,3])+1,8)),[4,5,6,7])
# Actual same input under GBN and SR receive semantics.
def receive(stream,sr):
    expected=2;buf=set();delivered=[]
    for x in stream:
        if x==expected or (sr and expected<=x<expected+4):buf.add(x)
        while expected in buf:buf.remove(expected);delivered.append(expected);expected+=1
    return {'delivered':delivered,'expected':expected,'buffer':sorted(buf)}
record('CN-CAL-030','GBN discards3,4 before2; SR preserves them',[receive([3,4,2],False),receive([3,4,2],True)],[{'delivered':[2],'expected':3,'buffer':[]},{'delivered':[2,3,4],'expected':5,'buffer':[]}])
# Enumerate potential old/new sequence overlap for all windows in an8-number space.
for ws,wr in product(range(1,8),repeat=2):
    old=set(range(ws));new={(ws+i)%8 for i in range(wr)}
    assert bool(old & new)==(ws+wr>8)
record('CN-CAL-031','window ambiguity enumeration49 cases satisfiesWs+Wr<=8',49,49,['枚举旧窗口与新接收窗口序号集合交叠，非仅检查文件存在'])
record('CN-CAL-032','CDMA targetA normalized dot products',[sum(t)/4 for t in [(2,0,2,0),(0,-2,0,-2),(0,2,0,2)]],[1.,-1.,1.])
close('CN-CAL-033','CSMACD frame decrease800bit requires80m decrease',800/1e9/2*2e8,80.)
close('CN-CAL-034','4collisions max15slots',((2**min(4,10))-1)*51.2,768.)
close('CN-CAL-035','11collisions cap exponent10',((2**min(11,10))-1)*51.2e-3,52.3776)
close('CN-CAL-036','2024NAV twoSIFS+DATA+ACK',2*28+1998*8/54+2,354.)
close('CN-CAL-037','cut-through6B@100Mb/s',6*8/100e6,.48e-6)
record('CN-CAL-038','VLAN/native minimum payload and padding',[64-22,64-18,(64-22)-40,(64-18)-40],[42,46,2,6],['采用书题最短64B、标签首尾22B的模型'])
# IPv4 arithmetic and routing independent library cross-checks.
dv=[[1,23,20,22],[12,35,30,28],[24,18,16,36],[36,30,8,24]];cost=[8,10,12,6]
record('CN-CAL-039','2021q37 distance vectors add local link first',[min(a+b for a,b in zip(row,cost)) for row in dv],[9,20,28,20])
g={'A':{'B':1,'C':4},'B':{'A':1,'C':2,'D':5},'C':{'A':4,'B':2,'D':1},'D':{'B':5,'C':1}}
dist={v:math.inf for v in g};dist['A']=0;seen=set();order=[]
while len(seen)<len(g):
 u=min((x for x in g if x not in seen),key=dist.get);seen.add(u);order.append([u,dist[u]])
 for v,w in g[u].items():dist[v]=min(dist[v],dist[u]+w)
record('CN-CAL-040','Dijkstra actual settle sequence',order,[['A',0],['B',1],['C',3],['D',4]])
def fragment(total,header,mtu):
    remain=total-header;off=0;out=[];cap=(mtu-header)//8*8
    while remain:
        size=remain if remain<=mtu-header else cap
        out.append({'payload':size,'total':size+header,'offset':off//8,'mf':int(size<remain)})
        off+=size;remain-=size
    return out
fr=fragment(1580,20,800)
record('CN-CAL-041','2021q36 exact fragments and intermediate offsets',fr,[{'payload':776,'total':796,'offset':0,'mf':1},{'payload':776,'total':796,'offset':97,'mf':1},{'payload':8,'total':28,'offset':194,'mf':0}])
n=ipaddress.ip_network('168.16.84.24/20',strict=False)
record('CN-CAL-042','2023q39 subnet host bounds',[str(n.network_address+1),str(n.broadcast_address-1)],['168.16.80.1','168.16.95.254'])
blocks=[ipaddress.ip_network(x) for x in ['101.200.24.0/21','101.200.20.0/22','101.200.18.0/23','101.200.16.0/24','101.200.17.0/24']]
record('CN-CAL-043','2019q37 constructive full five-subnet partition',[len(blocks),str(list(ipaddress.collapse_addresses(blocks))[0]),min(x.num_addresses-2 for x in blocks)],[5,'101.200.16.0/20',254])
blocks=[ipaddress.ip_network(f'35.230.{x}.0/21') for x in [32,40,48,56]]
record('CN-CAL-044','2018q38 exact aggregation',[str(x) for x in ipaddress.collapse_addresses(blocks)],['35.230.32.0/19'])
record('CN-CAL-045','ARP same-subnet check under20-bit mask',str(ipaddress.ip_interface('211.71.136.23/20').network)==str(ipaddress.ip_interface('211.71.130.25/20').network),True)
record('CN-CAL-046','chapter4 review network/broadcast',['192.168.10.128','192.168.10.191'],[str(ipaddress.ip_interface('192.168.10.131/26').network.network_address),str(ipaddress.ip_interface('192.168.10.131/26').network.broadcast_address)])
record('CN-CAL-047','chapter4 review fragmentation',[fragment(1620,20,620)[0]['payload'],fragment(1620,20,620)[1]['offset']],[600,75])
# UDP checksum and TCP events.
def ones_checksum(words):
 s=sum(words)
 while s>>16:s=(s&0xffff)+(s>>16)
 return (~s)&0xffff
record('CN-CAL-048','2024q39 end-around carry yieldsE083',ones_checksum([0xb9b6,0x65c5]),0xe083)
record('CN-CAL-049','TCP2009 byte ranges produceACK1000',200+300+500,1000)
record('CN-CAL-050','SYN/FIN application bytes only',985-211-2,772)
record('CN-CAL-051','close minimal C1650/S75',[50+2*800,1.5*50],[1650,75.],['服务器收到FIN后立即合并ACK+FIN；单向传播RTT/2'])
# Sequence-ledger independent of min-window answer shortcut.
seqs=[(2001,1000),(3001,1000)];ack=3001
unacked=sum(max(0,a+l-max(a,ack)) for a,l in seqs)
cwnd=2000+1000;window=min(cwnd,4000);available=window-unacked
record('CN-CAL-052','2025q38 actual acknowledged/inflight/new-send states',[unacked,cwnd,window,available,available//1000],[1000,3000,3000,2000,2])
record('CN-CAL-053','linear longest8KBto32KB',[32-8,(32-8)*2],[24,48])
# Explicit13 transmission-round state model in typical33.
rounds=[];cwnd=1;sst=8
for r in range(1,14):
 rounds.append(cwnd)
 if r==8:sst=6;cwnd=1
 else:cwnd=min(cwnd*2,sst) if cwnd<sst else cwnd+1
record('CN-CAL-054','typical33 thirteen rounds',rounds,[1,2,4,8,9,10,11,12,1,2,4,6,7])
# Fixed receiver cap; only model growth until reached (no fictitious exact cwnd after cap).
c=1;hist=[]
while c<10:
 c=min(2*c,4) if c<4 else c+1;hist.append(c)
record('CN-CAL-055','2014q38 reaches rwnd10 by eighthRTT',hist,[2,4,5,6,7,8,9,10])
record('CN-CAL-056','selfcheck FIN and window',[100+1+500,100+1+500+1,min(3000,4000)-1500,5001+3000-1],[601,602,1500,8000])
# DNS and HTTP dependency/event counts.
name='www.abc.xyz.com';labels=name.split('.')[1:]
queries=['root']+['.'.join(labels[i:]) for i in range(len(labels)-1,-1,-1)]
record('CN-CAL-057','2016DNS four delegated steps',queries,['root','com','xyz.com','abc.xyz.com'])
record('CN-CAL-058','nonpersistent serial8objects',sum(1+1 for _ in range(8)),16)
record('CN-CAL-059','already connected pipeline HTMLthen3images',1+1,2)
record('CN-CAL-060','2020DNS and Web shortest/longestms',[(0+1+1)*10,(3+1+1)*10],[20,50])
def send_rounds(segments,window):
 out=[]
 while segments:
  sent=min(segments,window);segments-=sent;out.append(sent);window+=sent
 return out
record('CN-CAL-061','2022image afterHTML withcwnd2MSS',send_rounds(3,2),[2,1])
record('CN-CAL-062','2022TCP+HTML+two image rounds',1+1+len(send_rounds(3,2)),4)
record('CN-CAL-063','larger initial window changes2022 numeric result',1+1+len(send_rounds(3,10)),3,['明确新增初始cwnd较大的变式；原题教材模型仍40ms'])
record('CN-CAL-064','chapter6 review persistent nonpipeline/pipeline',[1+1+4,1+1+1],[6,3])
# Graphic shared data is bound to actual independently computed outcomes.
data=json.loads((ROOT/'figures/CN_model_data.json').read_text())
record('CN-CAL-065','NAV figure data matches independent result',data['shared_values']['nav']['nav_us'],2*28+1998*8/54+2)
record('CN-CAL-066','fragment graphic shares actual computed arrays',[data['shared_values']['fragment']['payloads'],data['shared_values']['fragment']['offsets']],[[r['payload'] for r in fr],[r['offset'] for r in fr]])
record('CN-CAL-067','TCP graphic shares actual remaining segment count',data['shared_values']['tcp2025']['remaining_segments'],available//1000)
result={'status':'PASS','checks':checks,'count':len(checks),'limitations':['计算核验不替代题源全文核验、正式大纲核验或PDF逐页视觉检查','协议计时与增长采用正文已说明的教材模型；未声称所有现代实现数值相同'],'algorithm_processes':['存储转发逐组逐跳事件递推','CRC逐次异或余数','海明综合征与实际翻转恢复','GBN长ACK受窗口约束的发送时刻','GBN/SR接收缓存不同轨迹','序号窗口49种重叠枚举','Dijkstra定型状态','IPv4分片偏移','TCP按ACK移除在途区间','TCP13轮cwnd与HTTP图片分轮']}
(HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'CN independent verification PASS: {len(checks)} recorded checks')
