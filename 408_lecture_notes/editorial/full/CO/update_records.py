#!/usr/bin/env python3
"""Refresh CO editorial ledger from already-read local evidence; no source-library dependency."""
from pathlib import Path
import json,re,hashlib,collections,csv
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
previous=json.loads((HERE/'chapter_records.json').read_text()) if (HERE/'chapter_records.json').exists() else {}
scope=json.loads((ROOT/'editorial/scope/CO_coverage.json').read_text())
sources=json.loads((HERE/'selected_source_locators.json').read_text())
src_by_id={r['id']:r for r in sources}
errors=[r for r in json.loads((ROOT/'editorial/errors/ds_co_errors.json').read_text())['records'] if r['subject']=='CO']
figs=json.loads((HERE/'figure_manifest.json').read_text())
knowledge_by_id={r['知识点 ID']:r for r in scope}

# Each selected exercise has a distinct operation, boundary or integrated task.
tasks={
'CO1-1':('CO-01-01 CO-01-02','机器语言作为普通CPU的直接执行接口'),
'CO1-2':('CO-01-03','按动态指令比例加权CPI并换算时间单位'),
'CO1-3':('CO-01-03','加速部分与未加速部分分别计时'),
'CO2-1':('CO-02-01','整数、小数分别换基数并检查合法数字'),
'CO2-2':('CO-02-03','无符号窄类型扩展的零扩展规则'),
'CO2-3':('CO-02-03','负的源值转宽无符号类型，避免错误零扩展'),
'CO2-4':('CO-02-04 CO-02-05','辨别取反输入与最低位加1，不重复求负'),
'CO2-5':('CO-02-02 CO-02-05','十六进制补码解码、数学差值和机器编码'),
'CO2-6':('CO-02-05','同一次减法的有符号溢出与无符号借位分别判定'),
'CO2-7':('CO-02-07','负二进制小数规格化、偏置阶码与字段拼接'),
'CO2-8':('CO-02-07','不完全转十进制，利用符号和指数比较负浮点数'),
'CO2-9':('CO-02-08','分开尾数暂时溢出与指数范围溢出'),
'CO2-10':('CO-02-02 CO-02-03 CO-02-05 CO-02-07 CO-02-08','完整求和程序：无符号循环边界、补码范围、binary32机器数、逐次舍入与有限/精确上界'),
'CO3-1':('CO-03-02 CO-03-03','DRAM行列地址复用，逻辑地址位不等于引脚数'),
'CO3-2':('CO-03-03 CO-03-05','MAR覆盖地址空间而非只覆盖当前已装容量'),
'CO3-3':('CO-03-04','低位交叉既查同体，也查请求间隔'),
'CO3-4':('CO-03-05','ROM/RAM分区，字扩展和位扩展分别计算'),
'CO3-5':('CO-03-06','寻道、半圈等待、扇区传输按同一单位相加'),
'CO3-6':('CO-03-07','读后写按两次访问统计，利用块内空间局部性'),
'CO3-7':('CO-03-08','路数、组数、标记位宽和比较器数量'),
'CO3-8':('CO-03-08 CO-03-10','数据区以外的标记、有效位和修改位'),
'CO3-9':('CO-03-11 CO-03-12','虚页号进制转换、存在位与原样页内偏移'),
'CO3-10':('CO-03-12','虚拟地址标记而非物理页框位数决定TLB匹配'),
'CO3-11':('CO-03-07 CO-03-08 CO-03-09 CO-03-11 CO-03-12','把数组地址、跨页缺页、组映射与两种遍历连成完整过程'),
'CO3-12':('CO-03-09 CO-03-12','用完整虚页序列逐项求TLB组选/标记并更新组内LRU，辨明虚址扩展只增加标记'),
'CO4-1':('CO-04-01','扩展操作码逐层保留前缀，避免编码重叠'),
'CO4-2':('CO-04-02','按取指后PC和带符号位移求转移目标'),
'CO4-3':('CO-04-03','先布局成员和填充，再确定小端低地址字节'),
'CO4-4':('CO-04-04','RISC的典型风格与流水实现的关系'),
'CO4-5':('CO-04-05','编译工具链的正确先后和各阶段输出'),
'CO4-6':('CO-04-02 CO-04-03 CO-04-06 CO-04-07 CO-02-06 CO-05-05','递归调用次数、call后继与相对位移、小端编码、宽类型乘法及溢出自陷的完整链'),
'CO5-1':('CO-05-01 CO-05-03','组合操作元件与保存状态的元件分别识别'),
'CO5-2':('CO-05-01 CO-05-02 CO-05-03 CO-05-04 CO-02-05','从完整原通路求标志、Y/Z作用、端口译码和7周期取指'),
'CO5-3':('CO-05-03 CO-04-02','按源操作数路径选取数/执行阶段的必要部件'),
'CO5-4':('CO-05-04','互斥微命令分组编码还要保留不发命令状态'),
'CO5-5':('CO-05-04','公共取指只存一份，按微存储位置求下地址位宽'),
'CO5-6':('CO-05-05','可修复缺页应重试当前指令，区别调用和设备完成'),
'CO6-1':('CO-06-01','非均匀阶段按最慢路径确定时钟，而非取平均'),
'CO6-2':('CO-06-02 CO-06-03','load的形成时刻晚于消费者使用时刻，转发仍要一拍等待'),
'CO6-3':('CO-06-03','连续检查ALU转发、load-use和分支控制等待'),
'CO6-4':('CO-06-05 CO-06-06','Flynn分类、SMP地址空间与单核硬件多线程'),
'CO6-5':('CO-06-01 CO-06-02 CO-06-03 CO-02-03','按无转发和不同拍读写约束解释14拍图，构造17拍最短调度并证明依赖下界'),
'CO7-1':('CO-07-01','总线周期含两个时钟周期的有效带宽'),
'CO7-2':('CO-07-01','MT/s已经是传送率，避免再乘每周期次数'),
'CO7-3':('CO-07-02','无突发时每个数据反复付地址与准备延迟'),
'CO7-4':('CO-07-01 CO-07-02','峰值数据节拍与整事务有效速率的区别'),
'CO8-1':('CO-08-01 CO-07-01','命令/状态编码与数据线的对应，不按名字分线'),
'CO8-2':('CO-08-02','每秒查询次数乘每次周期，再除每秒总周期'),
'CO8-3':('CO-08-03','固定响应优先级与屏蔽形成的嵌套、逐层恢复'),
'CO8-4':('CO-08-03','服务开销和允许响应延迟不是可直接相加的量'),
'CO8-5':('CO-08-04','按缓冲单位计DMA请求，周期挪用不独占整块期间'),
'CO8-6':('CO-08-04','驱动设置、控制器申请与传送、完成中断收尾'),
'CO8-7':('CO-08-02 CO-08-03 CO-08-04 CO-07-01','同一主频和缓冲单位下比较查询间隔、中断服务可行性与DMA块级CPU开销，分清上下界')
}
fig_chapters={1:[],2:[1],3:[2,3,4],4:[5,6],5:[7,8],6:[9,13],7:[10],8:[11,12]}
theory_pages={1:[15,17,19,23],2:[33,35,37,46,49,51,54,66,67,68,70,72],3:[90,95,98,109,116,123,124,127,129,131,138,149],4:[161,163,170,172,185,187,193,202],5:[208,215,221,225,239,242,246,254],6:[259,263,265,281],7:[288,289,296,297],8:[306,307,313,317,319,322,325,327]}
mechanisms=[
 {'id':'CO2-M1','knowledge_ids':['CO-02-06'],'location':'§2.6 无符号部分积轨迹','source':'王道书§2.2基本乘法机制，13×11','task':'四轮部分积形成143，分清左移累加器布局与右移组合寄存器布局'},
 {'id':'CO2-M2','knowledge_ids':['CO-02-06'],'location':'§2.6 Booth逐轮轨迹','source':'原创机制示例；标准Booth规则','task':'A5位、Q4位、附加位1位，−3×5展示跨寄存器算术右移，独立穷举256对验证','priority_check':'现有2020第43题考乘法实现与溢出，但不提供这个小位宽的跨界传位过程；补的是执行轨迹，不以原创替换真题设问'},
 {'id':'CO2-M3','knowledge_ids':['CO-02-06'],'location':'§2.6 长除法与不恢复余数逐轮轨迹','source':'王道书§2.2基本除法机制；以7÷3展开','task':'展示R/Q状态、负余数后加法和末尾余数校正，独立穷举65280组8位合法除法'},
 {'id':'CO2-M4','knowledge_ids':['CO-02-08'],'location':'§2.8 4位有效数正中取偶','source':'原创机制示例','task':'用最小有效位观察正中向上与向下两种舍入；真题2-9承担阶码/尾数溢出边界，不展示该最小舍入状态'},
 {'id':'CO3-M1','knowledge_ids':['CO-03-09'],'location':'§3.9 LRU与FIFO的A、B、A、C轨迹','source':'标准替换机制教学小例','task':'第三次命中是否改变次序，是两法分歧而非换数字重复'},
 {'id':'CO3-M2','knowledge_ids':['CO-03-13'],'location':'§3.13 段末地址与段页式最后一页','source':'原创机制示例','task':'段长3000、页1024，展示页框尚有空位也不能越段界'},
 {'id':'CO3-V1','knowledge_ids':['CO-03-08','CO-03-09'],'location':'例3-11关键变式','source':'2023第43题的原创条件变式','changes':'仅把Cache由8KiB/4路改为4KiB/2路，64组及32B块不变；原题仍完整保留','task':'每组3块超过2路，列遍历全失配；这是会改变解法的映射容量边界'},
 {'id':'CO4-M1','knowledge_ids':['CO-04-06'],'location':'§4.6 选择结构与数组循环轨迹','source':'原创机制示例，明确教学指令和差值可表示条件','task':'条件取否、入口零次执行、4字节元素地址和n+1次测试'},
 {'id':'CO4-M2','knowledge_ids':['CO-04-07'],'location':'§4.7 调用与栈帧','source':'标准栈式调用机制，明确向低地址、先减SP后写与4B槽','task':'SP1000→0FFC→0FF8→0FF0及反向恢复；不将栈式保存推广到所有ISA'},
 {'id':'CO6-M1','knowledge_ids':['CO-06-04'],'location':'§6.4 动态调度与重命名','source':'标准动态流水机制的小状态辨析','task':'新物理位置去假相关，不能去真实RAW'},
]
original_decisions={
'CO8-3':{'nearest_existing':['2011年第21题：给响应序求屏蔽字','王道书§7.3综合应用题4：四源屏蔽字与轨迹'], 'comparison':'上述题可承担屏蔽字求解，但四源题预设屏蔽关系较复杂；当前三源小例专门分离“先响应A”与“C先完成”，并展示逐层恢复旧屏蔽。原题2024第21题仍在章末保留检验响应/处理优先级，2014第22题承担服务代价。','increment':'一次最小可连续阅读的三层请求—入口—恢复状态；不以新数字重复2014开销模型','decision':'保留为机制例；未声称无现有真题，后续可用2011/四源练习追加迁移，不挤占已选真题'},
'CO5-2-old':{'nearest_existing':['2022年第43题；王道书§5.3综合10'], 'comparison':'完整真题可直接承担单总线Y/Z、译码、控制源及取指过程，原先原创ADD八步没有足够补缺理由。','decision':'已删除原创题并完整替换为2022真题，原题图按位宽/连接/控制号重绘，不保留重复ADD例。','review_resolution':'落实真题优先；不是笼统解释成无合适真题'}
}

