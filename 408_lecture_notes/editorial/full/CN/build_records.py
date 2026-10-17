#!/usr/bin/env python3
"""Build editorial registers from delivered CN manuscripts and source records."""
from pathlib import Path
import json,re,hashlib,csv
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
load=lambda p:json.loads(p.read_text())
coverage=load(ROOT/'editorial/scope/CN_coverage.json')
errors=[r for r in load(ROOT/'editorial/errors/os_cn_errors.json') if r['subject']=='CN']
pack=load(ROOT/'editorial/full/sources/cn_candidates/candidate_sources.json')
pack={(r['year'],r['question']):r for r in pack}
book='/workspace/study_analysis/v2/books/王道2027计算机网络_高清带书签版.pdf'
# Explicit source identity, separate from student-facing markers.
sources={
'1-1':(2009,33),'1-2':(2022,33),'2-1':(2022,34),'2-2':('2.1',17),'2-3':(2023,33),'2-4':(2020,34),'2-5':(2018,34),
'3-1':(2013,37),'3-2':(2023,37),'3-3':(2025,34),'3-4':(2020,36),'3-5':(2009,35),'3-6':('3.4',19),'3-7':(2014,37),'3-8':(2009,37),'3-9':(2024,36),'3-10':('3.6',8),'3-11':(2013,38),
'4-1':(2021,37),'4-2':(2021,36),'4-3':(2023,39),'4-4':(2019,37),'4-5':(2018,38),'4-6':('4.2',43),'4-7':(2025,36),'4-8':(2010,36),'4-9':(2023,40),
'5-1':(2018,39),'5-2':(2024,39),'5-3':(2009,38),'5-4':(2022,39),'5-5':(2020,38),'5-6':(2025,38),'5-7':(2014,38),
'6-1':(2016,40),'6-2':(2009,40),'6-3':(2025,40),'6-4':(2024,40),'6-5':('6.5',12),'6-6':(2020,40),'6-7':(2022,40)}
# Teaching task and concrete loss if deleted; no frequency claims.
tasks={
'1-1':('区分一跳、主机间和进程端到端','失去端点范围决定最低服务层的真题判断'),
'1-2':('同叫流量控制时由相邻节点条件定位','失去相同功能在不同层次出现的边界检查'),
'2-1':('频率带宽→码元率→bit/s','失去奈氏计算和ASK状态数的完整转换'),
'2-2':('固定调制和噪声两个速率上界共同限制','失去提高SNR仍受固定状态数约束的边界'),
'2-3':('时延带宽积反求传播时间，逐组流水','失去BDP与存储转发组合的代表过程'),
'2-4':('虚电路逻辑状态与固定带宽分离','失去虚电路不必预留带宽的反例'),
'2-5':('MAC名称中的物理不等于物理层','失去按实际接口功能排除术语误导'),
'3-1':('跨字节连续计1与填充/去填充','失去透明传输的逐位执行例'),
'3-2':('CRC模2除法及检验通过的严格边界','失去按接收串逐项复算与原题措辞辨析'),
'3-3':('全部码字两两距离→保证检纠错数','失去最小码距的实际计算'),
'3-4':('停止等待数据/传播/ACK完整周期','失去长ACK对利用率的影响'),
'3-5':('GBN累计确认覆盖与重传区间','失去ACK缺号不等于帧需重传的模型'),
'3-6':('长ACK求所需窗口再求序号位数','失去两个不同单位约束连续转换'),
'3-7':('按目标站码解扩而非按接收站码','失去CDMA码片分组和带符号内积'),
'3-8':('最小帧限制往返传播和距离','失去单向/往返差2倍的可计算检查'),
'3-9':('CTS接收后剩余预约区间','失去NAV计时起点而非机械加间隔'),
'3-10':('标记帧与非标记帧首尾长度','失去42/46B载荷下限不同的题源边界'),
'3-11':('直通先读6B目的地址','失去转发时延和收整帧时延的区别'),
'4-1':('距离向量必须加本地邻接代价','失去逐网络候选和并列最短的计算'),
'4-2':('分片8B对齐、总长、偏移和MF','失去完整三片而非只给第二片答案的状态'),
'4-3':('非整字节前缀的网络与广播边界','失去/20跨第三字节块的地址计算'),
'4-4':('完整子网分割的前缀二叉树叶数','失去完整覆盖条件改变最小块的推理'),
'4-5':('连续对齐块精确聚合','失去共同前缀与块总量交叉检查'),
'4-6':('发送者掩码决定本地交付和下一跳MAC','失去/20非肉眼前三字节比较的实际纠正'),
'4-7':('DHCP初始Request尚未取得地址','失去阶段、源目的顺序和原图字段歧义的说明'),
'4-8':('历史ICMP类型与现行废弃标准','失去旧题答案不能直接作现行操作的来源边界'),
'4-9':('IPv6地址空间比例与基本首部','失去2^96与96倍、基本/扩展首部的辨析'),
'5-1':('UDP目的端口分用','失去进程端点与其他首部字段的辨析'),
'5-2':('反码求和端回卷再取反','失去校验和最易漏的一步实际演算'),
'5-3':('TCP连续字节区间和累计ACK','失去起始序号、载荷总长、末字节的联系'),
'5-4':('关闭最短时序与两端状态终点','失去2MSL从哪时刻开始及服务器等待末ACK'),
'5-5':('最长增长考虑拥塞避免而非默认翻倍','失去题干最值词改变增长模型的入口'),
'5-6':('新ACK只移除第一段，再减仍在途数据','失去rwnd/cwnd/FlightSize三量联合的完整例'),
'5-7':('超时恢复和固定接收窗口限制','失去达到rwnd后不再把cwnd当发送额度'),
'6-1':('DNS查询次数的计数主体和委派链','失去本地发出0/4与主机发出请求的区别'),
'6-2':('FTP控制/数据与TCP/UDP两个维度','失去命令通道及第一阶段的真题检查'),
'6-3':('邮件发送与读取角色及一连接多邮件','失去POP3会话非每封新连接的边界'),
'6-4':('非持久且串行，HTML也计对象','失去连接重复开销与对象总数检查'),
'6-5':('流水线不能消除HTML发现图片的依赖','失去已建连接计时起点与请求依赖'),
'6-6':('DNS缓存/逐级查询+TCP+HTTP依赖链','失去跨协议最短/最长请求模型'),
'6-7':('HTTP持久连接还受初始拥塞窗口约束','失去教材初始1MSS与现代较大初始窗口的边界')}
# Fallback two selected questions not requested in initial shared pack.
extra={
(2013,37):{'section':'3.2','number':1,'answer':'A','answer_pages':[67,68],'question_pages':[67],'rebuild_pages':[4],'evidence':['editorial/full/CN/source_checks/book_p67.png','editorial/full/CN/source_checks/book_p68.png','editorial/full/CN/source_checks/exam_2013_p4.png']},
(2018,38):{'section':'4.2','number':62,'answer':'C','answer_pages':[184],'question_pages':[169],'rebuild_pages':[4],'evidence':['editorial/full/CN/source_checks/book_p184.png','editorial/full/CN/source_checks/exam_2018_p4.png']}}
# Stable group headings are concrete locations, not only chapter-level assignment.
chapters=[];group_locations={};example_by_pair={};figdata=load(ROOT/'figures/CN_model_data.json')
for file in sorted((ROOT/'manuscript/CN').glob('[0-9][0-9]_*.md')):
 text=file.read_text();num=int(file.name[:2]);title=re.search(r'^# (.*?) \{',text).group(1)
 groups=[];examples=[];current=None
 for line_number,line in enumerate(text.splitlines(),1):
  m=re.match(r'## (.*?) \{#(cn-\d\d-\d\d)\}',line)
  if m:
   anchor=m.group(2);gid=anchor.upper();current=gid
   row=next(r for r in coverage if r['知识点 ID']==gid)
   location=f'{file.relative_to(ROOT)}#{anchor}'
   g={'id':gid,'title':row['知识点'],'anchor':anchor,'location':location,'heading':m.group(1),'line':line_number,'status':'已完成正文与技术复核；正式2027细目待核','learning_requirements':row['学习要求'],'source_baseline':'王道2027计算机网络考研复习指导；具体原章/节见来源清单','methods':[],'example_ids':[]}
   groups.append(g);group_locations[gid]=g
  m=re.match(r'### 例 (\d+-\d+)\u3000(.*?) \{#([^}]+)\}',line)
  if m:
   eid=m.group(1);display=m.group(2);anchor=m.group(3);src=sources[eid];task,loss=tasks[eid]
   if isinstance(src[0],int):
    year,q=src;r=pack.get((year,q));marker=f'【{year}】'
    if r:
     loc=r['wangdao_location'];a=r['answer_reference'];sec=loc['section'];n=loc['book_question_number'];answer=a['answer']
     source={'year':year,'national_question_number':q,'exam_pdf':f'editorial/sources/exams/exam_{year}_rebuild.pdf','exam_pdf_physical_pages':r['rebuild_pdf_pages'],'exam_source_type':'社区二手复原完整卷，不是官方原版/官方答案','book':book,'book_section':sec,'book_question_number':n,'book_question_horizontal_pdf_page':loc['horizontal_pdf_page'],'book_answer_pdf_pages':sorted(set(c['page'] for c in a['crops'])),'answer_reference':answer,'evidence':{'source_pack':f'editorial/full/sources/cn_candidates/{year}_{q}_text.txt','answer_images':[str(Path(v).relative_to(ROOT)) for v in r['answer_crop_images']]}}
    else:
     v=extra[(year,q)];sec=v['section'];n=v['number'];answer=v['answer'];source={'year':year,'national_question_number':q,'exam_pdf':f'editorial/sources/exams/exam_{year}_rebuild.pdf','exam_pdf_physical_pages':v['rebuild_pages'],'exam_source_type':'社区二手复原完整卷','book':book,'book_section':sec,'book_question_number':n,'book_answer_pdf_pages':v['answer_pages'],'answer_reference':answer,'evidence':v['evidence']}
    category='408真题';verification='已核对完整题意、数据、四选项、年份题号与题图；王道完整答案段及独立解答一致；不称官方答案认证'
   else:
    sec,n=src;marker=f'〖{sec}-{n:03}〗';r=next(r for r in errors if r['section']==sec and r['source']['error_json_question_number']==n);answer=r['actual_answer_information']['book_correct_answer'];source=r['source'].copy();source['answer_reference']=answer;category='王道典型题；兼个人错题身份';verification='已读取题干选项和主书答案段；独立计算通过；个人原作答不进入读者正文'
   er=[e['id'] for e in errors if e['section']==sec and e['source']['error_json_question_number']==n]
   ex={'id':f'EX-CN-{eid}','number':eid,'title':re.sub(r'[【〖].*','',display),'anchor':anchor,'location':f'{file.relative_to(ROOT)}#{anchor}','marker':marker,'category':category,'priority':1 if isinstance(src[0],int) else 2,'is_personal_error':bool(er),'personal_error_ids':er,'knowledge_ids':[current],'methods':[task],'source':source,'verification':verification,'difficulty':'综合' if eid in ['2-3','3-6','4-4','5-6','6-6','6-7'] else '基础至中等','selection_reason':task,'deletion_check':loss,'additional_value':loss,'answer':answer,'rewriting_note':'统一标点/单位书写与等义表述，未改条件、数值、设问、选项；图形重新绘制；具体勘误另记'}
   if eid=='4-1':ex['rewriting_note']='原5列表按A/B和C/D配对重排为3列，全部16个通告距离和选项保持'
   if eid=='3-9':ex['source_conflict']='复原卷误排DIFS=128s、SIFS≥28μs；王道扫描与N诺完整题文为128μs、28μs。正文采用后者；NAV起点后不含DIFS。完整来源处理记录另见source_review.md'
   if eid=='4-7':ex['source_conflict']='保留原题DHCPREQUEST中的yiaddr标记；按RFC2131邻近辨析Requested IP Address与yiaddr，不用错字段推导已分配地址'
   if eid=='6-7':ex['conditions']='题干未单列初始cwnd；题源答案采用1MSS教材模型，正文明确该假设，并对较大初始窗口作条件变式'
   examples.append(ex);example_by_pair[(sec,n)]=ex['id'];group_locations[current]['methods'].append(task);group_locations[current]['example_ids'].append(ex['id'])
 figures=[]
 for f in re.findall(r'!\[(.*?)\]\((CN[^)]+)\.png\)\{#([^ }]+)',text):
  desc,name,anchor=f;meta=next(r for r in figdata['figures'] if r['id']==name);figures.append({**meta,'anchor':anchor,'caption':desc,'status':'已独立看PNG并核图文数据；PDF合并后视觉检查由总构建记录'})
 chapters.append({'chapter':num,'title':title,'manuscript':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'knowledge':groups,'examples':examples,'figures':figures,'checks':{'range':'临时范围本章全部知识组有实质解释','correctness':'作者核条件、独立复算；跨科审校已读六章','style':'标题定位任务；无统一微节模板；自测明确原创','pdf':'等待全科统一构建及逐页检查'},'self_tests':{'category':'原创回顾题','purpose':'仅用于复述概念、核查已讲条件和最小边界，不替代真题主例；与正文答案就近分开','location':f'{file.relative_to(ROOT)}#cn-ch{num}-review'}})
