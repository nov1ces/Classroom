#!/usr/bin/env python3
"""Independent numerical/state checks for the CO manuscript (stdlib only)."""
from pathlib import Path
from fractions import Fraction
from collections import OrderedDict
import json, struct, math, hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
checks=[]
def add(name, actual, expected, detail=None):
    if isinstance(expected,float): ok=math.isclose(actual,expected,rel_tol=1e-11,abs_tol=1e-12)
    else: ok=actual==expected
    checks.append({'id':name,'actual':actual,'expected':expected,'pass':ok,'detail':detail})
    assert ok,(name,actual,expected)
def signed(u,n): return u-(1<<n) if u>>(n-1) else u

# A real bit-by-bit ripple circuit, compared against separate integer arithmetic.
def circuit(a,b,n,sub):
    c=sub;result=0;c_in_sign=0
    for i in range(n):
        if i==n-1:c_in_sign=c
        x=(a>>i)&1;y=((b>>i)&1)^sub
        z=x^y^c;result|=z<<i
        c=(x&y)|((x^y)&c)
    return result,c^sub,c^c_in_sign,(result>>(n-1))&1,int(result==0)
count=0
for sub in [0,1]:
 for a in range(256):
  for b in range(256):
   r,cf,of,sf,zf=circuit(a,b,8,sub)
   truth=signed(a,8)+(-signed(b,8) if sub else signed(b,8))
   assert r==truth%256
   assert of==int(not -128<=truth<=127)
   assert cf==int(a<b if sub else a+b>255)
   count+=1
add('8bit_add_sub_exhaustive',count,131072,'Independent ripple carries versus exact signed/unsigned arithmetic')
add('69_minus_38',list(circuit(69,38,8,1)),[31,0,0,0,0])
add('7f_plus_01',list(circuit(127,1,8,0)),[128,0,1,1,0])
add('10_minus_negative20',list(circuit(10,(-20)%256,8,1))[:3],[30,1,0])
add('2018_difference',hex((0xffffffdf-0x41)&0xffffffff),'0xffffff9e')
add('unsigned_short_65530',65530%65536,0xfffa)
add('negative_short_to_unsigned',(-32767)%(2**32),2**32-2**15+1)

# Booth with a guard bit in A, n bits in Q and one appended bit.
def booth(x,y,n=4):
    A=0;Q=y%2**n;qm=0;M=x;rows=[];aw=n+1
    for step in range(n):
        pair=((Q&1)<<1)|qm;op='无'
        if pair==1:A+=M;op='A+M'
        elif pair==2:A-=M;op='A−M'
        before=A
        concat=((A%(1<<aw))<<(n+1))|(Q<<1)|qm
        width=aw+n+1
        concat=(concat>>1)|((concat>>(width-1))<<(width-1))
        qm=concat&1;Q=(concat>>1)&((1<<n)-1);A=signed(concat>>(n+1),aw)
        rows.append({'round':step+1,'pair':format(pair,'02b'),'operation':op,'A_before_shift':before,'A':format(A%(1<<aw),f'0{aw}b'),'A_signed':A,'Q':format(Q,f'0{n}b'),'q_minus1':qm})
    product=signed(((A%2**aw)<<n)|Q,aw+n)
    return product,rows
for x in range(-8,8):
 for y in range(-8,8):assert booth(x,y)[0]==x*y
add('booth_4bit_all_pairs',256,256,'All signed 4-bit operands with 5-bit accumulator')
bp,bt=booth(-3,5);add('booth_minus3_times5',bp,-15,bt)

def nonrest(a,d,n):
    R=0;Q=a;rows=[]
    for step in range(n):
        neg=R<0;R=2*R+((Q>>(n-1))&1);Q=(Q<<1)&(2**n-1)
        shifted=R;R=R+d if neg else R-d
        Q|=int(R>=0)
        rows.append({'round':step+1,'shifted_R':shifted,'operation':'+D' if neg else '−D','R':R,'Q':format(Q,f'0{n}b')})
    correction=R<0
    if correction:R+=d
    return Q,R,rows,correction
for a in range(256):
 for d in range(1,256):
    q,r,_,_=nonrest(a,d,8);assert (q,r)==divmod(a,d)
