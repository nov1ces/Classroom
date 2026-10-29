#!/usr/bin/env python3
"""Map baseline lecture sources onto the new, explicitly authored knowledge targets."""
from pathlib import Path
import json,re,shutil
from build_notes import ROOT,BASE,read,jwrite
errors=[];files=[]
for ch in sorted((ROOT/'chapters').iterdir()):
 if not (ch/'sources/coverage.json').exists():continue
 mappings=read(ch/'sources/coverage.json')
 if isinstance(mappings,dict):mappings=mappings.get('mappings',mappings.get('coverage',[]))
 remap={m['baseline_anchor']:m['targets'] for m in mappings}
 actual=set(re.findall(r'\{#([^}]+)\}',(ch/'content.md').read_text()))|{e['id'] for e in read(ch/'examples.json')}
 source=read(BASE/'chapters'/ch.name/'sources/course_coverage.json');entries=[]
 for f in source['lecture_files']:
  targets=[]
  for anchor in f['targets']:
   anchor=anchor.lstrip('#')
   matched=remap.get(anchor,[anchor] if anchor in actual else [])
   targets.extend(matched)
  targets=list(dict.fromkeys(targets))
  if not targets or any(t not in actual for t in targets):errors.append({'chapter':ch.name,'source':f['path'],'targets':f['targets']})
  entries.append({'path':f['path'],'file_pages':f.get('pages',[]),'targets':targets,'baseline_targets':f['targets'],'baseline_review_scope':f.get('verification',''),'current_review':'author synthesis and chapter-specific content review; source limitations remain in baseline records'})
 files.extend({'chapter':ch.name,**e} for e in entries)
 jwrite(ch/'sources/course_coverage.json',{'chapter':ch.name,'lecture_files':entries,'scope':'Knowledge-group source mapping; does not assert every animation frame or tiny figure label was independently reviewed.'})
for name in ['source_inventory.json','textbook_inventory.json','blog_index.json']:
 shutil.copy2(BASE/'sources'/name,ROOT/'sources'/name)
expected={r['path'] for r in read(BASE/'sources/source_inventory.json')['files'] if r['kind']=='lecture'}
mapped={r['path'] for r in files}
report={'expected_lectures':len(expected),'mapped_lectures':len(mapped),'missing':sorted(expected-mapped),'errors':errors,'records':files}
jwrite(ROOT/'sources/source_coverage.json',report)
print(json.dumps({'expected':len(expected),'mapped':len(mapped),'missing':len(expected-mapped),'errors':errors},ensure_ascii=False))
if errors or expected!=mapped:raise SystemExit(1)
