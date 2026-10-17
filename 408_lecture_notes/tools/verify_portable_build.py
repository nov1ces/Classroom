#!/usr/bin/env python3
"""Run the complete offline build in a separate directory and compare all pages.

The production files and their human visual approvals are never rebuilt here.
The copy uses the same inclusion rule as the release ZIP, excluding build caches.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path
import fitz
from bundle_release import NAMES, included_in_release

ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--build-only',action='store_true',help='Build the isolated copy; compare after production lock')
    parser.add_argument('--existing-copy',type=Path,help='Compare a copy previously built by this program')
    args=parser.parse_args()
    if args.existing_copy:
        target=args.existing_copy.resolve()
        invocation=json.loads((target.parent/'invocation.json').read_text())
        if invocation['returncode']!=0:raise RuntimeError('The isolated build did not succeed')
        start=datetime.fromisoformat(invocation['started_at']);files=invocation['source_files']
    else:
        target=Path(tempfile.mkdtemp(prefix='408-portable-'))/'408_lecture_notes'
        target.mkdir()
        files=0
        for p in ROOT.rglob('*'):
            if p.is_file() and included_in_release(p.relative_to(ROOT)):
                q=target/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(p,q);files+=1
        start=datetime.now(timezone.utc)
        print(json.dumps({'copy':str(target),'source_files':files},ensure_ascii=False),flush=True)
        with (target.parent/'build.log').open('w') as f:
            completed=subprocess.run(['bash','build.sh','--no-render'],cwd=target,stdout=f,stderr=subprocess.STDOUT)
        invocation=dict(started_at=start.isoformat(),source_files=files,returncode=completed.returncode)
        (target.parent/'invocation.json').write_text(json.dumps(invocation,indent=2)+'\n')
        if completed.returncode:
            raise RuntimeError(f'Portable build failed; inspect {target.parent / "build.log"}')
    log=target.parent/'build.log'
    if args.build_only:
        print(json.dumps({'status':'BUILT; page comparison pending','copy':str(target)},ensure_ascii=False));return
    books=[]
    for sub,title in NAMES.items():
        mf=json.loads((target/f'build/{sub}/build_manifest.json').read_text())
        for source in mf['sources']:
            if source['sha256']!=digest(ROOT/source['path']):
                raise AssertionError('Manuscript changed since isolated build: '+source['path'])
        a=ROOT/'dist'/f'{title}_讲义.pdf';b=target/'dist'/a.name
        old=fitz.open(a);new=fitz.open(b)
        if len(old)!=len(new):raise AssertionError(f'{sub}: page count changed')
        changed=[]
        for i,(op,np) in enumerate(zip(old,new),1):
            x=op.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
            y=np.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
            if (x.width,x.height,x.samples)!=(y.width,y.height,y.samples):changed.append(i)
        results=json.loads((target/f'editorial/full/{sub}/results.json').read_text())
        if results['status']!='PASS':raise AssertionError(f'{sub}: calculation verification failed')
        if changed:raise AssertionError(f'{sub}: rebuilt pixels differ on pages {changed}')
        books.append(dict(subject=sub,pages=len(new),pixel_identical_pages=len(new),
            production_sha256=digest(a),rebuilt_sha256=digest(b),calculation_status=results['status'],
            checks=len(results['checks']) if isinstance(results.get('checks'),list) else results.get('checks')))
        print(json.dumps(books[-1],ensure_ascii=False),flush=True)
    report=dict(status='PASS',started_at=start.isoformat(),finished_at=datetime.now(timezone.utc).isoformat(),
        source_root=str(ROOT),independent_directory=str(target),source_files=files,
        command='bash build.sh --no-render',network_needed=False,
        source_materials_needed=False,cache_included=False,books=books,
        scope='实际执行全套模型复算、65幅图生成与四科三遍排版，逐页比较重建PDF与交付PDF的渲染像素；不替代人工知识/视觉审查。',
        log_sha256=digest(log))
    out=ROOT/'editorial/full/portable_build_verification.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    shutil.copyfile(log,out.with_suffix('.log'))
    print(json.dumps(dict(status='PASS',total_pages=sum(b['pages'] for b in books),report=str(out.relative_to(ROOT))),ensure_ascii=False))

if __name__=='__main__':main()
