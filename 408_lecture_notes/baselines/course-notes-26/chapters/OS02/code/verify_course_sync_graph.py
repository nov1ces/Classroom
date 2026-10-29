from collections import deque
from pathlib import Path
import json
# Wangdao course 2.3.4_2: one signal per precedence edge.
programs=[['S1','Va','Vb'],['Pa','S2','Vc','Vd'],['Pb','S3','Vg'],['Pc','S4','Ve'],['Pd','S5','Vf'],['Pe','Pf','Pg','S6']]
requirements={1:[],2:[1],3:[1],4:[2],5:[2],6:[3,4,5]}
start=((0,)*6,(0,)*7,0);seen={start};queue=deque([start]);terminal=0
while queue:
 pc,tokens,done=queue.popleft(); actions=0
 for i,prog in enumerate(programs):
  if pc[i]==len(prog):continue
  op=prog[pc[i]];values=list(tokens);mask=done
  if op[0]=='P':
   j=ord(op[1])-ord('a')
   if values[j]==0:continue
   values[j]-=1
  elif op[0]=='V':values[ord(op[1])-ord('a')]+=1
  else:
   k=int(op[1:]);assert all(mask&(1<<(x-1)) for x in requirements[k]),(k,pc,tokens,done)
   mask|=1<<(k-1)
  actions+=1;nextpc=list(pc);nextpc[i]+=1
  state=(tuple(nextpc),tuple(values),mask)
  if state not in seen:seen.add(state);queue.append(state)
 if not actions:
  assert all(pc[i]==len(prog) for i,prog in enumerate(programs)),('deadlock',pc,tokens,done)
  assert done==63;terminal+=1

def reduce(available,alloc,req):
 work=list(available);todo=set(alloc);order=[]
 while True:
  possible=sorted(p for p in todo if all(req[p][i]<=work[i] for i in range(2)))
  if not possible:return order,work,sorted(todo)
  p=possible[0];order.append(p);todo.remove(p)
  work=[work[i]+alloc[p][i] for i in range(2)]
alloc={'P1':(2,0),'P2':(1,1)};req={'P1':(0,1),'P2':(1,0)}
a=reduce((0,1),alloc,req);assert a==(['P1','P2'],[3,2],[]),a
alloc2={**alloc,'P3':(0,1)};req2={**req,'P1':(0,2),'P3':(0,0)}
b=reduce((0,0),alloc2,req2);assert b==(['P3'],[0,1],['P1','P2']),b
result={'model':'one-shot P/V per each original course edge; unit-action interleavings', 'reachable_states':len(seen),'terminal_states':terminal,'all_precedence_conditions':'passed','deadlock_scenario_1':a,'deadlock_scenario_2':b}
(Path(__file__).with_name('course_sync_graph_checks.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
