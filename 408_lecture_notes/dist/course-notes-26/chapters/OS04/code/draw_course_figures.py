from pathlib import Path
import html, subprocess
R=Path(__file__).resolve().parents[2]
class Fig:
 def __init__(self,w=960,h=440):
  self.w=w;self.h=h;self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#47677b"/></marker></defs>','<rect width="100%" height="100%" fill="white"/>','<g font-family="Noto Sans CJK SC, Noto Sans SC, sans-serif" fill="#223644" font-size="20">']
 def text(self,x,y,t,size=20,anchor='middle',bold=False):
  self.s.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}"'+(' font-weight="bold"' if bold else '')+'>'+html.escape(t)+'</text>')
 def box(self,x,y,w,h,labels,fill='#e4eff3'):
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" stroke="#809eae" fill="{fill}"/>')
  lines=labels if isinstance(labels,list) else [labels]
  for i,t in enumerate(lines):self.text(x+w/2,y+h/2+(i-(len(lines)-1)/2)*25+7,t)
 def edge(self,x1,y1,x2,y2,label='',curve=''):
  self.s.append(f'<path d="M{x1},{y1} '+(curve if curve else f'L{x2},{y2}')+'" fill="none" stroke="#47677b" stroke-width="2" marker-end="url(#arr)"/>')
  if label:self.text((x1+x2)/2+5,(y1+y2)/2-8,label,17)
 def save(self,cid,stem):
  p=R/cid/'figures'/stem;p.parent.mkdir(exist_ok=True)
  p.with_suffix('.svg').write_text('\n'.join(self.s+['</g></svg>']))
  for ext in ['png','pdf']:
   subprocess.run(['inkscape',str(p.with_suffix('.svg')),'--export-type='+ext,'--export-filename='+str(p.with_suffix('.'+ext))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
  print(cid,stem)
# Signal vectors use columns numbered 1 to 8, not an unspecified endian convention.
f=Fig(960,350); f.text(480,35,'普通信号位向量：待处理不等于可递送',23, bold=True)
for row,(label,bits,col) in enumerate([('pending',[1,0,0,0,0,0,0,1],'#e4eff3'),('blocked',[0,0,0,0,0,0,0,1],'#f6e4e9'),('可递送 D',[1,0,0,0,0,0,0,0],'#e0efdf')]):
 y=92+row*65;f.text(135,y+25,label,21)
 for j,b in enumerate(bits):
  if row==0:f.text(255+j*75,y-12,f'信号{j+1}',16)
  f.box(225+j*75,y,60,40,str(b),col)
f.text(480,315,'D = pending & ~blocked：信号8暂缓递送，进程本身不必阻塞。',20)
f.save('OS02','OS_signal_masks')
f=Fig(960,410);f.text(480,35,'容量为1的盘子：空盘、苹果、橘子三种状态',22,bold=True)
f.box(360,75,240,58,['空盘：plate许可'],'#e0efdf');f.box(80,245,240,58,['满盘：苹果'],'#f6e4e9');f.box(640,245,240,58,['满盘：橘子'],'#f5ead9')
f.edge(365,130,240,245);f.edge(595,130,720,245);f.edge(120,245,360,105,curve='C60,80 140,45 360,105');f.edge(840,245,600,105,curve='C900,80 820,45 600,105');f.text(300,200,'父亲放苹果',18);f.text(660,200,'母亲放橘子',18);f.text(125,108,'女儿取苹果',18);f.text(835,108,'儿子取橘子',18)
f.text(480,365,'初值plate=1，apple=orange=0；放取动作完成后再发布下一许可。',20)
f.save('OS02','OS_fruit_plate')
f=Fig(960,340);f.text(480,35,'动态分区回收：释放[28,32)并合并前后空闲区',22,bold=True)
def memrow(y,parts):
 x=65;unit=13
 for start,end,lab,color in parts:
  xx=x+start*unit;ww=(end-start)*unit
  f.s.append(f'<rect x="{xx}" y="{y}" width="{ww}" height="60" stroke="#809eae" fill="{color}"/>')
  if ww>=80:f.text(xx+ww/2,y+34,lab,17)
  else:f.text(xx+ww/2,y+88,lab,15)
 for v in [0,8,28,32,42,60,64]:f.text(x+v*unit,y-9,str(v),16)
memrow(85,[(0,8,'系统','#e4eff3'),(8,28,'空闲20 MB','#e0efdf'),(28,32,'回收4 MB','#f6e4e9'),(32,42,'空闲10 MB','#e0efdf'),(42,60,'占用18 MB','#e4eff3'),(60,64,'空闲4 MB','#e0efdf')])
memrow(245,[(0,8,'系统','#e4eff3'),(8,42,'合并为空闲34 MB','#e0efdf'),(42,60,'占用18 MB','#e4eff3'),(60,64,'空闲4 MB','#e0efdf')]);f.save('OS03','OS_partition_merge')
f=Fig(960,470);f.text(480,33,'基本分页：页号转换，页内偏移保持不变',23,bold=True)
f.box(30,75,240,70,['逻辑地址A=2500','页大小L=1024 B']);f.box(345,75,220,70,['页号p=2','偏移w=452']);f.edge(270,110,345,110)
f.box(345,210,220,65,['检查p < 页表长M'],'#f5ead9');f.edge(455,145,455,210)
f.box(665,210,250,65,['读F+2e处页表项','页框号b=8']);f.edge(565,243,665,243)
f.box(620,360,295,65,['物理地址E=8×1024+452','E=8644'],'#e0efdf');f.edge(790,275,790,360)
f.text(250,315,'越界或权限非法：进入异常处理',18);f.edge(345,242,220,285)
f.save('OS03','OS_page_translation')
f=Fig(960,430);f.text(480,35,'每个逻辑段独立分页：页大小4 KiB',23,bold=True)
for i,(name,size,pages,frag) in enumerate([('MAIN',7,2,1),('X',3,1,1),('D',6,2,2)]):
 x=35+i*310;f.box(x,80,270,60,[f'{name}段：{size} KiB']);f.box(x,205,270,75,[f'{pages}页，共{pages*4} KiB',f'末页空余{frag} KiB'],'#e0efdf');f.edge(x+135,140,x+135,205)
f.text(480,335,'总驻留页框5个，占20 KiB，内部未用空间共4 KiB。',21)
f.text(480,385,'段号 → 段表 → 该段页表 → 页框；段号与段内页号分别检查。',20)
f.save('OS03','OS_segment_pages')
f=Fig(960,430);f.text(480,32,'记录索引与分组索引：定位逻辑记录',23,bold=True)
f.text(245,85,'逐记录索引：10000项',22);f.text(725,85,'分组索引：100项',22)
for i,lab in enumerate(['索引0 → 记录0','索引1 → 记录1','…','索引9999 → 记录9999']):f.box(55,115+i*57,365,43,lab)
for i,lab in enumerate(['组0 → 记录0～99','组1 → 记录100～199','…','组99 → 记录9900～9999']):f.box(535,115+i*57,365,43,lab,'#e0efdf')
f.text(480,400,'组内仍顺序查找；每组100条时，两段平均扫描近似各50次。',20);f.save('OS04','OS_record_indexes')
f=Fig(960,510);f.text(480,32,'文件系统分层：名称、权限、记录、块地址与资源',23,bold=True)
labels=['用户接口：接收系统调用','文件目录系统：按名找到FCB／inode','存取控制：验证本次权限','逻辑文件系统：记录号→文件逻辑地址','物理文件系统：逻辑地址→物理位置']
for i,t in enumerate(labels):
 f.box(190,65+i*65,580,44,t)
 if i:f.edge(480,44+i*65,480,65+i*65)
f.box(80,420,360,50,'辅助分配：分配／回收块','#e0efdf');f.box(520,420,360,50,'设备管理：调度／执行I/O','#f5ead9');f.edge(400,369,260,420);f.edge(560,369,700,420)
f.save('OS04','OS_file_layers')
f=Fig(1200,450);f.text(600,32,'成组链接：原课件空闲块组与结束标记',23,bold=True)
f.box(15,95,255,135,['内存超级块','计数100','201～300'],'#e4eff3')
f.box(310,95,255,135,['300号块存下一组','计数100','301～400'],'#f5ead9')
f.box(605,95,255,135,['400号块存下一组','计数100','7801～7899、7900'],'#f5ead9')
f.box(915,95,270,135,['7900号块存末组','计数99；9901～9999','结束标记 −1'],'#e0efdf')
f.edge(270,160,310,160);f.edge(565,160,605,160);f.edge(860,160,915,160)
f.text(600,290,'取尽当前组时：先读取承载块中下一组的目录，再将承载块分配出去。',21)
f.text(600,335,'回收块时：组未满则直接登记；组已满则先把旧组目录写入新回收块。',21)
f.text(600,395,'组内块号无需连续；结束标记 −1 不计入99个空闲块。',21)
f.save('OS04','OS_grouped_free')
f=Fig(960,440);f.text(480,32,'缓冲池：三队列与四种工作角色',23,bold=True)
f.box(350,65,260,55,'空缓冲队列','#e0efdf');f.box(40,220,250,60,'输入满队列');f.box(670,220,250,60,'输出满队列','#f5ead9')
f.edge(350,92,165,220,'取得hin并冲满');f.edge(165,280,350,118,'取得sin并读空','C165,380 440,400 350,118')
f.edge(610,92,795,220,'取得hout并冲满');f.edge(795,280,610,118,'取得sout并读空','C795,380 520,400 610,118')
f.text(480,405,'hin/sin用于输入；hout/sout用于输出；每次转移都维护队列与独占使用权。',19);f.save('OS05','OS_buffer_pool')
f=Fig(960,460);f.text(480,32,'设备分配的数据结构与依赖路径',23,bold=True)
for i,(lab,col) in enumerate([('SDT：系统设备目录','#e4eff3'),('DCT：设备状态与等待队列','#e0efdf'),('COCT：控制器状态与等待队列','#e4eff3'),('CHCT：通道状态与等待队列','#f5ead9')]):
 f.box(180,65+i*78,600,53,lab,col)
 if i:f.edge(480,40+i*78,480,65+i*78)
f.text(480,407,'LUT另记录逻辑名称 → 物理设备名称与驱动入口。',21)
f.text(480,442,'只有设备、控制器与通道均取得，才可启动这次I/O。',19);f.save('OS05','OS_device_tables')
f=Fig(960,370);f.text(480,32,'扇区布局：为处理和切换保留角时间',23,bold=True)
f.text(480,80,'一周8个物理角位置，箭头表示旋转经过顺序',19)
for row,(label,nums) in enumerate([('顺序编号',[0,1,2,3,4,5,6,7]),('交替编号',[0,4,1,5,2,6,3,7]),('相邻盘面错位',[7,3,0,4,1,5,2,6])]):
 y=120+row*67;f.text(110,y+28,label,20)
 for j,n in enumerate(nums):f.box(240+j*82,y,70,42,str(n),'#e0efdf' if row else '#e4eff3')
f.text(480,343,'相邻逻辑号留间隔；下一盘面起始号错位，配合处理／磁头切换时间。',20);f.save('OS05','OS_sector_layout')
f=Fig(960,450);f.text(480,32,'SSD地址层次：读写页，擦除块',23,bold=True)
f.box(20,80,230,70,['主机逻辑块地址','文件系统提供请求']);f.box(330,80,260,70,['FTL：逻辑→物理','维护映射与回收'],'#e0efdf');f.edge(250,115,330,115)
f.box(680,80,250,70,['多个Flash芯片','并行组织存储']);f.edge(590,115,680,115)
f.box(650,225,280,65,['芯片内多个擦除块','整块擦除'],'#f5ead9');f.edge(805,150,805,225)
f.box(650,355,280,60,['块内多个页','按页读／编程']);f.edge(790,290,790,355)
f.box(60,250,455,90,['异地更新使旧页失效','迁移有效页后才能回收整个块','磨损均衡分散擦除次数'],'#e4eff3');f.save('OS05','OS_flash_hierarchy')
f=Fig(960,400);f.text(480,32,'传统BIOS／MBR引导链',23,bold=True)
labels=[['固件ROM','自检与初始引导'],['磁盘MBR','引导代码与分区表'],['活动分区PBR','装入后续引导程序'],['启动管理器／装入器','装入并初始化内核']]
for i,lab in enumerate(labels):
 x=15+i*238;f.box(x,100,215,105,lab,'#e4eff3' if i%2==0 else '#e0efdf')
 if i:f.edge(x-23,152,x,152)
f.text(480,275,'程序逐级读入RAM后执行；MBR和PBR位于不同的磁盘结构层次。',20)
f.text(480,332,'UEFI／GPT等采用相应启动流程，不能把某一传统链条当作所有平台通则。',18)
f.save('OS01','OS_boot_chain')
f=Fig(960,430);f.text(480,32,'第一类与第二类VMM的层次',23,bold=True)
left=[['客户应用／客户OS','各虚拟机相互隔离'],['第一类VMM','直接控制物理资源'],['物理硬件','CPU、内存、I/O']]
right=[['客户应用／客户OS','各虚拟机相互隔离'],['第二类VMM','使用宿主服务'],['宿主操作系统','设备驱动与资源管理'],['物理硬件','CPU、内存、I/O']]
for side,items in [(0,left),(1,right)]:
 for i,label in enumerate(items):
  x=35+side*490;y=65+i*83;f.box(x,y,400,65,label,'#e0efdf' if i==1 else '#e4eff3')
  if i:f.edge(x+200,y-18,x+200,y)
f.save('OS01','OS_vmm_layers')
