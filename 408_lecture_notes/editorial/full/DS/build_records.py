#!/usr/bin/env python3
"""Editorial assembly only. Not needed for rebuilding the student PDFs."""
from pathlib import Path
import re,json,csv,hashlib,collections
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BOOK='/workspace/study_analysis/v2/books/王道2027数据结构_高清带书签版.pdf'
HORIZONTAL='/workspace/Classroom/01_数据结构/【横版】27王道数据结构选择题做题本.pdf'
raw=json.loads((HERE/'source_records.json').read_text())
by_source={(r['section'],r['question_number']):r for r in raw}
coverage=json.loads((ROOT/'editorial/scope/DS_coverage.json').read_text())
examindex=json.loads((ROOT/'editorial/full/sources/exam_question_index.json').read_text())
exams={(r['year'],r['question']):r for r in examindex}
answercache=json.loads(Path('/workspace/study_analysis/v2/book_answers.json').read_text())

# n, section, item, type, exam year, exam number, book stem pages, answer pages,
# teaching model, decisive condition/boundary, loss if removed.
SPECS=[
('1-1','1.1',5,'选择',None,None,[15],[16],'值与关系的表示','关系可由位置隐含，不一定另有指针域','失去逻辑/存储结构的第一道条件辨析'),
('1-2','1.2',15,'选择',2017,1,[19],[22],'累计和决定循环次数','每轮增量递增，停止方程不是k=n','失去由题干停止条件建立平方根模型的连续推导'),
('1-3','1.2',17,'选择',2022,1,[20],[22],'倍增外层与等比求和','内层长度依赖外层，不能直接相乘两个最大值','失去两层循环仍为线性时间的反例'),
('2-1','2.3',12,'选择',None,None,[52],[59],'删除位置与存储方式','题干未指定顺序或链式；定位成本另计','失去未给存储方式时答案不唯一的边界'),
('2-2','2.3',17,'综合',2009,42,[56],[71],'固定间距双指针','带头结点、不改链表、k正且可能大于表长','失去链表一次扫描及k=n/k>n的完整算法'),
('2-3','2.3',15,'选择',None,None,[53],[59],'双链表四条关系更新','p有有效前驱，须保存旧前驱到最后','失去双向指针覆盖顺序的可执行检查'),
('2-4','2.2',10,'综合',2010,42,[32],[38,39],'分段逆置交换连续区段','0<p<n，时间线性且辅助常数','失去数组原地处理的主要综合模型'),
('2-5','2.3',18,'综合',2012,42,[57],[71,72],'对齐尾部寻找共享结点','地址相同而非字符相同，有限无环链','失去不等长链表转成等剩余长度的迁移'),
('2-6','2.2',12,'综合',2013,41,[32,33],[40],'不同元素配对抵消','严格多数，候选仍须二次计数','失去候选存在不等于答案存在的验证步骤'),
('3-1','3.1',26,'选择',2009,2,[80],[84],'栈输出模拟与最小容量','队列保序；必须恢复原题bdcfeag','失去栈深最大值作为最小容量的模型'),
('3-2','3.2',6,'选择',None,None,[95],[97],'指针含义决定有效区间','front在队首前一位、rear在队尾；M=21','失去相近指针约定下不能只看下标差的辨析'),
('3-3','3.4',11,'选择',2016,4,[117],[118],'按完整行数加本行偏移','首行2项，其余内部行3项；数组0起始','失去三对角首行与下标原点的计算边界'),
('3-4','3.4',14,'选择',2020,1,[117],[119],'先利用对称性再压缩寻址','上三角、列优先、C数组0起始','失去非保存半边坐标需先交换的迁移'),
('3-5','3.3',18,'选择',2018,1,[108],[111],'栈保存操作数的运算次序','先弹右操作数，按b op a计算','失去减法不交换性与逐次状态的示范'),
('4-1','4.2',10,'选择',2015,8,[130],[132,133],'已匹配前后缀复用','题干i=j=5确定0起始，主串指针不退','失去KMP失败条件到next链接的主要入口'),
('4-2','4.2',12,'选择',2024,6,[130],[133],'nextval跳过必失败字符','须使用修正表，位移j−nextval[j]','失去优化为何正确及最大位移的完整计算'),
('5-1','5.1',9,'选择',2010,5,[139],[140],'边数的两种计数','树而非任意图，度指孩子数','失去一般树叶结点公式的实际推导'),
('5-2','5.2',28,'选择',2020,3,[147],[150],'满树位置编号的保证容量','任意形态的保证，不是选最省空间形态','失去顺序存储中结点少但位置大这一边界'),
('5-3','5.3',43,'选择',2024,3,[162],[170],'中序邻接到子树边界','v左右孩子均存在，p/q紧邻v','失去遍历前驱后继的局部结构判断'),
('5-4','5.4',15,'选择',2009,6,[186],[189],'左孩子右兄弟逐边翻译','二叉树两条链接不直接等于森林两代','失去森林转换的关系迁移'),
('5-5','5.5',22,'选择',2023,4,[199],[202],'哈夫曼反复取当前两最小','平均按频次总和36加权','失去WPL与合并权值和的完整核验'),
('5-6','5.5',4,'选择',None,None,[197],[200],'前缀码占用整棵子树','码长最多4，1与01排除对应全部后代','失去码字容量受前缀限制的独立边界'),
('6-1','6.1',16,'选择',2010,7,[211],[212],'不连通图最大边数的反证','简单无向图，要求保证任意形态连通','失去必要边数与充分保证的区分'),
('6-2','6.3',11,'选择',None,None,[232],[234],'DFS回退条件的轨迹检查','尚有未访问邻点时不允许提前回退','失去合法遍历序列不是相邻输出必邻接的辨析'),
('6-3','6.4',33,'选择',2015,6,[253],[262],'Prim割边与Kruskal分量','Prim从V4，权8同权边可分支','失去两个最小生成树算法中间状态的区别'),
('6-4','6.4',44,'选择',2021,8,[254],[265],'Dijkstra确定与暂定距离','第二条路径后停止，不能使用未来松弛','失去从初值到21再到15的中间数组'),
('6-5','6.4',13,'综合',2024,41,[257],[272,273],'零入度候选唯一且处理全体','有环无序，多候选若可完成则不唯一','失去拓扑唯一性与环检测的完整代码'),
('6-6','6.4',31,'选择',2013,9,[252],[262],'AOE事件时间与多关键路径','d方向3→2，需同时影响全部最长路径','失去单个关键活动缩短未必降工期的边界'),
('7-1','7.2',26,'选择',2025,7,[283],[288],'分块两级平均代价求最小','索引和块内都顺序，400等概率','失去由访问方式导出平方根块长的条件'),
('7-2','7.2',20,'选择',2010,9,[282],[287],'闭区间折半失败路径','下中点；空区间本身不做关键字比较','失去16项失败需5次而非log2n的边界'),
('7-3','7.3',3,'综合',None,None,[307],[],'最小失衡子树及旋转','原题正是7次插入逐次平衡，不是同号选择题','失去LL、RR、RL连续更新的完整轨迹'),
('7-4','7.3',29,'选择',2015,4,[304],[311],'逆向搜索次序与AVL形态','中序降序、关键字互异，不沿用升序方向','失去颜色/平衡与关键字序各自独立的辨析'),
('7-5','7.4',9,'选择',None,None,[321],[325],'最少/最多容量约束树高','高度按数据结点层数，不计空外部叶','失去B树高度两端不等式方向的检验'),
('7-6','7.4',25,'选择',2025,8,[323],[327],'按根键数和等高子树计形态','4阶7互异键，非根至少1项','失去低高度与最稀疏高一层需同时枚举的边界'),
('7-7','7.5',23,'选择',2023,9,[334,335],[338],'删除标记与失败探查ASL','遇从未用空槽才停，初始地址等概率','失去开放定址删除不能直接清空的机制'),
('7-8','7.5',7,'综合',2024,42,[336],[342],'二次探查从同一H0求址','平方增量而非累加上次地址，模表长11','失去不同冲突策略的可执行地址轨迹'),
('8-1','8.2',12,'选择',None,None,[349],[351],'希尔按余数分组逐趟插入','增量5后3，各趟处理全部组','失去增量有序不等于全局有序的实际轨迹'),
('8-2','8.3',18,'选择',2019,10,[358],[360],'划分全区间分隔与趟定义','所有未就位区间一遍算一趟，首枢轴可能端点','失去快排过程反推而非机械执行的考法'),
('8-3','8.4',17,'选择',2015,10,[368],[371],'堆下滤中的关键字比较','孩子比较与候选比较，单孩子不补虚比较','失去调整比较次数的准确口径'),
('8-4','8.5',20,'选择',2024,10,[381],[384],'两段耗尽后不再比较','按从左至右归并，不能次次取最坏上界','失去实际比较次数与最坏上界的区别'),
('8-5','8.5',12,'选择',None,None,[381],[383],'LSD稳定分配收集','首趟个位，相同桶保持原序','失去不同位排序的中间结果与稳定性联系'),
('8-6','8.7',5,'综合',2023,42,[398],[402],'置换选择的冻结与解冻','工作区4条，段长可超过4；输出后换入','失去19记录全部中间归属及首段长度边界'),
('8-7','5.5',2,'综合',2012,41,[199],[204],'不等长合并的哈夫曼模型','5次二路合并，成本为新段长−1','失去WPL与关键字比较成本的跨章联系'),
('8-8','8.7',4,'综合',None,None,[398],[401,402],'多路最佳归并补虚段','4路12段，补1零权使叶数满足条件','失去非二叉归并的零权补齐及I/O解释'),
('S1-1','1.2',16,'选择',2019,1,[19],[22],'平方界限直接计循环','非负n，while使用>=与(x+1)^2','保留已有真题作自测，区别累计和与平方停止条件'),
('S3-2','3.1',25,'选择',None,None,[80],[84],'共享栈边界','两个top都指向已有栈顶，初值−1与n','使用已有错题替代只换数字的原创共享栈自测'),
('S8-2',None,None,'综合',2022,42,[],[],'选择而非完整排序','n>100000，仅需最小10个，不要求内部有序','使用已有真题替代指定堆法的原创自测，补平均线性选择'),
]

