#!/usr/bin/env python3
"""Build editable CN SVG and matching PNG/PDF figures; no external data inputs."""
from pathlib import Path
from html import escape
import json, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
ACCENT='#245579'; INK='#17212a'; GRAY='#eef1f3'
class SVG:
    def __init__(self,w,h):
        self.w=w;self.h=h
        self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#17212a"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="Noto Sans CJK SC, sans-serif" font-size="20" fill="#17212a" stroke-linejoin="round">']
    def text(self,x,y,t,size=20,anchor='middle',weight='normal',color=INK):
        self.p.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(str(t))}</text>')
    def line(self,x1,y1,x2,y2,arrow=False,dash=False,color=INK,width=2):
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def box(self,x,y,w,h,label='',fill='white',size=20,round=False):
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" stroke-width="2" rx="{8 if round else 0}"/>')
        if label:self.text(x+w/2,y+h/2+7,label,size)
    def circle(self,x,y,r,label):
        self.p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{INK}" stroke-width="2"/>');self.text(x,y+7,label)
    def path(self,d,color=INK,width=2):self.p.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def save(self,name):
        f=OUT/(name+'.svg');f.write_text('\n'.join(self.p+['</g></svg>']),encoding='utf-8')
        for ext in ('png','pdf'):
            cmd=['inkscape',str(f),'--export-type='+ext,'--export-filename='+str(OUT/(name+'.'+ext))]
            if ext=='png':cmd+=['--export-dpi=150']
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        return {'id':name,'svg':str(f.relative_to(ROOT)),'png':f'figures/{name}.png','pdf':f'figures/{name}.pdf','width':self.w,'height':self.h}
figs=[]
# 1 Encapsulation: boundaries distinguished by labels and fill.
s=SVG(980,390)
labels=[('应用数据',430,130),('TCP首部',310,120),('IP首部',220,90),('以太网首部',40,180)]
s.text(490,30,'应用 → TCP → IP → 当前链路',24,weight='bold')
s.box(430,65,440,46,'应用数据',GRAY)
s.box(310,135,120,46,'TCP首部');s.box(430,135,440,46,'应用数据',GRAY)
s.box(220,205,90,46,'IP首部');s.box(310,205,120,46,'TCP首部');s.box(430,205,440,46,'应用数据',GRAY)
s.box(40,275,180,46,'以太网首部');s.box(220,275,90,46,'IP首部');s.box(310,275,120,46,'TCP首部');s.box(430,275,440,46,'应用数据',GRAY);s.box(870,275,70,46,'FCS')
for x in (650,):
 for y in (115,185,255):s.line(x,y,x,y+16,arrow=True)
s.text(490,365,'同一IP分组到下一跳时，链路首部与FCS按下一链路重新封装',19)
figs.append(s.save('CN01_encapsulation'))
# 2 Packet pipeline, pure send slots with propagation omitted as stated.
s=SVG(980,380);s.text(490,30,'两段等速链路：每组发送时间 T，图中暂略传播时间',23,weight='bold')
for x,label in [(130,'H1'),(470,'路由器'),(810,'H2')]:s.text(x,78,label);s.line(x,95,x,330,arrow=True)
for k in range(3):
 y=108+k*56;s.line(130,y,470,y+56,arrow=True);s.text(280,y+14,f'分组{k+1}',19)
 y2=164+k*56;s.line(470,y2,810,y2+56,arrow=True);s.text(640,y2+14,f'分组{k+1}',19)
s.text(490,365,'第一组经历2T；随后每隔T完成一组，共(3+2−1)T',21)
figs.append(s.save('CN02_packet_pipeline'))
# 3 Line coding exact bit convention and initial level.
bits=[1,0,1,1,0,0];s=SVG(980,435);x0=235;step=105
s.text(490,29,'比特串101100；NRZ高=1，曼彻斯特低→高=0',22,weight='bold')
for i,b in enumerate(bits):s.text(x0+i*step+step/2,72,b,23)
for label,y in [('NRZ',135),('曼彻斯特',245),('差分曼彻斯特',355)]:
 s.text(200,y+6,label,20,'end');s.line(x0,y,x0+6*step,y,dash=True,color='#999999',width=1)
 for i in range(7):s.line(x0+i*step,y-38,x0+i*step,y+38,dash=True,color='#aaaaaa',width=1)
