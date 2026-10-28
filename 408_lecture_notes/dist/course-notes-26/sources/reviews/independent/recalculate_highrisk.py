#!/usr/bin/env python3
"""Independent calculations from named printed examples; no author verification imports."""
from pathlib import Path
from fractions import Fraction as F
from collections import deque
from itertools import combinations, product
import struct, math, ipaddress, json, hashlib
ROOT=Path(__file__).resolve().parents[3]
checks=[]
def ck(ch,what,got,want):
 ok=math.isclose(got,want,rel_tol=1e-9,abs_tol=1e-9) if isinstance(got,float) else got==want
 checks.append(dict(chapter=ch,item=what,actual=got,expected=want,passed=ok))
 if not ok: print('FAIL',ch,what,got,want)
def stuff(s):
 out='';n=0
 for x in s:
  out+=x;n=n+1 if x=='1' else 0
  if n==5:out+='0';n=0
 return out
def crc(s,g):
 a=int(s,2);b=int(g,2)
 while a and a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
 return format(a,f'0{len(g)-1}b')
def checksum(words):
 a=sum(words)
 while a>>16:a=(a&65535)+(a>>16)
 return (~a)&65535
def fragment(data,header,mtu):
 cap=(mtu-header)//8*8;out=[];offset=0
 while data:
  n=min(data,cap);data-=n;out.append([n+header,offset//8,int(data>0)]);offset+=n
 return out
# CN03: each check is recalculated from its input, including intermediate code constraints.
ck('CN03','HDLC stuffed example',stuff('0111110001111110'),'011111000011111010')
ck('CN03','transparent flag data',stuff('01111110'),'011111010')
ck('CN03','CRC101001 G1101',crc('101001000','1101'),'001')
ck('CN03','CRC appended receive',crc('101001001','1101'),'000')
for s,w in zip(['101110000','101110100','101111000','101111100'],['1100','1000','0100','0000']):ck('CN03','CRC option '+s,crc(s,'10011'),w)
cs=['10011010','01011100','11110000','00001111'];dist=[sum(a!=b for a,b in zip(x,y))for x,y in combinations(cs,2)]
ck('CN03','four-code minimum distance',min(dist),4);ck('CN03','four-code pair distances',dist,[4,4,4,4,4,8])
word=[None,1,0,1,1,0,1,0];received=word[:];received[6]^=1
syndrome=sum((sum(received[i] for i in range(1,8)if i&p)%2)*p for p in [1,2,4]);ck('CN03','Hamming single error pos6',syndrome,6)
ck('CN03','stopwait long ACK',F(8000,10000)/(F(8000,10000)*2+F(400,1000)),F(2,5))
ck('CN03','GBN fill-window frames',math.ceil(F(628,64)),10);ck('CN03','GBN sequence bits',math.ceil(math.log2(10+1)),4)
ck('CN03','GBN repeated interval length',len(range(4,8)),4)
ck('CN03','NAV data transmission us',F(1998*8,54),296);ck('CN03','NAV after CTS us',28+296+28+2,354)
ck('CN03','untagged min payload pad',64-6-6-2-4-40,6);ck('CN03','tagged book-model pad',64-6-6-4-2-4-40,2)
ck('CN03','cutthrough destination wait us',6*8/100,0.48)
ck('CN03','GBN2017 maximum utilization',F(7*8,100)/F(112,100),F(1,2))
ck('CN03','window W4 1kbps',F(16,19),F(16,19));ck('CN03','window W5 capped',min(F(20,19),1),1)
# CN04: address calculations are performed by the independent standard ipaddress model.
ck('CN04','distance vector columns',[min(c+d for c,d in zip([8,10,12,6],v))for v in [[1,23,20,22],[12,35,30,28],[24,18,16,36],[36,30,8,24]]],[9,20,28,20])
ck('CN04','1580B IP fragments',[*fragment(1560,20,800)],[[796,0,1],[796,97,1],[28,194,0]])
a=ipaddress.ip_interface('168.16.84.24/20').network
ck('CN04','/20 network',str(a.network_address),'168.16.80.0');ck('CN04','/20 broadcast',str(a.broadcast_address),'168.16.95.255')
networks=[ipaddress.ip_network(f'35.230.{n}.0/21')for n in [32,40,48,56]];ck('CN04','exact four route aggregate',[str(x)for x in ipaddress.collapse_addresses(networks)],['35.230.32.0/19'])
ck('CN04','IP header data boundaries',100-6*4,76)
ck('CN04','satellite one-way seconds',2*36000/300000,0.24);ck('CN04','satellite upload ideal bound seconds',4000*8/200000+0.24,0.4)
ck('CN04','satellite ARQ window',math.ceil(F(4,5)*F(540,60)),8);ck('CN04','satellite seq bits',math.ceil(math.log2(8+1)),4)
vlsm=[ipaddress.ip_network(x)for x in ['10.10.10.0/26','10.10.10.64/26','10.10.10.128/25']]
ck('CN04','satellite VLSM capacities',[n.num_addresses-2 for n in vlsm],[62,62,126]);ck('CN04','satellite VLSM full cover',sum(n.num_addresses for n in vlsm),256)
ck('CN04','recall fragmentation',[*fragment(1600,20,620)],[[620,0,1],[620,75,1],[420,150,0]])
ck('CN04','ipv6 expansion',str(ipaddress.ip_address('2001:0db8:85a3:0000:0000:8a2e:0370:7334')),'2001:db8:85a3::8a2e:370:7334')
# CN05/06: byte ranges and time dependencies.
ck('CN05','UDP max IPv4 payload',65535-20-8,65507);ck('CN05','one complement checksum',checksum([0xB9B6,0x65C5]),0xE083)
ck('CN05','TCP selected payload',100-6*4-6*4,52);ck('CN05','two TCP segments next ACK',200+300+500,1000)
ck('CN05','active close ms',50+2*800,1650);ck('CN05','passive close ms',F(3,2)*50,75)
ck('CN05','SRTT update ms',F(7,8)*100+F(1,8)*140,105);ck('CN05','avoidance growth longest ms',(32-8)*2,48)
ck('CN05','recall FIN seq',100+1+500,601);ck('CN05','recall FIN ACK',100+1+500+1,602)
ck('CN05','available sending bytes',min(3000,4000)-(6500-5001+1),1500);ck('CN05','new max byte',5001+min(3000,4000)-1,8000)
ack=600;free=8;trace=[]
for count in [3,2,2,1]:ack+=count;free-=count;trace.append([ack,free])
ck('CN05','receive byte-by-byte ACK/rwnd',trace,[[603,5],[605,3],[607,1],[608,0]])
ck('CN06','nonpersistent html+7 images RTT',2*(7+1),16);ck('CN06','persistent pipeline after HTTP request RTT',1+1,2)
ck('CN06','DNS+Web min ms',2*10,20);ck('CN06','DNS+Web max ms',(3+2)*10,50)
ck('CN06','html1 image3 initialcwnd1 ms',(1+1+2)*10,40)
ck('CN06','FTP data first byte',100+1,101);ck('CN06','FTP release ACK',100+1+18000+1,18102)
ck('CN06','FTP rounds total segments',sum([1,2,4,5,6]),18);ck('CN06','FTP completion ms',(1+len([1,2,4,5,6]))*10,60);ck('CN06','FTP full-interval Mb/s',18000*8/0.06/1e6,2.4)
# CO02: machine bits and rounding by independent binary32 pack/unpack.
def bits32(x):return struct.unpack('>I',struct.pack('>f',x))[0]
def f32bits(x):return struct.unpack('>f',struct.pack('>I',x))[0]
ck('CO02','137.5 octal components',[137//64,(137//8)%8,137%8,int(.5*8)],[2,1,1,4])
ck('CO02','short -32767 unsigned32',(-32767)%(1<<32),0xFFFF8001)
ck('CO02','8-bit subtraction low/carry',[(69+(~38&255)+1)&255,(69+(~38&255)+1)>>8],[31,1])
ck('CO02','32bit subtract encoded',(-33-65)%(1<<32),0xFFFFFF9E);ck('CO02','negative .4375 binary32',bits32(-.4375),0xBEE00000)
ck('CO02','CC900000 exponent',((0xCC900000>>23)&255)-127,26);ck('CO02','B0C00000 exponent',((0xB0C00000>>23)&255)-127,-30)
ck('CO02','f(23) float encoding',bits32((1<<24)-1),0x4B7FFFFF);ck('CO02','f(24) float encoding',bits32((1<<25)-1),0x4C000000)
for v,w in [(2**24+.5,16777216),(2**24+1,16777216),(2**24+1.5,16777218),(2**24+3,16777220)]:ck('CO02','nearest-even '+str(v),f32bits(bits32(v)),w)
# Booth register simulation, independent signed conversion.
p=0;y=6;last=0;x=(-3)&15;booth=[]
for _ in range(4):
 pair=(y&1,last)
 if pair==(0,1):p=(p+x)&15
 elif pair==(1,0):p=(p-x)&15
 allbits=(p<<5)|(y<<1)|last
 signed=allbits-(1<<9) if allbits&(1<<8) else allbits
 allbits=(signed>>1)&511;p=(allbits>>5)&15;y=(allbits>>1)&15;last=allbits&1
 booth.append([p,y,last])
ck('CO02','Booth -3x6 post-shift registers',booth,[[0,3,0],[1,9,1],[0,12,1],[14,14,0]])
ck('CO02','Booth product',((p<<4)|y)-256,-18)
# CO03: chip organization, cache fields, address bits, set-local replacement.
ck('CO03','4Mx8 DRAM multiplexed pins',22//2+8,19);ck('CO03','ROM/RAM chip counts',[4//2,(64-4)//4*2],[2,30])
ck('CO03','disk sector mean ms',8+60000/7200/2+60000/7200/1000,12.175)
ck('CO03','8way 32KiB64B tag',[32768//64//8,32-6-6],[64,20]);ck('CO03','cache total Kbits',1024*(128+18+1+1)//1024,148)
ck('CO03','TLB32entries4way1KiB tag',32-10-int(math.log2(32//4)),19)
ck('CO03','hex VPN decimal',0x82,130);ck('CO03','virtual physical translate',0x18*4096+0x840,0x18840)
ck('CO03','24x64 array bytes',24*64*4,6144);ck('CO03','array cache lines',24*64*4//32,192)

def cache_misses(addresses,sets,ways,block):
 state=[[]for _ in range(sets)];miss=0
 for address in addresses:
  blk=address//block;row=state[blk%sets]
  if blk in row:row.remove(blk)
  else:
   miss+=1
   if len(row)==ways:row.pop(0)
  row.append(blk)
 return miss
row=[0x422000+(i*64+j)*4 for i in range(24)for j in range(64)]
col=[0x422000+(i*64+j)*4 for j in range(64)for i in range(24)]
ck('CO03','row traversal cache misses',cache_misses(row,64,4,32),192);ck('CO03','column traversal cache misses',cache_misses(col,64,4,32),192)
state=[[]for _ in range(8)];evicted=[]
for vpn in [10,12,16,7,26,4,12,20]:
 q=state[vpn%8]
 if vpn in q:q.remove(vpn)
 elif len(q)==2:evicted.append(q.pop(0))
 q.append(vpn)
ck('CO03','2way grouped TLB victim',evicted,[4])
ck('CO03','03D4 VPN offset',[0x3D4//64,0x3D4%64],[0xF,0x14]);ck('CO03','03D4 physical',0xD*64+0x14,0x354)
ck('CO03','354 cache tag row offset',[0x354>>6,(0x354>>2)&15,0x354&3],[0xD,5,0])
ck('CO03','00F1 physical',2*64+0x31,0xB1);ck('CO03','B1 cache tag row offset',[0xB1>>6,(0xB1>>2)&15,0xB1&3],[2,12,1])
# FIFO and LRU must use independent replacement state and count hits by event position.
cache_events={}
for mode in ['FIFO','LRU']:
 q=[];hits=[]
 for pos,block in enumerate([1,2,3,4,1,2,5,1,2,3,4,5],1):
  if block in q:
   hits.append(pos)
   if mode=='LRU':q.remove(block);q.append(block)
  else:
   if len(q)==4:q.pop(0)
   q.append(block)
 cache_events[mode]=hits
ck('CO03','4line FIFO hit positions',cache_events['FIFO'],[5,6])
ck('CO03','4line FIFO hits/misses',[len(cache_events['FIFO']),12-len(cache_events['FIFO'])],[2,10])
ck('CO03','4line LRU hit positions',cache_events['LRU'],[5,6,8,9])
ck('CO03','4line LRU hits/misses',[len(cache_events['LRU']),12-len(cache_events['LRU'])],[4,8])
# CO05/06/07: control encoding, instruction pipeline, bandwidth and software CPU budgets.
ck('CO05','microaddresses needed',math.ceil(math.log2(32*4+2)),8);ck('CO05','7commands+none bits',math.ceil(math.log2(7+1)),3)
ck('CO05','four-stage 10instruction ns',(4+10-1)*90,1170);ck('CO05','five-stage20 3stalls ns',(5+20-1+3)*2,54)
ck('CO05','throughput instruction/ns',20/54,0.37037037037037035)
ck('CO06','10MHz2cycles4B MB/s',4*10/2,20);ck('CO06','1333MT/s64bit GB/s',1333*8/1000,10.664)
ck('CO06','32B nonburst ns',(32//8)*(1+6+1),32);ck('CO06','420MHz2x64bit peakGB/s',420*2*8/1000,6.72);ck('CO06','burst transactionGB/s',64/(7/420)/1000,3.84)
ck('CO06','8words50MHz burst MB/s',32/(12*20e-9)/1e6,133.33333333333334);ck('CO06','nonburst same MB/s',32/(8*5*20e-9)/1e6,40)
ck('CO07','display frame bytes',1920*1080*24//8,6220800);ck('CO07','display double buffer',1920*1080*24//8*2,12441600);ck('CO07','display rateB/s',1920*1080*24//8*60,373248000)
ck('CO07','50MHz poll utilization percent',500*200/50e6*100,.2);ck('CO07','interrupt occupied percent',100/400*100,25)
ck('CO07','2MBps service gap us',4/2e6*1e6,2);ck('CO07','poll CPU lowerpercent',2e6/4*10*4/500e6*100,4)
ck('CO07','40MBps interrupt requiredpercent',40e6/4*400/500e6*100,800);ck('CO07','DMA1000B software percent',40e6/1000*500/500e6*100,4)
ck('CO07','DMA1024 software percent',1e6/1024*20e-6*100,1.953125)
# OS02: event-by-event scheduling; safety search considers every candidate independently.
def schedule(arr,bur,mode,prior=None):
 n=len(arr);rem=bur[:];done=[None]*n;timeline=[];time=0;cur=None
 while any(rem):
  eligible=[i for i in range(n)if arr[i]<=time and rem[i]>0]
  if not eligible:time+=1;continue
  if mode=='SRTF':i=min(eligible,key=lambda i:(rem[i],arr[i],i))
  elif mode=='priority':i=max(eligible,key=lambda i:(prior[i],-arr[i],-i))
  elif cur is not None and rem[cur]>0:i=cur
  elif mode=='FCFS':i=min(eligible,key=lambda i:(arr[i],i))
  elif mode=='SJF':i=min(eligible,key=lambda i:(bur[i],arr[i],i))
  elif mode=='HRRN':i=max(eligible,key=lambda i:(F(time-arr[i]+bur[i],bur[i]),-arr[i],-i))
  cur=i;timeline.append(i);rem[i]-=1;time+=1
  if not rem[i]:done[i]=time;cur=None
 return done,timeline
arr=[0,2,4,5];bur=[7,4,1,4]
for mode,w in [('FCFS',[7,11,12,16]),('SJF',[7,12,8,16]),('SRTF',[16,7,5,11]),('HRRN',[7,12,8,16])]:
 done,_=schedule(arr,bur,mode);ck('OS02',mode+' completion vector',done,w)
 for label,actual,expected in [('turnaround',F(sum(c-a for c,a in zip(done,arr)),4),{'FCFS':F(35,4),'SJF':8,'SRTF':7,'HRRN':8}[mode]),('wait',F(sum(c-a-b for c,a,b in zip(done,arr,bur)),4),{'FCFS':F(19,4),'SJF':4,'SRTF':3,'HRRN':4}[mode])]:ck('OS02',mode+' mean '+label,actual,expected)
ck('OS02','preemptive priority completion',schedule([0,20,30],[60,42,13],'priority',[1,10,100])[0],[115,75,43])
ck('OS02','second SRTF completion',schedule([0,1,2,3],[8,4,9,5],'SRTF')[0],[17,5,26,10])
def roundrobin(arr,bur,quantum):
 n=len(arr);q=deque();rem=bur[:];done=[0]*n;pending=sorted(range(n),key=lambda i:(arr[i],i));t=0
 while pending or q:
  if not q and pending:t=max(t,arr[pending[0]])
  while pending and arr[pending[0]]<=t:q.append(pending.pop(0))
  i=q.popleft();run=min(quantum,rem[i]);t+=run;rem[i]-=run
  while pending and arr[pending[0]]<=t:q.append(pending.pop(0))
  if rem[i]:q.append(i)
  else:done[i]=t
 return done
ck('OS02','RR q2 completion same-time-new-first',roundrobin([0,1,2,3],[8,4,9,5],2),[22,12,26,23])
def safety(av,alloc,need):
 work=av[:];finished=set()
 while True:
  can=[i for i in range(len(alloc))if i not in finished and all(a<=b for a,b in zip(need[i],work))]
  if not can:break
  i=can[0];finished.add(i);work=[a+b for a,b in zip(work,alloc[i])]
 return len(finished)==len(alloc)
ck('OS02','unsafe partial sequence',safety([0,2,1],[[2,0,0],[1,2,0],[0,1,1],[0,0,1]],[[0,0,1],[1,3,2],[1,3,1],[2,0,0]]),False)
a=[[0,0,3],[1,0,0],[1,3,5],[0,0,2],[0,0,1]];need=[[0,0,1],[0,7,5],[1,0,0],[0,6,2],[0,6,4]]
ck('OS02','four independent safety candidates',[safety(x,a,need)for x in [[1,4,0],[0,6,2],[1,1,1],[0,4,7]]],[True,False,False,False])
ck('OS02','BAT request B30 unsafe',safety([10],[[50],[10],[30]],[[20],[30],[20]]),False)
ck('OS02','BAT request A20 safe',safety([20],[[20],[30],[30]],[[50],[10],[20]]),True)
# OS03/04/05: paging, file indexing, buffering, CHS and seek algorithms.
ck('OS03','page2 toframeB translate',0xB*1024+(0xA6F%1024),0x2E6F);ck('OS03','page2 toframe8 decimal',8*1024+2500%1024,8644)
ck('OS03','directory capacity',2**16//(1024//2),128);ck('OS03','20501225 fields',[0x20501225>>22,(0x20501225>>12)&1023,0x20501225&4095],[0x81,0x101,0x225])
ck('OS03','serialTLB us',.9*101+.1*201,111);ck('OS03','parallelTLB us',.9*101+.1*200,110.9)
q=[];fault=replace=0
for x in [0,1,2,7,0,5,3,5,0,2,7,6]:
 if x in q:q.remove(x)
 else:
  fault+=1
  if len(q)==4:q.pop(0);replace+=1
 q.append(x)
ck('OS03','LRU12ref faults/replacements',[fault,replace],[9,5]);ck('OS03','fault retry secondvisit ns',10+100+10**8+10+100,100000220);ck('OS03','replacement physical1565',0x101*4096+0x565,0x101565)
ck('OS04','mixedindex firstdouble regionbyte',(10+256)*1024,272384);ck('OS04','307400 logicalblock/offset',list(divmod(307400,1024)),[300,200]);ck('OS04','double index subindex',300-10-256,34)
ck('OS04','linkedrecord22 readwrite',math.ceil(22/(512//100))+1,6);ck('OS04','directory exact mean blocks',F(1+3200//(1024//16),2)+1,F(53,2))
ck('OS04','inode-limit filecount',min(2**20*(4096//64),512*2**20//math.ceil(5600/4096)),67108864)
ck('OS04','bitmap128KiB',2**20//8,131072)
ck('OS05','singlebuffer10 us',100+50+9*(max(100,50)+50)+50,1550);ck('OS05','doublebuffer10 us',100+9*max(100,50+50)+50+50,1100)
ck('OS05','CHS7866 record',78*8*8+6*8+6,5046);ck('OS05','SCAN seek',(199-58)+(199-15),325);ck('OS05','LOOK recall seek',(180-58)+(180-15),287)
requests=[130,42,180,15,199];pos=58;travel=0
for v in requests:travel+=abs(v-pos);pos=v
ck('OS05','FCFS seek',travel,647)
pos=58;pending=requests[:];travel=0;seq=[]
while pending:
 x=min(pending,key=lambda v:abs(v-pos));pending.remove(x);travel+=abs(x-pos);seq.append(x);pos=x
ck('OS05','SSTF order',seq,[42,15,130,180,199]);ck('OS05','SSTF seek',travel,227)
ck('OS05','diskcapacity B',300*10*200*512,307200000);ck('OS05','cluster CHS100530',[100530//1000,(100530%1000)//100,(100530%100)*2],[100,5,60]);ck('OS05','clusterseek sequence distance',15+1+9+50,75)
# Newly added OS04/05 course computations, checked after the author checkpoint.
ck('OS04','100groups success exact compares',F(101,2)+F(101,2),101)
ck('OS04','2level100size success exact compares',3*F(101,2),F(303,2))
ck('OS04','mixed8direct capacity KiB',8+256+256**2,65800)
ck('OS04','FCB64 directory blocks',640//(1024//64),40)
ck('OS04','small16entry directory blocks',640//(1024//16),10)
ck('OS04','directory64 success exactmean',F(41,2),F(41,2))
ck('OS04','directory16 success exactmean',F(11,2),F(11,2))
ck('OS04','bitmap409612 disk block',32+409612//8192,82)
ck('OS04','bitmap409612 byte',(409612%8192)//8,1)
ck('OS04','bitmap409612 bit',(409612%8192)%8,4)
diskseqs={
 'FCFS':[55,58,39,18,90,160,150,38,184],
 'SSTF':[90,58,55,39,38,18,150,160,184],
 'SCAN':[150,160,184,200,90,58,55,39,38,18],
 'LOOK':[150,160,184,90,58,55,39,38,18],
 'C-SCAN':[150,160,184,200,0,18,38,39,55,58,90],
 'C-LOOK':[150,160,184,18,38,39,55,58,90]}
for mode,want in zip(diskseqs,[498,248,282,250,390,322]):
 path=[100]+diskseqs[mode]
 actual=sum(abs(a-b)for a,b in zip(path,path[1:]))
 ck('OS05','course9request '+mode+' movement',actual,want)
# DS06/07/08 numerical model checks supplement author code tests.
d=[[0,6,13],[10,0,4],[5,math.inf,0]];states=[]
for k in range(3):
 for i in range(3):
  for j in range(3):d[i][j]=min(d[i][j],d[i][k]+d[k][j])
 states.append([row[:]for row in d])
ck('DS06','Floyd all three stages',states,[[[0,6,13],[10,0,4],[5,11,0]],[[0,6,10],[10,0,4],[5,11,0]],[[0,6,10],[9,0,4],[5,11,0]]])
ck('DS07','2047 minimum3way height',math.ceil(math.log(2048,3)),7);ck('DS07','2047 maximum3way height',int(math.log2(2048)),11)
count=0
for rootkeys in range(1,4):count+=sum(sum(x)==7-rootkeys for x in product(range(1,4),repeat=rootkeys+1))
ck('DS07','fourorder Btree7keys all shapes',count+1,9)
ck('DS08','external4500records IO',2*(4500//75)*(1+math.ceil(math.log(10,5))),360)
for c in checks:
 for key in ['actual','expected']:
  if isinstance(c[key],F):c[key]=str(c[key])
subjects=sorted({c['chapter']for c in checks});snapshot={c:hashlib.sha256((ROOT/'chapters'/c/'content.md').read_bytes()).hexdigest()for c in subjects}
result={'status':'pass'if all(x['passed']for x in checks)else'fail','checks_count':len(checks),'checks':checks,'source_sha256':snapshot,'scope':'Named high-risk numeric and algorithm-state examples only. Independent simulations use inputs read from current prose; no author verification modules are imported. Excludes exhaustive knowledge/source-image/PDF review.'}
(ROOT/'sources/reviews/independent/highrisk_recalculation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(result['status'],len(checks),'checks;',len(subjects),'chapters')
