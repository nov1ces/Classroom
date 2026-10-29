"""Check the Wangdao five-frame simple-Clock example against the printed table."""
import hashlib
import json
from pathlib import Path

SEQ = [1, 3, 4, 2, 5, 6, 3, 4, 7]
EXPECTED = [
    ([1, None, None, None, None], [1, None, None, None, None], 2, True, None),
    ([1, 3, None, None, None], [1, 1, None, None, None], 3, True, None),
    ([1, 3, 4, None, None], [1, 1, 1, None, None], 4, True, None),
    ([1, 3, 4, 2, None], [1, 1, 1, 1, None], 5, True, None),
    ([1, 3, 4, 2, 5], [1, 1, 1, 1, 1], 1, True, None),
    ([6, 3, 4, 2, 5], [1, 0, 0, 0, 0], 2, True, 1),
    ([6, 3, 4, 2, 5], [1, 1, 0, 0, 0], 2, False, None),
    ([6, 3, 4, 2, 5], [1, 1, 1, 0, 0], 2, False, None),
    ([6, 3, 4, 7, 5], [1, 0, 0, 1, 0], 5, True, 2),
]

def clock_trace(sequence, frame_count=5):
    frames = [None] * frame_count
    access = [None] * frame_count
    hand = 0
    rows = []
    for page in sequence:
        victim = None
        fault = page not in frames
        if not fault:
            access[frames.index(page)] = 1
        else:
            while frames[hand] is not None and access[hand] == 1:
                access[hand] = 0
                hand = (hand + 1) % frame_count
            victim = frames[hand]
            frames[hand] = page
            access[hand] = 1
            hand = (hand + 1) % frame_count
        rows.append((frames.copy(), access.copy(), hand + 1, fault, victim))
    return rows

if __name__ == '__main__':
    rows = clock_trace(SEQ)
    assert rows == EXPECTED, (rows, EXPECTED)
    assert sum(row[3] for row in rows) == 7
    assert sum(row[4] is not None for row in rows) == 2
    source = Path('/workspace/Classroom/03_操作系统/【课件】操作系统基础考点讲解/第三章 内存管理/3.2.4 页面置换算法.pdf')
    digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
    output = {'source': str(source), 'source_file_page': 8, 'source_sha256': digest,
              'source_visual_check': 'Checked source page 8; animation layers overlap in the PDF. The sequence, five frames and Clock rules are visible.',
              'assumptions': ['Five initially empty frames; hand starts at frame 1.',
                              'A loaded page has access bit 1; hand advances after insertion.',
                              'A hit sets access bit to 1 and leaves hand in place.'],
              'sequence': SEQ, 'faults': 7, 'replacements': 2,
              'rows': [{'page': page, 'frames': frames, 'access': access,
                        'next_frame': hand, 'fault': fault, 'victim': victim}
                       for page, (frames, access, hand, fault, victim) in zip(SEQ, rows)],
              'result': 'all nine printed table rows agree with independently executed simulation'}
    Path(__file__).with_suffix('.json').write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print('PASS: all 9 Clock rows; 7 faults and 2 replacements')
