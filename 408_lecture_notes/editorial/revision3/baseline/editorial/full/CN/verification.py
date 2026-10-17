#!/usr/bin/env python3
"""Portable arithmetic/state cross-checks for the CN manuscript (stdlib only)."""
from pathlib import Path
from itertools import combinations,product
import ipaddress, math, json, struct, zlib, re
import xml.etree.ElementTree as ET
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
# Revision 2: independent on-wire serialization, known boundaries and mutations.
# The specification below is independent of the figure generator's model.
specs={
 'ipv4':[
  [('版本',4),('IHL',4),('区分服务',8),('总长度',16)],
  [('标识',16),('标志',3),('片偏移',13)],
  [('TTL',8),('协议',8),('首部检验和',16)],
  [('源IPv4地址',32)],[('目的IPv4地址',32)]],
 'tcp':[
  [('源端口',16),('目的端口',16)],[('序号 seq',32)],[('确认号 ack',32)],
  [('数据偏移',4),('保留',6),('URG',1),('ACK',1),('PSH',1),('RST',1),('SYN',1),('FIN',1),('接收窗口',16)],
  [('检验和',16),('紧急指针',16)]],
 'udp':[[('源端口',16),('目的端口',16)],[('UDP长度',16),('检验和',16)]]}
def bit_layout(rows):
 out=[]
 for r,row in enumerate(rows):
  pos=32*r
  for name,width in row:out.append([name,pos,width]);pos+=width
  assert pos==32*(r+1)
 return out
models=data['protocol_formats']
for i,proto in enumerate(['ipv4','tcp','udp'],1):
 record(f'CN-FMT-{i:03}',f'{proto} every named field global bit offset and width',bit_layout(models[proto]['rows']),bit_layout(specs[proto]))