files=sorted((ROOT/'manuscript/DS').glob('*.md'));texts={int(f.name[:2]):f.read_text() for f in files}
chapters=[];all_examples=[];all_anchors={}
figmanifest=json.loads((HERE/'figure_manifest.json').read_text())['figures']
for f in files:
    ch=int(f.name[:2]);s=f.read_text();title=re.search(r'^# (.*?) \{#',s,re.M).group(1)
    anchors={m.group(2):{'heading':m.group(1),'line':s[:m.start()].count('\n')+1} for m in re.finditer(r'^#{1,3} (.*?) \{#([^}]+)\}',s,re.M)}
    for k,v in anchors.items():all_anchors[k]={'manuscript':str(f.relative_to(ROOT)),**v}
    knowledge=[]
    for a in coverage:
        kid=a['知识点 ID']
        if int(kid.split('-')[1])!=ch:continue
        anchor=kid.lower();assert anchor in anchors,kid
        knowledge.append({'id':kid,'name':a['知识点'],'anchor':anchor,'location':f'{f.relative_to(ROOT)}#{anchor}','heading':anchors[anchor]['heading'],'line':anchors[anchor]['line'],'prerequisites':a['前置知识'],'learning_requirements':a['学习要求'],'scope_basis':a['大纲依据'],'scope_status':'本地转录范围有去向；2027正式细目全文未获，逐条正式覆盖仍待核','status':'正文已完成；本轮及独立审校通读，相关数值和过程见results.json','sources':a['内容与题目来源'].split('（仅目录')[0],'conditions':a['重要条件与边界'],'methods':a['核心考法'],'teaching_treatment':'定义/机制与执行例示按实际正文展开；完整原题另列，不以某知识组有解释就宣称所有相关原题均已收录'})
    figures=[]
    for a in figmanifest:
        if f"({a['id']}.png)" in s:figures.append(a)
    chapters.append({'chapter':ch,'title':title,'manuscript':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'knowledge':knowledge,'examples':[],'figures':figures,'checks':{'content':'已完成正文通读、连续推理及来源身份检查；RV-024已关闭','calculation':'editorial/full/DS/results.json','style':'短题源、无原错选、无ERR编号、无做题本正文标签；各章结构按任务展开','PDF_visual':'由主代理锁定最终PDF后单独检查，不以本台账代替'},'unresolved':[]})

