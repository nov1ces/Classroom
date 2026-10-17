#!/usr/bin/env python3
"""Refresh CN-only chapter/example/source ledgers without touching shared exports."""
from pathlib import Path
import csv, hashlib, json, re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BOOK='/workspace/study_analysis/v2/books/王道2027计算机网络_高清带书签版.pdf'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

specs=[
 (3,'3-12',2017,47,'双向 GBN：确认号、回绕与重传要分开追踪',False,'3.4',7,[83],[89],[11],4,
  ['CN-03-05','CN-03-07'],['双向GBN分离累计确认与接收期待状态','模8回绕及超时重传更新捎带确认','长捎带确认计入利用率周期'],
  '新增双向状态与回绕的完整综合题，连接单向窗口计算与实际事件轨迹',
  '删除会失去失序R3不滑接收窗、重传时更新确认号与双向长确认的联合推算',
  '3帧S0,0/S1,0/S2,0；新发5帧S5,2至S1,2；重传3帧首S2,3；最大利用率50%',
  'CN20_gbn_2017'),
 (4,'4-10',2018,47,'等分子网后，主机余量与分片分别计算',False,'4.2',15,[174,175],[191],[11],2,
  ['CN-04-07','CN-04-08'],['等分CIDR后扣主机与路由接口地址','按8B对齐分片并守恒原数据'],
  '完整串联子网等分、余量与跨MTU分片，避免只做孤立公式',
  '删除会失去现有地址约束下45台余量及1500B分成776/704B的联合过程',
  '广播192.168.1.127；技术192.168.1.128/25；45台；数据776/704B，偏移0/97',
  'CN21_subnet_fragment_2018'),
 (4,'4-11',2013,47,'覆盖性聚合必须保留更具体的直连例外',False,'4.4',4,[212,213],[219],[11],3,
  ['CN-04-09','CN-04-15','CN-04-18'],['按出口聚合并保留更具体例外','最长前缀匹配覆盖路由','AS边界BGP由TCP承载'],
  '补足聚合并非仅精确折叠、必须与例外路由配合的完整真题',
  '删除会失去/23覆盖与E0的/25例外如何共同实现最少三项路由表',
  '3项：153.14.5.0/24经S0，194.17.20.0/23经S1，194.17.20.128/25直连E0；E0；BGP/TCP',
  'CN22_aggregate_2013'),
 (4,'4-12',2024,47,'RIP逐轮传播与BGP出口选择是两条过程',True,'4.4',6,[214],[219,220],[12],5,
  ['CN-04-16','CN-04-17','CN-04-18'],['首次交换t=0的RIP同步传播','TTL边界与RIP跳数区别','BGP会话和UPDATE','先AS路径再域内出口距离'],
  '完整保留五问，补动态路由从静态定义到逐轮传播与出口选择的过程',
  '删除会失去首轮不额外计30s及BGP跨域路径与IGP出口距离的分工',
  'OSPF；TTL16；30s/60s；eBGP、UPDATE、iBGP；R14选R11、R15选R13',
  'CN23_routing_2024'),
 (4,'4-13',2025,47,'卫星链路：瓶颈速率、窗口与VLSM各有约束',False,'4.2',18,[176,177],[192,193],[12],3,
  ['CN-04-08','CN-03-07','CN-01-03'],['两段卫星单向传播与瓶颈','80%利用率反推GBN窗口位数','既有主机掩码锁定VLSM划分'],
  '以最新完整综合题连接性能、可靠传输和有约束VLSM',
  '删除会失去1500B/200kbps/240ms模型的窗口下界与H地址约束下唯一三子网划分',
  '240ms、200kb/s、理想下界400ms；W至少8、4bit；作业64/26、管理0/26、生活128/25',
  'CN24_satellite_2025'),
 (5,'5-8',2012,47,'从完整字节表同时读出握手、填充与已确认数据',True,'5.3',13,[266,267],[276],[11],3,
  ['CN-05-04','CN-05-05','CN-03-15','CN-04-07','CN-04-10'],['网络字节序逐字段解码','SYN及累计确认分离应用字节','以太网填充与IP/TCP长度边界','TTL差匹配NAT前后同包'],
  '保留完整6行40B数据与三问，补报文到链路的跨层解析',
  '删除会失去从原始报文字节同时验证三次握手、6B填充、16B应用数据和15跳',
  'H发1/3/4；握手1/2/3；填充3/5各6B；S已收16B；15路由器',
  'CN25_packets_2012'),
 (5,'5-9',2016,41,'接收缓存只进不出，窗口最终怎样归零',True,'5.3',14,[267,268],[276,277],[5,6],4,
  ['CN-05-05','CN-05-07','CN-05-08','CN-05-09'],['逐ACK更新cwnd与剩余rwnd','零窗口五轮计时与字节序号','持续计时器边界','被动方最短释放1.5RTT'],
  '完整四问连接握手、逐ACK窗口、接收缓存耗尽、性能和释放时序',
  '删除会失去第8ACK与轮末不同、第五轮受缓存限制、零窗口终点和S释放时间',
  'SYN=ACK=1、ack101；rwnd12KB/cwnd9KB/send9KB；seq20581，163.84kb/s；300ms',
  None),
 (6,'6-8',2023,47,'FTP上传时，把连接、字节号与拥塞轮次放到同一时间轴',False,'6.3',4,[292],[294,295],[11],4,
  ['CN-06-04','CN-05-04','CN-05-08','CN-05-09'],['FTP双连接与一次传输的生命周期','SYN/FIN字节号','阈值内ACK与轮末cwnd区别','从数据SYN到末ACK的完整计时'],
  '将FTP知识与18段上传的完整TCP过程相连，不以协议名判断替代推演',
  '删除会失去ACK2101的轮内3MSS、7101的5MSS及包含握手的60ms上传时序',
  '控制持久/数据非持久，登录控制；101/18102；3MSS/5MSS；60ms，2.4Mb/s',
  'CN26_ftp_2023'),
 (6,'6-9',2021,47,'从DNS到HTTP，交换机只学习实际发送者',False,'6.5',4,[310],[314],[11],3,
  ['CN-06-02','CN-06-03','CN-06-08','CN-04-11','CN-03-19'],['DNS→ARP→交换学习→TCP→HTTP依赖链','按源MAC与入端口学习','已知单播避免持续泛洪','新DNS查询假设与缓存边界'],
  '补足应用访问与实际二层事件链，说明未发送主机为何不被学习',
  '删除会失去两次ARP前后交换表变化、H2只收广播以及DNS缓存条件边界',
  'DNS/UDP/IPv4/Ethernet II；cc→4、bb→1、aa→2；新查询流程2个广播ARP请求',
  'CN27_dns_switch_2021'),
]

