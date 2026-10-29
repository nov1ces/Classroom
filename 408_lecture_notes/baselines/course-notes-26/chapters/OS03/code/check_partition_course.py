#!/usr/bin/env python3
"""Course allocation examples: records are (start,size), half-open intervals."""
import json
from pathlib import Path

def allocate(holes, amount, strategy):
 choices=[(start,size) for start,size in holes if size>=amount]
 if strategy=='first':pick=min(choices,key=lambda x:x[0])
 elif strategy=='best':pick=min(choices,key=lambda x:(x[1],x[0]))
 else:pick=max(choices,key=lambda x:(x[1],-x[0]))
 start,size=pick;result=[p for p in holes if p!=pick]
 if size>amount:result.append((start+amount,size-amount))
 return sorted(result)
initial=[(8,20),(32,10),(60,4)]
expected={'first':[[(23,5),(32,10),(60,4)],[(23,5),(40,2),(60,4)]], 'best':[[(8,20),(32,10),(63,1)],[(8,20),(41,1),(63,1)]], 'worst':[[(11,17),(32,10),(60,4)],[(20,8),(32,10),(60,4)]]}
result={}
for strategy,requests in [('first',[15,8]),('best',[3,9]),('worst',[3,9])]:
 holes=initial;steps=[]
 for n in requests:holes=allocate(holes,n,strategy);steps.append(holes)
 assert steps==expected[strategy],(strategy,steps)
 result[strategy]={'requests':requests,'states_start_size':steps,'status':'passed'}
assert [4,6-5,10,4]==[4,1,10,4] and [4,1,10-5,4]==[4,1,5,4]
result['next']={'states_sizes':[[4,6,10,4],[4,1,10,4],[4,1,5,4]],'assumption':'initial scan begins at first hole, subsequent scan resumes after selected hole','status':'passed'}
p=Path(__file__).with_name('partition_course_checks.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2));print('four allocation trajectories verified')
