#!/usr/bin/env python3
"""Independent numerical/state checks for the CO manuscript (stdlib only)."""
from pathlib import Path
from fractions import Fraction
from collections import OrderedDict
from itertools import permutations
import json, struct, math, hashlib, re

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

# Revision 2: whole-question trajectories, kept independent of the manuscript tables.
def as_f32(value):
    try:return struct.unpack('>f',struct.pack('>f',value))[0]
    except OverflowError:return math.copysign(math.inf,value)
def sum_powers_f32(n):
    total=as_f32(1);power=as_f32(1);states=[]
    for step in range(n):
        power=as_f32(power*2)
        total=as_f32(total+power)
        states.append({'iteration':step+1,'power':power if math.isfinite(power) else '+inf','sum':total if math.isfinite(total) else '+inf'})
    return total,states
add('2017Q43_unsigned_zero_upper_bound',(0-1)%(2**32),0xffffffff)
add('2017Q43_unsigned_counter_wrap',(0xffffffff+1)%(2**32),0)
add('2017Q43_signed_zero_initial_condition',0<=-1,False)
add('2017Q43_f1_23',2**24-1,0x00ffffff)
for n,expected in [(23,0x4b7fffff),(24,0x4c000000),(126,0x7f000000),(127,0x7f800000)]:
    value,states=sum_powers_f32(n)
    add(f'2017Q43_f2_{n}_bits',f'{bits(value):08X}',f'{expected:08X}',states[-2:])
add('2017Q43_f1_31_machine_value',signed((2**32-1)%(2**32),32),-1)
add('2017Q43_int_exact_n',max(n for n in range(128) if 2**(n+1)-1<=2**31-1),30)
add('2017Q43_float_finite_n',max(n for n in range(128) if math.isfinite(sum_powers_f32(n)[0])),126)
add('2017Q43_float_exact_n',max(n for n in range(128) if sum_powers_f32(n)[0]==2**(n+1)-1),23)

tlb_sets=[OrderedDict() for _ in range(8)];tlb_trace=[];evicted=[]
for vpn in [10,12,16,7,26,4,12,20]:
    group=vpn%8;tag=vpn//8;s=tlb_sets[group];hit=tag in s
    if hit:s.pop(tag)
    elif len(s)==2:
        old,_=s.popitem(last=False);evicted.append(old*8+group)
    s[tag]=True
    tlb_trace.append({'vpn':vpn,'group':group,'tag':tag,'hit':hit,'LRU_to_MRU_vpns':[t*8+group for t in s]})
add('2021Q44_address_field_widths',[30-12-3,3,12,24-12],[15,3,12,12])
add('2021Q44_TLB_group_sequence',[row['group'] for row in tlb_trace],[2,4,0,7,2,4,4,4])
add('2021Q44_TLB_replaced_vpns',evicted,[4],tlb_trace)
add('2021Q44_TLB_added_tag_bits',(32-12-3)-(30-12-3),2)

next_pc=0x401025+len(bytes.fromhex('E8 D6 FF FF FF'))
displacement=int.from_bytes(bytes.fromhex('D6 FF FF FF'),'little',signed=True)
add('2019Q45_call_next_pc',f'{next_pc:08X}','0040102A')
add('2019Q45_call_displacement',displacement,-42)
add('2019Q45_call_target',f'{next_pc+displacement:08X}','00401000')
def factorial_call_tree(n):
    return [n]+(factorial_call_tree(n-1) if n>1 else [])
invocations=factorial_call_tree(10)
add('2019Q45_invocation_count',[len(invocations),len(invocations)-1],[10,9],invocations)
add('2019Q45_factorial13_exact',math.factorial(13),6227020800)
add('2019Q45_factorial13_low32',math.factorial(13)%(2**32),1932053504)
mult_cases=[]
for x,y in [(2**31-1,2),(-2**31,-1),(-2**31,1),(-1,1),(0,0),(46341,46341)]:
    exact=x*y;encoded=exact%(2**64);high=encoded>>32;low=encoded&0xffffffff
    sign_extension=0xffffffff if low>>31 else 0
    actual=int(high!=sign_extension);expected=int(not -2**31<=exact<=2**31-1)
    assert actual==expected
    mult_cases.append({'x':x,'y':y,'high':f'{high:08X}','low':f'{low:08X}','OF':actual})
