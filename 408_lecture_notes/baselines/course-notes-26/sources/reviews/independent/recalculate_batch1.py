#!/usr/bin/env python3
"""Independent recalculations for named examples; not a certificate of all knowledge coverage."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
checks=[]
def eq(chapter,item,actual,expected,units='',rel=1e-9):
 ok=(actual==expected) if not isinstance(actual,float) else math.isclose(actual,expected,rel_tol=rel,abs_tol=rel)
 checks.append({'chapter':chapter,'item':item,'actual':actual,'printed_expected':expected,'units':units,'pass':ok})
 if not ok:raise AssertionError((chapter,item,actual,expected))
def pipeline(tx,prop,process,n):
 prev=[0.0]*len(tx);arrivals=[]
 for j in range(n):
  current=[]
  for i,t in enumerate(tx):
   ready=0 if i==0 else current[i-1]+prop[i-1]+process[i-1]
   current.append(max(ready,prev[i])+t)
  arrivals.append(current[-1]+prop[-1]);prev=current
 return arrivals
# CN01: SI arithmetic and independent packet event recurrence.
eq('CN01','1500 B at 100 Mb/s',1500*8/1e8*1e6,120,'microseconds')
eq('CN01','200 km propagation',200000/2e8*1000,1,'milliseconds')
eq('CN01','last bit at receiver',(1500*8/1e8+200000/2e8)*1000,1.12,'milliseconds')
eq('CN01','delay-bandwidth product',1e8*(200000/2e8),100000,'bits')
eq('CN01','delay-bandwidth product bytes',1e8*(200000/2e8)/8/1000,12.5,'kB')
eq('CN01','1500 B at 1 Gb/s',1500*8/1e9*1e6,12,'microseconds')
eq('CN01','two equal links 1000 packets',pipeline([80e-6]*2,[10e-6]*2,[0],1000)[-1]*1000,80.10,'milliseconds')
eq('CN01','first packet of two links',pipeline([80e-6]*2,[10e-6]*2,[0],1)[0]*1e6,180,'microseconds')
eq('CN01','100 frames throughput',100*1000*8/1000,800,'kb/s')
eq('CN01','100 frames goodput',100*900*8/1000,720,'kb/s')
eq('CN01','queue model U=.5',1/(1-.5),2,'D0')
eq('CN01','queue model U=.9',1/(1-.9),10,'D0')
eq('CN01','queue delay ratio',(1/(1-.9))/(1/(1-.5)),5,'ratio')
eq('CN01','four packet three link process timeline',pipeline([2]*3,[1]*3,[.5]*2,4),[10.,12.,14.,16.],'milliseconds')
eq('CN01','full message process .5',pipeline([8]*3,[1]*3,[.5]*2,1)[0],28.,'milliseconds')
eq('CN01','full message process 2',pipeline([8]*3,[1]*3,[2]*2,1)[0],31.,'milliseconds')
eq('CN01','established circuit',8+3,11,'milliseconds')
eq('CN01','unequal rate two links',(8000/1e8+8000/8e7)*1000+.01+.05,.24,'milliseconds')
eq('CN01','unequal rate plus .04ms',.24+.04,.28,'milliseconds')
eq('CN01','20 photos active time',20*10e6*8/8e7,20.,'seconds')
eq('CN01','photo utilization',20*10e6*8/8e7/60,1/3,'ratio')
eq('CN01','recall 1MB at 10Mb/s',1e6*8/1e7+.02,.82,'seconds')
eq('CN01','recall ten packets three links',pipeline([1]*3,[2]*3,[0]*2,10)[-1],18.,'milliseconds')
# CN02: capacity/quantization examples and device distances.
eq('CN02','1000baud 4kbps states',2**(4000/1000),16.,'states')
eq('CN02','16state every 1/8second',8*math.log2(16),32.,'bit/s')
eq('CN02','8kHz 8states Nyquist',2*8000*math.log2(8),48000.,'bit/s')
eq('CN02','30dB ratio',10**(30/10),1000.,'power ratio')
eq('CN02','binary4kHz noisy127',min(2*4000*math.log2(2),4000*math.log2(1+127)),8000.,'bit/s')
eq('CN02','4ASK200kHz Nyquist',2*200000*math.log2(4),800000.,'bit/s')
qam_old=min(2*1e7*math.log2(32),1e7*math.log2(1001));qam_new=min(2*2e7*math.log2(32),2e7*math.log2(10001))
eq('CN02','QAM32 before',qam_old/1e6,99.67226258835993,'Mb/s')
eq('CN02','QAM32 after',qam_new/1e6,200.,'Mb/s')
eq('CN02','QAM32 ratio rounds to 2.01',round(qam_new/qam_old,2),2.01,'ratio')
eq('CN02','4phases x 4amplitudes bits',math.log2(4*4),4.,'bit/symbol')
eq('CN02','PCM8kHz 8bits',8000*8,64000,'bit/s')
eq('CN02','5host hub fair share',10/5,2.,'Mb/s')
eq('CN02','hub path propagation 200m',200/2e8*1e6,1.,'microseconds')
eq('CN02','hub roundtrip',2*200/2e8*1e6,2.,'microseconds')
eq('CN02','8kHz30dB Shannon rounded',round(8000*math.log2(1001),1),79737.8,'bit/s')
eq('CN02','half Shannon rounded',round(8000*math.log2(1001)*.5,1),39868.9,'bit/s')
eq('CN02','3kHz 16states',2*3000*math.log2(16),24000.,'bit/s')
eq('CN02','8host hub fair share',10/8,1.25,'Mb/s')
eq('CN02','recall 2000baud 8states',2000*math.log2(8),6000.,'bit/s')
eq('CN02','recall 2000baud16states',2000*math.log2(16),8000.,'bit/s')
eq('CN02','recall2kHz16states',2*2000*math.log2(16),16000.,'bit/s')
# OS01 numeric examples: CPU occupation and base/limit examples.
eq('OS01','single process elapsed',2+4+2,8,'milliseconds')
eq('OS01','single process utilization',(2+2)/(2+4+2),.5,'ratio')
eq('OS01','overlap utilization',(2+4+2)/8,1.,'ratio')
eq('OS01','base12000 logical1500',12000+1500,13500,'address')
eq('OS01','base4096 logical1023',4096+1023,5119,'address')
eq('OS01','base12000 logical1999',12000+1999,13999,'address')
# DS04 tables and trace counts computed from the definition rather than copied code.
def next_brute(p):
 out=[0]*(len(p)+1)
 for j in range(2,len(p)+1):
  pre=p[:j-1]; borders=[k for k in range(1,len(pre)) if pre[:k]==pre[-k:]]
  out[j]=1+max(borders,default=0)
 return out

def nextval_brute(p,n):
 v=[0]*(len(p)+1)
 for j in range(2,len(p)+1):v[j]=v[n[j]] if p[j-1]==p[n[j]-1] else n[j]
 return v

def counted_naive(s,p):
 count=0
 for i in range(len(s)-len(p)+1):
  for j in range(len(p)):
   count+=1
   if s[i+j]!=p[j]:break
  else:return i+1,count
 return 0,count

def counted_kmp(s,p,n):
 i=j=1;c=0
 while i<=len(s) and j<=len(p):
  if j==0:i+=1;j+=1;continue
  c+=1
  if s[i-1]==p[j-1]:i+=1;j+=1
  else:j=n[j]
 return (i-len(p) if j>len(p) else 0),c
for p,n,v in [('abaabc',[0,1,1,2,2,3],[0,1,0,2,1,3]),('ababaa',[0,1,1,2,3,4],[0,1,0,1,0,4]),('aaaab',[0,1,2,3,4],[0,0,0,0,4]),('google',[0,1,1,1,2,1],None)]:
 nn=next_brute(p);eq('DS04',p+' next',nn[1:],n)
 if v is not None:eq('DS04',p+' nextval',nextval_brute(p,nn)[1:],v)
s='abaabaabcabaabc';p='abaabc';eq('DS04','naive position/count',counted_naive(s,p),(4,15));eq('DS04','KMP position/count',counted_kmp(s,p,next_brute(p)),(4,10))
s='aaacaaaabdaaaab';p='aaaab';nn=next_brute(p);eq('DS04','repeat KMP position/count',counted_kmp(s,p,nn),(5,12));eq('DS04','repeat optimized position/count',counted_kmp(s,p,nextval_brute(p,nn)),(5,9))
eq('DS04','google first position','googlogoogoogle'.find('google')+1,10)
eq('DS04','single char linked density',1/(1+4),.2,'ratio');eq('DS04','four char linked density',4/(4+4),.5,'ratio')
source_hashes={ch:hashlib.sha256((ROOT/'chapters'/ch/'content.md').read_bytes()).hexdigest() for ch in ['DS04','CN01','CN02','OS01']}
report={'status':'pass','checks':checks,'source_sha256':source_hashes,'scope':'Named numerical examples and table values from the four listed chapter snapshots; excludes completeness, source-image review and evolving DS04 capacity convention.'}
(OUT/'batch1_recalculation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'status':'pass','checks':len(checks)},ensure_ascii=False))
