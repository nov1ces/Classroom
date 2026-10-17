#!/usr/bin/env python3
"""Repeatable offline build. Source verification is preserved in the ledgers."""
from __future__ import annotations
import argparse, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ['DS','CO','OS','CN']

def call(command):
    subprocess.run(command,cwd=ROOT,check=True)

def subject_checks(sub):
    verify = ROOT/f'editorial/full/{sub}/verification.py'
    draw = ROOT/f'tools/draw_{sub.lower()}_figures.py'
    if not verify.exists() or not draw.exists():
        raise FileNotFoundError(f'{sub}: missing verification or figure build script')
    call(['python',str(verify)])
    call(['python',str(draw)])

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--subjects',nargs='+',choices=SUBJECTS,default=SUBJECTS)
    p.add_argument('--typeset-only',action='store_true',help='Keep checked figures and calculation outputs')
    p.add_argument('--no-render',action='store_true',help='Skip page PNGs; does not confer visual approval')
    args=p.parse_args()
    if not args.typeset_only:
        if 'OS' in args.subjects:
            call(['python','tools/verify_models.py'])
            call(['python','tools/draw_figures.py'])
            call(['python','editorial/sources/os_exam_checks/verify_os_examples.py'])
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(subject_checks,s) for s in args.subjects]
            for future in futures: future.result()
    call(['python','tools/build_books.py','--subjects',*args.subjects])
    call(['python','editorial/full/review/review_tools.py'])
    if set(args.subjects)==set(SUBJECTS):
        call(['python','tools/sync_full_editorial.py'])
        call(['python','tools/index_figures.py'])
        call(['python','tools/index_chapters.py'])
    if not args.no_render:
        call(['python','tools/audit_books.py','--subjects',*args.subjects])

if __name__=='__main__': main()
