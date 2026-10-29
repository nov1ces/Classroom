#!/usr/bin/env python3
"""One-time, lossless organization of the 2026-10-28 notes workspace."""
from pathlib import Path
import hashlib, json, shutil, os

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / '408_lecture_notes'
ARCHIVE = NOTES / 'archive'
RECORDS = ARCHIVE / 'project-records-2026-10-28'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest = NOTES/'maintenance/archive_manifest_2026-10-28.json'
    if manifest.exists():
        raise SystemExit('Already organized; consult the manifest before changing paths.')
    RECORDS.mkdir(parents=True, exist_ok=True)
    for src, name in [(ROOT/'README.md','repository-README.md'), (ROOT/'NOTES_PROJECT.md','NOTES_PROJECT.md'), (NOTES/'README.md','lecture-notes-README.md')]:
        shutil.copy2(src, RECORDS/name)
    moves = [
        ('408_lecture_notes/dist/course-notes-26','408_lecture_notes/baselines/course-notes-26'),
        ('408_lecture_notes/dist/mindmap-26','408_lecture_notes/archive/mindmap-26'),
        ('408_lecture_notes/dist/basic-foundations','408_lecture_notes/archive/basic-foundations'),
        ('408_lecture_notes/dist/final','408_lecture_notes/archive/legacy-29/dist/final'),
        ('408_lecture_notes/dist/408四科26章_完整笔记_源码素材.zip','408_lecture_notes/archive/packages/408四科26章_完整笔记_源码素材.zip'),
    ]
    for name in ['PROJECT_STATE.json','build_final.sh','requirements.txt','editorial','figures','manuscript','tools']:
        moves.append(('408_lecture_notes/'+name,'408_lecture_notes/archive/legacy-29/'+name))
    records=[]
    for old,new in moves:
        src,dst=ROOT/old,ROOT/new
        assert src.exists() and not src.is_symlink(),src
        assert not dst.exists(),dst
        paths=[src] if src.is_file() else sorted(p for p in src.rglob('*') if p.is_file() and not p.is_symlink())
        entries=[{'relative':str(p.relative_to(src)) if src.is_dir() else '.', 'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(src),str(dst))
        for e in entries:
            p=dst if e['relative']=='.' else dst/e['relative']
            assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],p
        src.symlink_to(os.path.relpath(dst,src.parent), target_is_directory=dst.is_dir())
        records.append({'old':old,'new':new,'compatibility_symlink':True,'files':entries})
    manifest.write_text(json.dumps({'date':'2026-10-28','timezone':'Asia/Shanghai','policy':'move whole version bundles; retain compatibility symlinks; verify every regular file before and after; no deletion','moves':records},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'moved_groups':len(records),'verified_files':sum(len(r['files']) for r in records)},ensure_ascii=False))

if __name__=='__main__': main()
