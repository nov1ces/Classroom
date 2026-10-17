#!/usr/bin/env python3
"""Check the user-requested source-marker move against the saved manuscripts.

This records only a comparison of changed headings, never a new full-text read.
A previous actual technical read must already cover the unchanged body.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
MARKER=re.compile(r'(【\d{4}】(?:\s*改编(?:（[^）]*）)?)?|〖[^〗]+〗)')
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def body(s):
    out=[]
    for x in s.splitlines():
        if x.startswith('#'):continue
        m=MARKER.match(x)
        if m:x=x[m.end():].lstrip(' \u3000')
        if x.strip():out.append(x)
    return out
def headers(s):
    return [re.sub(r'\s+','',MARKER.sub('',x)) for x in s.splitlines() if x.startswith('#')]

def main():
    p=ROOT/'editorial/full/review/chinese_layout_revision.json'
    report=json.loads(p.read_text())
    lp=ROOT/'editorial/full/review/read_log.json';log=json.loads(lp.read_text())
    reads={(x['path'],x['sha256']) for x in log};pending=[]
    snapshots=json.loads((ROOT/'editorial/full/review/final_snapshot_index.json').read_text())
    for item in report['files']:
        old=(ROOT/item['backup']).read_text();new=(ROOT/item['path']).read_text()
        checks=dict(body_text_identical=body(old)==body(new),
            heading_wording_and_anchors_identical=headers(old)==headers(new),
            source_markers_identical=Counter(MARKER.findall(old))==Counter(MARKER.findall(new)),
            saved_before_fingerprint_valid=digest(old)==item['before_sha256'],
            current_fingerprint_valid=digest(new)==item['after_sha256'])
        if not all(checks.values()):raise AssertionError((item['path'],checks))
        item['comparison_checks']=checks
        final=(item['path'],item['after_sha256'])
        previous=(item['path'],item['before_sha256'])
        if final not in reads:
            if previous not in reads:
                for snapshot in snapshots:
                    candidate=(snapshot['path'],snapshot['sha256'])
                    if snapshot['path']!=item['path'] or candidate not in reads:continue
                    text=(ROOT/snapshot['snapshot']).read_text()
                    if digest(text)!=snapshot['sha256']:raise AssertionError('Snapshot fingerprint changed')
                    if (body(text)==body(new) and headers(text)==headers(new)
                        and Counter(MARKER.findall(text))==Counter(MARKER.findall(new))):
                        previous=candidate
                        item['actual_read_baseline']=snapshot
                        break
            if previous not in reads:
                pending.append(item['path']);continue
            log.append(dict(path=item['path'],sha256=item['after_sha256'],characters=len(new),
                read_lines=[i for i,x in enumerate(new.splitlines(),1) if x.startswith('#')],
                read_at=datetime.now(timezone.utc).isoformat(),reviewer='root',
                scope='对照已实际审读的前版，逐项检查题源移至题干首行；忽略题源位置后普通正文逐行不变、标题措辞与锚点不变、题源标记多重集相同。不是重新全文知识审读。',
                inherited_actual_read_sha256=previous[1],
                evidence='editorial/full/review/chinese_layout_revision.json',
                not_claimed=['新一轮全部题源核验','PDF视觉通过']))
            reads.add(final)
    report['body_changes']=0;report['comparison_status']='PASS'
    report['actual_read_provenance_pending']=pending
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lp.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(comparison='PASS',files=len(report['files']),body_changes=0,
        actual_read_provenance_pending=pending),ensure_ascii=False))

if __name__=='__main__':main()
