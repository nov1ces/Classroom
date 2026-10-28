from pathlib import Path
import html,subprocess
root=Path(__file__).resolve().parents[1]
out=root/'figures';out.mkdir(exist_ok=True)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="980" height="640" viewBox="0 0 980 640">','<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#466c82"/></marker></defs>','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" font-size="23" fill="#20343f">']
def text(x,y,t,size=23):svg.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(t)}</text>')
def box(x,y,w,h,t,fill='#DDEFF5'):
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#7c9aa9"/>');text(x+16,y+h/2+8,t)
text(25,38,'无符号恢复余数除法：0000 1111 ÷ 0010（15 ÷ 2）',26)
box(25,64,405,56,'初态 R=0000，Q=1111')
box(542,64,410,56,'除数 Y=0010；计数 Cn=4')
text(25,160,'每轮：RQ整体左移 → 试减Y → 结果非负保留；负则恢复R → 写商位')
rows=[('第1轮','0001','1110','−1，恢复','0001','1110'),('第2轮','0011','1100','1，保留','0001','1101'),('第3轮','0011','1010','1，保留','0001','1011'),('第4轮','0011','0110','1，保留','0001','0111')]
for i,(n,r,q,trial,rf,qf) in enumerate(rows):
 y=190+i*82
 text(25,y+30,n)
 box(130,y,275,56,f'移位后 R={r} Q={q}')
 box(441,y,180,56,trial,'#FFF1D3')
 box(657,y,295,56,f'轮末 R={rf} Q={qf}','#DFEFE6')
 svg.append(f'<path d="M405 {y+28} H435 M621 {y+28} H651" fill="none" stroke="#466c82" stroke-width="2" marker-end="url(#arrow)"/>')
text(25,565,'终态：R=0001（余数1），Q=0111（商7），Cn=0')
text(25,607,'回代：15 = 7 × 2 + 1，且 0 ≤ 1 < 2')
svg.append('</g></svg>');p=out/'CO02_restoring_division.svg';p.write_text('\n'.join(svg))
for ext in ['png','pdf']:
 args=['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(p.with_suffix('.'+ext))]
 if ext=='png':args.append('--export-dpi=160')
 else:args.append('--export-text-to-path')
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
