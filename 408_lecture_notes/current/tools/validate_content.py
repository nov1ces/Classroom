#!/usr/bin/env python3
"""Check chapter coverage, example registry consistency, and editorial constraints."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'baselines/course-notes-26'
errors=[];warnings=[];records=[];ids=set()
for ch in sorted((ROOT/'chapters').iterdir()):
 required=['content.md','sidebars.json','examples.json','sources/coverage.json']
 if any(not (ch/f).exists() for f in required):errors.append(f'{ch.name}: author files incomplete');continue
 text=(ch/'content.md').read_text(); ex=json.loads((ch/'examples.json').read_text()); coverage=json.loads((ch/'sources/coverage.json').read_text())
 if isinstance(coverage,dict):coverage=coverage.get('mappings',coverage.get('coverage',[]))
 old=set(re.findall(r'^#{1,6} .+?\{#([^}]+)\}',(BASE/'chapters'/ch.name/'content.md').read_text(),re.M))
 covered={r['baseline_anchor'] for r in coverage};missing=old-covered
 if missing:errors.append(f'{ch.name}: unmapped baseline anchors {sorted(missing)}')
 anchors=set(re.findall(r'\{#([^}]+)\}',text))|{e['id'] for e in ex}
 for r in coverage:
  if not r.get('targets') or any(t not in anchors for t in r.get('targets',[])):errors.append(f'{ch.name}: invalid coverage target {r}')
 placeholders=re.findall(r'\{\{example:([^}]+)\}\}',text)
 if len(placeholders)!=len(set(placeholders)) or set(placeholders)!={e['id'] for e in ex}:errors.append(f'{ch.name}: example placement mismatch')
 for i,e in enumerate(ex,1):
  if e['id'] in ids:errors.append('Duplicate '+e['id'])
  ids.add(e['id'])
  if e['number']!=f'{int(ch.name[2:])}-{i}':errors.append('Unexpected display number '+e['id'])
  if not all(e.get(k) for k in ['question','answer','solution']):errors.append('Incomplete '+e['id'])
 for s in json.loads((ch/'sidebars.json').read_text()):
  if s['anchor'] not in anchors:errors.append(f'{ch.name}: unknown sidebar anchor {s["anchor"]}')
  if s.get('kind'):errors.append(f'{ch.name}: redundant sidebar kind')
 prose=re.sub(r'```.*?```','',text,flags=re.S)
 for pattern in ['不是[^。\\n]*而是','并非[^。\\n]*而是','要[^。\\n]*而不是','值得注意的是','从某种意义上说','这充分说明了','≺']:
  if re.search(pattern,prose):errors.append(f'{ch.name}: editorial pattern {pattern}')
 for para in prose.split('\n\n'):
  if len(para)>230 and not para.startswith(('|','!','#','{{','-','1.')):warnings.append({'chapter':ch.name,'long_paragraph':para[:100],'characters':len(para)})
 records.append({'id':ch.name,'characters':len(text),'baseline_characters':len((BASE/'chapters'/ch.name/'content.md').read_text()),'examples':len(ex),'covered_anchors':len(covered)})
report={'errors':errors,'warnings':warnings,'chapters':records,'examples':len(ids)}
(ROOT/'sources/content_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'chapters':len(records),'examples':len(ids),'errors':errors,'warnings':len(warnings)},ensure_ascii=False))
if errors:sys.exit(1)
