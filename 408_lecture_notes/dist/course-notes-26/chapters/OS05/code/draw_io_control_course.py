#!/usr/bin/env python3
"""王道I/O控制方式课件的精确流程与硬件示意，可重建SVG/PNG/PDF。"""
from pathlib import Path
from html import escape
import subprocess
out=Path(__file__).resolve().parent.parent/'figures';out.mkdir(exist_ok=True)
FONT='Noto Sans CJK SC, sans-serif'
def start(w,h):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#425f72"/></marker></defs>',f'<rect width="{w}" height="{h}" fill="white"/>',f'<g font-family="{FONT}" fill="#223644">']
def box(s,x,y,w,h,lines,fill='#e1eef3',size=24):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#7796a5" stroke-width="2"/>')
 center=y+h/2-(len(lines)-1)*size*.62
 for i,line in enumerate(lines):s.append(f'<text x="{x+w/2}" y="{center+i*size*1.24+size*.35}" text-anchor="middle" font-size="{size}">{escape(line)}</text>')
def text(s,x,y,t,size=22,color='#223644',anchor='start'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(t)}</text>')
def arrow(s,path):s.append(f'<path d="{path}" fill="none" stroke="#425f72" stroke-width="2.5" marker-end="url(#arrow)"/>')
def export(s,name):
 s.append('</g></svg>');(out/f'{name}.svg').write_text('\n'.join(s))
 for typ in ('png','pdf'):
  subprocess.run(['inkscape',str(out/f'{name}.svg'),'--export-type='+typ,'--export-dpi=200','--export-filename='+str(out/f'{name}.{typ}')],check=True,stdout=subprocess.DEVNULL)

panels=[(25,35,'① 程序直接控制', ['CPU 发读命令','轮询设备状态','就绪：设备 → CPU','CPU → 内存；检查是否完成']),
        (635,35,'② 中断驱动', ['CPU 发读命令','CPU 执行其他任务','中断：CPU 检查状态','设备 → CPU → 内存']),
        (25,655,'③ DMA 控制', ['CPU 设置方向、地址、计数','DMA 启动并执行传送','设备 ⇄ 内存（DMA）','整块完成：中断 CPU']),
        (635,655,'④ 通道控制', ['CPU 给出通道程序地址','通道取指并自主执行','设备 ⇄ 内存（通道）','整组任务结束：中断 CPU'])]
def render_panels(group,name):
 s=start(1240,640)
 for x,y,title,lines in group:
  y=35
  s.append(f'<rect x="{x}" y="{y}" width="580" height="585" rx="12" fill="#fafcfd" stroke="#b1c4cc" stroke-width="2"/>');text(s,x+20,y+40,title,28)
  for i,line in enumerate(lines):
   yy=y+70+i*100;box(s,x+60,yy,460,65,[line], '#e1eef3' if i%2==0 else '#e6f2e9',24)
   if i:arrow(s,f'M{x+290} {yy-35} V{yy-2}')
  if title.startswith('①'):
   arrow(s,f'M{x+520} {y+202} H{x+548} V{y+170} H{x+521}')
   text(s,x+55,y+520,'未就绪时沿右侧回路继续轮询',21,'#94616d')
  elif title.startswith('②'):text(s,x+55,y+520,'CPU 在每字中断服务中搬运数据',21)
  elif title.startswith('③'):text(s,x+55,y+520,'CPU 介入启动、异常和结束处理',21)
  else:text(s,x+55,y+520,'通道程序位于内存，组织一组数据块',21)
 export(s,name)

render_panels(panels[:2],'OS_io_control_poll_interrupt_course')
render_panels(panels[2:],'OS_io_control_dma_channel_course')

