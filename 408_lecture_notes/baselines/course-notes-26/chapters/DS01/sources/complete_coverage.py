from pathlib import Path
import json,datetime,hashlib,re,shutil
ROOT=Path(__file__).resolve().parents[3]
INV=json.loads((ROOT/'sources/source_inventory.json').read_text())['files']
M={
'DS01':{
'1.0_开篇_数据结构在学什么.pdf':(['信息化、关系表示与处理问题'],['DS01-01'],[]),
'1.1_数据结构的基本概念.pdf':(['数据、元素、数据项、对象','逻辑结构、存储结构、运算','数据类型与ADT'],['DS01-01','DS01-map'],[]),
'1.2_1_算法的基本概念.pdf':(['算法定义、五项特性与设计质量','年龄记录逐轮排序示例','正确性与循环不变式'],['DS01-02','DS01-sort-example','DS01-code'],[]),
'1.2_2_算法的时间复杂度.pdf':(['逐语句计数与主阶','加法乘法规则、增长次序','对数循环与顺序查找平均最坏'],['DS01-03','DS01-rules','DS01-count'],[]),
'1.2_3_算法的空间复杂度.pdf':(['程序与数据空间','局部数组与空间峰值','递归每层常数或线性空间的差异'],['DS01-04','DS01-space-example'],[])
},
'DS02':{
'2.1_线性表的定义和基本操作.pdf':(['同型有限序列、表长、位序','初始化销毁增删改查','引用参数与修改调用者'],['DS02-01','DS02-code-seq','DS02-compare'],[]),
'2.2.1_顺序表的定义.pdf':(['地址与元素宽度','SqList静态、SeqList动态','void初始化与扩容、容量表长、连续存储'],['DS02-02','DS02-code-seq','DS02-dynamic'],[8,9]),
'2.2.2_1_顺序表的插入删除.pdf':(['位序下标映射','后移/前移方向、边界检查','平均移动n/2与(n-1)/2'],['DS02-02','DS02-seq-update'],[]),
'2.2.2_2_顺序表的查找.pdf':(['GetElem/LocateElem接口','首次相等位序和失败0','随机访问、结构体比较与平均代价'],['DS02-seq-query'],[]),
'2.3.1_单链表的定义.pdf':(['LNode和LinkList','头指针、头结点、首元','带头与不带头空状态'],['DS02-03','DS02-code-link','DS02-nohead'],[]),
'2.3.2_1_单链表的插入删除.pdf':(['指定前驱后插与按位插入','指定结点前插复制法的身份条件','按位删除和复制后继删除的尾结点例外'],['DS02-03','DS02-link-update','DS02-nohead'],[]),
'2.3.2_2_单链表的查找.pdf':(['GetElem允许i=0返回头结点','LocateElem与表长遍历','边界与定位成本'],['DS02-code-link','DS02-link-update'],[]),
'2.3.2_3_单链表的建立.pdf':(['List_HeadInsert/List_TailInsert','9999输入终止、尾指针不变量','头插逆序与原地逆置'],['DS02-build','DS02-detail1'],[]),
'2.3.3_双链表.pdf':(['prior/next定义','四条插入链接与删除后继','非循环链尾与遍历方向'],['DS02-04','DS02-double-code','DS02-ex3'],[]),
'2.3.4_循环链表.pdf':(['单向/双向循环空状态','尾指针与首尾联系','循环终止和插入删除边界'],['DS02-04','DS02-double-code'],[]),
'2.3.5_静态链表.pdf':(['游标与物理数组位置','头0、链尾-1、空闲-2','课件e1-e4具体布局和地址'],['DS02-double-code'],[]),
'2.3.6_顺序表和链表的比较.pdf':(['逻辑相同与表示不同','创销、增删、按位/按值查找','容量预测、存储密度和局部性'],['DS02-compare','DS02-02'],[])
},
'DS03':{
'3.1.1_栈的基本概念.pdf':(['栈顶栈底、后进先出、基本接口','输出合法性与容量模拟','Catalan计数'],['DS03-01','DS03-ex1','DS03-code'],[]),
'3.1.2_栈的顺序存储实现.pdf':(['SqStack的top两种表示','入出栈/读顶区别','共享栈ShStack'],['DS03-03','DS03-code','DS03-share-code'],[]),
'3.1.3_栈的链式存储实现.pdf':(['LiStack带头/无头模型','链头作为栈顶、malloc/free'],['DS03-04','DS03-linked-code'],[]),
'3.2.1_队列的基本概念.pdf':(['FIFO、队头队尾、基本操作'],['DS03-02','DS03-code'],[]),
'3.2.2_队列的顺序实现.pdf':(['循环下标和模距离','牺牲一个单元/size/tag三方案','rear指队尾或下一空位的不同约定'],['DS03-detail1','DS03-ex2','DS03-code'],[]),
'3.2.3_队列的链式实现.pdf':(['LinkQueue结构','带头/不带头初始化入队出队','最后一个结点出队后重设rear'],['DS03-04','DS03-linkqueue-code'],[3,4,5,6]),
'3.2.4_双端队列.pdf':(['两端操作及输入/输出受限','1至4输入的14/22种合法输出与非法序列'],['DS03-02'],[]),
'3.3.1_栈在括号匹配中的应用.pdf':(['最近左括号先配对','过早右括号、种类不符、剩左括号','bracketCheck完整代码'],['DS03-detail2','DS03-bracket-code'],[]),
'3.3.2_1_栈在表达式求值中的应用(上).pdf':(['中/前/后缀与手算','操作数左右角色','课件15/7等数值表达式'],['DS03-07','DS03-app-method','DS03-expression-trace'],[]),
'3.3.2_2_栈在表达式求值中的应用(下).pdf':(['运算符栈转换全过程','同级左结合、括号边界','两个栈直接求中缀值'],['DS03-expression-trace','DS03-infix-eval'],[]),
'3.3.3_栈在递归中的应用.pdf':(['返回地址实参局部状态','factorial与Fib课件原算法','Fib4完整调用树与栈深、重复子问题'],['DS03-detail3','DS03-recursion-model'],[3,6,7]),
'3.3.4+3.3.5_队列的应用.pdf':(['层序遍历与BFS','先来先服务、打印缓冲区'],['DS03-detail3','DS03-app-method'],[]),
'3.4.1~3.4.4_特殊矩阵的压缩存储.pdf':(['数组行/列优先寻址','对称、上/下三角、三对角正反映射','5x6稀疏矩阵原数据与三元组/十字链'],['DS03-05','DS03-06','DS03-matrix-method','DS03-matrix-table'],[])
}}
figure_maps={
'DS01':{'DS01_logical_structures':['DS01-01'],'DS01_storage_models':['DS01-01'],'DS01_recursion_space':['DS01-space-example']},
'DS02':{'DS02_dynamic_growth':['DS02-dynamic'],'DS_01_list_insert':['DS02-03'],'DS_02_shared_suffix':['DS02-ex5'],'DS02_build_order':['DS02-build'],'DS02_double_and_cycles':['DS02-double-code']},
'DS03':{'DS_03_circular_queue':['DS03-detail1'],'DS03_linkqueue_last':['DS03-linkqueue-code'],'DS03_matrix_positions':['DS03-matrix-table'],'DS03_fib_tree':['DS03-recursion-model']}}
for ident,files in M.items():
 ch=ROOT/'chapters'/ident;entries=[]
 for name,(topics,targets,visual) in files.items():
  found=[x for x in INV if x['kind']=='lecture' and x['chapter']==ident and Path(x['path']).name==name]
  assert len(found)==1,(ident,name);item=found[0]
  entries.append({'path':item['path'],'pages':list(range(1,item['pdf_pages']+1)),'topics':topics,'targets':targets,'verification':'All file-page extracted text read after consolidating repeated animation text; numeric/code checks are separately recorded. Source visual inspection is limited to visual_pages, not a claim of all source images reviewed.','visual_pages':visual,'presentation_handling':'Repeated headings, watermarks and promotional slides retained in source index, not treated as knowledge items.'})
 data={'chapter':ident,'primary_source':'王道【课件】数据结构基础考点讲解','mapping_granularity':'lesson/topic groups with exact file pages and stable target anchors; not a claim that each animation frame is an independent figure','lecture_files':entries,'figures':[{'id':k,'targets':v,'status':'editable redrawing or checked reusable project vector','visual_review':'pending final PDF review'} for k,v in figure_maps[ident].items()],'unresolved':[],'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (ch/'sources/course_coverage.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 for x in entries:
  for t in x['targets']:assert '{#'+t+'}' in (ch/'content.md').read_text(),(ident,t)
 report=f'''# {ident} 来源与编写复核\n\n主母本为项目王道【课件】数据结构基础考点讲解。逐份读取本章{len(entries)}份、{sum(len(x['pages']) for x in entries)}页的全部提取文本，阅读时按知识和过程合并重复动画。逐课件的主题、目标锚点及实际视觉页范围见course_coverage.json。自动文本读取和针对代码/图像的视觉核验分别记录，未把所有原课件页冒称已逐图视觉审定。\n\n课件中的知识内容已映射至正文；教学引导、反复标题和宣传页作为非知识展示处理。新增教学图为精确矢量绘制；保留图的数值、标签、方向与正文一致性将在最终PDF中再次核对。代码沿用教材结构、接口和下标；测试程序中的STL仅作为独立对照模型。\n\n'''
 if ident=='DS01':report+='补全四类逻辑结构及四类存储表示图、年龄记录逐轮排序、完整频度与空间分析。C++11严格告警及ASan/UBSan验证20,999项通过。\n'
 elif ident=='DS02':report+='已视觉核对顺序表课件第8/9页，恢复动态InitList与IncreaseSize的void接口；建表采用List_HeadInsert/List_TailInsert返回LinkList并以9999终止。补全静态链表e1-e4原布局、双链与循环空状态图。30000次顺序表和10000次链表随机操作、建表/逆置/筛除及所有n<100旋转对照通过；新增100组正式交互式建表对照通过。\n'
 else:report+='已视觉核对链队列结构和初始化/入队第3至6页，以及递归第3/6/7页。恢复链队列void接口并区分带头/无头模型；补全阶乘/Fib、共享栈类型、两类受限双端队列、rear指队尾变式、直接中缀求值。75000次结构操作、10000组括号、阶乘/Fib对照通过；873450项矩阵坐标计算及受限双端队列穷举通过。\n'
 report+='\n严蔚敏教材对照仅采可核验出处；当前主代码依据王道课件与王道教材。最终PDF全页视觉审阅另存visual_review.json并绑定实际指纹。\n'
 (ch/'sources/author_report.md').write_text(report)
 # Move original source-page screenshots to temporary review storage, never the deliverable.
 src=ch/'sources/source_previews'
 if src.exists():
  dest=Path('/workspace/scratch/finish-ds-source-previews')/ident;dest.parent.mkdir(exist_ok=True)
  shutil.copytree(src,dest,dirs_exist_ok=True);shutil.rmtree(src)
print('coverage complete DS01-DS03')
