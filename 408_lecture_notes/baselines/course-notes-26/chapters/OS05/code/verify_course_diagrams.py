#!/usr/bin/env python3
"""Independently check the four illustrative buffer schedules and disk paths."""
from pathlib import Path
import json

def buffer_transitions(initial, operations):
    full=initial; end=-1
    for begin,finish,kind in sorted(operations):
        assert end<=begin and finish>begin,(begin,finish,kind)
        if kind=='in':
            assert not full,(begin,kind,'overwrite')
            full=True
        else:
            assert full,(begin,kind,'empty read')
            full=False
        end=finish
    return full

def cpu_no_overlap(operations):
    seq=sorted(operations)
    assert all(seq[i-1][1]<=seq[i][0] for i in range(1,len(seq)))

cases=[
 (False,[(0,5,'in'),(5,6,'out'),(6,11,'in'),(11,12,'out'),(12,17,'in'),(17,18,'out')]),
 (False,[(0,3,'in'),(5,6,'out'),(6,9,'in'),(11,12,'out'),(12,15,'in'),(17,18,'out')]),
 (True,[(0,1,'out'),(5,10,'in'),(10,11,'out')]),
 (False,[(0,5,'in'),(5,6,'out'),(10,15,'in')]),
 (True,[(0,1,'out'),(2,4,'in'),(8,9,'out'),(9,11,'in')]),
 (False,[(0,2,'in'),(4,5,'out'),(5,7,'in'),(12,13,'out'),(13,15,'in')]),
]
for initial,ops in cases:buffer_transitions(initial,ops)
cpu_no_overlap([(0,3),(5,6),(6,9),(11,12),(12,15),(17,18)])
cpu_no_overlap([(0,5),(5,6),(6,11),(11,12),(12,17),(17,18)])
cpu_no_overlap([(0,1),(1,4),(5,6),(6,9),(10,11),(11,14)])
cpu_no_overlap([(0,1),(1,4),(4,5),(5,8),(8,9),(9,12),(12,13),(13,16)])

# Given fixed positions, recompute each total without reading the drawing code.
paths={
 'FCFS':[100,55,58,39,18,90,160,150,38,184],
 'SSTF':[100,90,58,55,39,38,18,150,160,184],
 'SCAN':[100,150,160,184,200,90,58,55,39,38,18],
 'LOOK':[100,150,160,184,90,58,55,39,38,18],
 'C-SCAN':[100,150,160,184,200,0,18,38,39,55,58,90],
 'C-LOOK':[100,150,160,184,18,38,39,55,58,90],
}
totals={name:sum(abs(a-b) for a,b in zip(path,path[1:])) for name,path in paths.items()}
assert list(totals.values())==[498,248,282,250,390,322],totals
result={'buffer_scenarios':4,'buffer_checks':'state transitions, exclusive use and CPU non-overlap passed',
        'disk_totals':totals,'limitations':'Illustrative timelines; OS05 printed content still needs PDF visual review.'}
Path(__file__).with_name('course_diagram_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
