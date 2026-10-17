#!/usr/bin/env python3
"""OS-only content/provenance guards; never reads or builds lecture PDFs."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[2];B=R/'editorial/revision3/baseline';O=R/'editorial/full/OS';checks=[]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok,detail=None):
 assert ok,(name,detail)
 checks.append({'check':name,'status':'PASS','detail':detail})
d=load(O/'chapter_records.json');old=load(B/'editorial/full/OS/chapter_records.json')
check('original_133_error_records_unchanged',d['errors']==old['errors'] and len(d['errors'])==133)
a={e['id']:e for c in old['chapters'] for e in c['examples']};z={e['id']:e for c in d['chapters'] for e in c['examples']}
check('all_38_old_example_records_unchanged',all(z[k]==v for k,v in a.items()),len(a))
check('seven_new_complete_examples',len(z)-len(a)==7)
check('all_21_new_subquestions_registered',sum(e.get('subquestion_count',0) for k,e in z.items() if k not in a)==21)
locked=load(R/'editorial/revision3/OS_locked_manuscript_sha256.json')['sha256']
check('six_locked_manuscript_hashes_match',all(sha(R/p)==v for p,v in locked.items()),locked)
p=Path('manuscript/OS/03_同步互斥与信号量.md')
check('sync_sample_unmodified',(R/p).read_bytes()==(B/p).read_bytes())
check('manuscript_counts_hashes_and_characters_match_records',all(c['question_count']==len(c['examples']) and c['sha256']==sha(R/c['manuscript']) and c['characters']==len((R/c['manuscript']).read_text()) for c in d['chapters']))
results=load(O/'results.json');old_results=load(B/'editorial/full/OS/results.json')
check('first_37_calculation_results_preserved',results['checks'][:37]==old_results['checks'])
check('66_calculations_all_pass',results['count']==66 and all(c['status']=='PASS' for c in results['checks']))
check('revision3_result_copy_matches',(O/'results.json').read_bytes()==(R/'editorial/revision3/OS_results.json').read_bytes())
sel=load(R/'editorial/revision3/OS_selection_destinations.json')
check('all_new_source_evidence_files_exist',all((R/f).is_file() for s in sel['selected'] for f in s['source']['evidence']))
check('all_new_community_volume_paths_exist',all((R/s['source']['exam_rebuild_pdf']).is_file() for s in sel['selected']))
for c in d['chapters']:
 if c['chapter']==3:continue
 text=(R/c['manuscript']).read_text()
 check(f'chapter_{c["chapter"]}_old_numbered_anchors_retained',all(f'{{#{e["anchor"]}}}' in text for e in old['chapters'][c['chapter']-1]['examples']))
for s in sel['selected']:
 text=(R/s['manuscript']).read_text().split(f'{{#{s["anchor"]}}}',1)[1]
 first=next(line for line in text.splitlines() if line.strip())
 check(f'{s["id"]}_year_and_question_share_first_line',bool(re.match(r'^【\d{4}】\s+\S',first)))
fig=load(O/'figures.json')
check('new_directory_figure_svg_png_present',all((R/'figures'/('OS_file_directory_2022.'+e)).is_file() for e in ['svg','png']))
if (B/'editorial/full/OS/figures.json').exists():
 old_fig=load(B/'editorial/full/OS/figures.json');byid={f['id']:f for f in fig}
 check('old_11_figure_records_preserved',all(byid[f['id']]==f for f in old_fig),len(old_fig))
with tempfile.TemporaryDirectory(prefix='os-r3-local-verification-') as td:
 target=Path(td)/'editorial/full/OS';target.mkdir(parents=True)
 for name in ['verification.py','model_data.json']:shutil.copyfile(O/name,target/name)
 run=subprocess.run(['python',str(target/'verification.py')],cwd=td,capture_output=True,text=True,check=True)
 isolated=load(target/'results.json')
 check('verification_rebuilds_from_only_local_data_and_stdlib',isolated['count']==66 and isolated['checks']==results['checks'],run.stdout.strip())
report={'status':'PASS','scope':'OS content/provenance integrity only; no lecture PDF generated or opened','checks':checks,'count':len(checks)}
(R/'editorial/revision3/OS_integrity_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','integrity_checks':len(checks),'calculation_checks':66,'new_examples':7,'unchanged_personal_errors':133},ensure_ascii=False))
