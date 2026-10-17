#!/usr/bin/env python3
"""Build editable CN SVG and matching PNG/PDF figures; no external data inputs."""
from pathlib import Path
from html import escape
import argparse, json, subprocess
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only-protocol-formats',action='store_true',help='只重建本轮新增的四种报文/帧格式图；保留既有图产物')
args=parser.parse_args()
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
        meta={'id':name,'svg':f'figures/{name}.svg','png':f'figures/{name}.png','pdf':f'figures/{name}.pdf','width':self.w,'height':self.h}
        if args.only_protocol_formats and name not in {'CN16_ipv4_header','CN17_tcp_header','CN18_udp_header','CN19_ethernet_frame'}:
            return meta
        f=OUT/(name+'.svg');f.write_text('\n'.join(self.p+['</g></svg>']),encoding='utf-8')
        for ext in ('png','pdf'):
            cmd=['inkscape',str(f),'--export-type='+ext,'--export-filename='+str(OUT/(name+'.'+ext))]
            if ext=='png':cmd+=['--export-dpi=150']
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        return meta
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
# 16--19: textbook packet formats. Fixed header rows use the same 32-bit scale.
# The models are exported so independent verification can compare every boundary.
formats={
 'ipv4':{'row_bits':32,'fixed_bytes':20,'length_unit_bytes':4,'total_length_unit_bytes':1,'fragment_offset_unit_bytes':8,
  'rows':[
   [('版本',4),('IHL',4),('区分服务',8),('总长度',16)],
   [('标识',16),('标志',3),('片偏移',13)],
   [('TTL',8),('协议',8),('首部检验和',16)],
   [('源IPv4地址',32)],[('目的IPv4地址',32)]],
  'options_padding_bytes':[0,40],'checksum_scope':['header'],'pseudoheader_transmitted':False},
 'tcp':{'row_bits':32,'fixed_bytes':20,'data_offset_unit_bytes':4,'reserved_bits':6,
  'rows':[
   [('源端口',16),('目的端口',16)],[('序号 seq',32)],[('确认号 ack',32)],
   [('数据偏移',4),('保留',6),('URG',1),('ACK',1),('PSH',1),('RST',1),('SYN',1),('FIN',1),('接收窗口',16)],
   [('检验和',16),('紧急指针',16)]],
  'options_padding_bytes':[0,40],'checksum_scope':['pseudoheader','header','data'],'pseudoheader_transmitted':False},
 'udp':{'row_bits':32,'fixed_bytes':8,'length_unit_bytes':1,
  'rows':[[('源端口',16),('目的端口',16)],[('UDP长度',16),('检验和',16)]],
  'checksum_scope':['pseudoheader','header','data'],'pseudoheader_transmitted':False},
 'ethernet_ii':{'vlan_tags':0,'header_bytes':14,'frame_bytes':[64,1518],
  'fields':[('目的MAC',6),('源MAC',6),('类型',2),('数据及填充',[46,1500]),('FCS',4)],
  'preamble_bytes':7,'sfd_bytes':1,'ifg_bit_times':96,'mtu_bytes':1500,
  'fcs_scope':['目的MAC','源MAC','类型','数据及填充']}}

def bit_ruler(s,x,y,step):
    s.text(x-14,y-13,'位',16,'end')
    for i in range(33):s.line(x+i*step,y-7,x+i*step,y, width=1)
    for i in range(32):s.text(x+(i+.5)*step,y-14,i,12)
    s.text(x+16*step,y-42,'每行32 bit = 4 B；固定字段按位宽等比例绘制',19)

def header_rows(s,model,x=155,y=114,step=28,rh=66):
    bit_ruler(s,x,y-12,step)
    for row_index,row in enumerate(model['rows']):
        yy=y+row_index*rh;pos=0
        s.text(x-18,yy+rh/2+6,f'{row_index*4} B',17,'end')
        for label,bits in row:
            xx=x+pos*step;ww=bits*step
            s.box(xx,yy,ww,rh,fill=GRAY if row_index%2==0 else 'white')
            if label in ('URG','ACK','PSH','RST','SYN','FIN'):
                for j,c in enumerate(label):s.text(xx+ww/2,yy+19+j*18,c,15)
            elif label=='数据偏移':
                s.text(xx+ww/2,yy+23,'数据偏移',17);s.text(xx+ww/2,yy+49,'4 bit',16)
            elif label=='标志':
                s.text(xx+ww/2,yy+21,'标志3 bit',15)
                for j,lab in enumerate(['0','DF','MF']):
                    if j:s.line(xx+j*step,yy+30,xx+j*step,yy+rh,width=1)
                    s.text(xx+(j+.5)*step,yy+53,lab,13)
            else:
                s.text(xx+ww/2,yy+28,label,21 if bits>=8 else 18)
                s.text(xx+ww/2,yy+53,f'{bits} bit',16)
            pos+=bits
        assert pos==32
    return y+len(model['rows'])*rh

def variable_header(s,x,y,step=28):
    # This compressed band is NOT one 32-bit row. Its symbolic division is dashed.
    s.box(x,y,32*step,78)
    split=x+26*step;s.line(split,y,split,y+78,dash=True,width=1)
    s.text(x+13*step,y+30,'选项（长度可变）',21)
    s.text(x+13*step,y+58,'选项与填充合计0～40 B，即0～10个32 bit行',18)
    s.text(split+3*step,y+30,'填充',20);s.text(split+3*step,y+58,'0～3 B',18)
    s.text(x-18,y+31,'20 B起',17,'end');s.text(x+16*step,y+108,'可变区压缩示意；虚线分界随选项长度改变，首部总长须为4 B的整数倍',18)
    return y+130

