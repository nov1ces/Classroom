"""Independent, executable checks for the five OS candidate solutions.

No check infers truth from a file name or heading. P operations below use the
equivalent nonnegative permit model: a failed P has no state transition.
Finite exhaustive checks do not replace the general invariant arguments.
"""
from collections import deque
from itertools import permutations
from pathlib import Path
import json
import random

OUT = Path(__file__).resolve().parent


def exhaustive(initial, step, invariant, terminal=lambda s: False):
    seen = {initial}
    todo = deque([initial])
    transitions = deadlocks = terminals = 0
    while todo:
        state = todo.popleft()
        invariant(state)
        next_states = list(step(state))
        if terminal(state):
            terminals += 1
        elif not next_states:
            deadlocks += 1
            raise AssertionError(('deadlock', state))
        for nxt in next_states:
            invariant(nxt)
            transitions += 1
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return dict(states=len(seen), transitions=transitions,
                deadlocks=deadlocks, terminal_states=terminals)


def check_2022():
    programs = [('A', 'V0', 'P1', 'E', 'F'),
                ('B', 'P0', 'C', 'V1', 'D')]
    complete = set()

    def step(s):
        pcs, sem, trace = s
        for t in range(2):
            if pcs[t] == len(programs[t]):
                continue
            op = programs[t][pcs[t]]
            ns = list(sem)
            tr = trace
            if op[0] == 'P':
                i = int(op[1])
                if not ns[i]:
                    continue
                ns[i] -= 1
            elif op[0] == 'V':
                ns[int(op[1])] += 1
            else:
                tr += op
            pc = list(pcs)
            pc[t] += 1
            yield tuple(pc), tuple(ns), tr

    def invariant(s):
        pcs, sem, trace = s
        assert all(v >= 0 for v in sem)
        for a, b in [('A','C'),('B','C'),('C','D'),('C','E'),('E','F')]:
            if b in trace:
                assert a in trace and trace.index(a) < trace.index(b)
        if pcs == (5, 5):
            complete.add(trace)

    result = exhaustive(((0,0),(0,0),''),step,invariant,
                        lambda s: s[0] == (5,5))
    expected = {''.join(p) for p in permutations('ABCDEF')
                if all(p.index(a) < p.index(b) for a,b in
                       [('A','C'),('B','C'),('C','D'),('C','E'),('E','F')])}
    assert complete == expected
    result.update(visible_complete_orders=sorted(complete),
                  complete_orders_equal_graph_topological_orders=True)
    return result


def check_2024():
    # Part (2): distinguish operation entry and exit, so overlap is checked.
    programs = [('write_begin','write_end','V'), ('P','read_begin','read_end')]
    def step(s):
        pcs, permit, active, occupied = s
        for t in range(2):
            if pcs[t] == 3:
                continue
            op = programs[t][pcs[t]]
            pp,aa,oo = permit,active,occupied
            if op == 'P':
                if pp == 0: continue
                pp -= 1
            elif op == 'V': pp += 1
            elif op.endswith('begin'):
                assert aa == -1
                assert oo == (0 if t == 0 else 1)
                aa = t
            else:
                assert aa == t
                aa = -1
                oo = 1 if t == 0 else 0
            pc=list(pcs);pc[t]+=1
            yield tuple(pc),pp,aa,oo
    once = exhaustive(((0,0),0,-1,0),step,
                      lambda s: (s[1]>=0) or (_ for _ in ()).throw(AssertionError()),
                      lambda s: s[0]==(3,3))

    # Part (3): use a read/modify/write teaching instance to expose lost updates.
    def modification(use_lock):
        program = ('P','read','write','V') if use_lock else ('read','write')
        finals=set()
        def step(s):
            pcs,sem,value,locals_=s
            for t in range(2):
                if pcs[t] == len(program): continue
                op=program[pcs[t]]
                se=sem;v=value;loc=list(locals_)
                if op=='P':
                    if se==0:continue
                    se-=1
                elif op=='V':se+=1
                elif op=='read':loc[t]=v
                else:v=loc[t]+1
                pc=list(pcs);pc[t]+=1
                yield tuple(pc),se,v,tuple(loc)
        def inv(s):
            assert s[1]>=0
            if s[0] == (len(program),len(program)):finals.add(s[2])
        r=exhaustive(((0,0),1,0,(-1,-1)),step,inv,
                     lambda s:s[0]==(len(program),len(program)))
        r['final_values']=sorted(finals)
        return r
    locked=modification(True);unlocked=modification(False)
    assert locked['final_values']==[2]
    assert unlocked['final_values']==[1,2]
    return dict(part2_once=once,part3_read_modify_write_illustration_with_mutex=locked,
                illustration_without_mutex=unlocked,
                limitation='加一仅为读改写互斥的教学检查实例，非真题C3的附加条件。')


