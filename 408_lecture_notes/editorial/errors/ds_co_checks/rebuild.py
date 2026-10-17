"""在源文件完全相同的前提下重建已人工审读的台账；源改变则停止，不能沿用视觉核验。"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
baseline=json.loads((R/'audit_baseline.json').read_text())
for x in baseline['files']:
 p=Path(x['path']);h=hashlib.sha256()
 if not p.exists():raise SystemExit('缺少既有原文件：'+str(p))
 with p.open('rb') as f:
  while True:
   b=f.read(4*1024*1024)
   if not b:break
   h.update(b)
 if h.hexdigest()!=x['sha256']:raise SystemExit('源文件已经变化，需要重新读取/目验，未沿用旧核验：'+str(p))
for filename in ['extract.py','render_extra.py','classify.py','link_coverage.py','recalculate.py','finalize.py']:
 subprocess.run([sys.executable,str(R/filename)],check=True)
