#!/usr/bin/env python3
"""Rebuild the OS book's precise vector figures; no external source materials required."""
from pathlib import Path
import html, json, subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)
BLUE='#24506b'; GRAY='#f2f3f4'; WAIT='#fff5dc'

class Figure:
    def __init__(self,name,w,h,title):
        self.name,self.w,self.h=name,w,h
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<defs><marker id="arr" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7" fill="#333"/></marker></defs>',
        f'<rect width="{w}" height="{h}" fill="white"/>']
        self.text(w/2,31,title,23,anchor='middle',bold=True)
    def text(self,x,y,t,size=20,anchor='middle',bold=False):
        for j,ln in enumerate(str(t).split('\n')):
            self.s.append(f'<text x="{x}" y="{y+j*(size+8)}" text-anchor="{anchor}" font-family="Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="#111">{html.escape(ln)}</text>')
    def box(self,x,y,w,h,t,fill=GRAY,size=20):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#333" stroke-width="2"/>')
        ls=str(t).split('\n');self.text(x+w/2,y+h/2-(len(ls)-1)*(size+8)/2+size*.35,t,size)
    def circle(self,x,y,r,t):
        self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="#333" stroke-width="2"/>');self.text(x,y+7,t)
    def line(self,x1,y1,x2,y2,arrow=True,dash=False,color='#333'):
        self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+(' marker-end="url(#arr)"' if arrow else '')+'/>')
    def path(self,d,dash=False):
        self.s.append(f'<path d="{d}" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arr)"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def finish(self):
        p=OUT/f'{self.name}.svg';p.write_text('\n'.join(self.s+['</svg>']))
        subprocess.run(['inkscape',str(p),'--export-type=png',f'--export-filename={OUT/self.name}.png','--export-width=1800'],check=True,capture_output=True)
        subprocess.run(['inkscape',str(p),'--export-type=pdf',f'--export-filename={OUT/self.name}.pdf'],check=True,capture_output=True)
        return {'id':self.name,'svg':str(p.relative_to(ROOT)),'png':f'figures/{self.name}.png','pdf':f'figures/{self.name}.pdf','source':'tools/draw_os_figures.py','width':self.w,'height':self.h}

def build():
    fs=[]
    f=Figure('OS_control_transfer',960,390,'系统调用入口与返回：模式改变不必更换进程')
    f.box(30,80,230,65,'用户程序：准备参数')
    f.box(365,80,230,65,'执行陷入指令')
    f.box(700,80,230,65,'硬件保存必要状态\n转入受控内核入口',size=18)
    f.line(260,112,365,112);f.line(595,112,700,112)
    f.box(700,245,230,65,'入口代码保存现场\n执行服务例程',size=18)
    f.box(365,245,230,65,'恢复现场\n执行异常返回',size=18)
    f.box(30,245,230,65,'用户程序继续执行')
    f.line(815,145,815,245);f.text(825,195,'内核态',18,anchor='start')
    f.line(700,277,595,277);f.line(365,277,260,277)
    f.text(480,364,'可在同一进程内完成；阻塞或调度时才可能转交其他执行者',18)
    fs.append(f.finish())

    f=Figure('OS_process_states',960,430,'三种基本状态：等待事件与等待CPU分别判断')
    f.box(100,130,220,80,'就绪\n只缺CPU')
    f.box(640,130,220,80,'运行\n正在CPU上执行')
    f.box(370,315,220,75,'阻塞\n等待事件',fill=WAIT)
    f.line(320,150,640,150);f.text(480,132,'调度分派',18)
    f.path('M640,142 C550,55 410,55 320,142');f.text(480,61,'抢占、时间片到或主动让出',17)
    f.line(710,210,550,315);f.text(735,284,'等待I/O、资源或事件',18)
    f.line(400,315,250,210);f.text(220,286,'事件满足后唤醒',18)
    fs.append(f.finish())

    data=json.loads((ROOT/'editorial/full/OS/model_data.json').read_text())
    f=Figure('OS_priority_timeline',960,250,'【2023】抢占式优先级：运行段与剩余时间')
    seg=data['priority_2023']['segments'];left=65;scale=7.2
    for i,(a,b,p) in enumerate(seg):
        f.box(left+a*scale,100,(b-a)*scale,65,p,fill=GRAY if p=='P1' else '#e4eef4',size=19)
        f.text(left+a*scale,88,a,17)
    f.text(left+seg[-1][1]*scale,88,seg[-1][1],17)
    f.text(480,213,'P1：20+40=60 ms；P2：10+32=42 ms；P3：13 ms',19)
    fs.append(f.finish())

    f=Figure('OS_resource_graph',960,375,'单实例资源等待环：分配边与请求边方向不同')
    f.circle(210,125,40,'P');f.circle(750,125,40,'Q')
    f.box(170,265,80,60,'A');f.box(710,265,80,60,'B')
    f.line(210,265,210,165);f.text(130,222,'持有',18)
    f.line(750,265,750,165);f.text(828,222,'持有',18)
    f.line(245,146,715,265,dash=True);f.text(468,200,'P请求B',18)
    f.path('M715,100 C600,55 355,60 170,265',dash=True);f.text(470,75,'Q请求A',18)
    f.text(480,359,'实线：资源→持有者；虚线：进程→请求资源。每类仅一个实例。',18)
    fs.append(f.finish())

    f=Figure('OS_address_fields',960,285,'【2019】2050 1225H按10+10+12位分割')
    x=40;y=100
    for width,t,bits in [(275,'页目录号：081H','0010000001'),(275,'页号：101H','0100000001'),(330,'页内偏移：225H','001000100101')]:
        f.box(x,y,width,75,t,size=19);f.text(x+width/2,220,bits,20);x+=width
    f.text(480,267,'右移22位取目录；右移12位后取低10位得到页号；低12位为偏移。',17)
    fs.append(f.finish())

    f=Figure('OS_page_fault',960,470,'请求分页：未驻留页面怎样成为有效映射')
    nodes=[(40,80,250,62,'访存：查TLB/页表'),(355,80,250,62,'合法页面不在内存'),(670,80,250,62,'陷入缺页处理'),
           (670,260,250,82,'取得页框\n必要时淘汰并回写脏页'),(355,260,250,82,'从后备存储调入\n更新页表与TLB'),(40,260,250,82,'重新就绪并获CPU\n重试原访存')]
    for x,y,w,h,t in nodes:f.box(x,y,w,h,t,fill=WAIT if x==670 else GRAY,size=18)
    f.line(290,111,355,111);f.line(605,111,670,111);f.line(795,142,795,260)
    f.line(670,300,605,300);f.line(355,300,290,300)
    f.text(480,408,'调页I/O等待期间可阻塞；有空闲页框时不必发生置换。',19)
    f.text(480,440,'非法地址或权限错误走错误处理，不能一律当作可调入页面。',19)
    fs.append(f.finish())

    f=Figure('OS_file_index',960,435,'混合索引：inode已在内存，数据块前经过0/1/2个索引块')
    f.box(20,140,195,130,'内存inode\n直接项\n一级项、二级项',size=18)
    f.box(715,55,210,60,'直接区数据块',size=18);f.path('M215,158 L640,158 L640,85 L715,85')
    f.box(370,195,200,60,'一级索引块',size=18);f.box(715,195,210,60,'一级区数据块',size=18)
    f.line(215,210,370,225);f.line(570,225,715,225)
    f.box(260,325,190,60,'二级索引块',size=18);f.box(495,325,190,60,'一级索引块',size=18);f.box(730,325,190,60,'二级区数据块',size=18)
    f.line(215,250,260,355);f.line(450,355,495,355);f.line(685,355,730,355)
    f.text(480,421,'本题每块1024 B、每项4 B，每个索引块含256项；箭头表示块号引用。',17)
    fs.append(f.finish())

    f=Figure('OS_file_links',960,405,'硬链接关联同一文件；软链接保存目标路径')
    f.box(40,80,210,60,'目录项：/u/f1',size=19);f.box(40,190,210,60,'目录项：/v/f2',size=19)
    f.box(390,130,190,85,'同一inode\n硬链接计数=2',size=19);f.box(730,140,180,65,'文件数据',size=19)
    f.line(250,110,390,155);f.line(250,220,390,193);f.line(580,172,730,172)
    f.box(40,310,220,60,'符号链接文件',size=19);f.box(390,310,250,60,'内容：目标路径/u/f1',size=18)
    f.line(260,340,390,340);f.path('M640,340 L680,340 L680,275 L15,275 L15,110 L40,110',dash=True)
    f.text(480,55,'名字与对象分离：删除一个名字不必删除数据',17)
    fs.append(f.finish())

    f=Figure('OS_io_path',960,430,'阻塞读未命中缓存：请求提交与完成通知')
    xs=[25,260,495,730]
    for x,t in zip(xs,['应用与I/O库','系统调用/设备无关层','设备驱动程序','控制器与设备']):f.box(x,85,205,65,t,size=17)
    for x in xs[:-1]:f.line(x+205,117,x+235,117)
    f.box(730,275,205,65,'设备完成：发中断',size=17);f.line(832,150,832,275)
    f.box(495,275,205,65,'中断处理：确认完成',size=17);f.line(730,307,700,307)
    f.box(260,275,205,65,'标记数据可用并唤醒',size=17);f.line(495,307,465,307)
    f.box(25,275,205,65,'再获CPU，复制并返回',size=17);f.line(260,307,230,307)
    f.text(480,216,'请求者等待I/O时阻塞；CPU可运行其他进程',19)
    f.text(480,398,'命中缓存时可省去设备分支；DMA搬运与完成中断可以配合使用。',18)
    fs.append(f.finish())

    f=Figure('OS_buffer_timeline',1000,560,'【2011】前三块的输入、复制与分析（单位：μs）')
    left=130;scale=1.62
    for base,title,single in [(95,'单缓冲',True),(320,'双缓冲',False)]:
        f.text(40,base-15,title,19,anchor='start')
        for row,l in enumerate(['设备输入','复制','CPU分析']):f.text(115,base+row*48+24,l,17,anchor='end')
        for k in range(3):
            st=k*(150 if single else 100)
            for row,a,b,lab in [(0,st,st+100,f'入{k+1}'),(1,st+100,st+150,f'复{k+1}'),(2,st+150,st+200,f'析{k+1}')]:
                f.box(left+a*scale,base+row*48,(b-a)*scale,35,lab,fill=GRAY if row!=1 else '#e4eef4',size=16)
        for t in range(0,501,50):f.text(left+t*scale,base+165,t,15)
    f.text(500,515,'单缓冲：第10块1500完成复制，1550完成分析。\n双缓冲：1000+50+50=1100。',17)
    fs.append(f.finish())

    f=Figure('OS_scan',1000,340,'【2015】SCAN：58→130→180→199→42→15')
    scale=4.2;left=70
    f.line(left,95,left+199*scale,95,False)
    for t in [0,15,42,58,130,180,199]:
        x=left+t*scale;f.line(x,87,x,103,False);f.text(x,72,t,17)
    seq=[58,130,180,199,42,15]
    for i in range(len(seq)-1):
        y=130+i*29;f.line(left+seq[i]*scale,y,left+seq[i+1]*scale,y)
    f.text(500,308,'向内为编号增大；总距离(199−58)+(199−15)=325，服务完15即停止。',19)
    fs.append(f.finish())
    (ROOT/'editorial/full/OS/figures.json').write_text(json.dumps(fs,ensure_ascii=False,indent=2))
    print(json.dumps({'figures':len(fs),'formats':['SVG','PNG','PDF']},ensure_ascii=False))

if __name__=='__main__': build()
