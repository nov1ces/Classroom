"""Independently simulate textbook replacement examples, preserving frame slots."""
import json
from pathlib import Path
CASES=[('OPT',3,[7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1],9,6),('FIFO',3,[3,2,1,0,3,2,4,3,2,1,0,4],9,6),('FIFO',4,[3,2,1,0,3,2,4,3,2,1,0,4],10,6),('LRU',4,[1,8,1,7,8,2,7,2,1,8,3,8,2,1,3,1,7,1,3,7],6,2)]
def simulate(method,n,sequence):
 slots=[None]*n; entered={}; used={}; rows=[]
 for i,page in enumerate(sequence):
  hit=page in slots; victim=None
  if not hit:
   if None in slots: idx=slots.index(None)
   else:
    if method=='OPT':
     def next_use(p):
      try: return sequence.index(p,i+1)
      except ValueError: return len(sequence)+1
     victim=max(slots,key=next_use)
    elif method=='FIFO': victim=min(slots,key=entered.get)
    else: victim=min(slots,key=used.get)
    idx=slots.index(victim); entered.pop(victim); used.pop(victim)
   slots[idx]=page; entered[page]=i
  used[page]=i
  rows.append({'step':i+1,'page':page,'slots':slots.copy(),'fault':not hit,'victim':victim})
 return rows
if __name__=='__main__':
 result=[]
 for method,n,seq,expected_faults,expected_replacements in CASES:
  rows=simulate(method,n,seq);faults=sum(r['fault'] for r in rows);replacements=sum(r['victim'] is not None for r in rows)
  assert (faults,replacements)==(expected_faults,expected_replacements)
  result.append({'method':method,'frames':n,'sequence':seq,'faults':faults,'replacements':replacements,'steps':rows})
 path=Path(__file__).resolve().parent/'course_replacement_checks.json'
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print('4 王道课件页面置换轨迹通过，输出',path)