# Horizontal path at levels +/-25, each subinterval half-bit.
def waveform(vals,y):
 d=f'M {x0} {y-25 if vals[0] else y+25}'
 for j,v in enumerate(vals):
  xx=x0+(j+1)*step/2;yy=y-25 if v else y+25;d+=f' H {xx}'
  if j+1<len(vals):d+=f' V {y-25 if vals[j+1] else y+25}'
 s.path(d,width=3)
waveform([v for b in bits for v in (b,b)],135)
waveform([v for b in bits for v in ((1,0) if b else (0,1))],245)
prev=1;diff=[]
for b in bits:
 first=1-prev if b==0 else prev;second=1-first;diff.extend((first,second));prev=second
waveform(diff,355);s.text(490,420,'差分约定：起点跳变=0、不跳变=1；第一位之前电平为高',20)
figs.append(s.save('CN03_line_coding'))
# 4 GBN/SR same loss with intermediate buffer.
s=SVG(980,375);s.text(490,30,'0、1按序交付后，2丢失，3和4先到',23,weight='bold')
for y,label in [(105,'GBN'),(240,'SR')]:
 s.text(90,y+25,label,24,weight='bold')
 for i in range(2,5):s.box(190+(i-2)*125,y,95,50,str(i),GRAY if i==2 else 'white',24)
 s.text(237,y+86,'缺失',20)
 if label=='GBN':
  s.text(425,y+25,'×',32);s.text(550,y+25,'×',32);s.text(760,y+25,'失序帧丢弃',23)
  s.text(640,y+84,'超时重发2、3、4',21)
 else:
  s.text(760,y+25,'3、4进入缓存',23);s.text(640,y+84,'补到2后连续交付2、3、4',21)
figs.append(s.save('CN04_gbn_sr'))
# 5 NAV origin explicitly CTS end, exactly 2 SIFS.
s=SVG(980,340);s.text(490,30,'CTS接收结束 → NAV剩余时间',24,weight='bold')
parts=[('SIFS',100,28),('DATA',430,296),('SIFS',100,28),('ACK',95,2)]
x=120;y=115
s.line(65,y+125,930,y+125,arrow=True)
for lab,w,dur in parts:
 s.box(x,y,w,65,lab,GRAY if lab=='SIFS' else 'white',21);s.text(x+w/2,y+99,f'{dur} μs',20);x+=w
s.line(120,88,120,252,dash=True);s.text(120,70,'起点',20);s.text(490,290,'NAV = 28 + 296 + 28 + 2 = 354 μs',24,weight='bold');s.text(490,326,'各区段不按时长比例绘制',18)
figs.append(s.save('CN05_nav_2024'))
# 6 Learning table before/after.
s=SVG(980,360);s.text(490,30,'交换机：按源地址学习，按目的地址查表',23,weight='bold')
s.box(370,110,220,85,'交换机');
for x,y,lab,port in [(110,150,'A','1'),(810,95,'B','2'),(810,240,'C','3')]:
 s.box(x,y-24,90,50,lab);xx=x+90 if x<370 else x;s.line(xx,y,370 if x<370 else 590,150 if x<370 else (135 if lab=='B' else 175));s.text(330 if x<370 else 625,145 if lab!='C' else 206,port,20)