# Assign all97 actual supplied questions, preserving source identity separately.
full={e for c in chapters for x in c['examples'] for e in x['personal_error_ids']}
practice={'ERR-CN-3.8-013','ERR-CN-4.7-018'}
repeat={'ERR-CN-1.2-015','ERR-CN-1.2-017','ERR-CN-1.2-023','ERR-CN-1.2-025','ERR-CN-1.2-028','ERR-CN-2.1-001','ERR-CN-2.1-016','ERR-CN-2.3-006','ERR-CN-3.6-003','ERR-CN-3.6-004','ERR-CN-3.6-023','ERR-CN-3.8-015','ERR-CN-4.1-006','ERR-CN-4.1-011','ERR-CN-4.2-021','ERR-CN-4.2-024','ERR-CN-4.2-042','ERR-CN-4.3-002','ERR-CN-4.3-005','ERR-CN-4.4-020','ERR-CN-5.3-029','ERR-CN-5.3-013','ERR-CN-6.3-005'}
error_records=[]
for r in errors:
 ids=r['knowledge_ids'];locations=[group_locations[k]['location'] for k in ids];pair=(r['section'],r['source']['error_json_question_number'])
 if r['id'] in full:destination='正文完整例题';target=example_by_pair[pair]
 elif r['id'] in practice:destination='复习练习保留；正文讲清计算入口，不重复重印原图';target=locations[0]
 elif r['id'] in repeat:destination='重复合并至知识解释或相关真题解析';target=locations[0]
 else:destination='并入正文辨析或短算例';target=locations[0]
 status='已读取原题、归类及登记实际去向；不推定个人心理错因'
 unresolved=[]
 if r['id']=='ERR-CN-4.1-003':unresolved=['原书路由器协议转换概括过宽；正文限定额外转换能力，不无条件重复书答案C']
 if r['id']=='ERR-CN-4.2-040':unresolved=['完整覆盖和原始地址块假设影响唯一结论；正文保留前缀树方法，不作为无条件完整例题']
 if r['id']=='ERR-CN-6.5-018':unresolved=['原题初始cwnd未独立明写；已邻近说明书答1MSS模型及改变初窗会改变答案']
 error_records.append({'id':r['id'],'subject':'CN','source':r['source'],'knowledge_ids':ids,'core_method':r['core_method'],'actual_answer_information':r['actual_answer_information'],'confirmed_personal_error_cause':r['confirmed_personal_error_cause'],'destination':destination,'target':target,'locations':locations,'reason':r['question_specific_correction'],'status':status,'conditions_or_source_issues':unresolved})
