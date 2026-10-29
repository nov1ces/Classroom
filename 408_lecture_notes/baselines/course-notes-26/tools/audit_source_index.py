#!/usr/bin/env python3
"""Check source-index/file consistency; does not certify note content or source coverage."""
from pathlib import Path
import collections,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'sources/source_inventory.json').read_text())
pages=json.loads((ROOT/'sources/page_inventory.json').read_text())
issues=[];paths=[x['path'] for x in source['files']]
if len(paths)!=len(set(paths)):issues.append('duplicate source path')
page_map={x['path']:x for x in pages['files']}
for f in source['files']:
 p=ROOT/f['extracted_text']
 if not p.exists():issues.append('missing extraction: '+f['path']);continue
 text=p.read_text()
 found=[int(x) for x in re.findall(r'^===== 文件页 (\d+) / \d+ =====$',text,re.M)]
 if found!=list(range(1,f['pdf_pages']+1)):issues.append('page marker mismatch: '+f['path'])
 if f['path'] not in page_map or len(page_map[f['path']]['pages'])!=f['pdf_pages']:issues.append('page inventory mismatch: '+f['path'])
 if f['extraction_status']!='all_pages_extracted':issues.append('incomplete extraction status: '+f['path'])
summary=collections.defaultdict(lambda:collections.Counter())
for f in source['files']:
 summary[f['kind']]['files']+=1;summary[f['kind']]['pages']+=f['pdf_pages']
blog=json.loads((ROOT/'sources/blog_index.json').read_text())
if len(blog['chapters'])!=26:issues.append('blog chapter count mismatch')
if len([x for x in blog['chapters'] if x['url']])!=25:issues.append('blog URL count mismatch')
report={'index_consistency':'pass' if not issues else 'fail','issues':issues,'totals':dict(summary),'sources':len(source['files']),'blog_entries':len(blog['chapters']),'scope':'all source extraction files and file-page records checked; content, figures and note coverage require separate verification'}
(ROOT/'sources/source_index_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(issues))