for num,sec,q,kind,year,eq,pages,apages,method,condition,loss in SPECS:
    if num.startswith('S'):
        ch=int(num[1]);anchor=f'ds-ch{ch}-check';label=f'自测{num.split("-")[1]}'
    else:
        ch=int(num.split('-')[0]);anchor='ds-ex'+num;label='例'+num
    assert anchor in all_anchors,anchor
    loc=all_anchors[anchor];marker=f'【{year}】' if year else f'〖{sec}-{q:03d}〗'
    error=by_source.get((sec,q)) if kind=='选择' else None
    answer=answercache.get(f'DS:{sec}:{q}') if kind=='选择' else None
    if error and year and str(year) not in error.get('book_claimed_exam_years',[]):raise AssertionError(num)
    src={'kind':'408真题（社区复原卷与用户主资料互证）' if year else '王道典型例题','book_title':'2027年数据结构考研复习指导','edition':'2026年1月第1版；电子工业出版社；ISBN 978-7-121-51791-4','book_path':BOOK,'section':sec,'question_type':kind+'题','book_question_number':q,'book_pdf_pages':pages,'book_printed_pages':[x-12 for x in pages],'book_answer_pdf_pages':apages}
    if error:src.update({'provided_question_pdf':error['question_pdf'],'provided_question_pdf_page':error['question_pdf_page'],'raw_record_id':error['id']})
    if kind=='选择':
        # The supplied native-text question PDF is an exact, actually-read stem
        # locator. Do not publish guessed main-book stem pages from chapter ranges.
        src['book_pdf_pages']=[];src['book_printed_pages']=[]
        src['book_stem_page_note']='题干以实际提供的可搜索题页为精确定位；未逐项确认的主书题干页不填估计页码。主书答案页单列。'
        extra_native={('3.3',18):149,('4.2',10):177,('4.2',12):179,('6.4',33):395,('7.2',26):435,('8.5',20):602}
        if not error:
            src['provided_question_pdf']=HORIZONTAL
            src['provided_question_pdf_page']=extra_native[(sec,q)]
        if answer:src['book_answer_pdf_pages']=sorted({z['page'] for z in answer['crops']})
    if year:
        x=exams[(year,eq)];src.update({'exam_year':year,'exam_question':eq,'exam_pdf':x['full_pdf'],'exam_pdf_page':x['pdf_page'],'exam_origin_url':f'https://raw.githubusercontent.com/neville-studio/408-exam-paper/main/papers-rebuild/{year}.pdf','exam_source_level':'社区复原完整卷；不是官方原卷或官方答案认证'})
    verification={'stem':'题意、数据、设问与实际源文核对，正文允许中文句式整理而不改条件','options':'选择题四项完整保留' if kind=='选择' else '综合题无选项；各设问保留','diagram':'原图拓扑/方向/权值/头结点保留并原创重绘' if num in ['2-5','6-3','6-4','6-6'] else '无原题必要图，或用可编辑框表示数据结构','year_and_number':'已核对完整复原卷年份及原题号' if year else '不作真题身份声明','answer':'主书答案已目验，并结合本书独立推导/复算' if answer else '综合题自主求解，算法/计算独立复算；主书对应解析见所列页（页未列者不伪造）','official_answer_certified':False,'calculation_record':'editorial/full/DS/results.json','visual_evidence':'editorial/full/DS/sources/；原97条答案字母图核沿用editorial/errors/ds_co_checks/answer_labels/','status':'已核对可用题源并完成解答；官方认证不作声明'}
    if num=='7-3':verification.update({'stem_visual':'editorial/full/DS/sources/DS_7.3_comprehensive_003.png','identity_note':'§7.3二、综合应用题03，PDF307/印刷295；不是横版选择第003题。原题本就要求全部七次插入后逐次构树，无设问改编。','review_issue':'RV-024 closed'})
    if num=='3-1':verification['source_correction']='横版PDF102误排bdefeag，按原卷2009Q2与主书PDF80恢复bdcfeag；不把排印损坏当作条件改编。'
    if num=='S8-2':verification['answer']='未定位主书同号整题解析，不虚列页；按已讲划分/选择与大小10堆独立复算，记录DS-C57覆盖实际选择结果。'
    kid_matches=[]
    if not num.startswith('S'):
        s=texts[ch];start=s.index('{#'+anchor+'}')
        prefix=s[:start];secanchors=re.findall(r'^## .*?\{#(ds-\d\d-\d\d)\}',prefix,re.M)
        if secanchors:kid_matches=[secanchors[-1].upper()]
    else:kid_matches={'S1-1':['DS-01-03'],'S3-2':['DS-03-03'],'S8-2':['DS-08-06','DS-05-11','DS-08-11']}[num]
    ident='DS-'+num;example={'id':ident,'reader_label':label,'title':loc['heading'] if not num.startswith('S') else label+' '+method,'anchor':anchor,'marker':marker,'category':'真题' if year else '典型例题','priority':1 if year else 2,'personal_error':bool(error),'personal_error_ids':[error['id']] if error else [],'knowledge_ids':kid_matches,'source':src,'verification':verification,'methods':[method],'key_steps':method+'；按正文连续步骤执行并核对结束状态','conditions':condition,'difficulty':'综合执行' if kind=='综合' else '概念/单模型执行','selection_reason':loss,'deletion_check':{'loss_if_deleted':loss,'decision':'保留；与已选题承担的任务不同或具有单独条件边界'},'incremental_value':loss,'adaptation':'无数据、条件或设问改编；语句、符号按本书约定整理，图按原关系重绘','location':f"{loc['manuscript']}#{anchor}"}
    chapters[ch-1]['examples'].append(example);all_examples.append(example)

