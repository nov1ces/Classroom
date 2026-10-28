#!/usr/bin/env python3
"""Build chapters in isolated subprocesses, then assemble all reading editions."""
from pathlib import Path
import argparse, concurrent.futures, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def build(ident):
    log = ROOT / 'build-logs' / (ident + '.txt')
    log.parent.mkdir(exist_ok=True)
    with log.open('w') as stream:
        process = subprocess.run([sys.executable, str(ROOT / 'tools/build_notes.py'), ident],
                                 cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    return ident, process.returncode, str(log)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('chapters', nargs='*')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    identifiers = args.chapters or [p.name for p in sorted((ROOT / 'chapters').iterdir()) if p.is_dir()]
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        for ident, code, log in executor.map(build, identifiers):
            print(f'{ident}: {"built" if code == 0 else "FAILED"}; {log}', flush=True)
            if code:
                failures.append(ident)
    if failures:
        raise SystemExit('Failed chapters: ' + ', '.join(failures))
    if not args.chapters:
        subprocess.run([sys.executable, 'tools/release.py', 'assemble'], cwd=ROOT, check=True)
        subprocess.run([sys.executable, 'tools/release.py', 'audit'], cwd=ROOT, check=True)
