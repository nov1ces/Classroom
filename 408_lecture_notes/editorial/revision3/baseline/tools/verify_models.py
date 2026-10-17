#!/usr/bin/env python3
"""Independent finite-state checks used in the synchronization chapter.

Semaphore availability models use nonnegative permits and leave a failed P at
its program counter. This is equivalent to the chapter's blocking P for these
safety/deadlock checks, but it does not model scheduling fairness.
"""
from collections import deque
from itertools import permutations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'editorial' / 'verification'


def signed_semaphore():
    value, queue, held = 2, [], set()
    actions = [('A', 'P'), ('B', 'P'), ('C', 'P'), ('D', 'P'),
               ('A', 'V'), ('B', 'V')]
    rows = []
    for actor, op in actions:
        wake = None
        if op == 'P':
            value -= 1
            if value < 0:
                queue.append(actor)
            else:
                held.add(actor)
        else:
            assert actor in held
            held.remove(actor)
            value += 1
            if value <= 0:
                wake = queue.pop(0)
                held.add(wake)  # permit already reserved; resumed P does not decrement
        assert len(queue) == max(0, -value)
        assert len(held) + max(value, 0) == 2
        rows.append(dict(action=f'{actor}:{op}', value=value,
                         queue=list(queue), wake=wake, holders=sorted(held)))
    assert [x['value'] for x in rows] == [1, 0, -1, -2, -1, 0]
    return rows


def buffer_search(capacity=2, mutant=False):
    # Two producers and two consumers, one item per actor; all primitive steps
    # interleave. A put/take is a short critical operation, guarded by mutex.
    prod = ['P:e', 'P:m', 'put', 'V:m', 'V:f']
    cons = ['P:f', 'P:m', 'take', 'V:m', 'V:e']
    if mutant:
        prod[:2], cons[:2] = ['P:m', 'P:e'], ['P:m', 'P:f']
    programs = [prod, prod, cons, cons]
    start = ((0, 0, 0, 0), capacity, 0, 1, 0, -1)
    todo, seen = deque([start]), {start}
    parent = {start: None}
    terminal, dead = 0, []
    while todo:
        s = todo.popleft()
        pcs, empty, full, mutex, count, owner = s
        assert 0 <= count <= capacity and mutex in (0, 1)
        assert (owner == -1) == (mutex == 1)
        moved = False
        for actor, pc in enumerate(pcs):
            if pc == len(programs[actor]):
                continue
            op = programs[actor][pc]
            tokens = {'e': empty, 'f': full, 'm': mutex}
            nc, no = count, owner
            if op.startswith('P:'):
                key = op[-1]
                if tokens[key] == 0:
                    continue
                tokens[key] -= 1
                if key == 'm':
                    assert owner == -1
                    no = actor
            elif op.startswith('V:'):
                key = op[-1]
                tokens[key] += 1
                if key == 'm':
                    assert owner == actor
                    no = -1
            elif op == 'put':
                assert owner == actor and count < capacity
                nc += 1
            elif op == 'take':
                assert owner == actor and count > 0
                nc -= 1
            newpc = list(pcs)
            newpc[actor] += 1
            ns = (tuple(newpc), tokens['e'], tokens['f'], tokens['m'], nc, no)
            moved = True
            if ns not in seen:
                seen.add(ns)
                todo.append(ns)
                parent[ns] = (s, f'actor{actor} {op}')
        if not moved:
            if all(pc == len(p) for pc, p in zip(pcs, programs)):
                assert count == 0 and empty == capacity and full == 0
                terminal += 1
            else:
                dead.append(s)
    witness = []
    if dead:
        cur = dead[0]
        while parent[cur] is not None:
            prev, desc = parent[cur]
            witness.append(dict(step=desc, state=cur))
            cur = prev
        witness.reverse()
    return dict(capacity=capacity, mutant=mutant, states=len(seen),
                terminal_states=terminal, deadlocks=len(dead), witness=witness)