add('nonrest_8bit_all_valid_divisions',256*255,65280)
q,r,dt,corr=nonrest(7,3,3);add('nonrest_7_div3',[q,r,corr],[2,1,True],dt)

def f32(u): return struct.unpack('>f',struct.pack('>I',u))[0]
def bits(x):return struct.unpack('>I',struct.pack('>f',x))[0]
add('2022_float_minus04375',bits(-.4375),0xbee00000)
add('2014_float_comparison',[f32(0xcc900000)<f32(0xb0c00000),math.copysign(1,f32(0xcc900000))==math.copysign(1,f32(0xb0c00000))],[True,True])
add('min_positive_subnormal',f32(1),2**-149)
add('min_positive_normal',f32(0x00800000),2**-126)
# Nearest-even using exact fractions, independent of binary32 examples.
def nearest_even_integers(v):
 q=v.numerator//v.denominator;r=v-q
 return q+int(r>Fraction(1,2) or (r==Fraction(1,2) and q%2==1))
add('round4_significand_even_down',nearest_even_integers(Fraction(17,2)),8)
add('round4_significand_even_up',nearest_even_integers(Fraction(19,2)),10)
a=f32(bits(2**25));b=-a;c=1.
add('float_non_associative',[f32(bits(f32(bits(a+b))+c)),f32(bits(a+f32(bits(b+c))))],[1.,0.])