record('CN-FMT-004','IPv4/TCP/UDP fixed header bytes from independent layouts',
 [sum(w for row in specs[p] for _,w in row)//8 for p in ['ipv4','tcp','udp']],
 [models[p]['fixed_bytes'] for p in ['ipv4','tcp','udp']])
record('CN-FMT-005','length units in figures: IHL/TCP offset/total/fragment/UDP',
 [models['ipv4']['length_unit_bytes'],models['tcp']['data_offset_unit_bytes'],models['ipv4']['total_length_unit_bytes'],models['ipv4']['fragment_offset_unit_bytes'],models['udp']['length_unit_bytes']],
 [4,4,1,8,1])
record('CN-FMT-006','TCP classic 6 reserved bits plus six single-bit controls',
 [models['tcp']['reserved_bits'],[[n,w] for n,w in models['tcp']['rows'][3][2:-1]]],
 [6,[[n,1] for n in ['URG','ACK','PSH','RST','SYN','FIN']]])
for i,(proto,name,rh) in enumerate([('ipv4','CN16_ipv4_header',66),('tcp','CN17_tcp_header',66),('udp','CN18_udp_header',68)],7):
 root=ET.parse(ROOT/'figures'/f'{name}.svg').getroot()
 rects=[r for r in root.iter('{http://www.w3.org/2000/svg}rect') if 'x' in r.attrib]
 expected=[]
 for ri,row in enumerate(specs[proto]):
  pos=0
  for _,w in row:expected.append([155+pos*28,114+ri*rh,w*28,rh]);pos+=w
 actual=[[float(r.attrib[k]) for k in ['x','y','width','height']] for r in rects[:len(expected)]]
 record(f'CN-FMT-{i:03}',f'{proto} SVG rectangles have actual 32-bit row boundaries',actual,expected)
padding_cases=[]
for opt in [0,1,3,4,39,40]:
 pad=(-opt)%4;header=20+opt+pad;padding_cases.append([opt,pad,header,header//4])
record('CN-FMT-010','options length to zero padding/header length/encoded offset',padding_cases,[[0,0,20,5],[1,3,24,6],[3,1,24,6],[4,0,24,6],[39,1,60,15],[40,0,60,15]])
record('CN-FMT-011','all option lengths0..40 fit legal20..60-byte headers',
 all((20+n+(-n)%4)%4==0 and 5<=(20+n+(-n)%4)//4<=15 for n in range(41)),True)
src=ipaddress.IPv4Address('192.0.2.1').packed;dst=ipaddress.IPv4Address('198.51.100.2').packed
iph=struct.pack('!BBHHHBBH4s4s',0x46,0,100,0x3456,0x2061,64,6,0,src,dst)+bytes([1,1,0,0])
encoded_flags=struct.unpack('!H',iph[6:8])[0]
record('CN-FMT-012','serialized IPv4 decodes IHL6/total100/offset97/MF1/DF0/protocol6',
 [iph[0]>>4,iph[0]&15,(iph[0]&15)*4,int.from_bytes(iph[2:4],'big'),100-len(iph),(encoded_flags&0x1fff)*8,bool(encoded_flags&0x2000),bool(encoded_flags&0x4000),iph[9]],
 [4,6,24,100,76,776,True,False,6])
record('CN-FMT-013','raw IPv4 source/destination occupy byte12..19',
 [str(ipaddress.IPv4Address(iph[12:16])),str(ipaddress.IPv4Address(iph[16:20]))],['192.0.2.1','198.51.100.2'])
tcph=struct.pack('!HHIIBBHHH',12345,80,2001,3001,6<<4,0x10,4000,0,0)+bytes([1,1,0,0])
record('CN-FMT-014','serialized TCP independent byte offsets and payload length',
 [len(tcph),int.from_bytes(tcph[4:8],'big'),int.from_bytes(tcph[8:12],'big'),(tcph[12]>>4)*4,bool(tcph[13]&0x10),int.from_bytes(tcph[14:16],'big'),100-len(iph)-len(tcph)],
 [24,2001,3001,24,True,4000,52])
udp=struct.pack('!HHHH',12345,53,20,0)+bytes(12)
record('CN-FMT-015','serialized UDP four16-bit fields and actual payload boundary',
 [list(struct.unpack('!HHHH',udp[:8])),len(udp),len(udp[8:])],[[12345,53,20,0],20,12])
record('CN-FMT-016','UDP length-field ceiling differs from IPv4 application limit',
 [(1<<16)-1,(1<<16)-1-20,(1<<16)-1-20-8],[65535,65515,65507])
def byte_checksum(blob):
 if len(blob)%2:blob+=b'\x00'
 return ones_checksum(struct.unpack('!'+str(len(blob)//2)+'H',blob))
record('CN-FMT-017','known Internet checksum word vector',byte_checksum(bytes.fromhex('0001f203f4f5f6f7')),0x220d)
def with_checksum(blob,offset,pre=b''):
 chk=byte_checksum(pre+blob)
 return blob[:offset]+struct.pack('!H',chk)+blob[offset+2:]
ip20=struct.pack('!BBHHHBBH4s4s',0x45,0,40,1,0,64,6,0,src,dst)
ip20=with_checksum(ip20,10)
def ip_header_valid(packet):return byte_checksum(packet[:(packet[0]&15)*4])==0
ip_packet=ip20+bytes(20);changed_data=ip_packet[:-1]+b'\x01'
changed_ttl=bytearray(ip_packet);changed_ttl[8]-=1
record('CN-FMT-018','IPv4 checksum sees TTL changes but excludes IP payload',
 [ip_header_valid(ip_packet),ip_header_valid(changed_data),ip_header_valid(changed_ttl)], [True,True,False])
zero_ip=bytearray(struct.pack('!BBHHHBBH4s4s',0x45,0,20,0,0,64,6,0,src,dst))
zero_ip[4:6]=struct.pack('!H',byte_checksum(zero_ip))
record('CN-FMT-019','a legitimate zero IPv4 checksum still satisfies full header check',
 [int.from_bytes(zero_ip[10:12],'big'),byte_checksum(zero_ip),ip_header_valid(zero_ip)],[0,0,True])
record('CN-FMT-020','TTL mutation invalidates a zero-checksum header',
 ip_header_valid(zero_ip[:8]+bytes([zero_ip[8]-1])+zero_ip[9:]),False)
def pseudo(proto,length,source=src,destination=dst):return struct.pack('!4s4sBBH',source,destination,0,proto,length)
odd=struct.pack('!HHHH',12345,53,11,0)+b'abc';pre=pseudo(17,len(odd))
udpchk=byte_checksum(pre+odd);wire_udp=odd[:6]+struct.pack('!H',udpchk or 0xffff)+odd[8:]
record('CN-FMT-021','UDP odd-byte padding and 12-byte pseudoheader do not go on wire',
 [len(pre),len(wire_udp),int.from_bytes(wire_udp[4:6],'big'),byte_checksum(pre+wire_udp)], [12,11,11,0])
bad_src=ipaddress.IPv4Address('192.0.2.2').packed
record('CN-FMT-022','UDP validates data/header/pseudoheader rather than just its8-byte header',
 [byte_checksum(pre+wire_udp)==0,byte_checksum(pre+wire_udp[:-1]+b'd')==0,byte_checksum(pseudo(17,11,source=bad_src)+wire_udp)==0,byte_checksum(pre+bytes([wire_udp[0]^1])+wire_udp[1:])==0],
 [True,False,False,False])
udp10=struct.pack('!HHHH',12345,53,10,0)
cancel_word=byte_checksum(pseudo(17,10)+udp10+b'\x00\x00')
udp10+=struct.pack('!H',cancel_word);raw_zero=byte_checksum(pseudo(17,10)+udp10)
udp10wire=udp10[:6]+b'\xff\xff'+udp10[8:]
record('CN-FMT-023','UDP computed0 is encodedFFFF to distinguish IPv4 disabled0',
 [raw_zero,int.from_bytes(udp10wire[6:8],'big'),byte_checksum(pseudo(17,10)+udp10wire)],[0,65535,0])
tcp_wire=with_checksum(tcph+bytes(52),16,pseudo(6,len(tcph)+52))
record('CN-FMT-024','TCP checksum binds protocol6/addresses/header/data',
 [byte_checksum(pseudo(6,76)+tcp_wire)==0,byte_checksum(pseudo(17,76)+tcp_wire)==0,byte_checksum(pseudo(6,76,source=bad_src)+tcp_wire)==0,byte_checksum(pseudo(6,76)+tcp_wire[:8]+bytes([tcp_wire[8]^1])+tcp_wire[9:])==0,byte_checksum(pseudo(6,76)+tcp_wire[:-1]+b'\x01')==0],
 [True,False,False,False,False])
record('CN-FMT-025','IP/TCP/UDP figure models state exact checksum scopes',
 [models[p]['checksum_scope'] for p in ['ipv4','tcp','udp']],
 [['header'],['pseudoheader','header','data'],['pseudoheader','header','data']])
eth=models['ethernet_ii']
record('CN-FMT-026','Ethernet II no-VLAN header/payload/frame/prefix/MTU boundaries',
 [eth['vlan_tags'],eth['header_bytes'],eth['fields'],eth['frame_bytes'],eth['preamble_bytes'],eth['sfd_bytes'],eth['mtu_bytes']],
 [0,14,[['目的MAC',6],['源MAC',6],['类型',2],['数据及填充',[46,1500]],['FCS',4]],[64,1518],7,1,1500])
mac_head=bytes.fromhex('00112233445566778899aabb0800')
ip40=bytes([0x45])+bytes(39);pad=bytes(max(0,46-len(ip40)))
fcs_input=mac_head+ip40+pad;fcs=struct.pack('<I',zlib.crc32(fcs_input));frame=fcs_input+fcs
record('CN-FMT-027','actual Ethernet bytes:40-byte IP+6 pad+14 header+4FCS',
 [len(mac_head),len(ip40),len(pad),len(fcs_input),len(fcs),len(frame)],[14,40,6,60,4,64])
record('CN-FMT-028','Ethernet FCS includes pad and excludes preamble/SFD',
 [zlib.crc32(fcs_input)==int.from_bytes(fcs,'little'),zlib.crc32(fcs_input[:-1]+b'\x01')==int.from_bytes(fcs,'little'),zlib.crc32(b'\x55'*7+b'\xd5'+fcs_input)==int.from_bytes(fcs,'little')],
 [True,False,False])
record('CN-FMT-029','Ethernet max frame and min/max on-wire byte-time periods',
 [len(mac_head)+1500+4,7+1+len(frame),7+1+len(frame)+96//8,7+1+1518+96//8],[1518,72,84,1538])
close('CN-FMT-030','96bit-time IFG at10Mb/s is9.6us',eth['ifg_bit_times']/10e6,9.6e-6)
record('CN-FMT-031','MAC min frame plus prefix/IFG consumes672bit-times',(7+1+64)*8+96,672)
record('CN-FMT-032','FCS field is distinct from protected MAC header+payload',eth['fcs_scope'],['目的MAC','源MAC','类型','数据及填充'])
record('CN-FMT-033','HTTP common-condition counts for1/3/7 dependent objects',
 [[2*(m+1),1+1+m,1+1+1] for m in [1,3,7]],[[4,3,3],[8,5,3],[16,9,3]],
 ['DNS完成，未建TCP，必须先HTML，单站点，无并行连接，小对象且忽略发送/流控/拥塞'])
# Content invariants preserve prior question identity and all supplied-error routes.
baseline=ROOT/'editorial/revision2/baseline'
if (baseline/'manuscript/CN').exists():
 def selected_stems(folder):
  found={}
  for f in sorted(folder.glob('*.md')):
   for match in re.finditer(r'^### 例 (\d+-\d+)\u3000[^\n]+\n(.*?)(?=^### |^## |\Z)',f.read_text(),re.S|re.M):
    found[match[1]]=match[2].split('**解析。**')[0].strip()
  return found
 old_stems=selected_stems(baseline/'manuscript/CN');new_stems=selected_stems(ROOT/'manuscript/CN')
 record('CN-FMT-034','all41 original full-example stems/options/figures remain unchanged',
 [len(new_stems),new_stems==old_stems],[41,True])
 def anchors(folder):return sorted(re.findall(r'\{#(cn-\d\d-\d\d)\}', '\n'.join(f.read_text() for f in sorted(folder.glob('*.md')))))
 old_ids=anchors(baseline/'manuscript/CN');new_ids=anchors(ROOT/'manuscript/CN')
 record('CN-FMT-035','all71 knowledge anchors preserved',[len(new_ids),new_ids==old_ids],[71,True])
 old_error=baseline/'editorial/full/CN/chapter_records.json'
 if old_error.exists():
  def error_routes(record):return [{k:r[k] for k in ['id','knowledge_ids','destination','target','locations']} for r in record['errors']]
  old_routes=error_routes(json.loads(old_error.read_text()));new_routes=error_routes(json.loads((HERE/'chapter_records.json').read_text()))
  record('CN-FMT-036','97 supplied-error identities/knowledge IDs/destinations/targets preserved',
   [len(new_routes),new_routes==old_routes],[97,True])
reader_text='\n'.join(f.read_text() for f in sorted((ROOT/'manuscript/CN').glob('*.md')))
record('CN-FMT-037','41 source markers share their unindented question first lines',
 len(re.findall(r'^(?:【\d{4}】|〖[^〗]+〗)\s+\S.+$',reader_text,re.M)),41)
record('CN-FMT-038','reader manuscript excludes internal error IDs and long source names',
 bool(re.search(r'ERR-|做题本|个人原答|错选',reader_text)),False)
# Export syntax guard: a TeX control word must not absorb following CJK letters.
assert not re.search(r'\\[A-Za-z]+[\u4e00-\u9fff]',reader_text),'TeX control sequence directly joined to CJK'
src6=ipaddress.IPv6Address('2001:db8::1').packed;dst6=ipaddress.IPv6Address('2001:db8::2').packed
pre6=struct.pack('!16s16sI3xB',src6,dst6,len(odd),17)
v6chk=byte_checksum(pre6+odd);v6udp=odd[:6]+struct.pack('!H',v6chk or 0xffff)+odd[8:]
def ordinary_udp_valid(packet,pre,version):
 if int.from_bytes(packet[4:6],'big')!=len(packet):return False
 if packet[6:8]==b'\x00\x00':return version==4
 return byte_checksum(pre+packet)==0
record('CN-FMT-039','ordinary UDP: zero checksum disables IPv4 check but IPv6 rejects it',
 [len(pre6),ordinary_udp_valid(odd,pre,4),ordinary_udp_valid(odd,pre6,6),ordinary_udp_valid(v6udp,pre6,6),ordinary_udp_valid(v6udp[:-1]+b'd',pre6,6)],
 [40,True,False,True,False],['普通UDP数据报；不讨论IPv6特定隧道零检验和例外或jumbogram'])
record('CN-FMT-040','textbook SR also requiresWr<=Ws; asymmetric maximum remains9+7',
 [1<=wr<=ws and ws+wr<=2**k for k,ws,wr in [(3,4,3),(3,4,4),(3,3,4),(3,7,1),(3,7,2),(4,9,7)]],
 [True,True,False,True,False,True],['主书PDF p78与SR课件p3–6的常用配置；序号不重叠条件独立枚举见CN-CAL-031'])
result={'status':'PASS','checks':checks,'count':len(checks),'limitations':['计算核验不替代题源全文核验、正式大纲核验或PDF逐页视觉检查','协议计时与增长采用正文已说明的教材模型；未声称所有现代实现数值相同'],'algorithm_processes':['存储转发逐组逐跳事件递推','CRC逐次异或余数','海明综合征与实际翻转恢复','GBN长ACK受窗口约束的发送时刻','GBN/SR接收缓存不同轨迹','序号窗口49种重叠枚举','Dijkstra定型状态','IPv4分片偏移','TCP按ACK移除在途区间','TCP13轮cwnd与HTTP图片分轮']}
result['revision2']={'original_checks':67,'new_checks':len([c for c in checks if c['id'].startswith('CN-FMT-')]),'stage':'正文内容修订与协议图机制核验；待用户审阅','lecture_pdf_layout_review':'按用户要求本轮未执行'}
result['algorithm_processes']+=['IPv4/TCP/UDP字节序列化及字段解码','独立位段规格对照SVG实际矩形几何','选项长度与4B对齐枚举','IPv4/TCP/UDP校验范围变异与合法零值构造','普通IPv4/IPv6 UDP零检验和条件','Ethernet II实际封装、CRC范围、前导与间隔时间','71知识锚点、41题题干/选项/题图与97错题去向的基线保持']
(HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'CN independent verification PASS: {len(checks)} recorded checks')
