#!/usr/bin/env python3
"""Build editable CO teaching diagrams. Run from any directory; no source-library dependency."""
from pathlib import Path
import html, json, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
BLUE = '#24516b'
LIGHT = '#e9f0f3'
GRAY = '#eeeeee'

class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#333"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>']
    def text(self, x,y,s,size=21,anchor='middle',fill='#111'):
        self.items.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Noto Sans CJK SC, sans-serif" font-size="{size}" fill="{fill}">{html.escape(str(s))}</text>')
    def rect(self,x,y,w,h,s='',fill='white',size=21):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#333" stroke-width="2"/>')
        if s: self.text(x+w/2,y+h/2+size*.35,s,size)
    def line(self,x1,y1,x2,y2,arrow=True,dash=False):
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def path(self,d,arrow=True,dash=False):
        self.items.append(f'<path d="{d}" fill="none" stroke="#333" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def save(self,name,title):
        svg=OUT/(name+'.svg');svg.write_text('\n'.join(self.items+['</svg>']),encoding='utf-8')
        for ext in ['png','pdf']:
            subprocess.run(['inkscape',str(svg),'--export-type='+ext,'--export-filename='+str(OUT/(name+'.'+ext)),'--export-dpi=160'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        return {'id':name,'title':title,'svg':'figures/'+name+'.svg','png':'figures/'+name+'.png','pdf':'figures/'+name+'.pdf','source':'tools/draw_co_figures.py','color_semantics':'蓝灰为字段或有效步骤，黑色箭头为依赖/传送；所有含义另有文字标签，黑白可辨'}

manifest=[]

s=SVG(1000,310)
s.text(500,30,'IEEE 754 binary32：32 位',24)
for x,w,label in [(35,95,'s：1位'),(130,250,'E：8位'),(380,585,'F：23位')]:s.rect(x,55,w,60,label,LIGHT)
s.text(500,150,'E=1…254：隐含 1，指数 E−127',22)
s.text(500,195,'E=0：隐含 0，指数 −126；F=0 时为带符号零',22)
s.text(500,240,'E=255：F=0 为 ±∞；F≠0 为 NaN',22)
s.text(500,285,'负号只由 s 决定，不把整个位串取补码',20)
manifest.append(s.save('CO_F01_ieee754','单精度浮点字段与指数边界'))

s=SVG(1000,535);s.text(500,30,'64 K×8 位：四组，每组两片 16 K×4 位',23)
s.rect(25,230,170,70,'CPU / 接口',LIGHT)
s.rect(235,65,175,55,'高2位译码',LIGHT)
s.line(195,245,215,245,False);s.path('M215,245 L215,92 L235,92')
s.text(120,200,'地址共16位',19)
for i in range(4):
 y=150+i*88
 s.rect(510,y,190,55,'16 K×4：D0…D3',size=18)
 s.rect(735,y,230,55,'16 K×4：D4…D7',size=18)
 s.text(465,y+35,f'组{i}',19)
 s.path(f'M{250+i*37},120 L{250+i*37},{y+28} L510,{y+28}')
 s.line(700,y+28,735,y+28,False)
 s.text(720,y-7,'CS共用',15)
s.text(500,515,'低14位送所有芯片；同组片选相同，数据位各占一半',21)
manifest.append(s.save('CO_F02_memory_expand','字扩展与位扩展'))

s=SVG(1000,350);s.text(500,30,'32 KiB 数据区，64 B/块，8 路组相联',23)
for x,w,label in [(30,550,'标记 20位'),(580,185,'组号 6位'),(765,205,'块内偏移 6位')]:s.rect(x,60,w,65,label,LIGHT)
s.line(672,125,672,185);s.text(815,170,'选64组中的一组',20)
for i in range(8):s.rect(38+i*120,205,110,55,f'路{i}',fill=LIGHT,size=20)
s.text(500,300,'选中组的8个有效标记并行比较；命中后由偏移选字节',21)
manifest.append(s.save('CO_F03_cache_address','组相联地址字段与比较范围'))

s=SVG(1000,390);s.text(500,30,'页大小 4 KiB：页内偏移12位保持不变',23)
s.rect(30,60,580,55,'虚页号20位：082H = 十进制130',LIGHT)
s.rect(610,60,360,55,'偏移12位：840H',LIGHT)
s.line(320,115,320,165);s.rect(100,165,440,65,'页表：130 → 018H，存在位1',size=21)
s.line(320,230,320,280);s.rect(30,280,580,55,'物理页框号12位：018H',LIGHT)
s.rect(610,280,360,55,'原偏移：840H',LIGHT);s.line(790,115,790,280)
s.text(500,375,'物理地址 = 018H × 1000H + 840H = 01 8840H',22)
manifest.append(s.save('CO_F04_virtual_address','页表转换与不变的偏移'))

s=SVG(1000,335);s.text(500,30,'record 首地址 C008H；小端；int 4 B，short 2 B',23)
vals=['11','01','00','00','b','填充','c低','c高']
for i,v in enumerate(vals):
 x=30+i*117;s.rect(x,100,117,65,v,LIGHT if i<4 or i>5 else GRAY);s.text(x+58,83,f'+{i}',20)
s.text(260,215,'a = 273 = 0000 0111H',22)
s.text(785,215,'c 起于偏移6（C00EH）',22)
s.text(500,285,'成员对齐决定填充；字节序决定 a 的低地址字节',21)
manifest.append(s.save('CO_F05_struct_layout','结构体对齐与小端字节序'))

s=SVG(1000,465);s.text(500,30,'栈向低地址增长；每槽4 B；push先减SP再写',23)
for y,addr,label in [(90,'1000H','调用前SP'),(155,'0FFCH','返回地址 2004H'),(220,'0FF8H','旧FP'),(285,'0FF4H','局部区：4 B'),(350,'0FF0H','局部区：4 B')]:
 s.text(190,y+30,addr,22);s.rect(300,y,400,55,label,LIGHT if addr!='1000H' else 'white')
s.line(825,100,825,385);s.text(875,220,'低地址',21)
s.text(500,450,'撤局部区 → 恢复FP → 弹返回地址；最终SP回到1000H',20)
manifest.append(s.save('CO_F06_stack_frame','调用与栈帧状态'))

s=SVG(1000,535);s.text(500,28,'单总线数据通路：同拍只能有一个内部总线驱动源',23)
s.items.append('<line x1="130" y1="65" x2="960" y2="65" stroke="#333" stroke-width="3"/>')
s.text(500,55,'系统总线',20)
s.items.append('<line x1="130" y1="220" x2="960" y2="220" stroke="#24516b" stroke-width="4"/>')
s.text(500,206,'内部总线',20)
s.rect(18,105,90,115,'主存',LIGHT)
s.path('M63,105 L63,65 L130,65',False)
for x,label in [(150,'MAR'),(335,'MDR'),(520,'PC'),(710,'IR')]:
 s.rect(x,125,90,45,label,LIGHT,size=21)
 s.line(x+45,220,x+45,170)
 if label in ['MDR','PC']:s.line(x+53,170,x+53,220)
 s.line(x+120,147,x+90,147,True,True)
 s.text(x+110,110,label+'in',18,anchor='start')
s.line(195,125,195,65);s.line(380,65,380,125);s.line(390,125,390,65)
s.line(655,190,573,190,True,True);s.text(660,195,'PCout',18,anchor='start')
s.line(755,125,755,95);s.text(755,87,'送CU等部件',18)
s.line(465,190,388,190,True,True);s.text(470,185,'MDRout',18,anchor='start')
for x,label in [(905,'Read'),(955,'Write')]:
 s.line(x,140,x,65,True,True);s.text(x,160,label,18)
s.rect(150,305,90,45,'Y',LIGHT)
s.line(195,220,195,305)
s.line(275,327,240,327,True,True);s.text(279,323,'Yin',18,anchor='start')
s.path('M195,350 L195,385 L325,385 L325,285 L450,285 L450,310')
s.rect(410,310,190,65,'ALU',LIGHT)
s.text(438,303,'A：16',18,anchor='end');s.text(570,303,'B：16',18,anchor='start')
s.line(555,220,555,310)
s.path('M675,385 L650,385 L650,343 L600,343',True,True);s.text(680,390,'ALUop',18,anchor='start')
s.line(505,375,505,425);s.text(535,401,'F：16',18)
s.rect(460,425,90,45,'Z',LIGHT)
s.path('M550,448 L630,448 L630,220')
s.line(680,435,630,435,True,True);s.text(682,440,'Zout',18,anchor='start')
s.rect(150,425,170,45,'FR：SF OF …',LIGHT,size=20)
s.path('M455,375 L455,400 L235,400 L235,425')
s.rect(760,305,150,70,'GPRs',LIGHT)
s.line(835,220,835,305);s.path('M910,340 L950,340 L950,220')
s.line(835,415,835,375,True,True);s.text(835,440,'GPRin',18)
s.line(970,320,950,320,True,True);s.text(945,297,'GPRout',17)
s.line(705,340,760,340);s.text(710,330,'rd：4',18)
s.line(960,365,910,365);s.text(952,395,'rs：4',18)
s.text(500,515,'实线：数据/地址；虚线：控制；A、B、F为16位，rs和rd为4位',20)
manifest.append(s.save('CO_F07_datapath','2022年第43题单总线数据通路原图重绘'))

s=SVG(1000,295);s.text(500,30,'外部中断：请求产生 ≠ 立即执行服务程序',23)
labels=['当前指令','硬件响应','入口保护','事件处理','恢复并返回'];x=25
for i,(w,label) in enumerate(zip([180,180,180,190,220],labels)):
 s.rect(x,100,w,70,label,LIGHT if i in [1,2] else 'white');x+=w
s.line(90,65,90,100);s.text(90,57,'请求到达',19)
s.line(205,65,205,100);s.text(285,57,'指令边界接受请求',19)
s.text(500,220,'硬件：保存断点/规定状态、确定入口；软件：保存通用寄存器等',20)
s.text(500,263,'处理后可回原进程；是否调度其他进程由系统另行决定',21)
manifest.append(s.save('CO_F08_interrupt_response','中断的请求响应与处理阶段'))

s=SVG(1000,390);s.text(500,30,'五段流水线：load-use停顿一拍（有MEM→EX转发）',22)
stages=[['IF','ID','EX','MEM','WB','','',''],['','IF','ID','EX','MEM','WB','',''],['','','IF','ID','保持ID','EX','MEM','WB']]
for c in range(8):s.text(205+c*100,75,c+1,21)
for r,row in enumerate(stages):
 y=100+r*80;s.text(75,y+35,f'I{r+1}',22)
 for c,v in enumerate(row):s.rect(155+c*100,y,100,60,v,LIGHT if v and v!='保持ID' else GRAY if v else 'white',size=20)
s.path('M605,240 L605,250 L705,250 L705,260')
s.text(500,370,'I2在第5拍末得到r3；I3的EX推迟到第6拍使用它',21)
manifest.append(s.save('CO_F09_pipeline_load','装入相关的流水状态'))

s=SVG(1000,360);s.text(500,30,'异步全互锁：请求和应答的撤销也要相互确认',22)
s.text(95,125,'请求',22);s.text(95,215,'应答',22)
s.path('M170,145 L240,145 L240,85 L580,85 L580,145 L940,145',False)
s.path('M170,235 L410,235 L410,175 L770,175 L770,235 L940,235',False)
for x,a,b in [(240,85,280),(410,175,280),(580,145,280),(770,235,280)]:s.line(x,a,x,b,False,True)
for x,t in [(240,'置请求'),(410,'置应答'),(580,'撤请求'),(770,'撤应答')]:s.text(x,315,t,20)
s.line(245,80,405,170);s.line(415,175,575,145);s.line(585,145,765,230)
manifest.append(s.save('CO_F10_bus_handshake','全互锁握手过程'))

s=SVG(1000,355);s.text(500,30,'硬件响应A>B>C；处理时允许C抢占B、B抢占A',22)
for y,lab in [(85,'A：100'),(165,'B：110'),(245,'C：111')]:s.text(95,y+25,lab,21)
for x,y,w,label in [(195,75,165,'A入口'),(360,155,160,'B入口'),(520,235,170,'C处理'),(690,155,130,'B返回'),(820,75,150,'A返回')]:s.rect(x,y,w,55,label,LIGHT)
s.line(360,103,360,155);s.line(520,183,520,235);s.line(690,263,690,210);s.line(820,183,820,130)
s.text(500,340,'屏蔽字位序ABC，1为屏蔽；退出逐层恢复旧屏蔽字',21)
manifest.append(s.save('CO_F11_interrupt_nesting','中断嵌套和逐层返回'))

s=SVG(1000,400);s.text(500,30,'DMA输入：CPU设置和收尾，控制器组织传送',23)
s.rect(25,80,200,75,'CPU / 驱动',LIGHT);s.rect(345,80,260,75,'DMA控制器',LIGHT);s.rect(760,80,215,75,'主存',LIGHT)
s.rect(345,255,260,75,'设备接口',LIGHT);s.rect(25,255,200,75,'外部设备',LIGHT)
s.line(225,105,345,105);s.text(285,85,'设置',19)
s.line(345,140,225,140);s.text(285,183,'完成中断',19)
s.line(475,255,475,155);s.text(565,218,'请求/控制',19)
s.line(225,292,345,292,False)
s.path('M605,292 L865,292 L865,155');s.text(760,340,'输入数据：接口 → 主存',22)
s.text(500,385,'CPU不逐字搬运；DMA仍占用相应总线和存储资源',21)
manifest.append(s.save('CO_F12_dma_path','DMA传送的数据与控制路径'))

s=SVG(1320,555)
s.text(660,32,'x=x*2+a：无转发，同一寄存器不能同拍读写',25)
s.text(660,65,'由2012年第44题条件展开；先装x，再装a，最短17拍',21)
schedule=[
    ('I1  LOAD x',{'IF':1,'ID':2,'EX':3,'M':4,'WB':5}),
    ('I2  LOAD a',{'IF':2,'ID':3,'EX':4,'M':5,'WB':6}),
    ('I3  SHL x',{'IF':3,'ID':6,'EX':7,'M':8,'WB':9}),
    ('I4  ADD',{'IF':6,'ID':10,'EX':11,'M':12,'WB':13}),
    ('I5  STORE x',{'IF':10,'ID':14,'EX':15,'M':16,'WB':17}),
]
x0=230;cw=61
for cycle in range(1,18):s.text(x0+(cycle-.5)*cw,108,cycle,20)
for row,(label,stages) in enumerate(schedule):
    y=126+row*70;s.text(116,y+31,label,20)
    labels={cycle:stage for stage,cycle in stages.items()}
    for cycle in range(1,18):
        waiting=stages['IF']<cycle<stages['ID']
        value=labels.get(cycle,'等' if waiting else '')
        s.rect(x0+(cycle-1)*cw,y,cw,52,value,GRAY if waiting else LIGHT if value else 'white',size=18)
s.text(660,510,'关键链：LOAD x的WB5 → SHL的ID6/WB9 → ADD的ID10/WB13 → STORE的ID14',20)
s.text(660,545,'“等”为ID端等待取数，保持前级状态；STORE的WB为空段，五段流出计17拍',20)
entry=s.save('CO_F13_pipeline_schedule','2012年第44题无转发五指令最短17拍时空图')
entry['basis']='2012年第44题原题条件；依据王道主书PDF物理271题、277解及完整社区复原卷物理8页，独立按依赖下界复算'
entry['mechanism_data']={'clock_count':17,'register_read_write_same_cycle':False,'forwarding':False,'instruction_stages':schedule,'completion_convention':'All five stages, including STORE empty WB'}
manifest.append(entry)

dest=ROOT/'build/CO/figure_manifest.json';dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'figures':len(manifest),'formats':['svg','png','pdf'],'directory':str(OUT)},ensure_ascii=False))