add('2019Q45_signed_product_overflow_cases',len(mult_cases),6,mult_cases)

add('2012Q44_arithmetic_shift',f'{((-513)>>1)%(2**16):04X}','FEFF')
add('2012Q44_ideal_cycles',5+4-1,8)
def no_forward_schedule(instructions):
    # Single IF/ID latch, in-order flow, ID reads only strictly after the source WB.
    ready={};previous_id=1;trajectory=[]
    for number,(name,sources,dest) in enumerate(instructions):
        fetch=1 if number==0 else previous_id
        decode=max([fetch+1]+[ready[source]+1 for source in sources])
        stages={'IF':fetch,'ID':decode,'EX':decode+1,'M':decode+2,'WB':decode+3}
        if dest:ready[dest]=stages['WB']
        trajectory.append({'name':name,**stages});previous_id=decode
    return trajectory
original=no_forward_schedule([('LOAD_a',[],'a'),('LOAD_b',[],'b'),('ADD',['a','b'],'sum'),('STORE',['sum'],None)])
add('2012Q44_original_stage_cycles',[[row[s] for s in ['IF','ID','EX','M','WB']] for row in original],[[1,2,3,4,5],[2,3,4,5,6],[3,7,8,9,10],[7,11,12,13,14]])
operations={'LOAD_x':([], 'x'),'LOAD_a':([], 'a'),'SHL':(['x'],'twox'),'ADD':(['twox','a'],'sum'),'STORE':(['sum'],None)}
possible=[]
for order in permutations(operations):
    produced=set();valid=True
    for name in order:
        sources,dest=operations[name]
        if any(s not in produced for s in sources):valid=False;break
        if dest:produced.add(dest)
    if valid:
        trace=no_forward_schedule([(name,*operations[name]) for name in order])
        possible.append({'order':order,'finish':trace[-1]['WB'],'trajectory':trace})
add('2012Q44_legal_orders',len(possible),3)
add('2012Q44_all_legal_finish_cycles',sorted(row['finish'] for row in possible),[17,18,18],possible)
best=min(possible,key=lambda row:row['finish'])
add('2012Q44_shortest_stage_cycles',[[row[s] for s in ['IF','ID','EX','M','WB']] for row in best['trajectory']],[[1,2,3,4,5],[2,3,4,5,6],[3,6,7,8,9],[6,10,11,12,13],[10,14,15,16,17]])
figure_manifest=json.loads((HERE/'figure_manifest.json').read_text())
figure13=next(f for f in figure_manifest if f['id']=='CO_F13_pipeline_schedule')
figure_stages=[row[1] for row in figure13['mechanism_data']['instruction_stages']]
add('2012Q44_figure_matches_independent_schedule',figure_stages,[{s:row[s] for s in ['IF','ID','EX','M','WB']} for row in best['trajectory']])

add('2018Q43_A_max_interval_us',4/(2e6)*1e6,2.)
add('2018Q43_A_min_cpu_fraction',(2e6/4)*10*4/500e6,.04)
add('2018Q43_B_cycles_between_buffers',(4/40e6)*500e6,50.)
add('2018Q43_B_interrupt_required_fraction',(40e6/4)*400/500e6,8.)
add('2018Q43_B_DMA_blocks_per_second',40e6/1000,40000.)
add('2018Q43_B_DMA_max_cpu_fraction',(40e6/1000)*500/500e6,.04)

# Wangdao OS 3.2.9: trace the three independent initial-snapshot queries.
# These are textbook example data, not an exam or a personal mistake record.
page_bytes=64;tlb_entries=16;tlb_ways=4;cache_lines=16;line_bytes=4
tlb_snapshot={
    0:[(0x03,0,None),(0x00,0,None),(0x09,1,0x0d),(0x07,1,0x02)],
    3:[(0x07,0,None),(0x0a,1,0x34),(0x03,1,0x0d),(0x02,0,None)]}