adaptations={
 '5-8':'社区复原卷第2包首字节43、主书45；第3包控制字节50 f0、主书50 10。正文及图采用主书45/50 10，显式标【2012】改编。第3包校验和2b32、第4包e655及其余源字节保留，不擅自修正未考查的校验和。',
 '5-9':'主书共用题图R2 E0侧为201.1.2.0/24，与DNS 201.1.1.1不一致；社区PDF第5页为201.1.1.0/24。沿用已交付CN14的201.1.1.0/24，标【2016】改编。第4页仅共用图说明，第5页实际图，第6页第41题题干。',
 '4-12':'社区复原卷有R13—R16直连边，主书题图及答案图无此边。本文明确采用无边图，标【2024】改编；分别计算两版传播集合，最终30s/60s相同不等于拓扑相同。',
}

records_path=ROOT/'editorial/full/CN/chapter_records.json'
d=json.loads(records_path.read_text())
fig_data=json.loads((ROOT/'figures/CN_model_data.json').read_text())
figures={x['id']:x for x in fig_data['figures']}
cases=[]
for (chapter,num,year,q,title,adapt,section,bq,qp,ap,ep,parts,kids,methods,reason,deletion,answer,figure) in specs:
 c=d['chapters'][chapter-1];p=ROOT/c['manuscript'];body=p.read_text();anchor='cn-ex'+num
 heading=re.search(r'^### 例 '+re.escape(num)+r'\u3000([^\n]+) \{#'+anchor+r'\}',body,re.M)
 assert heading,title
 source={
  'year':year,'national_question_number':q,'score':7 if year==2018 else 9,
  'exam_pdf':f'editorial/sources/exams/exam_{year}_rebuild.pdf','exam_pdf_physical_pages':ep,
  'exam_source_type':'社区二手复原完整卷，不是官方原版或官方答案；只用于题面/年份题号交叉核对',
  'book':BOOK,'book_section':section,'book_question_number':bq,
  'book_question_pdf_physical_pages':qp,'book_answer_pdf_pages':ap,
  'question_parts':parts,'options':'综合题无选择项，所有原设问保留',
  'evidence':{
   'community_transcription':f'editorial/revision3/CN_sources/{year}_{q}_community_question.txt',
   'book_question_images':[f'editorial/revision3/CN_sources/book_p{x:03}.png' for x in qp],
   'book_answer_images':[f'editorial/revision3/CN_sources/book_p{x:03}.png' for x in ap],
   'community_question_images':[f'editorial/revision3/CN_sources/exam_{year}_p{x}.png' for x in ep if (HERE/f'exam_{year}_p{x}.png').exists()],
   'independent_calculation':'editorial/revision3/CN_independent_sources/independent_verification.py',
   'independent_results':'editorial/revision3/CN_independent_sources/results.json'},
  'authentication_boundary':'核对本地主书、社区复原卷及独立解答，不声称取得官方原卷/官方答案认证',
 }
 if year==2021:source['evidence']['community_question_images'].append('editorial/revision3/CN_sources/exam_2021_p11_full.png')
 verification='已实际图读主书题面、答案及社区关键题页；核对年份题号、全部设问、数值和必要图；独立复算通过；不称官方答案认证'
 note=adaptations.get(num,'统一术语/标点/单位和等义表述；保留全部原条件、数据、设问及必要图，非选择题不虚构选项。')
 ex={'id':'EX-CN-'+num,'number':num,'title':title,'anchor':anchor,'location':c['manuscript']+'#'+anchor,
  'marker':f'【{year}】'+('改编' if adapt else ''),'category':'408真题改编' if adapt else '408真题',
  'priority':1,'is_personal_error':False,'personal_error_ids':[],'knowledge_ids':kids,'methods':methods,
  'source':source,'verification':verification,'difficulty':'综合','selection_reason':reason,
  'deletion_check':deletion,'additional_value':deletion,'answer':answer,'rewriting_note':note,
  'revision3':True,'original_identity':f'{year}年408第{q}题','all_parts_preserved':True}
 c['examples']=[x for x in c['examples'] if x['id']!=ex['id']]+[ex]
 for item in c['knowledge']:
  if item['id'] in kids:
   item['example_ids']=list(dict.fromkeys(item['example_ids']+[ex['id']]))
   item['methods']=list(dict.fromkeys(item['methods']+methods))
 if figure:
  m=re.search(r'!\[([^\]]+)\]\('+figure+r'\.png\)\{#([^\s}]+)',body)
  f=dict(figures[figure],anchor=m[2],caption=m[1],status='已实际查看独立PNG并按源页核标签/连接/数据；本轮未做讲义PDF视觉检查')
  c['figures']=[x for x in c['figures'] if x['id']!=figure]+[f]
 else:
  c['reused_figures']=[dict(figures['CN14_dns_topology_2016'],anchor='cn-fig-window2016',
   caption='复用既有CN14；E0采用201.1.1.0/24，保留全拓扑',status='实际view独立PNG与社区共用题图核语义')]
 cases.append(ex)

