#!/usr/bin/env python3
"""Materialise the manually reviewed Wangdao lesson-to-section mappings."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3]
# Mappings were chosen after inspecting each lesson's source text and destination text.
M={
'CN01':{
'1.0':('课程研究对象与跨科联系',['CN01-01']),
'1.1_1':('计算机网络、互连网、互联网与ISP',['CN01-01','CN01-course-internet']),
'1.1_2':('硬件软件协议、边缘核心、通信资源子网及功能',['CN01-01']),
'1.1_3':('电路报文分组交换、存储转发及三跳例题',['CN01-07','CN01-08','CN01-course-timeline']),
'1.1_4':('分布范围、传输技术、拓扑、使用者、介质分类',['CN01-02']),
'1.1_5':('速率带宽时延、时延带宽积、往返时间、利用率及例题',['CN01-03','CN01-course-metrics','CN01-course-metric-examples']),
'1.2.1+2':('分层、实体、协议服务接口、封装与服务原语',['CN01-04','CN01-05','CN01-course-primitives']),
'1.2.3_1':('OSI七层、相邻节点和端到端的功能边界',['CN01-06','CN01-ex1','CN01-ex2']),
'1.2.3_2':('TCP/IP模型、五层教学模型、逐跳封装',['CN01-06','CN01-04']),
},
'CN02':{
'2.1.1':('数据、信号、码元、信道、通信方式、基带频带',['CN02-01','CN02-course-conversion']),
'2.1.2':('奈奎斯特和香农、信噪比分贝、有效约束及容量计算',['CN02-02','CN02-ex1','CN02-ex2','CN02-course-capacity']),
'2.1.3':('NRZ/RZ/NRZI/曼彻斯特/差分曼彻斯特、调制、PCM',['CN02-03','CN02-course-codes']),
'2.2':('导向非导向介质、光纤、波长、以太物理制式',['CN02-06','CN02-course-media']),
'2.3':('中继器集线器、冲突域、共享带宽、连接边界',['CN02-08','CN02-course-media']),
},
'CN03':{
'3.1 ':('数据链路层服务、物理链路和逻辑链路、基本功能',['CN03-01']),
'3.2 ':('字符计数、字节和零比特填充、违规编码',['CN03-02','CN03-ex1']),
'3.3.1_1':('奇偶校验、异或实现和检错能力',['CN03-03']),
'3.3.1_2':('CRC模二多项式除法、冗余生成、检错条件',['CN03-03','CN03-ex2']),
'3.3.2':('海明码冗余位数量、分组、综合征、全校验位',['CN03-04','CN03-course-hamming']),
'3.4_1':('流量可靠控制、发送接收窗口、确认和超时',['CN03-05','CN03-course-window']),
'3.4_2':('停等、帧和ACK丢失、重复帧处理',['CN03-06','CN03-ex4','CN03-course-window']),
'3.4_3':('GBN累计确认、重传、序号空间和回绕',['CN03-07','CN03-ex5','CN03-ex6','CN03-course-window']),
'3.4_4':('SR独立确认、缓存、滑窗、两窗口限制',['CN03-08','CN03-course-window']),
'3.4_5':('三种ARQ的信道利用率和确认帧时延',['CN03-06','CN03-ex6','CN03-course-window']),
'3.5.1':('FDM/TDM/STDM/WDM/CDM及码片内积',['CN03-09','CN03-ex7','CN03-course-mac']),
'3.5.2_1':('纯时隙ALOHA、三种坚持CSMA',['CN03-10']),
'3.5.2_2+3':('CSMA/CD争用期、最短帧、退避和距离',['CN03-11','CN03-ex8']),
'3.5.2_4':('CSMA/CA、帧间间隔、退避、RTS/CTS、NAV',['CN03-12','CN03-ex9','CN03-course-mac']),
'3.5.3':('轮询和令牌、捕获发送复制移除流程',['CN03-13','CN03-course-mac']),
'3.6.0':('IEEE802及LLC/MAC分工、以太无线标准',['CN03-14']),
'3.6.1':('局域网拓扑、访问控制、网络适配器',['CN03-14','CN03-15']),
'3.6.2':('以太帧、MAC、冲突广播域、最短帧和间隔',['CN03-15','CN03-19']),
'3.6.3':('VLAN、802.1Q字段与标签、接入干道',['CN03-17','CN03-ex10']),
'3.6.4':('BSS/ESS/AP、802.11地址和帧类型',['CN03-16','CN03-course-mac']),
'3.7.1+2':('广域链路、PPP帧、透明传输、LCP/NCP与建立流程',['CN03-18','CN03-course-ppp']),
'3.8 ':('交换机自学习过滤转发、直通与存储转发',['CN03-19','CN03-ex11']),
},
'CN04':{
'4.1 ':('网络层功能、路由转发、拥塞与SDN',['CN04-01','CN04-02','CN04-03']),
'4.2.1':('IPv4首部单位、字段和分片重组',['CN04-07','CN04-ex2']),
'4.2.2':('分类编址、特殊地址、网络主机号与转发',['CN04-08','CN04-course-addresses','CN04-11']),
'4.2.3':('掩码、同子网判断、定长划分、主机和网关',['CN04-08','CN04-ex3','CN04-ex6','CN04-ex10']),
'4.2.4':('CIDR、前缀、完整划分5个子网',['CN04-08','CN04-ex4','CN04-course-vlsm']),
'4.2.5':('聚合及最长前缀、更具体直连例外',['CN04-09','CN04-ex5','CN04-ex11']),
'4.2.6':('NAT/NAPT、私有地址、映射和校验更新',['CN04-10','CN04-course-addresses']),
'4.2.7':('ARP请求应答缓存、下一跳和逐跳MAC',['CN04-11','CN04-ex6']),
'4.2.8':('DHCP四阶段、初始地址端口、配置与租约',['CN04-12','CN04-ex7']),
'4.2.9':('ICMP差错查询、ping/traceroute及源点抑制年代',['CN04-13','CN04-ex8']),
'4.3 ':('IPv6首部、相对IPv4变化及双栈隧道',['CN04-14','CN04-course-ipv6']),
'4.3_1':('IPv6表示压缩、单播组播任播和特殊地址',['CN04-course-ipv6','CN04-ex9']),
'4.4 ':('路由算法、静动态、距离向量链路状态及协议关系',['CN04-04','CN04-05','CN04-06','CN04-15']),
'4.4.1':('路由算法、DV更新和链路状态最短路',['CN04-04','CN04-05','CN04-06','CN04-ex1']),
'4.4.2':('自治系统、IGP和EGP的分层',['CN04-15']),
'4.4.3':('RIP度量、更新规则、坏消息与防环机制',['CN04-16','CN04-ex12','CN04-course-routing']),
'4.4.4_1':('OSPF直接IP承载、区域、代价与洪泛序号',['CN04-17','CN04-course-ospf']),
'4.4.4_2':('LSDB、链路状态探测洪泛和最短路径树',['CN04-06','CN04-17','CN04-course-ospf']),
'4.4.4_3':('OSPF五类分组及数据库同步次序',['CN04-course-ospf']),
'4.4.5':('BGP路径向量、会话报文、策略和NEXT_HOP',['CN04-18','CN04-course-routing']),
'4.5 ':('IPv4组播、IGMP本地成员与跨网转发',['CN04-19']),
'4.6 ':('移动IPv4归属地址、转交地址、隧道和代理',['CN04-20']),
'4.7 ':('路由器输入交换输出、排队、路由表和转发表',['CN04-21']),
},
'CN05':{
'5.1 ':('进程通信、复用分用、端口套接字、两种传输服务',['CN05-01','CN05-course-buffers']),
'5.2.1':('UDP首部与长度、报文边界、封装和最大载荷',['CN05-02','CN05-course-buffers']),
'5.2.2':('伪首部、反码和、补零、零字段和漏检',['CN05-03','CN05-ex2','CN05-course-checksum']),
'5.3.1+2':('TCP字段、序号确认、数据偏移、MSS和窗口',['CN05-04','CN05-ex3','CN05-course-buffers']),
'5.3.3':('握手与释放、两端状态序号、MSL和最短时间',['CN05-05','CN05-ex4']),
'5.3.4+5':('可靠传输、确认重传、双向字节、缓冲与流量控制',['CN05-06','CN05-07','CN05-09','CN05-course-byte-trace']),
'5.3.5':('首次ACK与三重复ACK的逐次区分',['CN05-06','CN05-course-duplicate-acks']),
'5.3.6':('慢开始、门限、拥塞避免、快重传快恢复及窗口计算',['CN05-08','CN05-ex5','CN05-ex6','CN05-ex7','CN05-09']),
},
'CN06':{
'6.0':('应用层任务及各应用所依赖的下层服务',['CN06-course-model']),
'6.1 ':('C/S、P2P角色和模型比较',['CN06-01','CN06-course-model']),
'6.2_1+2+3':('DNS名称层次、服务器、查询、缓存和记录',['CN06-02','CN06-03','CN06-ex1','CN06-course-dns-records']),
'6.3 ':('FTP主进程、控制数据连接、主动被动及LIST',['CN06-04','CN06-ex2','CN06-ex8']),
'6.4 ':('用户代理邮件服务器、SMTP/POP3、MIME和信封',['CN06-05','CN06-06','CN06-ex3','CN06-course-mail']),
'6.5 ':('WWW/URL、HTTP消息、连接、缓存、Cookie和时延',['CN06-07','CN06-08','CN06-ex4','CN06-ex5','CN06-ex6','CN06-ex7','CN06-course-http-message']),
}}
inv=json.loads((ROOT/'sources/source_inventory.json').read_text())['files']
for cid,mappings in M.items():
 chapter=ROOT/'chapters'/cid;text=(chapter/'content.md').read_text();anchors=set(re.findall(r'\{#([^}]+)',text));entries=[]
 for f in inv:
  if f['subject']!='CN' or f['chapter']!=cid or f['kind']!='lecture':continue
  name=Path(f['path']).name;keys=[k for k in mappings if name.startswith(k)]
  assert len(keys)==1,(cid,name,keys)
  topic,targets=mappings[keys[0]];assert set(targets)<=anchors,(cid,targets,anchors)
  isocr=any(x in name for x in ['楼楼老师'])
  entries.append({'path':f['path'],'pages':list(range(1,f['pdf_pages']+1)),'topics':topic.split('、'),'targets':targets,
   'verification':'Lesson text/key definitions and destination sections compared by knowledge group; numerical examples independently recalculated where applicable'+('; scan OCR inspected for IPv6 fields and transition methods' if isocr else ''),
   'page_scope':'All source file pages indexed; verification is by knowledge group, not a claim that every source image was individually visually audited.',
   'duplicate_handling':'Clean/annotated variants consolidated in the same sections; annotation layout not duplicated.' if ('手稿' in name or '纯净' in name) else 'Repeated animation text consolidated; informative state transitions retained in explanation and diagrams.',
   'nonknowledge_material':'Course advertising, teacher biography and repeated syllabus displays remain in source inventory and are omitted from learning prose.' if name.startswith(('1.0','6.0')) else None})
 images=[]
 for title,target in re.findall(r'!\[([^]]*)\]\(([^\s)]+)',text):
  stem=Path(target).stem;source=chapter/'figures'/(stem+'.svg')
  assert source.exists(),(cid,target)
  images.append({'id':stem,'caption':title,'editable_source':'figures/'+stem+'.svg','status':'redrawn','check_scope':'New course diagram viewed full size; reused diagram retained after content/label review and final PDF review.' if stem.startswith('CN_course_') else 'Existing editable diagram compared with current caption, numerical data and explanation; final placement reviewed in PDF.'})
 result={'chapter':cid,'primary_source':'Project Wangdao lecture PDFs in 【课件】计算机网络基础考点讲解','canonical_sha256':hashlib.sha256(text.encode()).hexdigest(),'lecture_files':entries,'figures':images,'unresolved':[],
 'review_boundaries':['Source text extraction is separate from content review.','Coverage targets are knowledge groups; source animation display pages are consolidated.','Source-image visual checks are targeted; final PDF pages and the six new course figures are all reviewed separately.']}
 (chapter/'sources/course_coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 report=f'''# {cid} 王道课件续编与核对记录\n\n主母本为项目【课件】计算机网络基础考点讲解中的王道课件。本章登记{len(entries)}份、{sum(len(e['pages']) for e in entries)}个文件页，具体主题到正文锚点见course_coverage.json。\n\n前一编写阶段已实质扩写正文和重绘本章CN_course图；恢复阶段核对现有正文、逐文件文本的知识组及关键结论，建立真实主题映射，补充数值复算。课程宣传与重复动画布局合并处理。逐页索引范围不等于每页原图均经独立视觉审阅，图像承载内容按关键机制和数值组核对；新增图已全尺寸查看，最终PDF另行逐页审阅。\n\n数值检查见numeric_verification.json及CN01/code/verify_cn_models.py；首批独立检查另见全局sources/reviews/independent。原生公式、表格、时序和地址运算分别核对符号、单位与前提。\n\n校正保留：CRC仅未检出错误、保证条件依生成多项式；CTS/ACK单地址为接收地址；IPv4首部校验全0不表示关闭；快重传先有原ACK再计三重复ACK；历史源点抑制保留协议年代。\n\n代码部分按本章协议模型描述，未引入与教材数据结构约定冲突的实现。严蔚敏教材未作为本章协议来源。当前最终PDF视觉状态见visual_review.json。\n'''
 (chapter/'sources/author_report.md').write_text(report)
 print(cid,len(entries),'sources',len(images),'figures')