add('weighted_CPI',Fraction(8,10)*1+Fraction(2,10)*10,Fraction(28,10))
add('CPU_time_ns',10000*2.8,28000.)
add('Amdahl_2012_seconds',90/1.5+10,70.)
add('compile_2014_seconds',20*.7*1.2,16.8)
add('DRAM_address_data_pins',22//2+8,19)
add('MAR_bits_64MiB',(64*2**20-1).bit_length(),26)
add('ROM_RAM_chip_counts',[4*1024//(2*1024),(60*1024//(4*1024))*2],[2,30])
add('interleave_modules',[a%4 for a in [8005,8006,8007,8008,8001,8002,8003,8004,8000]],[1,2,3,0,1,2,3,0,0])
add('disk_access_ms',8+60000/7200/2+60000/7200/1000,12.175)
add('Cache_2022_tag_comparators',[8,32-6-6],[8,20])
add('Cache_2015_total_Kbits',1024*(4*32+18+1+1)//1024,148)
add('TLB_2024_tag',32-10-int(math.log2(32//4)),19)
vpn,off=divmod(0x82840,4096);phys=0x018*4096+off
add('VA_to_PA_2022',[vpn,off,phys],[130,0x840,0x18840])

def cache_lru(addresses,capacity=1024,block=16,ways=1):
    sets=[OrderedDict() for _ in range(capacity//block//ways)];states=[];misses=0
    for a in addresses:
        q=a//block;g=q%len(sets);tag=q//len(sets);s=sets[g];hit=tag in s
        if not hit:
            misses+=1
            if len(s)>=ways:s.popitem(last=False)
        else:s.pop(tag)
        s[tag]=None;states.append({'address':a,'block':q,'group':g,'hit':hit,'LRU_to_MRU':list(s)})
    return misses,states
addresses=[i*4 for i in range(1000) for _ in range(2)]
misses,trace=cache_lru(addresses)
add('2016_array_read_write_misses',[misses,len(addresses)],[250,2000])
add('2016_array_miss_rate',misses/len(addresses),.125)
m,t=cache_lru([0,1,0,2,1],capacity=2,block=1,ways=2)
add('two_way_LRU_hits',[x['hit'] for x in t],[False,False,True,False,False],t)

# 2023 Q43: enumerate every actual byte address, page fault and mapped set.
base=0x422000
row_major=[base+(i*64+j)*4 for i in range(24) for j in range(64)]
column_major=[base+(i*64+j)*4 for j in range(64) for i in range(24)]
seen_pages=set();faults=[]
for address in row_major:
    vpn=address//4096
    if vpn not in seen_pages:seen_pages.add(vpn);faults.append(address)
add('2023Q43_page_fault_addresses',faults,[0x422000,0x423000])
add('2023Q43_array_blocks',len({a//32 for a in row_major}),192)
add('2023Q43_a10_address_group',[base+256,((base+256)//32)%64],[0x422100,8])
for label,seq in [('row',row_major),('column',column_major)]:
    miss,states=cache_lru(seq,capacity=8192,block=32,ways=4)
    add('2023Q43_'+label+'_miss_count',miss,192)
    add('2023Q43_'+label+'_hit_rate',1-miss/len(seq),.875)
miss,states=cache_lru(column_major,capacity=4096,block=32,ways=2)
add('2023Q43_variant_column_all_miss',miss,1536)
miss,states=cache_lru(row_major,capacity=4096,block=32,ways=2)
add('2023Q43_variant_row_miss',miss,192)

# Enumerate all 16-bit words left after reserving full operand subtrees.
available=[w for w in range(65536) if w>>12>=12]
one_prefixes=sorted({w>>6 for w in available})[:254]
zero=[w for w in available if w>>6 not in one_prefixes]
add('extended_opcode_2022_zero',len(zero),128)
add('relative_branch_2009',0x2000+2+6,0x2008)
add('struct_record_c',0xc008+6,0xc00e)
add('employee_byte_56H',0xa0b0+20+1,0xa0c5)
add('microcommand_bits',sum((v).bit_length() for v in [7,3,12,5,6]),15)
add('micro_address_bits',(32*4+2-1).bit_length(),8)
add('2022Q43_register_count',2**4,16)
add('2022Q43_fetch_cycles',1+5+1,7)
for a in range(2):
 for b in range(2):
  for f in range(2):
    add_of=(a&b&(1-f))|((1-a)&(1-b)&f)
    sub_of=(a&(1-b)&(1-f))|((1-a)&b&f)
    assert add_of==int(a==b and f!=a)
    assert sub_of==int(a!=b and f!=a)
add('2022Q43_sign_truth_rows',8,8,'Both displayed OF Boolean expressions checked for every input sign triple')

# EX start times from result-ready times, rather than a hardcoded timing table.
ready={};last_ex=2;sched=[]
for name,dest,src,load in [('I1','r1',[],False),('I2','r3',[],True),('I3','r5',['r1','r3'],False)]:
    ex=max([last_ex+1]+[ready[r]+1 for r in src]);last_ex=ex
    ready[dest]=ex+int(load)
    sched.append({'instruction':name,'EX':ex,'result_end_cycle':ready[dest],'WB':ex+2})
add('load_use_EX_cycles',[r['EX'] for r in sched],[3,4,6],sched)
add('load_use_final_WB',sched[-1]['WB'],8)
add('pipeline_selftest_ns',(5+20-1+3)*2,54)
add('nonuniform_pipeline_10_ns',(4+10-1)*90,1170)
add('bus_2009_MBps',4/(2/10e6)/1e6,20.)
add('bus_2025_GBps',1333e6*8/1e9,10.664)
add('bus_2023_ns',4*(1+6+1),32)
add('bus_2024_peak_GBps',420e6*2*8/1e9,6.72)
add('bus_2024_transaction_GBps',64/(7/420e6)/1e9,3.84)
add('burst_50MHz_MBps',32/(12/50e6)/1e6,400/3)
add('independent_50MHz_MBps',32/(40/50e6)/1e6,40.)
add('polling_2011_CPU_fraction',500*200/50e6,.002)
add('interrupt_2014_CPU_fraction',100/400,.25)
add('DMA_512B_transfers',512//4,128)
add('interrupt_selftest_CPU_fraction',(1e6/4)*2e-6,.5)
add('DMA_selftest_CPU_fraction',(1e6/1024)*20e-6,.01953125)
add('interrupt_masks',[int('100',2),int('110',2),int('111',2)],[4,6,7])

# Store all final paragraph hashes for a precise audit boundary.
manuscripts={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'manuscript/CO').glob('*.md'))}
result={'status':'PASS','checks':len(checks),'assertion_cases':131072+256+65280,'results':checks,'manuscript_sha256':manuscripts,'scope':'Actual values/state trajectories checked; this is not an official syllabus or visual PDF certification.'}
def conv(x):
    if isinstance(x,Fraction):return str(x)
    raise TypeError(type(x).__name__)
(HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=conv),encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks),'assertion_cases':result['assertion_cases']},ensure_ascii=False))
