from pathlib import Path
from html import escape
import subprocess,json
ROOT=Path(__file__).resolve().parents[2]
class SVG:
 def __init__(self,w=900,h=460,title=''):
  self.w=w;self.h=h;self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466C82" stroke-width="1.2"/></marker></defs>','<rect width="100%" height="100%" fill="#fff"/>','<g font-family="Noto Sans CJK SC,Noto Sans SC,sans-serif" font-size="19" fill="#263945">']
  if title:self.text(w/2,30,title,23,'middle')
 def text(self,x,y,t,size=18,anchor='middle',color='#263945'):
  lines=t.split('\n')
  self.p.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}">')
  for i,l in enumerate(lines): self.p.append(f'<tspan x="{x}" dy="{0 if i==0 else size*1.45}">{escape(l)}</tspan>')
  self.p.append('</text>')
 def box(self,x,y,w,h,t,fill='#DDEFF5',size=18):
  self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#8EA8B4" stroke-width="1.5"/>')
  self.text(x+w/2,y+h/2-(len(t.split(chr(10)))-1)*size*.72+size*.35,t,size)
 def line(self,x1,y1,x2,y2,label='',arrow=True):
  self.p.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#466C82" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
  if label:
   if x1==x2:self.text(x1+14,(y1+y2)/2+6,label,16,'start')
   else:self.text((x1+x2)/2,(y1+y2)/2-9,label,16)
 def path(self,d):self.p.append(f'<path d="{d}" fill="none" stroke="#466C82" stroke-width="2" marker-end="url(#arrow)"/>')
 def save(self,ch,name):
  out=ROOT/ch/'figures';out.mkdir(exist_ok=True);p=out/(name+'.svg');p.write_text('\n'.join(self.p+['</g></svg>']))
  subprocess.run(['inkscape',str(p),'--export-type=png','--export-dpi=160','--export-filename='+str(p.with_suffix('.png'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  subprocess.run(['inkscape',str(p),'--export-text-to-path','--export-type=pdf','--export-filename='+str(p.with_suffix('.pdf'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

s=SVG(900,390,'程序和数据共同存储：y = a×b+c')
s.box(25,90,180,240,'主存\n0～4：机器指令\n5：a = 2\n6：b = 3\n7：c = 1\n8：y = 0',size=20)
s.box(290,70,215,85,'控制器\nPC、IR与控制逻辑')
s.box(290,245,215,85,'运算器\nACC、MQ、ALU')
s.box(600,70,260,85,'取指：PC → MAR\nM[MAR] → MDR → IR',fill='#DFEFE6')
s.box(600,245,260,85,'执行：2 → 6 → 7\n最终写回 M[8] = 7',fill='#DFEFE6')
s.line(205,115,290,115,'指令');s.line(205,280,290,280,'数据');s.line(397,155,397,245,'控制信号');s.line(505,112,600,112);s.line(505,287,600,287)
s.save('CO01','CO01_program_path')

s=SVG(900,350,'MUX选择数据；三态门管理公共总线驱动')
s.box(20,75,120,55,'D0');s.box(20,175,120,55,'D1');s.box(245,75,140,155,'2选1\nMUX')
s.line(140,102,245,102);s.line(140,202,245,202);s.line(315,300,315,230,'s');s.line(385,152,470,152,'Y')
s.box(490,75,130,55,'源A');s.box(490,195,130,55,'源B');s.box(665,75,110,55,'三态门A');s.box(665,195,110,55,'三态门B');s.line(620,102,665,102);s.line(620,222,665,222);s.line(775,102,835,102);s.line(775,222,835,222);s.line(835,85,835,280,'',False);s.text(820,307,'公共总线',18);s.text(670,60,'每拍仅允许一个源驱动',16);s.text(670,280,'未使能端呈高阻态',18)
s.save('CO02','CO02_mux_bus')

s=SVG(900,430,'32K×16位存储器：16K×8位芯片的字位扩展')
s.box(15,150,150,80,'CPU\nA14…A0\nD15…D0')
s.box(220,140,150,95,'片选译码\nA14=0：组选0\nA14=1：组选1',fill='#DFEFE6',size=17)
s.box(435,65,190,90,'组0／低8位\n16K×8 → D7…D0');s.box(670,65,190,90,'组0／高8位\n16K×8 → D15…D8')
s.box(435,275,190,90,'组1／低8位\n16K×8 → D7…D0');s.box(670,275,190,90,'组1／高8位\n16K×8 → D15…D8')
s.line(165,175,220,175,'A14');s.path('M370,165 H400 V110 H435');s.path('M400,110 V45 H765 V65');s.path('M370,210 H400 V320 H435');s.path('M400,320 V390 H765 V365')
s.text(650,210,'A13…A0并联到全部芯片',20);s.text(650,240,'组0：0000H～3FFFH；组1：4000H～7FFFH',17);s.text(175,395,'按字编址，每个字16位',18)
s.save('CO03','CO03_chip_expansion')

s=SVG(900,490,'SSD层次：逻辑块号 → 闪存翻译层 → 芯片／块／页')
s.box(290,50,320,55,'I/O总线：逻辑块号',fill='#DFEFE6');s.box(270,145,360,65,'闪存翻译层 FTL\n逻辑地址映射到物理页');s.line(450,105,450,145)
for i in range(4):
 x=20+i*220;s.box(x,285,200,165,'',fill='#F6F6F6');s.text(x+100,310,f'闪存芯片{i}',20)
 for j in range(3):
  s.box(x+12,326+j*36,176,29,f'块{j}：页0｜页1｜…｜页n' if j<2 else '块2、…、块m',size=12)
 s.text(x+100,471,'块0、块1、…、块m',16)
s.path('M450,210 V245 H120 V285');s.path('M450,245 H340 V285');s.path('M450,245 H560 V285');s.path('M450,245 H780 V285')
s.text(450,272,'按页读写，按块擦除',17)
s.save('CO03','CO03_ssd_hierarchy')

s=SVG(900,410,'32位EBP栈帧示例（栈向低地址增长）')
items=[('EBP+12','第二个参数'),('EBP+8','第一个参数'),('EBP+4','返回地址'),('EBP','保存的旧EBP'),('EBP−4','局部变量'),('EBP−8','局部变量')]
for i,(off,lab) in enumerate(items):
 y=55+i*50;s.text(245,y+28,off,20,'end');s.box(280,y,380,45,lab,fill='#DFEFE6' if i<3 else '#DDEFF5')
s.line(760,75,760,335,'');s.text(780,185,'地址\n减小',18);s.text(450,390,'标准建帧：push ebp；mov ebp, esp',19)
s.save('CO04','CO04_stack_layout')

s=SVG(900,450,'微程序控制：主存指令地址与控存微地址分属不同空间')
s.box(20,80,210,85,'PC → 主存\n机器指令 → IR');s.box(345,60,235,90,'公共取指微程序\nCMAR选微指令地址');s.box(345,235,235,85,'微地址形成部件\n根据IR操作码分派',fill='#DFEFE6')
s.box(650,65,220,70,'LDA执行微程序');s.box(650,195,220,70,'STA执行微程序');s.box(650,325,220,70,'其他执行微程序')
s.line(345,120,230,120,'取指控制');s.path('M125,165 V275 H345');s.text(230,265,'IR操作码',16);s.line(463,150,463,235,'取指结束');s.path('M580,275 H610 V100 H650');s.line(580,275,650,230);s.path('M580,275 H610 V360 H650')
s.path('M760,65 V45 H465 V60');s.text(450,430,'执行结束回公共取指入口',18);s.text(120,355,'主存：程序／数据\n控存CM：微指令',19)
s.save('CO05','CO05_microprogram_flow')

s=SVG(900,330,'全互锁异步握手：建立与撤销都需确认')
s.text(40,105,'请求',21,'start');s.text(40,210,'应答',21,'start')
s.p.append('<path d="M130,130 H250 V75 H570 V130 H850 M130,235 H390 V180 H710 V235 H850" fill="none" stroke="#466C82" stroke-width="3"/>')
for x,y,lab in [(250,75,'①请求置位'),(390,180,'②应答置位'),(570,130,'③请求撤销'),(710,235,'④应答撤销')]:
 s.line(x,260,x,y,'',False);s.text(x,290,lab,17)
s.line(130,315,850,315,'时间')
s.save('CO06','CO06_handshake_full')

s=SVG(900,380,'DMA块传送的预处理、硬件搬运与后处理')
s.box(20,75,245,115,'CPU预处理\n方向、起始地址、字数\n启动设备',fill='#DFEFE6')
s.box(335,75,245,115,'DMA硬件传送\n申请总线 → 搬运数据\n地址更新、计数减1')
s.box(650,75,230,115,'CPU后处理\n检查状态、处理错误\n组织后续操作',fill='#DFEFE6')
s.line(265,132,335,132);s.line(580,132,650,132,'完成中断')
s.box(290,280,140,60,'I/O设备');s.box(570,280,140,60,'主存');s.line(430,310,570,310,'DMA直接数据通路');s.line(458,190,458,280,'控制')
s.text(450,365,'CPU负责设置与收尾，数据块逐字传送由DMA控制',19)
s.save('CO07','CO07_dma_phases')
