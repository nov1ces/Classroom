from collections import deque
import json
from pathlib import Path

def rr(quantum):
 arrivals=[0,2,4,5]; burst=[5,4,1,6]; remaining=burst[:]; q=deque(); t=0; nxt=0; trace=[]
 while nxt<len(arrivals) or q:
  if not q and nxt<len(arrivals) and t<arrivals[nxt]: t=arrivals[nxt]
  while nxt<len(arrivals) and arrivals[nxt]<=t:q.append(nxt);nxt+=1
  i=q.popleft(); start=t; ran=min(quantum,remaining[i]);t+=ran;remaining[i]-=ran;trace.append((f'P{i+1}',start,t))
  while nxt<len(arrivals) and arrivals[nxt]<=t:q.append(nxt);nxt+=1
  if remaining[i]:q.append(i)
 return trace
alloc=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
maxs=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
avail=[3,3,2]
def simulate(a,m,w,seq):
 w=w[:]; result=[w[:]]
 for i in seq:
  need=[m[i][j]-a[i][j] for j in range(3)]
  assert all(need[j]<=w[j] for j in range(3)),(i,w,need)
  w=[w[j]+a[i][j] for j in range(3)];result.append(w[:])
 return result
r2=rr(2);r5=rr(5)
assert r2==[('P1',0,2),('P2',2,4),('P1',4,6),('P3',6,7),('P2',7,9),('P4',9,11),('P1',11,12),('P4',12,14),('P4',14,16)]
assert r5==[('P1',0,5),('P2',5,9),('P3',9,10),('P4',10,15),('P4',15,16)]
base=simulate(alloc,maxs,avail,[1,3,0,2,4]); assert base==[[3,3,2],[5,3,2],[7,4,3],[7,5,3],[10,5,5],[10,5,7]]
a=[x[:] for x in alloc];a[0]=[2,2,1];trial=simulate(a,maxs,[1,2,1],[3,1,4,0,2]);assert trial==[[1,2,1],[3,3,2],[5,3,2],[5,3,4],[7,5,5],[10,5,7]]
unsafe=[row[:] for row in maxs];unsafe[0]=[8,5,3];unsafe[2]=[9,5,2];unsafe[4]=[4,3,6]
w=simulate(alloc,unsafe,avail,[1,3])[-1];blocked={str(i):[unsafe[i][j]-alloc[i][j] for j in range(3)] for i in [0,2,4]}
assert w==[7,4,3] and all(any(need[j]>w[j] for j in range(3)) for need in blocked.values())
out={'rr_q2':r2,'rr_q5':r5,'initial_safe_work':base,'p0_request_safe_work':trial,'unsafe_work':w,'unsafe_remaining_need':blocked}
Path(__file__).with_name('course_rr_banker_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('王道 RR 与银行家原例轨迹均验证通过')
