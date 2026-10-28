from pathlib import Path
import html, subprocess
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640">','<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="4" orient="auto"><path d="M0 0 L9 4 L0 8" fill="none" stroke="#527488"/></marker></defs>','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC,sans-serif" fill="#213946" font-size="23">']
def text(x,y,t,sz=23):s.append(f'<text x="{x}" y="{y}" font-size="{sz}">{html.escape(t)}</text>')
def rect(x,y,w,h,t,fill='#e5f0f5'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#7899aa"/>');text(x+10,y+32,t,20)
def arrow(x1,y1,x2,y2):s.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#527488" stroke-width="2" marker-end="url(#arr)"/>')
text(30,40,'记录的组织方式：用户角度（课件中的学生记录）',27)
text(35,90,'逻辑连续：',22)
for i in range(6):rect(180+i*135,57,130,50,f'学生 {i}')
text(35,170,'记录链式：',22)
for i in range(6):
 t={0:'学生 0',2:'学生 2',3:'学生 1',5:'学生 3'}.get(i,'未展开')
 rect(180+i*135,135,130,50,t,'#edf3ec' if t!='未展开' else '#fafafa');text(232+i*135,130,str(i),18)
for start,end,height in [(0,3,241),(3,2,265),(2,5,289)]:
 x1=245+135*start;x2=245+135*end
 s.append(f'<path d="M{x1} 186 V{height} H{x2} V190" fill="none" stroke="#527488" stroke-width="2" marker-end="url(#arr)"/>')
text(35,323,'下层磁盘块的分配方式由文件系统选择，与上层记录组织相互独立。',22)
text(35,375,'逻辑块：',22)
for i in range(6):rect(180+i*135,342,130,48,f'#{i}')
text(35,458,'连续分配：',22)
for i in range(6):rect(180+i*135,425,130,48,f'#{i}','#edf3ec')
text(35,548,'链接分配：',22)
for x,label in [(180,0),(450,1),(720,2),(990,3)]:rect(x,515,130,48,f'#{label}','#edf3ec')
for x in [310,580,850]:arrow(x+4,539,x+132,539)
text(35,615,'图中 #0、#1 等标记逻辑块；未展开部分不表示特定记录的物理位置，物理块号由具体分配确定。',19)
s.append('</g></svg>');p=out/'OS_record_layers_course.svg';p.write_text('\n'.join(s))
subprocess.run(['inkscape',str(p),'--export-type=png','--export-dpi=180','--export-filename='+str(p.with_suffix('.png'))],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['inkscape',str(p),'--export-type=pdf','--export-text-to-path','--export-filename='+str(p.with_suffix('.pdf'))],check=True,stdout=subprocess.DEVNULL)
