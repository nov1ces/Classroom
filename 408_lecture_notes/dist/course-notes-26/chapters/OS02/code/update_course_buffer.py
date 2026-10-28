from pathlib import Path
import re,subprocess
out=Path(__file__).resolve().parent.parent/'figures';p=out/'F04_buffer_permissions.svg';s=p.read_text()
start=s.index('<rect x="350" y="111"');end=s.index('<text x="500" y="216"',start)
a=[]
for i in range(5):
 x=350+62*i;a.append(f'<rect x="{x}" y="111" width="55" height="65" rx="4" fill="white" stroke="#243746" stroke-width="1.6"/>')
 a.append(f'<text x="{x+27}" y="151" text-anchor="middle" font-size="18" fill="#243746" font-weight="normal">槽{i}</text>')
p.write_text(s[:start]+'\n'.join(a)+'\n'+s[end:])
for ext in ['pdf','png']:
 args=['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/('F04_buffer_permissions.'+ext))]
 if ext=='pdf':args.insert(2,'--export-text-to-path')
 else:args.append('--export-dpi=180')
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
