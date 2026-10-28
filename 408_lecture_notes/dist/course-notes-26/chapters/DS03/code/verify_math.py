#!/usr/bin/env python3
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
import json,math
checks=0
for n in range(1,101):
 lower=[(i,j) for i in range(1,n+1) for j in range(1,i+1)]
 upper_col=[(i,j) for j in range(1,n+1) for i in range(1,j+1)]
 upper_row=[(i,j) for i in range(1,n+1) for j in range(i,n+1)]
 lower_col=[(i,j) for j in range(1,n+1) for i in range(j,n+1)]
 for cells,formula in [(lower,lambda i,j:i*(i-1)//2+j-1),(upper_col,lambda i,j:j*(j-1)//2+i-1),(upper_row,lambda i,j:(i-1)*(2*n-i+2)//2+j-i),(lower_col,lambda i,j:(j-1)*(2*n-j+2)//2+i-j)]:
  for k,(i,j) in enumerate(cells):assert formula(i,j)==k;checks+=1
 for k,(i,j) in enumerate(lower):
  rr=math.isqrt(8*k+1);r=(rr-1)//2
  while (r+1)*(r+2)//2<=k:r+=1
  assert (r,k-r*(r+1)//2)==(i-1,j-1);checks+=1
 band=[(i,j) for i in range(1,n+1) for j in range(1,n+1) if abs(i-j)<=1]
 assert len(band)==(1 if n==1 else 3*n-2)
 for k,(i,j) in enumerate(band):
  assert 2*i+j-3==k
  assert ((k+4)//3,k-2*((k+4)//3)+3)==(i,j)
  assert (k+1)//3+1==i
  checks+=1
@lru_cache(None)
def reachable(next_value,queue,input_restricted,output_restricted):
 if next_value==5 and not queue:return {()}
 results=set()
 if next_value<5:
  successors=[queue+(next_value,)]
  if not input_restricted:successors.append((next_value,)+queue)
  for q in successors:results.update(reachable(next_value+1,q,input_restricted,output_restricted))
 if queue:
  for index in ([0] if output_restricted else [0,-1]):
   value=queue[index];remaining=queue[1:] if index==0 else queue[:-1]
   results.update((value,)+suffix for suffix in reachable(next_value,remaining,input_restricted,output_restricted))
 return results
all_perms=set(__import__('itertools').permutations(range(1,5)))
in_only=reachable(1,(),True,False);out_only=reachable(1,(),False,True)
assert len(in_only)==len(out_only)==22
assert all_perms-in_only=={(4,2,1,3),(4,2,3,1)}
assert all_perms-out_only=={(4,1,3,2),(4,2,3,1)}
stack=[];peak=0
for token in '15 7 1 1 + - / 3 * 2 1 1 + + -'.split():
 if token.isdigit():stack.append(Fraction(int(token)))
 else:
  right=stack.pop();left=stack.pop();stack.append({'+':lambda:left+right,'-':lambda:left-right,'*':lambda:left*right,'/':lambda:left/right}[token]())
 peak=max(peak,len(stack))
assert stack==[5] and peak==4
assert 1000+((4-2)*4+(1-(-1)))*4==1040
assert 2*30+30-3==87
assert 7*6//2+2-1==22
result={'matrix_coordinate_checks':checks,'input_restricted_outputs':len(in_only),'output_restricted_outputs':len(out_only),'postfix_result':int(stack[0]),'postfix_peak':peak,'status':'passed'}
print(json.dumps(result,ensure_ascii=False))
(Path(__file__).resolve().parents[1]/'sources/math_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