s=start(1240,740);text(s,35,38,'DMA 控制器与通道程序：硬件分工',30)
text(s,30,78,'DMA 控制器',27);box(s,35,112,130,120,['CPU'],size=26);box(s,35,320,130,120,['内存'],size=26)
s.append('<rect x="255" y="100" width="400" height="460" rx="10" fill="#f4f8fa" stroke="#7796a5" stroke-width="2"/>');text(s,455,137,'DMA 控制器',25,anchor='middle')
for i,ls in enumerate([['DR 数据寄存器'],['MAR 内存地址寄存器'],['DC 数据计数器'],['CR 命令／状态寄存器']]):box(s,280,155+i*80,245,60,ls,size=20)
box(s,550,240,85,150,['I/O','控制','逻辑'],size=20);box(s,700,245,140,115,['设备'],size=24)
arrow(s,'M165 170 H253');text(s,170,155,'命令与参数',18);arrow(s,'M255 390 H168');arrow(s,'M168 418 H255');text(s,170,458,'数据',20)
arrow(s,'M655 277 H698');arrow(s,'M700 313 H657');text(s,657,239,'数据／控制',18)
arrow(s,'M255 206 H168');text(s,170,230,'完成中断',18)
text(s,35,615,'输入：设备 → DR → 内存；输出：内存 → DR → 设备。',24)
text(s,35,653,'MAR 指向本次主存地址，DC 保存剩余计数；完成后向 CPU 报告。',22)
text(s,35,691,'通道从内存取通道程序，控制多设备传送；整组任务结束后中断 CPU。',22)
export(s,'OS_dma_controller_course')


s=start(1240,680);text(s,35,42,'通道执行主存中的通道程序',30)
box(s,40,250,170,130,['CPU'],size=28)
box(s,330,70,250,130,['主存','通道程序（任务清单）'],size=23)
box(s,330,430,250,120,['主存','数据缓冲区'],size=23)
box(s,700,235,210,165,['I/O 通道','通道程序首地址','控制连接的设备'],size=23)
for i in range(3):box(s,1010,75+i*175,170,90,[f'I/O设备 {i+1}'],size=24)
arrow(s,'M210 285 H698');text(s,250,275,'① CPU 发 I/O 指令及通道程序地址',20)
arrow(s,'M582 145 H640 V245 H698');text(s,585,125,'② 从主存取指令',20)
arrow(s,'M760 400 V465 H583');arrow(s,'M583 510 H800 V402');text(s,600,455,'数据块传送',20)
arrow(s,'M910 260 H960 V120 H1008');arrow(s,'M910 285 H960 V295 H1008');arrow(s,'M910 310 H960 V470 H1008')
arrow(s,'M700 345 H212');text(s,260,373,'③ 任务结束后向 CPU 发中断',20)
text(s,50,605,'通道执行专用 I/O 指令；通道程序和数据均位于主存。',23)
text(s,50,645,'图中三台设备是接口示意；各设备请求由通道程序组织。',23)
export(s,'OS_channel_program_course')

s=start(1240,520);text(s,35,42,'SPOOLing：磁盘井、内存缓冲与独占设备',29)
box(s,20,115,170,100,['输入设备'],size=23)
box(s,300,100,340,160,['内存：输入进程','输入缓冲区'],size=24)
box(s,800,115,195,100,['磁盘','输入井'],size=23)
box(s,20,315,170,100,['输出设备','打印机'],size=23,fill='#f7e8e0')
box(s,300,300,340,160,['内存：输出进程','输出缓冲区'],size=24,fill='#f7e8e0')
box(s,800,315,195,100,['磁盘','输出井'],size=23,fill='#f7e8e0')
arrow(s,'M190 165 H298');arrow(s,'M640 165 H798')
arrow(s,'M800 365 H642');arrow(s,'M300 365 H192')
text(s,700,150,'输入',20);text(s,700,350,'输出',20)
text(s,1040,155,'预读入井',20);text(s,1040,355,'保存待输出数据',20)
text(s,1040,390,'由请求表定位',20)
export(s,'OS_spooling_course')