# Concrete destination statements. Most records are combined into the corresponding
# mechanism rather than reproduced a second time. No personal psychological cause is inferred.
DETAIL={
'1.1-005':('ds-ex1-1','正文例题','值以外仍须表示关系；相邻位置也能隐含关系'),
'1.2-002':('ds-01-02','并入辨析','算法必备特性与评价维度分别解释；原单选D措辞有歧义，不重复设题'),
'1.2-015':('ds-ex1-2','正文例题','累计和转为停止不等式'),
'1.2-016':('ds-ch1-check','复习练习（已收自测）','恢复2019完整原题，比较平方停止条件与累计和模型'),
'1.2-017':('ds-ex1-3','正文例题','按外层取值求等比和'),
'2.3-003':('ds-02-03','并入辨析','不同结点可分散与一个结点作为整体分配分开'),
'2.3-012':('ds-ex2-1','正文例题','顺序与链式导致移动数50或0'),
'2.3-015':('ds-ex2-3','正文例题','四条双链关系，最后覆盖p旧前驱'),
'2.3-021':('ds-02-04','并入辨析','带头循环空表L.next==L，不是头指针空'),
'2.3-025':('ds-02-04','并入辨析','尾指针让两个循环表常数时间拼接，头结点须另外处理'),
'3.1-001':('ds-01-01','重复合并','栈队列逻辑均线性，操作约束/ADT不同；第3章定义承接'),
'3.1-008':('ds-03-04','并入辨析','链栈可动态申请，仍会栈空且可能内存不足'),
'3.1-015':('ds-03-01','并入执行示例','abcd输入、cd开头的唯一余序ba已写出'),
'3.1-020':('ds-03-01','并入边界推理','第3输入1时P1不可能2，明确以栈顶阻挡给反证'),
'3.1-025':('ds-ch3-check','复习练习（已收自测）','原题直接检验top2−top1==1，替代只换数字原创'),
'3.1-026':('ds-ex3-1','正文例题','原文排印恢复bdcfeag，逐目标计算最大深3'),
'3.2-005':('ds-03-03','并入边界','A[0..n]有n+1单元，模数不是n'),
'3.2-006':('ds-ex3-2','正文例题','两端约定改变后先数有效区间'),
'3.2-009':('ds-03-03','并入辨析','分清物理数组M与牺牲后容量M−1；原措辞不无条件照抄'),
'3.2-013':('ds-03-04','并入结构比较','非循环双链只给队首仍不能常数取得队尾'),
'3.2-014':('ds-03-04','并入机制','单链队列链头出队，避免找尾前驱'),
'3.2-015':('ds-03-04','并入边界','删除最后数据结点时尾指针退回头结点'),
'3.2-017':('ds-03-04','复习练习（原题保留）','队头反设尾部时需要寻找前驱；正文先讲标准布局，原反设题不重复印'),
'3.3-006':('ds-03-07','并入执行示例','按调用树结点计F8=9，不把返回值+1当调用'),
'3.3-007':('ds-03-07','并入边界','先算func5后外层func4，第4次不依赖两个基例求值先后'),
'3.4-003':('ds-03-06','并入公式推导','下三角0起始先数完整行，再代对角j=i'),
'3.4-006':('ds-ch3-check','复习练习（原题保留）','三对角从1起始位置公式在自测3推导；原数值题不再完整排'),
'3.4-007':('ds-ex3-4','并入变式','上三角按列数1+…+(j−1)，矩阵与压缩下标分开'),
'3.4-008':('ds-03-06','并入变式','下三角按列长度递减，先数完整列再加i−j'),
'3.4-011':('ds-ex3-3','正文例题','首行2项且数组从0起，得87'),
'3.4-013':('ds-03-06','并入变式','上三角行优先递减行长；不再完整排同类算式题，复算50'),
'3.4-014':('ds-ex3-4','正文例题','对称交换后得到N22'),
'4.2-002':('ds-04-03','并入机制','主串i不退，模式j可退；不等于同一字符只比一次'),
'5.1-003':('ds-05-01','并入定义辨析','全树路径长度为和，高度取最大'),
'5.1-006':('ds-05-01','并入执行示例','3叉50节点以容量40与121夹出最小高5'),
'5.1-007':('ds-05-01','并入边界','度1结点可增加而不改叶数，不能只凭给定几类数确定总数'),
'5.1-008':('ds-ex5-1','重复合并','一般叶数公式由边数两种计数推出'),
'5.1-009':('ds-ex5-1','正文例题','2010树叶数82，保留真实题源身份'),
'5.2-007':('ds-05-02','并入执行示例','50结点最小高6，并列一般与完全树条件'),
'5.2-019':('ds-05-03','并入指针计数','三叉链表空域n+2，入指针不由自身度单独决定'),
'5.2-028':('ds-ex5-2','正文例题','任意合法10节点高5形态保证需要31位置'),
'5.3-021':('ds-05-04','并入算法解释','后序交换所有左右子树，中序反向但根叶身份不变'),
'5.3-023':('ds-05-05','并入条件辨析','n+1统计线索域含首尾，目标普通节点数另计'),
'5.3-029':('ds-05-05','并入遍历边界','后序叶X有左兄弟时，X后继为双亲'),
'5.3-038':('ds-05-04','并入计数说明','仅先序不唯一；4节点形态卡特兰14'),
'5.3-043':('ds-ex5-3','正文例题','中序前驱在左子树最右端，后继在右子树最左端'),
'5.4-004':('ds-05-07','并入结构说明','二叉根左子树a−1，不包含其他树'),
'5.4-015':('ds-ex5-4','正文例题','逐边翻译LR/RR等四类关系'),
'5.5-004':('ds-ex5-6','正文例题','前缀占子树，00下最多4叶'),
'5.5-006':('ds-05-09','并入边界','n叶哈夫曼最高n层，未必完全或平衡'),
'5.5-008':('ds-05-09','并入性质','无度1，WPL等于全部合并权值和；不混成度数差公式'),
'5.5-009':('ds-05-09','并入推广','m叉补零后内部数ceil((n−1)/(m−1))，说明虚叶与真实字符区别'),
'5.5-014':('ds-05-09','复习练习（原题保留）','正文明确哈夫曼不必完全；原四选项跨层权值关系不额外重复设题'),
'5.5-022':('ds-ex5-5','正文例题','频次总和36，WPL90，加权平均2.5'),
'6.1-001':('ds-06-01','并入边数判环','n边的n点无向图必有环，不必连通或单环'),
'6.1-010':('ds-06-01','重复合并','生成树为极小连通子图，通常不是原图连通分量'),
'6.1-011':('ds-06-01','并入极值示例','51顶点21边集中到K7加44孤立，45分量'),
'6.1-012':('ds-06-01','复习练习（原图保留）','定义已区分单向可达与强连通；本题独立图未入正文，不声称本轮重绘或二次复算该图'),
'6.1-016':('ds-ex6-1','正文例题','最多15边仍可不连通，16才保证'),
'6.1-018':('ds-06-01','并入必要条件','m<n−1必不连通，其逆命题不成立'),
'6.2-009':('ds-06-02','并入存储计数','邻接表空间n+e，顶点头数组也计入'),
'6.3-011':('ds-ex6-2','正文例题','e尚有d未访问，不能先退去c'),
'6.3-013':('ds-06-01','重复合并','与6.1-010同一生成树/连通分量辨析，保留一次机制'),
'6.4-008':('ds-06-07','并入算法条件','Dijkstra全源需重复n次；Floyd负边可、负环不可'),
'6.4-009':('ds-06-07','复习练习（原图数据保留）','最短路执行主例优先保留2021真题中间状态；本题同模型单终点仍供复习'),
'6.4-019':('ds-06-08','并入条件修正','按拓扑次序重新编号才三角；原“有序”措辞不能推出任意编号矩阵三角'),
'6.4-031':('ds-ex6-6','正文例题','三关键路径覆盖需选f和d'),
'6.4-036':('ds-06-08','并入复杂度','邻接表拓扑n+e与本章矩阵代码n²分开'),
'6.4-041':('ds-06-04','并入跨节解释','DAG退出前输出为逆拓扑，不是首次访问DFS序'),
'6.4-044':('ds-ex6-4','正文例题','第二条确定后dist2=21，最终才15'),
'7.2-002':('ds-07-02','并入条件纠正','相等要成功，严格大于才能失败；成功顺序ASL仍相同'),
'7.2-009':('ds-07-03','并入执行示例','11元素查11位序6,9,10,11'),
'7.2-011':('ds-07-03','并入执行示例','10元素查b顺序f,c,b'),
'7.2-020':('ds-ex7-2','正文例题','16项失败最多5次，区间空不再比键'),
'7.3-013':('ds-07-05','并入计数辨析','固定高度3形态15，用C2²+2C2C1而非节点数卡特兰'),
'7.3-015':('ds-07-05','复习练习（原题保留）','本题根高0与本书根层1换算；主例已完整逐次旋转，不以高度界替代原序列实际结果'),
'7.3-029':('ds-ex7-4','正文例题','中序降序意味着左大右小，最大无左子树'),
'7.4-009':('ds-ex7-5','正文例题','最少/最多容量分别推最大11/最小7'),
'7.4-025':('ds-ex7-6','正文例题','高度2八种，加高度3一种，共9'),
'7.5-004':('ds-07-09','并入冲突机制','同义与非同义探查链都可造成聚集'),
'7.5-014':('ds-07-09','复习练习（原题保留）','H内部模11、探查模表长14的边界已说明；主例优先真题且不另重复线性插入'),
'7.5-023':('ds-ex7-7','正文例题','删除标记保留探查，失败ASL1.8'),
'8.2-012':('ds-ex8-1','正文例题','d5与d3全部组填回，第二趟B'),
'8.2-015':('ds-08-05','并入稳定性','希尔远移可不稳，不能由组内稳定推出全局稳定'),
'8.3-018':('ds-ex8-2','正文例题','两内部枢轴不足以支持两趟，D不可能'),
'8.4-001':('ds-08-04','并入算法定义','每趟选未排序区最小与首位交换是简单选择'),
'8.4-005':('ds-05-11','并入堆边界','小根堆最大可在叶，叶从floor(n/2)+1起'),
'8.4-013':('ds-ex8-3','重复合并','大根堆删顶与2015小根题为对称下滤模型；保留单孩子比较口径'),
'8.4-014':('ds-05-11','并入数据结构对照','根到叶单调是堆序，不是BST左右区间'),
'8.4-017':('ds-ex8-3','正文例题','实际三次关键字比较，不计边界'),
'8.5-003':('ds-08-11','并入空间条件','快排栈平均/最坏分开，归并数组n；基数按链式r或数组n+r分开'),
'8.5-012':('ds-ex8-5','正文例题','LSD先个位、同桶保序，第一趟C'),
'8.6-007':('ds-08-11','并入过程比较','趟的定义与快排划分深度依初态，固定轮算法另论'),
'8.6-010':('ds-08-11','并入代价比较','折半插入比较与移动分开，简单选择比较固定'),
'8.6-012':('ds-08-11','并入适用边界','区分串行阶段依赖与任意实现不可并行，原题绝对表述不无条件复述'),
'8.7-001':('ds-08-01','并入定义','处理期间是否需内外存交换，不以数据量阈值定义'),
'8.7-010':('ds-08-10','并入逐层机制','败者树沿冠军路径每层一比，堆可提前停止，不把两过程等同'),
}
assert len(DETAIL)==97,len(DETAIL)
errors=[]
for r in raw:
    short=f"{r['section']}-{r['question_number']:03d}";anchor,dest,reason=DETAIL[short];assert anchor in all_anchors,anchor;loc=all_anchors[anchor]
    related=[e['id'] for e in all_examples if r['id'] in e['personal_error_ids']]
    errors.append({'id':r['id'],'original_location':{'source_json':r['source_json'],'json_pointer':r['json_pointer'],'question_pdf':r['question_pdf'],'question_pdf_page':r['question_pdf_page']},'subject':'DS','knowledge_ids':r['knowledge_ids'],'method':r['core_method'],'actual_answer_information':{'original_choice':r['original_wrong_choice'],'book_answer_observed':r['answer_observed'],'original_reasoning':None,'original_grading':r['original_grading']},'confirmed_personal_cause':None,'cause_status':'未见原推理，不由错选猜心理原因；正文仅解释已核验机制和一般错误条件','destination':dest,'anchor':anchor,'location':f"{loc['manuscript']}#{anchor}",'reader_heading':loc['heading'],'reason':reason,'related_examples':related,'identity':{'personal_error':True,'book_claimed_exam_years':r.get('book_claimed_exam_years',[]),'verified_exam_selected':any(e['category']=='真题' for e in all_examples if e['id'] in related)},'verification_scope':'原题题干选项已实读、原书答案字母目验沿用首轮；正文选用题另作源卷/过程检查。未入正文原题不一概宣称本轮二次解答完成。','missing_for_solution':r.get('missing_problem_information_requiring_user',[])})