page_snapshot={0x03:(1,0x02),0x08:(0,None),0x0f:(1,0x0d)}
cache_snapshot={5:(0x0d,1,[0x36,0x72,0xf0,0x1d]),12:(0x02,0,[None]*4)}
def trace_textbook_byte(va,tlb=tlb_snapshot,cache=cache_snapshot):
    vpn,offset=divmod(va,page_bytes)
    tlb_tag,tlb_group=divmod(vpn,tlb_entries//tlb_ways)
    matches=[pfn for tag,valid,pfn in tlb[tlb_group] if valid and tag==tlb_tag]
    row=dict(va=va,vpn=vpn,page_offset=offset,tlb_group=tlb_group,
             tlb_tag=tlb_tag,tlb_hit=bool(matches))
    if matches:pfn=matches[0]
    else:
        present,pfn=page_snapshot[vpn]
        if not present:return dict(row,outcome='page_fault')
    pa=pfn*page_bytes+offset
    block,byte_offset=divmod(pa,line_bytes)
    cache_tag,cache_line=divmod(block,cache_lines)
    stored_tag,valid,data=cache[cache_line]
    hit=bool(valid and stored_tag==cache_tag)
    return dict(row,ppn=pfn,pa=pa,cache_tag=cache_tag,cache_line=cache_line,
                byte_offset=byte_offset,cache_hit=hit,
                outcome='cache' if hit else 'memory',byte=data[byte_offset] if hit else None)
paths=[trace_textbook_byte(va) for va in [0x03d4,0x00f1,0x0229]]
add('textbook_joint_address_field_widths',
    [14-int(math.log2(page_bytes))-int(math.log2(tlb_entries//tlb_ways)),
     int(math.log2(tlb_entries//tlb_ways)),int(math.log2(page_bytes)),
     12-int(math.log2(line_bytes))-int(math.log2(cache_lines)),
     int(math.log2(cache_lines)),int(math.log2(line_bytes))],[6,2,6,6,4,2])
add('textbook_joint_address_three_paths',[r['outcome'] for r in paths],['cache','memory','page_fault'],paths)
add('textbook_joint_address_first_translation',
    [paths[0][k] for k in ['vpn','tlb_group','tlb_tag','ppn','pa','cache_line','cache_tag','byte_offset','byte']],
    [15,3,3,13,0x354,5,13,0,0x36])
add('textbook_joint_address_second_translation',
    [paths[1][k] for k in ['vpn','tlb_group','tlb_tag','tlb_hit','ppn','pa','cache_line','cache_tag','byte_offset','cache_hit']],
    [3,3,0,False,2,0xb1,12,2,1,False])
add('textbook_joint_address_fault_stops_before_cache',
    [paths[2]['vpn'],'pa' in paths[2],'cache_line' in paths[2]],[8,False,False])
changed_cache=dict(cache_snapshot);changed_cache[5]=(0x0c,1,[0x36,0x72,0xf0,0x1d])
add('textbook_joint_address_valid_bit_alone_insufficient',trace_textbook_byte(0x03d4,cache=changed_cache)['outcome'],'memory')
changed_tlb={group:list(items) for group,items in tlb_snapshot.items()}
changed_tlb[3]=[(tag,0 if tag==3 else valid,pfn) for tag,valid,pfn in changed_tlb[3]]
changed_path=trace_textbook_byte(0x03d4,tlb=changed_tlb)
add('textbook_joint_address_TLB_invalid_falls_back_to_page',
    [changed_path['tlb_hit'],changed_path['pa'],changed_path['outcome']],[False,0x354,'cache'])

# Revision 3: bind the parser and numerical checks to the actual new manuscript.
# The source audit separately compares every fenced character through Pandoc and
# the TeX verbatim payload; it does not compile or inspect lecture-note PDFs.
source_audit=json.loads((ROOT/'editorial/revision3/CO_sources/source_structure_checks.json').read_text())
add('revision3_source_structure_checks',
    [source_audit['status'],source_audit['checks'],all(c['passed'] for c in source_audit['results'])],
    ['PASS',70,True])
add('revision3_source_audit_matches_current_manuscripts',
    [hashlib.sha256((ROOT/c['manuscript']).read_bytes()).hexdigest()==c['sha256'] for c in source_audit['chapters']],
    [True]*8)
add('revision3_source_audit_matches_current_filter',
    hashlib.sha256((ROOT/source_audit['filter']['path']).read_bytes()).hexdigest(),
    source_audit['filter']['sha256'])
ch4=next((ROOT/'manuscript/CO').glob('04_*.md')).read_text()
machine_block=next(block for block in re.findall(r'^```[^\n]*\n(.*?)^```',ch4,re.M|re.S)
                   if '00401000' in block)
machine_rows=[re.split(r'\s{2,}',line.strip()) for line in machine_block.splitlines()]
machine={int(row[0]):row[1:] for row in machine_rows if row[0].isdigit()}
address,encoding,assembly=machine[16]
new_next=int(address,16)+len(bytes.fromhex(encoding))
new_delta=int.from_bytes(bytes.fromhex(encoding)[1:],'little',signed=True)
add('revision3_manuscript_call_decode',
    [f'{new_next:08X}',new_delta,f'{new_next+new_delta:08X}',assembly],
    ['0040102A',-42,'00401000','call f1 (00401000)'])
for line,target in [(12,0x401035),(20,0x40103a)]:
    address,encoding,assembly=machine[line];raw=bytes.fromhex(encoding)
    add(f'revision3_manuscript_branch_{line}_target',
        int(address,16)+len(raw)+int.from_bytes(raw[1:],'little',signed=True),target)

ch6=next((ROOT/'manuscript/CO').glob('06_*.md')).read_text()
programs=[block for block in re.findall(r'^```[^\n]*\n(.*?)^```',ch6,re.M|re.S)
          if block.startswith('I1  LOAD')]
def parse_actual_program(block):
    result=[]
    for line in block.splitlines():
        m=re.match(r'^(I\d+)\s+(LOAD|STORE|ADD|SHL)\s+(.+?)(?:\s*//.*)?$',line)
        assert m,line
        name,op,args=m.groups();operands=[a.strip() for a in args.split(',')]
        if op=='LOAD':sources=[];dest=operands[0]
        elif op=='STORE':sources=[operands[0]];dest=None
        elif op=='SHL':sources=operands;dest=operands[0]
        else:sources=operands;dest=operands[1]
        result.append((name,sources,dest))
    return result
for number,expected in enumerate([
        [[1,2,3,4,5],[2,3,4,5,6],[3,7,8,9,10],[7,11,12,13,14]],
        [[1,2,3,4,5],[2,3,4,5,6],[3,6,7,8,9],[6,10,11,12,13],[10,14,15,16,17]]]):
    trace=no_forward_schedule(parse_actual_program(programs[number]))
    add(f'revision3_manuscript_pipeline_{number+1}_trajectory',
        [[row[stage] for stage in ['IF','ID','EX','M','WB']] for row in trace],expected)

# Store all final paragraph hashes for a precise audit boundary.
manuscripts={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'manuscript/CO').glob('*.md'))}
binding_ids={'revision3_source_structure_checks','revision3_source_audit_matches_current_manuscripts','revision3_source_audit_matches_current_filter'}
result={'status':'PASS','checks':len(checks),'assertion_cases':131072+256+65280,'results':checks,'manuscript_sha256':manuscripts,
        'verification_breakdown':{'calculation_and_state_records':sum(c['id'] not in binding_ids for c in checks),
                                  'source_binding_records':sum(c['id'] in binding_ids for c in checks)},
        'scope':'Actual values/state trajectories checked; this is not an official syllabus or visual PDF certification.'}
def conv(x):
    if isinstance(x,Fraction):return str(x)
    raise TypeError(type(x).__name__)
(HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=conv),encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks),'assertion_cases':result['assertion_cases']},ensure_ascii=False))
