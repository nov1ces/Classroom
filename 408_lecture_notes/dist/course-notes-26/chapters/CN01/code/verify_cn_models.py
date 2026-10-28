#!/usr/bin/env python3
"""Recalculate printed CN examples from their model, with exact bit/address operations."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import ipaddress, math, json, hashlib
ROOT=Path(__file__).resolve().parents[3]
checks=[]
def check(ch,item,actual,expected):
 ok=math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8) if isinstance(actual,(int,float,Fraction)) and isinstance(expected,(int,float,Fraction)) else actual==expected
 checks.append({'chapter':ch,'item':item,'actual':str(actual) if isinstance(actual,Fraction) else actual,'expected':str(expected) if isinstance(expected,Fraction) else expected,'pass':ok})
 assert ok,(ch,item,actual,expected)
def rem(bits,poly):
 a=int(bits,2);g=int(poly,2)
 while a.bit_length()>=g.bit_length():a^=g<<(a.bit_length()-g.bit_length())
 return format(a,f'0{len(poly)-1}b')
def stuff(s):
 out='';n=0
 for bit in s:
  out+=bit;n=n+1 if bit=='1' else 0
  if n==5:out+='0';n=0
 return out
def checksum(words):
 s=sum(words)
 while s>>16:s=(s&0xffff)+(s>>16)
 return s^0xffff
# CN01: event-by-event recurrence includes processing, excludes duplicate display pages.
end=[0.0]*3;arrivals=[]
for k in range(4):
 arrival=0
 for link in range(3):
  start=max(end[link],arrival+(0.5 if link else 0));end[link]=start+2;arrival=end[link]+1
 arrivals.append(arrival)
check('CN01','three links, four packets arrivals/ms',arrivals,[10,12,14,16])
check('CN01','U=.9 vs U=.5 delay ratio',(1/(1-.9))/(1/(1-.5)),5)
check('CN01','two hops different rates no processing/ms',8000/100000+8000/50000,0.24)
check('CN01','two hops plus .04 ms processing',8000/100000+8000/50000+.04,.28)
# CN02 capacity and encoding numerical cases.
check('CN02','QAM32 new/old limiting rate',round(min(2*20e6*5,20e6*math.log2(10001))/min(2*10e6*5,10e6*math.log2(1001)),2),2.01)
check('CN02','8kHz 30dB Shannon rounded',round(8000*math.log2(1001),1),79737.8)
check('CN02','4 amplitude x4 phase 3kHz',2*3000*math.log2(16),24000)
# CN03 CRC, zero stuffing, code distance, both Hamming bit-order conventions.
check('CN03','HDLC zero insertion',stuff('0111110001111110'),'011111000011111010')
check('CN03','CRC textbook remainder',rem('101001000','1101'),'001')
check('CN03','CRC transmitted codeword',rem('101001001','1101'),'000')
check('CN03','CRC choices',[rem(x,'10011') for x in ['101110000','101110100','101111000','101111100']],['1100','1000','0100','0000'])
codes=['10011010','01011100','11110000','00001111']
check('CN03','six pair distances',[sum(x!=y for x,y in zip(a,b)) for a,b in combinations(codes,2)],[4,4,4,4,4,8])
def hamming(data):
 h=[0]*8
 for i,b in zip([3,5,6,7],data):h[i]=int(b)
 for p in [1,2,4]:h[p]=sum(h[i] for i in range(1,8) if i&p)%2
 return h
def syndrome(h):return sum(p*(sum(h[i] for i in range(1,8) if i&p)%2) for p in [1,2,4])
h=hamming('1010');check('CN03','H1..H7 information1010',''.join(map(str,h[1:])),'1011010');h[6]^=1;check('CN03','H6 single error syndrome',syndrome(h),6)
h=hamming('0101');check('CN03','H7..H1 informationD4..D1=1010',''.join(map(str,h[:0:-1])),'1010010');h[2]^=1;check('CN03','H2 single error syndrome',syndrome(h),2)
# Exhaustively check single-bit and double-bit SECDED decisions for every information nibble.
for data in range(16):
 h=hamming(f'{data:04b}');h.append(sum(h)%2)
 for errors in [(),*[(i,) for i in range(1,9)],*combinations(range(1,9),2)]:
  damaged=h.copy()
  for i in errors:damaged[i]^=1
  syn=syndrome(damaged);odd=sum(damaged[1:])%2
  decision='none' if syn==0 and odd==0 else 'overall' if syn==0 else 'single' if odd else 'double'
  expected='none' if not errors else ('overall' if errors==(8,) else 'single') if len(errors)==1 else 'double'
  assert decision==expected
check('CN03','SECDED exhaustive 16 data x37 patterns',16*(1+8+28),592)
check('CN03','stop wait with full ACK',Fraction(8000,10000)/(Fraction(16000,10000)+Fraction(400,1000)),Fraction(2,5))
window=math.ceil((64+500+64)/64);check('CN03','full utilization GBN minimum window',window,10);check('CN03','GBN bits',math.ceil(math.log2(window+1)),4)
A=[1]*4;rx=[2,0,2,0,0,-2,0,-2,0,2,0,2]
check('CN03','CDMA A bits',[sum(A[j]*rx[i+j] for j in range(4))//4 for i in [0,4,8]],[1,-1,1])
check('CN03','CSMA-CD cable reduction/m',800/1e9/2*2e8,80)
check('CN03','backoff fourth collision/us',(2**4-1)*51.2,768)
check('CN03','backoff collision11/ms',(2**10-1)*51.2/1000,52.3776)
check('CN03','CTS remaining NAV/us',2*28+1998*8/54+2,354)
check('CN03','VLAN padding bytes',64-(6+6+4+2+4)-40,2)
check('CN03','cut through destination address/us',6*8/100,0.48)
check('CN03','bidirectional GBN utilization',Fraction(7*8,96+8+8),Fraction(1,2))
check('CN03','course ARQ W4 utilization',Fraction(4*4,4+14+1),Fraction(16,19))
# CN04 address arithmetic and fragments.
def frags(total,header,mtu):
 remaining=total-header;payload=((mtu-header)//8)*8;offset=0;result=[]
 while remaining:
  n=min(payload,remaining);remaining-=n;result.append([n+header,offset//8,int(remaining>0)]);offset+=n
 return result
check('CN04','1580B MTU800 fragments [total,offset,MF]',frags(1580,20,800),[[796,0,1],[796,97,1],[28,194,0]])
n=ipaddress.ip_network('168.16.84.24/20',strict=False)
check('CN04','subnet /20 first and last usable',[str(n.network_address+1),str(n.broadcast_address-1)],['168.16.80.1','168.16.95.254'])
ns=[ipaddress.ip_network(s) for s in ['35.230.32.0/21','35.230.40.0/21','35.230.48.0/21','35.230.56.0/21']]
check('CN04','exact CIDR collapse',[str(s) for s in ipaddress.collapse_addresses(ns)],['35.230.32.0/19'])
subnets=[ipaddress.ip_network(s) for s in ['128.14.32.128/28','128.14.32.144/29','128.14.32.152/30','128.14.32.156/30']]
check('CN04','VLSM capacities',[n.num_addresses-2 for n in subnets],[14,6,2,2]);check('CN04','VLSM aggregate',[str(n) for n in ipaddress.collapse_addresses(subnets)],['128.14.32.128/27'])
check('CN04','satellite one-way s',Fraction(2*36000,300000),Fraction(6,25));check('CN04','satellite file lower bound s',Fraction(4000*8,200000)+Fraction(6,25),Fraction(2,5))
check('CN04','satellite 80% min window',math.ceil(.8*(60+480)/60),8)
check('CN04','remaining hosts technical dept',128-2-(208-129+1)-1,45)
check('CN04','IPv6 compress',ipaddress.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:7334').compressed,'2001:db8:85a3::8a2e:370:7334')
# CN05 checksums and byte/window states.
check('CN05','two words checksum',format(checksum([0x5065,0x6951]),'04X'),'4649')
check('CN05','three words checksum',format(checksum([0x5065,0x6951,0x65c5]),'04X'),'E083')
check('CN05','receive checksum including checksum',checksum([0x5065,0x6951,0x65c5,0xE083]),0)
check('CN05','close active time/ms',50+2*800,1650);check('CN05','close passive time/ms',1.5*50,75)
check('CN05','available segments after ACK',int((min(3000,4000)-1000)/1000),2)
check('CN05','105ms smoothed RTT',Fraction(7,8)*100+Fraction(1,8)*140,105)
check('CN05','zero-window sequence',101+20*1024,20581);check('CN05','zero-window goodput bit/s',20*1024*8/(5*.2),163840)
check('CN05','hex ACK difference',int('846b41d6',16)-int('846b41c6',16),16)
check('CN05','packet TTL hop difference',int('40',16)-int('31',16),15)
check('CN05','IP and TCP option sizes payload',100-4*6-4*6,52)
# CN06 dependency phases and FTP file rounds.
check('CN06','HTTP1.0 HTML plus7objects RTT',2*(1+7),16)
check('CN06','HTTP persistent nonpipeline4images RTT',1+1+4,6)
check('CN06','DNS no cache plus first text webpage ms',(3+2)*10,50)
check('CN06','DNS authority cache plus first page ms',20+2*30,80)
check('CN06','FTP 18KB rounds cumulative',[sum([1,2,4,5,6][:i]) for i in range(1,6)],[1,3,7,12,18])
check('CN06','FTP final FIN ACK',100+1+18000+1,18102)
check('CN06','FTP upload goodput Mb/s',18000*8/.060/1e6,2.4)
check('CN06','FTP fully-confirmed transfer ms',(1+5)*10,60)
for cid in [f'CN{i:02}' for i in range(1,7)]:
 p=ROOT/'chapters'/cid/'sources';p.mkdir(exist_ok=True)
 own=[c for c in checks if c['chapter']==cid]
 result={'status':'passed','method':'Independent exact bit operations, event recurrence and address arithmetic; bound to current canonical content','canonical_sha256':hashlib.sha256((p.parent/'content.md').read_bytes()).hexdigest(),'checks':own,'limitations':'Numerical/model checks do not certify all conceptual statements or every source image.'}
 (p/'numeric_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'checks':len(checks),'status':'passed'},ensure_ascii=False))