chapters=[];all_examples=[];files={}
for chapter in range(1,9):
 f=next((ROOT/'manuscript/CO').glob(f'{chapter:02d}_*.md'));s=f.read_text();rel=str(f.relative_to(ROOT));files[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
 title=s.splitlines()[0].removeprefix('# ').split(' {#')[0]
 rows=[r for r in scope if r['规划章ID']==f'CO-{chapter:02d}']
 examples=[]
 matches=list(re.finditer(r'^### 例 (\d+)-(\d+)　(.*?) \{#([^}]+)\}',s,re.M))
 for i,m in enumerate(matches):
  id=f'CO{m.group(1)}-{m.group(2)}';end=matches[i+1].start() if i+1<len(matches) else len(s);body=s[m.end():end]
  # Read only the immediate source line, not unrelated later exercises.
  head=body.strip().split('\n')[0];src=src_by_id.get(id)
  marker_match=re.match(r'^(【\d{4}】|〖[^〗]+〗|原创补充)',head)
  assert marker_match,(id,'source marker must be on stem first line')
  marker=marker_match.group(1)+('改编' if src and src.get('adapted') else '')
  category='真题改编' if src and src.get('adapted') else '408真题' if src and src.get('year') else '典型例题' if src else '原创机制例'
  ids,task=tasks[id];ids=ids.split()
  er=[r['id'] for r in errors if src and r['section']==src.get('wangdao_section') and r['question_number']==src.get('wangdao_question_number') and 'question_type_in_book' not in src]
  ex={'id':id,'title':m.group(3),'anchor':m.group(4),'marker':marker,'category':category,'priority':1 if category=='408真题' else 2 if category=='典型例题' else 3,'is_personal_error':bool(er),'personal_error_ids':er,'knowledge_ids':ids,'methods':[task],'key_step':task,'difficulty':'综合' if id in ['CO3-11','CO5-2','CO2-10','CO3-12','CO4-6','CO6-5','CO8-7'] else '基础至中等','selection_reason':task,'increment_over_selected':task,'deletion_check':'删除后会失去：'+task,'source':src if src else {'identity':'原创机制例','priority_comparison':original_decisions.get(id,{})},'verification':'详细题源实际阅读见source字段；实际数值/过程见results.json；不称官方答案认证','location':rel+'#'+m.group(4),'boundary':'须保留正文给出的位宽、地址单位、初态、时间模型与ISA/ABI约定；具体限定见题解'}
  examples.append(ex);all_examples.append(ex)
 knowledge=[]
 for row in rows:
  kid=row['知识点 ID'];anchor=kid.lower()
  assert '{#'+anchor+'}' in s,(kid,'missing anchor')
  exids=[e['id'] for e in all_examples if kid in e['knowledge_ids']]
  micros=[m['id'] for m in mechanisms if kid in m['knowledge_ids']]
  knowledge.append({'id':kid,'name':row['知识点'],'anchor':anchor,'location':rel+'#'+anchor,'learning_requirements':row['学习要求'],'prerequisites':row['前置知识'],'status':'正文完成，已编辑审读；适用正式大纲细目仍待核','examples':exids,'mechanism_examples':micros,'core_methods':row['核心考法'],'conditions':row['重要条件与边界'],'theory_basis':'王道2027计算机组成原理，相关章；实际抽读页单独记录','verification':'读正文与主书列出的实际抽读页；算法、位值、地址和时序另有独立执行验证，不由ID出现替代'})
 chapters.append({'chapter':chapter,'id':f'CO-{chapter:02d}','title':title,'manuscript':rel,'sha256':files[rel],'character_count':len(s),'knowledge':knowledge,'examples':examples,'figures':[q for q in figs if int(q['id'].split('_F')[1][:2]) in fig_chapters[chapter]],'theory_pages_actually_read':theory_pages[chapter],'checks':{'scope':'本地规划48组逐组有正文；正式2027细目不宣称全部核验','calculation':'editorial/full/CO/results.json','sources':'editorial/full/CO/selected_source_locators.json','style':'短标注；原作答不入正文；已按独立审校修具体段落','pdf_visual':'由主编最终PDF锁版后逐页核查，不把Markdown审读冒充视觉完成'}})

# Explicit handling of conditions/source faults; these are not requests to re-upload mistakes.
special={
'ERR-CO-3.2-026':('并入正文机制辨析','CO-03-04','单体多字通过扩宽一次读写提高带宽，与多体低位交叉并列对照；补为该组的支撑前置，不声称二者同机制。'),
'ERR-CO-2.2-024':('并入条件辨析，原题暂不作完整主例','CO-02-06','商0提前结束只对具备检测/退出逻辑的该除法器成立；正文写明固定轮数与提前退出的边界。'),
'ERR-CO-3.3-009':('并入已补条件的边界说明','CO-03-05','正文明确按字编址才有38000H—3FFFFH；改按字节编址须另算。不把缺编址单位的原题作为无条件唯一答案。'),
'ERR-CO-3.5-030':('其他：暂缓作为无条件真题主例；原题保留复习队列','CO-03-09','原书用特殊分组，整卷题文本身未给出该规则；正文讲清常规模组号及特殊映射须先给函数，完整主例采用无此歧义题。'),
'ERR-CO-3.6-005':('并入正文机制纠正','CO-03-12','区分OS建立维护映射与MMU运行时转换；不照搬把每次地址映射都归软件的笼统选项。'),
'ERR-CO-4.3-008':('并入调用模型边界','CO-04-07','返回地址可用主存栈或链接寄存器，正文对栈式轨迹显式给约定，不泛化原书特定模型。'),
'ERR-CO-5.6-008':('并入数据通路控制辨析','CO-06-02','明确阶段寄存器也有保持/清空/写使能；取指译码仍需控制。原题混用控制信号范围，不作机械背答案主例。'),
'ERR-CO-2.2-022':('复习练习，按原书恢复文本','CO-02-05','已据主书恢复输出字符串；正文的混合类型比较和CF/OF分别判定提供方法，内部保留原位置，不展示原错选。'),
'ERR-CO-2.3-021':('复习练习，按原书恢复数据','CO-04-03','已据主书把数组{-1.5}恢复为{-1,5}；正文给行优先地址、小端负short拆字节方法，原题与示范数据不混写。')
}
for c in chapters:
 for k in c['knowledge']:
  k['examples']=[e['id'] for e in all_examples if k['id'] in e['knowledge_ids']]

destinations=[]
for r in errors:
 selected=[e for e in all_examples if r['id'] in e['personal_error_ids']]
 self_sources=[q for q in sources if '-S' in q['id'] and q.get('wangdao_section')==r['section'] and q.get('wangdao_question_number')==r['question_number'] and 'question_type_in_book' not in q]
 kids=r.get('knowledge_ids',[]) or ['CO-03-04']
 if r['id'] in special:
  dest,kid,reason=special[r['id']];kids=list(dict.fromkeys([kid]+kids));location=next(k['location'] for c in chapters for k in c['knowledge'] if k['id']==kid)
 elif selected:
  dest='正文完整例题';location=selected[0]['location'];reason='已用相同原题完整讲解；'+selected[0]['selection_reason']
 elif self_sources:
  dest='章末复习练习';ch=int(self_sources[0]['id'][2:].split('-')[0]);location=chapters[ch-1]['manuscript']+f'#co-self{ch}';reason='原题已在章末保留，先作答后看答案；其模型在相应正文说明。'
 else:
  dest='复习练习队列，相关机制已反馈正文';kid=kids[0];location=next(k['location'] for c in chapters for k in c['knowledge'] if k['id']==kid)
  reason='保留原题供复习，避免与已有主例重复完整铺题；对应教学任务：'+r.get('core_method',r.get('knowledge_point',''))+'。正文已讲'+knowledge_by_id[kid]['知识点']+'及相关条件；不据缺少演算推测个人心理错因。'
 destinations.append({'id':r['id'],'original_location':{'json':r['source_json'],'json_pointer':r['json_pointer'],'question_pdf_page':r['question_pdf_page'],'section':r['section'],'question_number':r['question_number']},'knowledge_ids':kids,'destination':dest,'location':location,'reason':reason,'selected_example_ids':[e['id'] for e in selected],'source_identity':'题源身份与错题身份分别保存；完整原题、原作答和批改仍在首轮内部台账','actual_answer_information':r['answer_observed'],'confirmed_personal_cause':r['confirmed_personal_cause'],'personal_cause_status':'原演算不足，未补造个人错因；不在正文显示原选项','reading_provenance':'继承首轮已读取题文/选项及逐题图读书答；本轮只对实际选入者报告进一步完整题源核验'})

assert len(destinations)==130
assert len({k['id'] for c in chapters for k in c['knowledge']})==48
assert len(all_examples)==53
for c in chapters:
 for e in c['examples']:
  assert e['marker'].startswith(('【','〖','原创')),e
result={'schema_version':'2.0','subject':'CO','subject_name':'计算机组成原理','date':'2026-10-16','scope':'8章、48个稳定知识组，按本地暂定边界完成正文；正式2027大纲细目全文未取得，不能宣称官方逐条覆盖完成。','main_source':'王道2027计算机组成原理，电子工业出版社，2026年1月第1版，ISBN978-7-121-51794-5','reader_provenance_rule':'真题【年】，非真题〖节-三位题号〗；原创/改编显式区别；正文不显示原作答或做题本名。','chapters':chapters,'errors':destinations,'mechanism_examples':mechanisms,'original_and_replacement_decisions':original_decisions,'selfcheck_sources':[s for s in sources if '-S' in s['id']],'counts':{'chapters':8,'knowledge_groups':48,'full_examples':48,'full_exam_examples':sum(e['category']=='408真题' for e in all_examples),'full_adapted_examples':sum(e['category']=='真题改编' for e in all_examples),'full_typical_examples':sum(e['category']=='典型例题' for e in all_examples),'full_original_mechanism_examples':sum(e['category']=='原创机制例' for e in all_examples),'errors_registered':130,'figures':len(figs),'source_records_actually_read':len(sources),'personal_causes_inferred':0},'source_conflicts_resolved_by_adaptation':[{'id':'CO3-11','detail':'主书赋值10、二手复原i*j，明确标改编，两个赋值统一10，不计已核原题。'}],'unresolved':[{'id':'CO-SCOPE-2027','status':'待核验','detail':'2027正式大纲已出版但未取得细目全文，当前范围以本地转录交叉表为暂定边界。'},{'id':'CO-SOURCE-2012Q17','status':'原题选用受条件约束','detail':'Cache特殊分组源冲突登记于ERR-CO-3.5-030，已另选清楚题源并保留复习原题；不要求用户重整全部材料。'}],'verification':'results.json为实际复算；source实际读页在selected_source_locators.json；最终PDF视觉另记，三者互不替代。','manuscript_sha256':files}
result['schema_version']='2.1'
result['counts']['full_examples']=53
result['status']='第二轮内容审阅稿完成；本轮未生成或验收讲义PDF'
result['author_stage_status']='比较维度与5道完整综合真题已补，数值/机制独立复算通过；交内容审阅'
result['previous_release_pdf_review']=previous.get('previous_release_pdf_review',previous.get('final_pdf_review'))
result['final_pdf_review']={'status':'NOT_PERFORMED_FOR_REVISION2','reason':'用户要求先交内容审阅稿；本轮不做PDF分页、裁切、视觉或精排','prior_release':'previous_release_pdf_review仅记录第一轮既有PDF，不对本轮稿件背书'}
result['revision2']={
 'audit':'editorial/revision2/CO_revision.md',
 'source_audit':'editorial/revision2/sources/co_new_synthesis/CO_new_synthesis_source_verification.json',
 'independent_review':'editorial/revision2/review/independent_numbers.json',
 'new_examples':['CO2-10','CO3-12','CO4-6','CO6-5','CO8-7'],
 'new_figure':'CO_F13_pipeline_schedule',
 'depth_basis':'先按主要建模链与前置能力判断缺口，不以个人错题数量配置篇幅；第1/5/7章已有适用例题，补共同维度比较而不凑题',
 'comparisons':[
  {'chapter':'CO-01','dimensions':'ISA/编译器/微体系结构/OS的责任；动态指令数/CPI/主频/等待对同一任务时间的影响'},
  {'chapter':'CO-02','dimensions':'同一位串在无符号/补码下的范围、CF/OF/SF/ZF；整数范围与binary32有效精度/指数范围'},
  {'chapter':'CO-03','dimensions':'器件技术与存储角色；三种Cache映射的共同字段；映射/替换/写策略；TLB/页表/物理Cache的对象与失败路径'},
  {'chapter':'CO-04','dimensions':'寻址位移的基准/符号/单位；顺序/条件分支/调用/返回的PC与返回信息'},
  {'chapter':'CO-05','dimensions':'单周期/多周期/流水的时钟与资源复用；机器指令/微地址/微命令的计数对象'},
  {'chapter':'CO-06','dimensions':'无转发不同拍读写/同拍先写后读/ALU转发/load转发的形成点与使用点'},
  {'chapter':'CO-07','dimensions':'峰值/事务有效速率/设备速率/CPU占用；事务总历时与总线占用时间'},
  {'chapter':'CO-08','dimensions':'查询/中断/DMA的CPU事件粒度、数据搬运者、CPU与总线分别预算'}
 ],
 'error_destination_policy':'130条原错题ID与原去向保留；新综合题不冒充新增个人错题，相关知识组可回指新例题',
 'reader_layout_policy':'题源只在题干首行用【年份】或〖节号-号〗；该行无手工缩进；普通Markdown段落继续继承既有2em首行规则，本轮不改共享样式',
 'pdf_work':'未做；图像仅核机制与数字，不作为最终PDF视觉验收'
}
for c in result['chapters']:
 c['checks']['pdf_visual']='本轮内容稿未做PDF分页/裁切/视觉/精排；第一轮记录仅留历史'
 c['checks']['revision2']='editorial/revision2/CO_revision.md'
 c['checks']['sources']='editorial/full/CO/selected_source_locators.json；新增5题另有revision2独立逐页核验'
(HERE/'chapter_records.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (HERE/'error_destinations.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['id','knowledge_ids','destination','location','reason']);writer.writeheader();writer.writerows({k:';'.join(v) if isinstance(v,list) else v for k,v in r.items() if k in writer.fieldnames} for r in destinations)
print(json.dumps(result['counts'],ensure_ascii=False))