s.text(490,262,'① A→B：学A→1，未知B，向2、3泛洪',22)
s.text(490,313,'② B→A：学B→2，已知A，仅向1转发',22)
figs.append(s.save('CN06_switch_learning'))
# 7 Fragment data bands and table.
s=SVG(980,350);s.text(490,30,'原始数据1560 B；IP首部20 B，MTU800 B',23,weight='bold')
s.box(90,75,380,58,'0～775：776 B',GRAY);s.box(470,75,380,58,'776～1551：776 B');s.box(850,75,40,58,'',GRAY);s.text(869,165,'末8 B',19)
s.text(490,210,'第1片：总长796 B，偏移0，MF=1',22)
s.text(490,258,'第2片：总长796 B，偏移97，MF=1',22)
s.text(490,306,'第3片：总长28 B，偏移194，MF=0',22)
figs.append(s.save('CN07_ipv4_fragments'))
# 8 MAC/IP hop map.
s=SVG(980,390);s.text(490,30,'普通IP转发，无NAT',24,weight='bold')
s.box(65,85,130,65,'主机A');s.box(410,85,160,65,'路由器R');s.box(785,85,130,65,'主机B');s.line(195,118,410,118,arrow=True);s.line(570,118,785,118,arrow=True)
s.text(305,185,'A的MAC → R入口MAC',20);s.text(675,185,'R出口MAC → B的MAC',20)
s.box(110,225,760,55,'两跳IP地址：源=A的IP，目的=B的IP',GRAY,22)
s.text(490,330,'ARP查询当前下一跳；交换机转发同一帧不替换源MAC',20)
figs.append(s.save('CN08_ip_mac_hops'))
# 9 TCP handshake.
s=SVG(980,430);s.text(490,30,'连接建立：客户初始序号x，服务器初始序号y',23,weight='bold')
for x,lab in [(150,'客户C'),(830,'服务器S')]:s.text(x,80,lab,23);s.line(x,105,x,385,arrow=True)
for x1,y1,x2,y2,text in [(150,120,830,175,'SYN=1, seq=x'),(830,205,150,260,'SYN=1, ACK=1, seq=y, ack=x+1'),(150,290,830,345,'ACK=1, seq=x+1, ack=y+1')]:
 s.line(x1,y1,x2,y2,arrow=True)
 bg_y=(y1+y2)/2-39;s.p.append(f'<rect x="245" y="{bg_y}" width="490" height="29" fill="white"/>');s.text(490,(y1+y2)/2-15,text,21)
s.text(490,415,'SYN各占1个序号；纯ACK不占序号',21)
figs.append(s.save('CN09_tcp_handshake'))
# 10 Exact 2025 figure.
s=SVG(980,470);s.text(490,30,'MSS=1000 B；t₀窗口2000 B；门限8000 B',22,weight='bold')
for x,label in [(140,'甲'),(840,'乙')]:s.text(x,80,label,24);s.line(x,105,x,425,arrow=True)
s.text(110,132,'t₀',22);s.text(110,390,'t₁',22)
for a,b,c,d,lab in [(140,125,840,210,'seq=2001，1000 B数据'),(140,180,840,265,'seq=3001，1000 B数据'),(840,290,140,375,'seq=4001，ack_seq=3001，rcvwnd=4000 B')]:
 s.line(a,b,c,d,arrow=True)
 yy=(b+d)/2-17;s.p.append(f'<rect x="202" y="{yy-24}" width="576" height="30" fill="white"/>');s.text(490,yy,lab,21)
s.line(140,395,190,417,arrow=True)
s.text(490,455,'ACK只确认第一段；seq=3001的1000 B仍在途',21)
figs.append(s.save('CN10_tcp_window_2025'))
# 11 Exact DNS/Web topology.
s=SVG(980,450);s.text(490,30,'局域网时延忽略；到各远程服务器RTT=10 ms',22,weight='bold')
s.line(70,290,390,290,width=5);s.text(225,335,'局域网',21)
s.box(65,95,155,65,'本地DNS',size=21);s.line(140,160,140,290)
s.box(265,95,145,65,'路由器');s.line(335,160,335,290)
s.box(180,365,90,55,'H');s.line(225,290,225,365)
s.box(500,75,430,315,'',round=True)
s.text(715,110,'Internet',22,weight='bold');s.line(410,125,500,180)
for x,y,w,lab in [(525,140,185,'根域名服务器'),(525,230,185,'com顶级DNS'),(730,185,175,'abc.com权威'),(680,305,225,'www.abc.com')]:s.box(x,y,w,50,lab,size=19)
figs.append(s.save('CN11_dns_web_2020'))
# 12 HTTP pipeline after HTML.
s=SVG(980,410);s.text(490,30,'TCP已建立；忽略各对象传输时延',23,weight='bold')
for x,label in [(150,'浏览器'),(830,'Web服务器')]:s.text(x,80,label,23);s.line(x,100,x,365,arrow=True)
for x1,y1,x2,y2,t in [(150,115,830,150,'请求HTML'),(830,170,150,205,'返回HTML'),(150,240,830,275,'流水请求图1、图2、图3'),(830,295,150,330,'依次返回三个小图像')]:
 s.line(x1,y1,x2,y2,arrow=True);s.text(490,(y1+y2)/2-13,t,21)