original_self_checks={
1:['反复非递归函数调用空间可复用','链式表示不能推出逻辑类型'],
2:['连续删除时前驱不推进','公共尾结点给出至少一结点共同后缀','写读双指针消除相邻重复，明确无序时不保证全局唯一'],
3:['循环队列已用与剩余容量同时计算','三对角数组从1开始公式，限定内部行'],
4:['重复字符next与nextval全表','abab失配链接与主串不动','已有失败表时扫描成本与预处理成本分开'],
5:['度1结点数同时决定非完全性','先序中序相同迫使仅右孩子','路径压缩改变双亲但不改集合','关键字互异下第二大只能在堆根孩子'],
6:['n−1边需连通条件才能称树','新增一依赖让拓扑从两种变唯一','改边权不保证两种优化同时改变','多关键路径下缩短一个活动未必降工期'],
7:['只检查直接孩子不足以判BST','B树空根降高不必空树','删除标记计入失败探查','红叔情境只变色而非套旋转'],
8:['插入等号改变稳定性','外部归并取整趟数与I/O阶段口径','无等键输入不能观察稳定性差异'],
}
for ch,tasks in original_self_checks.items():
    chapters[ch-1]['original_supplements']=[{'type':'原创自测补充','task':task,'location':f"{chapters[ch-1]['manuscript']}#ds-ch{ch}-check",'source_priority_check':'已先检查本章实际选入真题、97条错题和所读主书题；用于检验明确边界，原题可用者已恢复为2019、2022及共享栈原题，不将原创计入真题覆盖','deletion_check':'删除将少一次对“'+task+'”的闭卷检验；不另引入同模型长题','verification':'答案见正文就近章末；可计算者纳入results.json，不以原创身份代替复算'} for task in tasks]