s=SVG(1180,720);s.text(590,32,'IPv4首部与数据的边界',26,weight='bold')
end=header_rows(s,formats['ipv4']);end=variable_header(s,155,end)
s.box(155,end,896,48,'IP数据：起点为4×IHL B；长度为总长度−4×IHL B',GRAY,21)
s.text(590,end+83,'IHL取5～15：首部20～60 B；总长度16 bit，以B计，最大65535 B',20)
s.text(590,end+119,'片偏移13 bit，以8 B计；DF=1禁止分片，MF=1表示后面还有分片',20)
figs.append(s.save('CN16_ipv4_header'))

s=SVG(1180,790);s.text(590,32,'TCP首部：主书采用的经典六控制位格式',25,weight='bold')
end=header_rows(s,formats['tcp']);end=variable_header(s,155,end)
s.box(155,end,896,48,'TCP数据：起点为4×数据偏移 B；序号按数据字节编号',GRAY,21)
s.text(590,end+83,'数据偏移取5～15：首部20～60 B；窗口16 bit，无扩大选项时以B计',20)
s.text(590,end+119,'保留6 bit + 六个1 bit控制位；控制位由左到右为URG、ACK、PSH、RST、SYN、FIN',18)
s.text(590,end+155,'检验和覆盖伪首部、TCP首部和数据；伪首部只参与计算，不随TCP段传送',20)
s.text(590,end+190,'MSS只限制TCP数据长度；cwnd由发送端维护，不是首部中的窗口字段',20)
figs.append(s.save('CN17_tcp_header'))

s=SVG(1180,470);s.text(590,32,'UDP首部固定8 B：四个字段各16 bit',26,weight='bold')
end=header_rows(s,formats['udp'],rh=68)
s.box(155,end,896,64,'UDP数据（可为0 B）：UDP长度−8 B',GRAY,22)
s.text(590,end+101,'UDP长度以B计，包含首部与数据，最小8；源端口不需回信时可为0',20)
s.text(590,end+140,'检验和覆盖伪首部、UDP首部和数据；伪首部不随UDP数据报传送',20)
s.text(590,end+179,'IPv4中全0检验和字段表示未启用；算得0时填FFFF；IPv6通常要求启用',20)
figs.append(s.save('CN18_udp_header'))

s=SVG(1200,610);s.text(600,32,'Ethernet II（DIX V2）：无802.1Q标签的MAC帧',25,weight='bold')
x=100;y=130;widths=[180,180,110,390,130]
labels=[('目的MAC','6 B'),('源MAC','6 B'),('类型','2 B'),('上层PDU + 必要填充','合计46～1500 B'),('FCS','4 B')]
header_end=x+sum(widths[:3]);data_end=x+sum(widths[:4]);frame_end=x+sum(widths)
s.line(x,87,header_end,87);s.line(x,81,x,100);s.line(header_end,81,header_end,100)
s.text((x+header_end)/2,73,'MAC帧头：14 B（6+6+2）',21)
cur=x
for w,(lab,sz) in zip(widths,labels):
    s.box(cur,y,w,78,fill=GRAY if lab.startswith('上层') else 'white')
    s.text(cur+w/2,y+31,lab,19);s.text(cur+w/2,y+61,sz,19);cur+=w
s.line(x,237,frame_end,237);s.line(x,228,x,245);s.line(frame_end,228,frame_end,245)
s.text((x+frame_end)/2,271,'完整MAC帧：目的MAC起至FCS止，共64～1518 B',22,weight='bold')
s.line(x,299,data_end,299);s.line(x,292,x,306);s.line(data_end,292,data_end,306)
s.text((x+data_end)/2,332,'FCS校验范围：目的MAC至数据/填充；不含前导码、SFD和FCS自身',19)
phy=[(100,180,'前同步码','7 B'),(280,110,'SFD','1 B'),(390,520,'上述完整MAC帧','64～1518 B'),(910,180,'帧间间隔','≥96 bit时间')]
for xx,w,lab,sz in phy:
    s.box(xx,372,w,69,fill=GRAY if lab=='上述完整MAC帧' else 'white')
    s.text(xx+w/2,398,lab,19);s.text(xx+w/2,426,sz,18)
s.text(600,476,'线路发送次序如上；前同步码与SFD合计8 B，在MAC帧之外',20)
s.text(600,511,'帧间间隔是空闲时间，不是帧字段；图中各字段宽度不按字节数比例绘制',19)
s.text(600,546,'以太网MTU=1500 B：只限制所承载的上层PDU，不含MAC帧头与FCS',20)
s.text(600,581,'40 B的IP数据报需填6 B；IP总长度仍为40 B，MAC帧为64 B',20)
figs.append(s.save('CN19_ethernet_frame'))
data={'schema_version':1,'figures':figs,'shared_values':{'bits':[1,0,1,1,0,0],'nav':{'sifs_us':28,'data_bytes':1998,'rate_mbps':54,'data_us':296,'ack_us':2,'remaining_sifs':2,'nav_us':354},'fragment':{'total':1580,'header':20,'mtu':800,'payloads':[776,776,8],'offsets':[0,97,194],'mf':[1,1,0]},'tcp2025':{'mss':1000,'cwnd_before':2000,'ssthresh':8000,'seqs':[2001,3001],'ack_seq':3001,'rwnd':4000,'remaining_segments':2}},'semantic_colors':{'ink':INK,'emphasis':ACCENT,'state_fill':GRAY},'black_white':'所有图通过字段、标签、位置、实虚线区别；颜色不单独编码状态'}
data['schema_version']=2
data['protocol_formats']=formats
(OUT/'CN_model_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
rebuilt=4 if args.only_protocol_formats else len(figs)
print(f'CN figures rebuilt: {rebuilt}; registered: {len(figs)} (SVG/PNG/PDF each)')
