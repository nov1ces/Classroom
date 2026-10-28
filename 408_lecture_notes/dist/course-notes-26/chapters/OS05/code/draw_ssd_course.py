from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]/'figures';root.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="540" viewBox="0 0 920 540">', '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="#446577"/></marker></defs>', '<rect width="920" height="540" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#253c48" font-size="16">','<text x="460" y="28" text-anchor="middle" font-size="20" font-weight="bold">课件示例：SSD闪存组织</text>','<rect x="130" y="45" width="660" height="36" rx="4" fill="#e5eef2" stroke="#7b9ba8"/><text x="460" y="69" text-anchor="middle">I/O总线：主机给出待读写的逻辑块号</text>','<path d="M460 81V96" stroke="#446577" stroke-width="2" marker-end="url(#a)"/>','<rect x="270" y="101" width="380" height="38" rx="4" fill="#e2f0e7" stroke="#7b9ba8"/><text x="460" y="126" text-anchor="middle">闪存翻译层：逻辑块号映射为物理地址</text>','<path d="M460 139V160" stroke="#446577" stroke-width="2" marker-end="url(#a)"/>','<text x="460" y="179" text-anchor="middle">四个闪存芯片组成的芯片组</text>']
for col in range(4):
 x=20+col*225;s += [f'<rect x="{x}" y="192" width="210" height="285" rx="4" fill="#f4f7f9" stroke="#8aa1aa"/>',f'<text x="{x+105}" y="218" text-anchor="middle" font-weight="bold">闪存芯片{col}</text>']
 for j,b in enumerate(['0','1','2','m']):
  y=229+j*55;s += [f'<rect x="{x+8}" y="{y}" width="194" height="45" fill="white" stroke="#a2b5bb"/>',f'<text x="{x+14}" y="{y+28}">块{b}</text>']
  for k,label in enumerate(['页0','页1','…','页n']):
   px=x+55+k*35;s += [f'<rect x="{px}" y="{y+8}" width="35" height="29" fill="#e3eff3" stroke="#a2b5bb"/>',f'<text x="{px+17.5}" y="{y+28}" font-size="13" text-anchor="middle">{label}</text>']
s += ['<text x="460" y="510" text-anchor="middle">课件示意：块约16–512 KB；页约512 B–4 KB（具体取值依设备而异）</text>','</g></svg>']
p=root/'OS_ssd_course.svg';p.write_text('\n'.join(s))
for fmt in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+fmt,'--export-filename='+str(p.with_suffix('.'+fmt))]
 if fmt=='pdf':args.insert(2,'--export-text-to-path')
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
