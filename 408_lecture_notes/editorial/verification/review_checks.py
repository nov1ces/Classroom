"""Extra independent checks used only by the manuscript technical review."""
from collections import deque
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
MANUSCRIPT=HERE.parent.parent/'manuscript/OS/03_同步互斥与信号量.md'


def peterson(cycles):
    # Separate reads of flag[j] and turn, matching && short-circuit evaluation.
    # pc: 0 flag=true, 1 turn=j, 2 read flag[j], 3 read turn,
    #     4 enter, 5 leave and flag=false, 6 completed all bounded cycles.
    initial=((0,0),(0,0),(False,False),0,(0,0))
    seen={initial};todo=deque([initial]);transitions=0;max_bypass=0
    while todo:
        pcs,done,flags,turn,bypass=todo.popleft()
        assert sum(p==5 for p in pcs)<=1
        assert max(bypass)<=2
        max_bypass=max(max_bypass,max(bypass))
        enabled=0
        for i in range(2):
            j=1-i;op=pcs[i]
            if op==6:continue
            pc=list(pcs);ds=list(done);fl=list(flags);bp=list(bypass);tu=turn
            if op==0:fl[i]=True;bp[i]=0;pc[i]=1
            elif op==1:tu=j;pc[i]=2
            elif op==2:pc[i]=3 if fl[j] else 4
            elif op==3:pc[i]=2 if tu==j else 4
            elif op==4:
                assert pc[j]!=5
                if fl[j] and pc[j]!=5:bp[j]+=1
                pc[i]=5
            elif op==5:
                fl[i]=False;ds[i]+=1;pc[i]=6 if ds[i]==cycles else 0
            nxt=(tuple(pc),tuple(ds),tuple(fl),tu,tuple(bp))
            assert sum(p==5 for p in pc)<=1
            assert max(bp)<=2
            enabled+=1;transitions+=1
            if nxt not in seen:seen.add(nxt);todo.append(nxt)
        assert enabled or done==(cycles,cycles)
    return dict(cycles_per_actor=cycles,states=len(seen),transitions=transitions,
                simultaneous_critical_sections_max=1,
                observed_max_bypass_after_flag_true=max_bypass,
                memory_model='顺序一致；flag与turn单次读写原子；&&两次读可分开交错',
                limit='每进程只检查给定有限轮数；不把有限轮数视为一般活性证明。计数从flag置真开始，包括尚未执行turn赋值的窗口，不声称此起点只有一次越过。')


def detached_reader_counterexample():
    # Mutant: the readCount check is outside the mutex; only ++ is protected.
    count=1;rw=0;active_readers={'R0'};active_writer=False
    trace=['R0正在读，readCount=1，读者组占有rw。']
    R1_should_acquire=(count==0)
    assert not R1_should_acquire
    trace.append('R1在锁外检查readCount!=0，决定跳过P(rw)，在++前暂停。')
    active_readers.remove('R0');count-=1
    if count==0:rw+=1
    trace.append('R0在计数锁内--至0，V(rw)，随后退出。')
    assert rw==1;rw-=1;active_writer=True
    trace.append('W执行P(rw)，开始写文件。')
    count+=1;active_readers.add('R1')
    trace.append('R1恢复，在计数锁内++至1，然后读文件。')
    assert active_writer and active_readers
    return dict(trace=trace,violation='读者R1与写者W重叠',
                applies_to='只保护readCount++而把首读者判断放在锁外的错误拆法，非正文正确代码。')


results=dict(
    manuscript_sha256=hashlib.sha256(MANUSCRIPT.read_bytes()).hexdigest(),
    checked_on='2026-10-15',
    peterson=[peterson(n) for n in (1,2,3)],
    reader_check_increment_separation=detached_reader_counterexample(),
)
(HERE/'technical_review_checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
