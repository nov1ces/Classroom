#!/usr/bin/env python3
"""Independent event simulation of the four-process Wangdao priority example."""
from pathlib import Path
import json
spec=[('P1',0,7,1),('P2',2,4,2),('P3',4,1,3),('P4',5,4,2)]

def simulate(preempt):
    remain={name:run for name,arr,run,pri in spec}; priority={name:pri for name,arr,run,pri in spec}
    ready=[]; serial=0; running=None; result=[]
    for t in range(16):
        for name,arrival,run,pri in spec:
            if arrival==t:ready.append((serial,name));serial+=1
        if running and preempt and ready and max(priority[n] for _,n in ready)>priority[running]:
            ready.append((serial,running));serial+=1;running=None
        if running is None:
            seq,name=min(ready,key=lambda a:(-priority[a[1]],a[0]));ready.remove((seq,name));running=name
        if result and result[-1][0]==running:result[-1][2]=t+1
        else:result.append([running,t,t+1])
        remain[running]-=1
        if remain[running]==0:running=None
    assert all(x==0 for x in remain.values())
    return result

expected_non=[['P1',0,7],['P3',7,8],['P2',8,12],['P4',12,16]]
expected_pre=[['P1',0,2],['P2',2,4],['P3',4,5],['P2',5,7],['P4',7,11],['P1',11,16]]
a,b=simulate(False),simulate(True)
assert a==expected_non,(a,expected_non)
assert b==expected_pre,(b,expected_pre)
out={'model':'higher numeric priority; ties by ready-queue entry order; arrivals at integer times; no switch overhead','non_preemptive':a,'preemptive':b,'result':'passed'}
Path(__file__).with_name('priority_course_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False))