def check_2009(capacity):
    # ppc 0 choose parity,1 Pempty,2 Pmutex,3 put,4 Vmutex,5 Vclass.
    # cpc 0 Pclass,1 Pmutex,2 get,3 Vmutex,4 Vempty,5 count.
    # State: producer pc/parity, two consumer pcs, four permits, actual counts.
    initial=(0,-1,(0,0),(capacity,0,0,1),(0,0))
    def step(s):
        pp,x,cp,sem,q=s
        if pp==0:
            for parity in (0,1):yield 1,parity,cp,sem,q
        else:
            se=list(sem);qq=list(q);np=pp+1;nx=x
            enabled=True
            if pp==1:
                if se[0]:se[0]-=1
                else:enabled=False
            elif pp==2:
                if se[3]:se[3]-=1
                else:enabled=False
            elif pp==3:
                assert sum(qq)<capacity;qq[x]+=1
            elif pp==4:se[3]+=1
            elif pp==5:se[1+x]+=1;np=0;nx=-1
            if enabled:yield np,nx,cp,tuple(se),tuple(qq)
        for t in range(2):
            se=list(sem);qq=list(q);pc=list(cp);enabled=True
            op=cp[t]
            if op==0:
                if se[1+t]:se[1+t]-=1
                else:enabled=False
            elif op==1:
                if se[3]:se[3]-=1
                else:enabled=False
            elif op==2:
                assert qq[t]>0;qq[t]-=1
            elif op==3:se[3]+=1
            elif op==4:se[0]+=1
            pc[t]=(op+1)%6
            if enabled:yield pp,x,tuple(pc),tuple(se),tuple(qq)
    def inv(s):
        pp,x,cp,sem,q=s
        assert all(z>=0 for z in sem+q)
        assert sum(q)<=capacity
        holders=int(pp in (3,4))+sum(p in (2,3) for p in cp)
        assert holders+sem[3]==1
        reserved_before_put=int(pp in (2,3))
        removed_not_released=sum(p in (3,4) for p in cp)
        assert sem[0]+sum(q)+reserved_before_put+removed_not_released==capacity
        for t in range(2):
            produced_not_signalled=int(pp in (4,5) and x==t)
            reserved_before_get=int(cp[t] in (1,2))
            assert q[t]==sem[1+t]+produced_not_signalled+reserved_before_get
    r=exhaustive(initial,step,inv)
    r['capacity']=capacity
    r['checks']=['分类取数前确有相应类别','容量不越界','单次缓冲操作互斥',
                 '许可与操作中预留量的精确守恒','不存在全局死锁状态']
    return r


def batch_model(capacity):
    # Producers: Pempty,Pmutex,put,Vmutex,Vfull.
    # Consumers: Pbatch,Pfull,Pmutex,get,Vmutex,Vempty,continue,Vbatch.
    initial=((0,0),(0,0),(0,0),(capacity,0,1,1),0)
    def step(s):
        pp,cp,k,sem,q=s
        for t in range(2):
            se=list(sem);pc=list(pp);qq=q;op=pp[t];ok=True
            if op in (0,1):
                idx=0 if op==0 else 2
                if se[idx]:se[idx]-=1
                else:ok=False
            elif op==2:assert qq<capacity;qq+=1
            elif op==3:se[2]+=1
            else:se[1]+=1
            pc[t]=(op+1)%5
            if ok:yield tuple(pc),cp,k,tuple(se),qq
        for t in range(2):
            se=list(sem);pc=list(cp);kk=list(k);qq=q;op=cp[t];ok=True
            if op in (0,1,2):
                idx={0:3,1:1,2:2}[op]
                if se[idx]:se[idx]-=1
                else:ok=False
            elif op==3:
                assert qq>0;qq-=1;kk[t]+=1
            elif op==4:se[2]+=1
            elif op==5:se[0]+=1
            elif op==7:se[3]+=1;kk[t]=0
            pc[t]=(op+1)%8
            if op==6:pc[t]=1 if kk[t]<10 else 7
            if ok:yield pp,tuple(pc),tuple(kk),tuple(se),qq
    def inv(s):
        pp,cp,k,sem,q=s
        assert all(z>=0 for z in sem)
        assert 0<=q<=capacity
        assert all(0<=z<=10 for z in k)
        lock_holders=sum(p in (2,3) for p in pp)+sum(p in (3,4) for p in cp)
        assert lock_holders+sem[2]==1
        batch_holders=sum(p!=0 for p in cp)
        assert batch_holders+sem[3]==1
        pre_put=sum(p in (1,2) for p in pp)
        post_get=sum(p in (4,5) for p in cp)
        assert sem[0]+q+pre_put+post_get==capacity
        post_put=sum(p in (3,4) for p in pp)
        pre_get=sum(p in (2,3) for p in cp)
        assert q==sem[1]+post_put+pre_get
        for t in range(2):
            if cp[t]==3:
                assert batch_holders==1
                assert k[t]<10
    return initial,step,inv


