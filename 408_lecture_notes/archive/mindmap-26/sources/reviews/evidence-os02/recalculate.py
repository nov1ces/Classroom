import json,itertools
from collections import deque
from pathlib import Path
out={}
# 独立单位时刻模拟，每次只按当时已到达集合挑选。
def priority(jobs,lower=False):
 rem={p:b for p,a,b,pr in jobs};done={};trace=[];t=0;first={}
 while len(done)<len(jobs):
  ready=[x for x in jobs if x[1]<=t and rem[x[0]]>0]
  if not ready:t+=1;continue
  x=min(ready,key=lambda x:(x[3] if lower else -x[3],x[1],x[0]));p=x[0]
  if not trace or trace[-1][0]!=p:trace.append([p,t,t+1])
  else:trace[-1][2]=t+1
  first.setdefault(p,t);rem[p]-=1;t+=1
  if rem[p]==0:done[p]=t
 return {'trace':trace,'completion':done,'turnaround':{p:done[p]-a for p,a,b,pr in jobs},'response':{p:first[p]-a for p,a,b,pr in jobs},'waiting':{p:done[p]-a-b for p,a,b,pr in jobs}}
out['2A-3']=priority([('P1',0,60,1),('P2',20,42,10),('P3',30,13,100)])
assert sum(out['2A-3']['turnaround'].values())/3==61
assert out['2A-3']['waiting']['P2']==13
out['2A-4']=priority([('P0',0,100,15),('P1',10,60,20),('P2',10,20,10),('P3',15,10,6)],True)
assert len(out['2A-4']['trace'])==6
jobs=[('P1',0,8),('P2',1,4),('P3',2,9),('P4',3,5)]
rem={p:b for p,a,b in jobs};done={};t=0;trace=[]
while len(done)<4:
 ready=[x for x in jobs if x[1]<=t and rem[x[0]]>0]
 p=min(ready,key=lambda x:(rem[x[0]],x[1]))[0]
 if not trace or trace[-1][0]!=p:trace.append([p,t,t+1])
 else:trace[-1][2]=t+1
 rem[p]-=1;t+=1
 if rem[p]==0:done[p]=t
out['2A-6-SRTF']={'trace':trace,'turnaround':{p:done[p]-a for p,a,b in jobs}}
assert sum(out['2A-6-SRTF']['turnaround'].values())/4==13
rem={p:b for p,a,b in jobs};done={};future=deque(jobs);queue=deque();trace=[];t=0
while len(done)<4:
 while future and future[0][1]<=t:queue.append(future.popleft()[0])
 p=queue.popleft();used=min(2,rem[p]);trace.append([p,t,t+used]);rem[p]-=used;t+=used
 # 先将新到达者排入，再归队片满未完成者。
 while future and future[0][1]<=t:queue.append(future.popleft()[0])
 if rem[p]:queue.append(p)
 else:done[p]=t
out['2A-6-RR']={'trace':trace,'turnaround':{p:done[p]-a for p,a,b in jobs}}
assert sum(out['2A-6-RR']['turnaround'].values())/4==19.25
# 枚举全部排列，独立于正文选择顺序，防止误把一条失败路线当无安全序列。
def safe_sequences(alloc,need,available):
 results=[]
 for seq in itertools.permutations(range(len(alloc))):
  w=list(available);valid=True
  for i in seq:
   if not all(n<=v for n,v in zip(need[i],w)):valid=False;break
   w=[v+a for v,a in zip(w,alloc[i])]
  if valid:results.append(seq)
 return results
alloc=[(2,0,0),(1,2,0),(0,1,1),(0,0,1)]
need=[(0,0,1),(1,3,2),(1,3,1),(2,0,0)]
out['2C-2-all-sequences']=safe_sequences(alloc,need,(0,2,1));assert not out['2C-2-all-sequences']
alloc=[(0,0,3),(1,0,0),(1,3,5),(0,0,2),(0,0,1)]
maxima=[(0,0,4),(1,7,5),(2,3,5),(0,6,4),(0,6,5)]
need=[tuple(m-a for m,a in zip(mr,ar)) for mr,ar in zip(maxima,alloc)]
out['2C-3']={str(v):safe_sequences(alloc,need,v) for v in [(1,4,0),(0,6,2),(1,1,1),(0,4,7)]}
assert [bool(v) for v in out['2C-3'].values()]==[True,False,False,False]
# 单类资源最小反例：给P前后分别枚举安全序列。
out['request-counterexample']={'before':safe_sequences([(1,),(1,)],[(3,),(2,)],(2,)),'after':safe_sequences([(2,),(1,)],[(2,),(2,)],(1,))}
assert out['request-counterexample']['before'] and not out['request-counterexample']['after']
value=2;wait=deque();pv=[]
for p in 'ABCD':
 value-=1
 if value<0:wait.append(p)
 pv.append({'op':'P'+p,'value':value,'queue':list(wait)})
for p in 'AB':
 value+=1;wake=wait.popleft() if value<=0 else None
 pv.append({'op':'V'+p,'value':value,'woken':wake,'queue':list(wait)})
out['semaphore']=pv
assert [x['value'] for x in pv]==[1,0,-1,-2,-1,0]
assert pv[-2]['woken']=='C' and pv[-1]['woken']=='D'
Path(__file__).with_name('recalculation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('independent recomputation passed: priority×2, SRTF, RR, banker×2, request counterexample, semaphore')
