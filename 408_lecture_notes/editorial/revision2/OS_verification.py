#!/usr/bin/env python3
"""Recalculate concrete paths behind the revised OS comparison tables."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
checks=[]
def check(identifier,actual,expected,scope):
    assert actual==expected,(identifier,actual,expected)
    checks.append(dict(id=identifier,actual=actual,expected=expected,status='PASS',scope=scope))

# Physical chain in the supplied file-allocation slide: 2 -> 5 -> 0 -> 1.
links={2:5,5:0,0:1,1:None}
block=2;implicit_reads=[]
for logical in range(4):
    implicit_reads.append(block)
    if logical<3:block=links[block]
check('OS-R2-01',implicit_reads,[2,5,0,1],
      '课件4.1_4页13/16/17模型：从首块读取第3号块，隐式链必须读四块。')
block=2;memory_lookups=[]
for _ in range(3):
    memory_lookups.append(block);block=links[block]
check('OS-R2-02',dict(memory_lookups=memory_lookups,disk_reads=[block]),
      dict(memory_lookups=[2,5,0],disk_reads=[1]),
      'FAT已驻留时同一目标只读目标数据块，仍需三次内存链查询；不当常数下标。')

# Recompute the existing 2015 example, independently of its written formula.
fanout=1024//4
def trace(offset):
    logical,within=divmod(offset,1024)
    if logical<10:return dict(logical=logical,within=within,path=['data'],index_items=[])
    logical_indirect=logical-10
    if logical_indirect<fanout:
        return dict(logical=logical,within=within,path=['level1','data'],index_items=[logical_indirect])
    first,second=divmod(logical_indirect-fanout,fanout)
    return dict(logical=logical,within=within,path=['level2','level1','data'],index_items=[first,second])
check('OS-R2-03',[trace(1234),trace(307400)],
      [dict(logical=1,within=210,path=['data'],index_items=[]),
       dict(logical=300,within=200,path=['level2','level1','data'],index_items=[0,34])],
      '既有2015真题、inode已在内存且间接块未缓存；实际追踪1次与3次读盘。')

# A concrete prefix of an extendable starvation execution, not a frequency claim.
low_remaining=4;timeline=[]
for tick in range(12):
    ready=[('low',1,low_remaining),('high_'+str(tick),0,1)]
    chosen=min(ready,key=lambda x:x[1]);timeline.append(chosen[0])
    if chosen[0]=='low':low_remaining-=1
check('OS-R2-04',(low_remaining,any(x=='low' for x in timeline)),(4,False),
      '高队列每单位到达一个一单位任务且没有提升规则，低队列连续12单位无服务；相同模式可延长。')

out=Path(__file__).with_name('OS_results.json')
out.write_text(json.dumps(dict(status='PASS',checks=checks,check_count=len(checks),
    scope='只核比较表所依赖的具体访盘/调度过程，不是PDF版式验收。'),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status='PASS',checks=len(checks)),ensure_ascii=False))