def check_2014(capacity, random_steps=None):
    initial,step,inv=batch_model(capacity)
    if random_steps is None:
        r=exhaustive(initial,step,inv)
    else:
        rng=random.Random(408)
        state=initial;puts=gets=0
        for _ in range(random_steps):
            inv(state)
            possible=list(step(state));assert possible
            nxt=rng.choice(possible)
            puts+=int(nxt[-1]>state[-1]);gets+=int(nxt[-1]<state[-1])
            state=nxt
        inv(state)
        assert puts>1000 and gets>1000
        r=dict(random_seed=408,steps=random_steps,puts=puts,gets=gets,
               final_occupancy=state[-1],deadlocks=0)
    r.update(capacity=capacity,batch_size=10,
             producers=2,consumers=2,
             checks=['实际缓冲容量守恒','单次缓冲操作互斥','十件批次不被其他消费者插入',
                     '批内允许生产者补货','不存在全局死锁状态'])
    return r


def check_2025(cycles):
    # A: Ppos,Pshovel,dig,Vshovel,Vpit.
    # B: Ppit,plant,Vpos,Pshovel,fill,Vshovel,Vtree.
    # C: Ptree,water. Completed cycles bound the otherwise unbounded pipeline.
    initial=((0,0,0),(0,0,0),(3,0,0,1),(0,0))
    lengths=(5,7,2)
    def step(s):
        pcs,done,sem,stocks=s
        for t in range(3):
            if done[t]==cycles:continue
            pc=list(pcs);ds=list(done);se=list(sem);st=list(stocks)
            op=pcs[t];ok=True
            waits={(0,0):0,(0,1):3,(1,0):1,(1,3):3,(2,0):2}
            signals={(0,3):3,(0,4):1,(1,2):0,(1,5):3,(1,6):2}
            if (t,op) in waits:
                i=waits[t,op]
                if se[i]:se[i]-=1
                else:ok=False
            elif (t,op) in signals:se[signals[t,op]]+=1
            elif (t,op)==(0,2):assert st[0]<3;st[0]+=1
            elif (t,op)==(1,1):assert st[0]>0;st[0]-=1
            elif (t,op)==(1,4):st[1]+=1
            elif (t,op)==(2,1):assert st[1]>0;st[1]-=1
            else:raise AssertionError((t,op))
            pc[t]=(op+1)%lengths[t]
            if pc[t]==0:ds[t]+=1
            if ok:yield tuple(pc),tuple(ds),tuple(se),tuple(st)
    def inv(s):
        pc,done,se,st=s
        assert all(z>=0 for z in se+st)
        assert st[0]<=3
        shovel_holders=int(pc[0] in (2,3))+int(pc[1] in (4,5))
        assert shovel_holders+se[3]==1
        A_reserved=int(pc[0] in (1,2))
        B_release_pending=int(pc[1]==2)
        assert st[0]+se[0]+A_reserved+B_release_pending==3
        dug_unpublished=int(pc[0] in (3,4))
        B_reserved=int(pc[1]==1)
        assert st[0]==se[1]+dug_unpublished+B_reserved
        filled_unpublished=int(pc[1] in (5,6))
        C_reserved=int(pc[2]==1)
        assert st[1]==se[2]+filled_unpublished+C_reserved
    r=exhaustive(initial,step,inv,lambda s:s[1]==(cycles,cycles,cycles))
    r.update(cycles_per_worker=cycles,
             checks=['未用空坑不超过3','铁锹互斥','先放苗再填土再浇水',
                     '坑配额与预留量守恒','全部工人可完成给定轮数'])
    return r


results={
    'verification_date':'2026-10-15',
    'method':'独立状态转移枚举；P/V按原子许可操作；有限穷举加一般不变量说明。',
    '2022-46':check_2022(),
    '2024-46':check_2024(),
    '2009-45':[check_2009(n) for n in (1,2,3)],
    '2014-47':{'exhaustive_small_capacity':[check_2014(n) for n in (1,2,3)],
               'actual_capacity_random_interleaving':check_2014(1000,100000)},
    '2025-45':[check_2025(n) for n in (1,3,4)],
    'limits':['小容量穷举不宣称穷举原题1000槽全部状态；原容量另外检查固定种子的100000步真实交错。',
              '证明无全局死锁不等于保证任意不公平调度下无饥饿。',
              '2009题按参考答案的初始为空；非空初态另由许可定义与守恒式说明。',
              '2024读改写加一是解释实例，未改写原题。']
}
(OUT/'verification_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
