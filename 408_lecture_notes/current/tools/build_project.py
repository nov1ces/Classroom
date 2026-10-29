#!/usr/bin/env python3
"""Rebuild notes, solutions, and links. Final layout review is a separate gated stage."""
import argparse,json,subprocess,sys
from pathlib import Path
from build_notes import ROOT,read,collect_assets,sha

def run(*args):subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--refresh-sources',action='store_true');ap.add_argument('--jobs',default=3,type=int);a=ap.parse_args()
 run('tools/validate_content.py');run('tools/link_sources.py')
 if a.refresh_sources:run('tools/prepare_solutions.py')
 idx=read(ROOT/'sources/example_index.json');known={e['id']:e for e in idx['examples']}
 for ch in (ROOT/'chapters').iterdir():
  examples=read(ch/'examples.json')
  for e in examples:
   if e['id'] not in known or any(known[e['id']][k]!=e[k] for k in ['question','answer','solution']):raise SystemExit('Source index must be refreshed for '+e['id'])
  collect_assets(ch,'\n\n'.join(e['solution'] for e in examples))
 for e in idx['examples']:
  for crop in e['crops']:
   if sha(ROOT/crop['png'])!=crop['png_sha256']:raise SystemExit('Screenshot changed: '+crop['png'])
 run('tools/build_all.py','--jobs',str(a.jobs));run('tools/build_solutions.py');run('tools/release.py','links')
 if (ROOT/'sources/annotations/input.json').exists():run('tools/import_annotations.py','--refresh-baseline')
 run('tools/release.py','audit');run('tools/audit_pdf_code.py')
 print('Build complete. Push to GitHub before running final_qa.py.')
if __name__=='__main__':main()
