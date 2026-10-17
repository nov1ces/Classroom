from pathlib import Path
import json,hashlib
from collections import Counter
BASE=0x00422000
trace_rows=[(i,j,BASE+4*(64*i+j)) for i in range(24) for j in range(64)]
trace_cols=[(i,j,BASE+4*(64*i+j)) for j in range(64) for i in range(24)]
def simulate(trace,ways):
    sets=[[] for _ in range(64)]; misses=[]; hits=0; pages=set(); faults=[]
    for k,(i,j,address) in enumerate(trace):
        if address//4096 not in pages:
            pages.add(address//4096); faults.append(f'{address:08X}H')
        block=address//32; si=block%64; tag=block//64
        if tag in sets[si]:
            hits+=1; sets[si].remove(tag)
        else:
            misses.append(k)
            if len(sets[si])==ways:sets[si].pop(0)
        sets[si].append(tag)
    return {'accesses':len(trace),'hits':hits,'misses':len(misses),'hit_rate':hits/len(trace),'first_misses':misses[:32],'page_faults':faults,'first_column_blocks_per_set':dict(sorted(Counter((BASE+4*64*i)//32%64 for i in range(24)).items()))}
array_results={'row_major_4_way':simulate(trace_rows,4),'column_major_4_way':simulate(trace_cols,4),'row_major_2_way_LRU_variant':simulate(trace_rows,2),'column_major_2_way_LRU_variant':simulate(trace_cols,2),'bytes':len(trace_rows)*4,'unique_blocks':len(set(a//32 for _,_,a in trace_rows)),'unique_pages':len(set(a//4096 for _,_,a in trace_rows)),'a_1_0':f'{BASE+256:08X}H','a_1_0_cache_set':((BASE+256)>>5)&63,'assumptions':['write allocate on first write miss','initially array absent from main memory and cache','distinct virtual pages backed by distinct page frames; Cache index lies inside unchanged page offset','no competing data accesses','LRU only required for the two-way original variant']}
assert array_results['row_major_4_way']['misses']==192
assert array_results['column_major_4_way']['misses']==192
assert array_results['column_major_2_way_LRU_variant']['misses']==1536
# Compare 16-bit Boolean sign formula with mathematical signed overflow,
# exhausting all 65536 first operands against nine independent boundary operands.
boundaries=[-32768,-32767,-16384,-1,0,1,16383,32766,32767]
checked=0; failures=[]
for au in range(65536):
    av=au if au<32768 else au-65536
    a=(au>>15)&1
    for bv in boundaries:
        b=((bv&0xffff)>>15)&1
        for op in ['add','sub']:
            value=av+bv if op=='add' else av-bv
            f=((value&0xffff)>>15)&1
            formula=(a and b and not f) or (not a and not b and f) if op=='add' else (a and not b and not f) or (not a and b and f)
            expected=not(-32768<=value<=32767)
            checked+=1
            if bool(formula)!=expected:failures.append([av,bv,op,value])
assert not failures
results={'CO3-11':array_results,'CO5-2':{'word_bits':16,'register_index_bits':4,'max_registers':2**4,'fetch_cycles':1+5+1,'boolean_overflow_tests':checked,'first_operand_exhaustive':65536,'second_operand_boundaries':boundaries,'operations':['add','sub'],'failures':failures}}
Path(__file__).with_name('co_new_question_calculations.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'array_misses':[array_results[k]['misses'] for k in ['row_major_4_way','column_major_4_way','row_major_2_way_LRU_variant','column_major_2_way_LRU_variant']],'overflows_checked':checked,'failures':len(failures)},ensure_ascii=False))