for c in d['chapters']:
 for item in c['knowledge']:
  for ex in cases:
   if item['id'] in ex['knowledge_ids']:
    item['example_ids']=list(dict.fromkeys(item['example_ids']+[ex['id']]))
    item['methods']=list(dict.fromkeys(item['methods']+ex['methods']))

for c in d['chapters']:
 p=ROOT/c['manuscript'];t=p.read_text();c['sha256']=sha(p);c['characters']=len(t)
 for k in c['knowledge']:
  k['line']=next(i for i,line in enumerate(t.splitlines(),1) if '{#'+k['anchor']+'}' in line)
 c['checks']['revision3']='新增完整综合题全部设问/图/数据核源；旧例、知识ID和错题去向保留'
 c['checks']['pdf']='本轮未生成、打开或检查讲义PDF；源页与独立图只核内容语义'

checks=json.loads((ROOT/'editorial/full/CN/results.json').read_text())['count']
d['date']='2026-10-17'
d['counts'].update(full_examples=50,real_exam_examples=42,adapted_exam_examples=3,typical_and_personal_examples=5,figures=27,arithmetic_checks=checks)
d['status']='第三轮CN正文与9道综合题落盘、CN专属复算通过；讲义PDF导出由主编执行'
d['author_stage_status']=d['status']
d.setdefault('version2_source_reading_notes',d.get('source_reading_notes'))
d['source_reading_notes']='第三轮新增9题实际图读范围及冲突见editorial/revision3/CN_sources/case_manifest.json；第二轮既有记录保留，不冒充重新读取97条错题。'
old_manifest=HERE/'case_manifest.json'
reading={
 'book_pdf_physical_pages_actually_viewed':sorted({x for ex in cases for key in ['book_question_pdf_physical_pages','book_answer_pdf_pages'] for x in ex['source'][key]}),
 'community_pages_actually_viewed':{'2012':[11],'2013':[11],'2016':[5,6],'2017':[11],'2018':[11],'2021':[10,11],'2023':[11],'2024':[12],'2025':[12]},
 'source_review_scope':'直接view来源PNG，逐题核数据、图和全部设问；未把仅渲染/仅OCR当实际图读。2021另从社区源PDF保存并实际view第11页全页PNG，明确看见47题号、9分、完整题干与三问；第10页为前题，仅用于核对相邻页身份。',
 'new_figure_pngs_actually_viewed':[f'figures/CN{i:02}_'+next(x['id'].split('_',1)[1] for x in fig_data['figures'] if x['id'].startswith(f'CN{i:02}_'))+'.png' for i in range(20,28)],
 'reused_figure_png_actually_viewed':'figures/CN14_dns_topology_2016.png',
 'lecture_pdf_review':'未生成、未打开、未渲染、未做讲义分页/裁切/版面检查',
}
manifest={'subject':'CN','revision':3,'date':'2026-10-17','base_examples':41,'added_examples':9,
 'source_conditions':{'2016q41':{'receive_buffer_B':20*1024,'MSS_B':1024,'ISN':100,'RTT_ms':200,'ssthresh_B':32*1024,'ACK_each_segment':True,'buffer_consumption_B':0}},
 'classification':{'complete_exam_questions':6,'explicit_adaptations':3},'cases':cases,'adaptations':adaptations,
 'actual_reading':reading,'source_file_manifest':'editorial/revision3/CN_independent_sources/source_manifest.json',
 'original_figure_hashes':'editorial/revision3/CN_sources/prior_figure_hashes.json',
 'authentication_boundary':'本地主书与社区二手复原题面交叉核验；没有取得官方原卷/官方答案或官方2027大纲全文，不据此宣称正式大纲全文认证。'}