unresolved=[
{'id':'DS-SCOPE-2027','status':'待核验','issue':'2027正式大纲已出版但完整细目未取得；本书60组按已读本地转录范围编排','action':'获得正式细目后逐条交叉核；不宣称正式覆盖完成'},
{'id':'DS-Q-1.2-002','status':'已规避原题单选歧义','issue':'原单选D“通常用效率衡量优劣”有可成立解读','action':'并入必备特性/质量评价辨析，不重复印为无歧义单选'},
{'id':'DS-Q-3.2-009','status':'正文已写明条件','issue':'原题把数组MaxSize与可用最大容量混写','action':'采用M单元牺牲1、容量M−1；满条件需依表示约定'},
{'id':'DS-Q-6.4-019','status':'正文已补成立条件','issue':'DAG存在拓扑序不保证任意原编号的邻接矩阵三角','action':'仅对按拓扑序重编号后的矩阵使用结论'},
{'id':'DS-Q-7.2-002','status':'正文已纠正原停机条件','issue':'原“不小于即失败”会误判相等','action':'相等成功、严格大于失败；不把缺陷题当完整主例'},
{'id':'DS-Q-8.6-012','status':'原题实现口径仍有限定','issue':'“算法不可以并行”绝对说法越过所给串行步骤模型','action':'正文按阶段依赖讲解，说明LSD内部也可设计并行；不照搬为普遍禁断'},
{'id':'DS-PDF-FINAL','status':'待最终锁版视觉检查','issue':'知识审读/计算不能替代最终PDF全页视觉检查','action':'等待主代理锁定最终PDF，按SHA单独记录editorial/full/pdf/DS/visual_review.json'},
]