def precedence():
    nodes = 'ABCDEF'
    question_edges = [('A','C'),('B','C'),('C','D'),('C','E'),('E','F')]
    thread_edges = [('A','E'),('E','F'),('B','C'),('C','D')]
    selected = [('A','C'),('C','E')]
    def orders(edges):
        return {''.join(p) for p in permutations(nodes)
                if all(p.index(a) < p.index(b) for a,b in edges)}
    desired = orders(question_edges + thread_edges)
    actual = orders(selected + thread_edges)
    assert actual == desired
    assert orders(selected[1:] + thread_edges) != desired
    assert orders(selected[:1] + thread_edges) != desired
    assert any(p.index('D') < p.index('E') for p in actual)
    assert any(p.index('D') > p.index('F') for p in actual)
    return dict(edges=question_edges, thread_edges=thread_edges,
                semaphore_edges=selected, allowed_orders=sorted(actual),
                count=len(actual), minimum_independent_semaphores=2)


def philosophers(mode):
    # Each philosopher makes one attempt: enter, acquire two forks, eat,
    # release forks, leave. A room permit covers acquisition through release.
    n = 5
    programs = []
    for i in range(n):
        forks = [i, (i+1)%n]
        if mode == 'ordered':
            forks.sort()
        ops = [('take', x) for x in forks] + [('eat', -1)]
        ops += [('give', x) for x in forks]
        if mode == 'room4':
            ops = [('enter', -1)] + ops + [('leave', -1)]
        programs.append(ops)
    start = ((0,)*n, (-1,)*n, 4)
    todo, seen = deque([start]), {start}
    dead = terminal = max_holders = 0
    while todo:
        s = todo.popleft()
        pcs, owners, room = s
        assert room >= 0
        max_holders = max(max_holders, sum(owners.count(i) == 2 for i in range(n)))
        moved = False
        for i,pc in enumerate(pcs):
            if pc == len(programs[i]):
                continue
            op,arg = programs[i][pc]
            no, nr = list(owners), room
            if op == 'take':
                if no[arg] != -1:
                    continue
                no[arg] = i
            elif op == 'give':
                assert no[arg] == i
                no[arg] = -1
            elif op == 'eat':
                assert owners.count(i) == 2
            elif op == 'enter':
                if room == 0:
                    continue
                nr -= 1
            elif op == 'leave':
                nr += 1
            np = list(pcs)
            np[i] += 1
            ns = (tuple(np), tuple(no), nr)
            moved = True
            if ns not in seen:
                seen.add(ns)
                todo.append(ns)
        if not moved:
            if all(pc == len(p) for pc,p in zip(pcs,programs)):
                terminal += 1
            else:
                dead += 1
    assert max_holders <= n//2
    return dict(mode=mode, states=len(seen), deadlocks=dead,
                terminal_states=terminal, max_holding_two=max_holders,
                scope='five philosophers; one finite attempt per actor; no fairness assertion')


def lost_update():
    finals = {}
    # Each actor reads, increments its private register, then writes.
    def walk(x, pcs, regs, path):
        if pcs == (3,3):
            finals.setdefault(x,path)
            return
        for a in range(2):
            pc = pcs[a]
            if pc == 3:
                continue
            nr, np, nx = list(regs), list(pcs), x
            if pc == 0: nr[a] = x
            elif pc == 1: nr[a] += 1
            else: nx = nr[a]
            np[a] += 1
            walk(nx, tuple(np), tuple(nr), path+[f'{"AB"[a]}:{["read","add","write"][pc]}'])
    walk(0, (0,0), (0,0), [])
    assert set(finals) == {1,2}
    return finals


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    good = [buffer_search(1),buffer_search(2)]
    bad = buffer_search(1,True)
    assert all(x['deadlocks'] == 0 and x['terminal_states'] > 0 for x in good)
    assert bad['deadlocks'] > 0
    phil = [philosophers(x) for x in ['naive','room4','ordered']]
    assert phil[0]['deadlocks'] > 0
    assert all(x['deadlocks'] == 0 for x in phil[1:])
    result = dict(status='PASS',signed_trace=signed_semaphore(),
                  buffer=good,buffer_wrong_order=bad,precedence=precedence(),
                  philosophers=phil,lost_update=lost_update(),
                  limits=['Finite-state exploration is a bounded independent check, not a proof of all executions.',
                          'No automatic fairness/starvation claim.',
                          'Question wording and figures require separate source inspection.'])
    (OUT/'model_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (ROOT/'figures'/'model_data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:result[k] for k in ['status','buffer','philosophers']},ensure_ascii=False))


if __name__ == '__main__':
    main()