assert len(group_locations)==71 and len(error_records)==97 and len({r['id'] for r in error_records})==97
examples=[x for c in chapters for x in c['examples']]
assert len(examples)==41 and len([x for x in examples if x['priority']==1])==36
record={'subject':'CN','date':'2026-10-16','reader_standard':'用户确认样章深度；真题只【年】、非真只〖原节-三位题号〗；无个人原选或做题本名称','scope':'71组按本地临时范围；2027正式大纲细目未取得，不宣称正式版全覆盖已核验','main_source':'王道2027计算机网络考研复习指导，电子工业出版社2026年1月第1版，ISBN978-7-121-51786-0','chapters':chapters,'errors':error_records,'unresolved':[{'id':'CN-SCOPE-2027','status':'待核验','issue':'2027正式大纲细目全文未取得，依临时范围分配全部71组并写成正文'},{'id':'CN-SRC-2024-36','status':'已处理并保留版本记录','issue':'复原卷DIFS/SIFS误排，以主书扫描及独立题文旁证校正'},{'id':'CN-SRC-2025-36','status':'正文已限定','issue':'题图yiaddr字段原标记有规范问题，保留原图并在解析说明'},{'id':'CN-SRC-2022-40','status':'正文已限定','issue':'原题初始拥塞窗口未明给，书答1MSS模型与现代实现不等价'},{'id':'CN-PDF','status':'待主构建','issue':'15图PNG已看；全科PDF尚需目录、分页、公式/代码及全部页面视觉检查'}],'counts':{'chapters':6,'knowledge_groups':71,'full_examples':41,'real_exam_examples':36,'typical_and_personal_examples':5,'personal_errors_registered':97,'personal_errors_used_as_full_examples':len(full),'figures':15,'arithmetic_checks':67},'source_reading_notes':'97题原JSON、原题与书答行读取见前期OS/CN总台账；本轮重读CN题文及纠正点。36真题与二手完整卷、王道题文及书答交叉，不使用未核验年份标签冒认真题。作者实际查看5张全答案段联系表、3.2原页和2018聚合原页；来源子代理另核30题与全部图。','visual_record':'editorial/full/CN/visual/figure_visual_check.json','verification':'editorial/full/CN/results.json'}
(HERE/'chapter_records.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
with (HERE/'errors_destinations.csv').open('w',newline='',encoding='utf-8-sig') as f:
 cols=['id','knowledge_ids','destination','target','reason','status'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for r in error_records:w.writerow({k:'；'.join(r[k]) if isinstance(r[k],list) else r[k] for k in cols})
with (HERE/'examples_register.csv').open('w',newline='',encoding='utf-8-sig') as f:
 cols=['id','title','marker','category','priority','is_personal_error','knowledge_ids','methods','location','selection_reason','deletion_check','verification'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for r in examples:w.writerow({k:'；'.join(r[k]) if isinstance(r[k],list) else r[k] for k in cols})
print(json.dumps(record['counts'],ensure_ascii=False))