write(old_manifest,manifest)
d['revision3']={'date':'2026-10-17','report':'editorial/revision3/CN_revision.md','status':d['status'],
 'new_example_ids':[x['id'] for x in cases],'source_manifest':'editorial/revision3/CN_sources/case_manifest.json',
 'classification':manifest['classification'],'actual_reading':reading,'original_checks_retained':107,
 'checks_total':checks,'original_invariants':{'knowledge_ids':71,'base_full_examples':41,'supplied_error_routes':97,'prior_unique_figures':19},
 'original_examples_unchanged':True,'original_error_routes_unchanged':True,'new_unique_figures':8,
 'new_example_numbering_note':'应用层原有6-1～6-7，新题顺延为6-8和6-9；不按预拟6-5/6-6覆盖旧题',
 'authentication_boundary':manifest['authentication_boundary'],
 'lecture_pdf_layout_review':reading['lecture_pdf_review']}
write(records_path,d)

csv_path=ROOT/'editorial/full/CN/examples_register.csv'
with csv_path.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
new_ids={x['id'] for x in cases};rows=[x for x in rows if x['id'] not in new_ids]
for x in cases:
 row={k:x.get(k,'') for k in fields}
 for k in ['knowledge_ids','methods']:row[k]='；'.join(x[k])
 rows.append(row)
with csv_path.open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
with (HERE/'new_examples_register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows([x for x in rows if x['id'] in new_ids])
write(HERE/'source_evidence_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.suffix in {'.png','.txt'} })
print('CN-only ledgers refreshed: 50 examples, 71 anchors, 97 preserved error routes, 27 unique figures')