for ch in chapters:
    ids={k['id'] for k in ch['knowledge']}
    for k in ch['knowledge']:
        k['example_ids']=[e['id'] for e in all_examples if k['id'] in e['knowledge_ids']]
        k['personal_error_ids']=[e['id'] for e in errors if k['id'] in e['knowledge_ids']]
    ch['error_ids']=[e['id'] for e in errors if e['location'].split('#')[0]==ch['manuscript']]
    ch['checks']['anchors']='稳定ID对应真实具体小节；程序断言60组全部唯一出现'

out={'schema_version':'DS-full-1','subject':'DS','subject_name':'数据结构','date':'2026-10-16','status':'8章正文与源图完成；内容锁定待最终PDF视觉检查','scope_declaration':'60个暂定知识组均有正文，正式2027大纲细目未获；不宣称官方逐条覆盖','book_baseline':{'title':'2027年数据结构考研复习指导','publisher':'电子工业出版社','edition':'2026年1月第1版','ISBN':'978-7-121-51791-4','path':BOOK},'source_label_policy':'真题仅【年份】，非真题仅〖原节号-原题号〗；详细来源和个人作答仅内部记录。综合与选择同号在本台账区分。','counts':{'chapters':8,'knowledge_groups':60,'full_main_examples':44,'selected_source_questions_including_self_checks':len(all_examples),'real_exam_source_questions':sum(bool(e['source'].get('exam_year')) for e in all_examples),'typical_source_questions':sum(not bool(e['source'].get('exam_year')) for e in all_examples),'original_short_self_checks':sum(map(len,original_self_checks.values())),'personal_errors_read_and_assigned':97,'figures':len(figmanifest),'executed_check_records':json.loads((HERE/'results.json').read_text())['checks_count']},'chapters':chapters,'errors':errors,'unresolved':unresolved,'review_resolution':{'RV-024':{'status':'closed','evidence':'editorial/full/DS/sources/DS_7.3_comprehensive_003.png','finding':'PDF307印刷295确为§7.3综合03，逐个插入相同七值并每次画AVL；未改数据/任务，非选择003。'}},'review_notes':['原97题只有错选而无思路，已读选项与批改可见范围保留，不编造个人错因。','错题去向包含主例、合并解释、复习保留及去重，不能把97个去向等同97题全部再次独立解答。','35道真题身份基于完整社区复原卷与可信主书互证，非官方原卷/答案认证。',f"{json.loads((HERE/'results.json').read_text())['checks_count']}条代码核验检查真实计算或过程；正式大纲、源题身份和PDF视觉另记。"]}
# Revision-2 content review is separate from the archived V1 PDF report.
revision2_path=ROOT/'editorial/revision2/DS_revision_sources.json'
if revision2_path.exists():
    previous=json.loads((HERE/'chapter_records.json').read_text()) if (HERE/'chapter_records.json').exists() else {}
    history=previous.get('historical_v1_pdf_review')
    if history is None and previous.get('final_pdf_review',{}).get('status')=='PASS':history=previous['final_pdf_review']
    if history:out['historical_v1_pdf_review']=history
    out.update({'schema_version':'DS-full-2-content-review','date':'2026-10-17','status':'第二轮正文与机制图完成，供内容审阅；主编仅导出正文审阅PDF，本轮未做排版检查','author_stage_status':'内容修订完成，待审阅','final_pdf_review':{'status':'NOT_RUN_REVISION2','reason':'本分支未生成讲义PDF或覆盖V1；主编仅导出正文审阅PDF，本轮未进行讲义PDF分页、裁切、视觉或排版检查'},'revision2':{'report':'editorial/revision2/DS_revision.md','sources':'editorial/revision2/DS_revision_sources.json','new_calculation_ids':[f'DS-C{i:02}' for i in range(58,67)],'changed_chapters':[7,8]}})
    for ch in chapters:ch['checks']['PDF_visual']='本轮未执行；V1结果仅见historical_v1_pdf_review'