s.text(490,398,'两层依赖：HTML 1RTT + 图片流水1RTT = 2RTT',21)
figs.append(s.save('CN12_http_pipeline'))
# 13 Preserve original problematic yiaddr labels, explained in text.
s=SVG(900,420);s.text(450,30,'新接入主机H与DHCP服务器192.168.5.1',23,weight='bold')
for x,label in [(125,'H'),(775,'DHCP服务器')]:s.text(x,85,label,23);s.line(x,110,x,370,arrow=True)
s.line(775,135,125,215,arrow=True);s.line(125,260,775,340,arrow=True)
s.box(290,120,320,85,'',GRAY);s.text(450,153,'DHCPOFFER',22);s.text(450,188,'yiaddr: 192.168.5.9',21)
s.box(290,245,320,85,'',GRAY);s.text(450,278,'DHCPREQUEST',22);s.text(450,313,'yiaddr: 192.168.5.9',21)
s.text(450,407,'题图保留原字段标注；其规范含义见紧邻题解',20)
figs.append(s.save('CN13_dhcp_2025'))
# 14 Reconstructed full shared topology (2016): retain all named nodes and addresses.
s=SVG(1100,675);s.text(550,30,'2016年题33—41共用网络拓扑',24,weight='bold')
s.box(30,65,235,90,'',round=True);s.text(148,96,'Internet');s.text(148,123,'Web S:130.18.10.1',19)
s.circle(390,105,37,'R1');s.circle(390,300,37,'R2');s.circle(880,300,37,'R3')
s.line(265,105,353,105);s.line(390,142,390,263);s.text(490,191,'201.1.3.9',19);s.text(360,241,'L0',19)
s.line(427,105,880,105);s.line(880,105,880,263)
s.line(427,300,843,300);s.text(470,282,'L1',19);s.text(645,282,'201.1.3.1',19)
s.box(30,255,225,70,'201.1.1.0/24',round=True);s.line(255,290,353,290);s.text(305,274,'E0',19)
s.box(40,365,205,60,'DNS 201.1.1.1',size=19);s.line(142,325,142,365)
s.box(925,260,160,65,'201.1.2.0/25',size=18,round=True);s.line(917,300,925,300)
s.box(290,425,200,60,'Switch');s.line(390,337,390,425);s.text(465,375,'E1:192.168.3.254',18)
s.box(690,425,150,60,'Hub');s.line(490,455,690,455)
for x,y,lab,ip in [(260,560,'H1','192.168.3.2'),(485,560,'H2','192.168.3.3'),(720,565,'H3','192.168.3.251'),(950,435,'H4','192.168.3.252')]:
 s.box(x-45,y,90,45,lab);s.text(x,y+75,ip,18)
 if lab in ('H1','H2'):s.line(360 if lab=='H1' else 425,485,x,y)
 elif lab=='H3':s.line(765,485,x,y)
 else:s.line(840,455,x-45,y+23)
s.text(340,220,'NAT',19)
s.text(550,660,'R1—R3为路由器；Switch/Hub为100Base-T；H1—H4默认DNS均为201.1.1.1',18)
figs.append(s.save('CN14_dns_topology_2016'))
# 15 Exact minimal line diagram 2023 q33.
s=SVG(980,210);s.text(490,30,'两段链路均为100 Mb/s、时延带宽积1000 bit',22,weight='bold')
s.box(35,85,130,70,'H1');s.box(400,85,180,70,'路由器');s.box(815,85,130,70,'H2');s.line(165,120,400,120);s.line(580,120,815,120)
s.text(280,95,'100 Mb/s',20);s.text(695,95,'100 Mb/s',20)
figs.append(s.save('CN15_two_links_2023'))
data={'schema_version':1,'figures':figs,'shared_values':{'bits':[1,0,1,1,0,0],'nav':{'sifs_us':28,'data_bytes':1998,'rate_mbps':54,'data_us':296,'ack_us':2,'remaining_sifs':2,'nav_us':354},'fragment':{'total':1580,'header':20,'mtu':800,'payloads':[776,776,8],'offsets':[0,97,194],'mf':[1,1,0]},'tcp2025':{'mss':1000,'cwnd_before':2000,'ssthresh':8000,'seqs':[2001,3001],'ack_seq':3001,'rwnd':4000,'remaining_segments':2}},'semantic_colors':{'ink':INK,'emphasis':ACCENT,'state_fill':GRAY},'black_white':'所有图通过字段、标签、位置、实虚线区别；颜色不单独编码状态'}
(OUT/'CN_model_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'CN figures built: {len(figs)} (SVG/PNG/PDF each)')