assert len({k['id'] for c in chapters for k in c['knowledge']})==60
assert len(errors)==97 and len({e['id'] for e in errors})==97
assert len(all_examples)==47
for f in files:
    s=f.read_text();assert not re.search(r'你的错题|你原选|原错选|做题本|ERR-|例\s*DS\d',s)
(HERE/'chapter_records.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
with open(HERE/'errors_destinations.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','destination','location','reason']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in errors)
with open(HERE/'selected_questions.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','reader_label','marker','category','personal_error','location','source','selection_reason']);w.writeheader()
    for r in all_examples:w.writerow({k:(json.dumps(r[k],ensure_ascii=False) if k=='source' else r[k]) for k in w.fieldnames})
lock=json.loads((HERE/'content_lock.json').read_text()) if (HERE/'content_lock.json').exists() else {}
lock.update({'subject':'DS','locked':not revision2_path.exists(),'date':'2026-10-17' if revision2_path.exists() else '2026-10-16','files':[{'path':c['manuscript'],'sha256':c['sha256']} for c in chapters],'review_issue_closed':'RV-024','remaining':'本轮仅正文内容供审阅，不做讲义PDF分页、裁切、视觉或排版检查' if revision2_path.exists() else '仅最终PDF分页、裁切、字号和跳转视觉检查；若需改排版不改知识口径'})
if revision2_path.exists():lock['stage']='revision2_content_review'
(HERE/'content_lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2))
print(json.dumps(out['counts'],ensure_ascii=False))

if __name__=='__main__':pass
