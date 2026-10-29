from pathlib import Path
import json,re,datetime
ROOT=Path(__file__).resolve().parents[3]
records=json.loads((ROOT/'sources/source_inventory.json').read_text())['files']
# This table is an editorial mapping assembled after comparing the actual lesson
# knowledge groups with the named sections. No target is inferred from a filename.
rows={
'CO01':[
('1.0_',['CO01-02','CO01-components'],['硬件的物理形态、二进制信息与四科联系']),
('1.1_',['CO01-history','CO01-history-complete'],['器件技术、发展阶段、摩尔经验趋势与应用背景']),
('1.2.1+',['CO01-components','CO01-03'],['五大部件、CPU与主机、冯诺依曼特点']),
('1.2.2（',['CO01-04','CO01-program-trace','CO01-words'],['ACC/MQ/IR/PC/MAR/MDR、取指与取数微操作、程序状态']),
('1.2.3 ',['CO01-software','CO01-05'],['系统/应用软件、机器/汇编/高级语言、编译解释、ISA功能等价']),
('1.2.4 ',['CO01-03','CO01-software'],['五级机器、体系结构与组成、透明性']),
('1.2.5 ',['CO01-program-trace','CO01-05'],['存储程序、y=ab+c执行、预处理编译汇编链接']),
('1.3 ',['CO01-07','CO01-performance-complete','CO01-capacity'],['机器字长、地址空间容量、主频时钟、CPI/IPC、执行时间、吞吐率/MIPS/FLOPS'])],
'CO02':[
('2.1.1 ',['CO02-02','CO02-03'],['位权、整数除基取余、小数乘基取整、基数分组、真值与机器数']),
('2.1.2+2.1.3 ',['CO02-04','CO02-proof'],['原码反码补码移码、定点整数/小数范围、零和取反加一']),
('2.1.2+2.1.3（',['CO02-04','CO02-proof'],['模运算补数、减法化加法、移码序关系']),
('2.1.4_1',['CO02-05','CO02-06','CO02-07'],['C整数类型及有符号/无符号、长短转换和机器模型条件']),
('2.1.4_2',['CO02-05'],['零扩展、符号扩展及保持真值条件']),
('2.2.0_1',['CO02-digital-logic'],['逻辑门、异或、真值表、德摩根律、优先级']),
('2.2.0_2',['CO02-mux-tristate'],['MUX选择位、高阻态、共享总线使能']),
('2.2.1_1',['CO02-09','CO02-adder-complete'],['半加/全加、本位和进位、串行进位与先行进位']),
('2.2.1_3',['CO02-09','CO02-adder-complete'],['ALU选择控制和功能组织']),
('2.2.2 ',['CO02-08'],['逻辑/算术移位、符号扩展、移位与乘除的条件']),
('2.2.3_1',['CO02-09','CO02-11'],['补码加减、溢出、同号加异号减']),
('2.2.3_2',['CO02-11','CO02-12'],['无符号进位/借位、CF/ZF及截断']),
('2.2.3_3',['CO02-09','CO02-10','CO02-14'],['异或取反和Sub进位、标志位电路、CF与OF不同判断']),
('2.2.4_0',['CO02-15','CO02-multiply-process','CO02-division-complete'],['书课乘除法适配、位宽与算法过程口径']),
('2.2.4_1',['CO02-16','CO02-unsigned-trace'],['13乘11、部分积/乘数组合右移、计数和双倍位宽']),
('2.2.4_2',['CO02-booth-trace','CO02-16'],['补码Booth、辅助位、-3乘6、乘法溢出与保护位']),
('2.2.4_3',['CO02-multiply-hardware'],['顺序复用、阵列组合、流水线乘法器']),
('2.2.4_4',['CO02-division-complete','CO02-division-registers'],['双精度被除数R/Q、15除2逐轮、商溢出、除数零']),
('2.2.4_5',['CO02-signed-division-trace','CO02-division-complete'],['符号扩展、-7除3寄存器过程、6除3/3除-7、商符号和异常']),
('2.3.1_1',['CO02-18','CO02-19'],['IEEE754符号阶码尾数、偏置、隐含位、单双精度编码']),
('2.3.1_2',['CO02-19','CO02-20','CO02-24'],['机器数与真值、负数大小、整数与浮点转换']),
('2.3.1_3+4',['CO02-18','CO02-23','CO02-precision'],['范围、正规/次正规、正负零、无穷NaN、精度']),
('2.3.2_1+2',['CO02-21'],['对阶、尾数加减、规格化、舍入与溢出步骤']),
('2.3.2_3',['CO02-precision','CO02-rounding-complete'],['保护/舍入/粘滞位、最近偶数、中点示例']),
('2.3.2_4',['CO02-22','CO02-24'],['右规/舍入上溢、左规下溢、尾数进位与最终范围']),
('2.3.4 ',['CO02-25','CO02-26','CO02-storage'],['大小端、字节编址、自然边界对齐和结构体填充'])],
'CO03':[
('3.1 ',['CO03-02','CO03-storage-details'],['存储层次、分类、速度容量成本、存取周期与时间']),
('3.2.0+',['CO03-03','CO03-04','CO03-06'],['存储阵列、MAR/MDR、译码、地址与数据位宽']),
('3.2.1 ',['CO03-03','CO03-05','CO03-storage-details'],['SRAM/DRAM、读后再生、地址复用、集中分散异步刷新']),
('3.2.2 ',['CO03-rom','CO03-rom-complete'],['掩膜ROM/PROM/EPROM/EEPROM/Flash与RAM比较']),
('3.2.4 ',['CO03-08','CO03-storage-details','CO03-interleave-complete'],['双端口同址冲突、单体多字、高低位交叉、多模块带宽']),
('3.3 ',['CO03-10','CO03-11','CO03-chip-expansion-complete','CO03-chip-example'],['字/位扩展、读写控制、片选译码、地址区间']),
('3.4.1 ',['CO03-12','CO03-13','CO03-disk-complete'],['磁道扇区容量、访问时间、RAID分级与冗余边界']),
('3.4.2 ',['CO03-03','CO03-12','CO03-ssd-details'],['SSD页读写/块擦除、FTL、垃圾回收和磨损均衡']),
('3.5.1+',['CO03-14','CO03-cache-model-complete'],['局部性、命中缺失、分块、同时访问/顺序访问平均时间']),
('3.5.3 ',['CO03-17','CO03-18','CO03-21'],['直接/全相联/组相联、标记索引偏移、有效位比较']),
('3.5.4 ',['CO03-19','CO03-replacement-complete'],['RAND/FIFO/LRU/LFU、命中更新、完整访问序列']),
('3.5.5 ',['CO03-20','CO03-assoc'],['写直达/回写、写分配/非写分配、脏位、多级Cache']),
('3.6 ',['CO03-22','CO03-23','CO03-24','CO03-28'],['虚拟地址到物理地址、TLB/页表/Cache、缺页与数据缺失'])],
'CO04':[
('4.1.1+',['CO04-02','CO04-formats-complete','CO04-implicit'],['操作码地址码、零一二三四地址、定长变长、访存次数']),
('4.1.4 ',['CO04-03','CO04-opcode-complete','CO04-proof'],['扩展操作码前缀、逐层保留、完整分配例']),
('4.2.1 ',['CO04-04','CO04-05'],['顺序/跳跃指令寻址、PC和指令长度']),
('4.2.2_1',['CO04-04','CO04-06','CO04-addressing-complete'],['立即/直接/间接/寄存器/寄存器间接寻址']),
('4.2.2_2',['CO04-addressing-complete','CO04-05'],['相对/基址/变址、偏移单位、PC基准和重定位']),
('4.2.2_3',['CO04-addressing-complete','CO04-stack-complete'],['软硬堆栈、SP、增长方向、压栈弹栈顺序']),
('4.3.1_1',['CO04-09','CO04-x86-complete'],['源程序机器级对应、x86寄存器、地址形成']),
('4.3.1_2',['CO04-x86-complete','CO04-effects'],['传送算术逻辑移位比较、lea/cmp/test副作用']),
('4.3.1_3',['CO04-x86-complete'],['Intel/AT&T操作数顺序、立即数/寄存器标志及位宽']),
('4.3.2 ',['CO04-11','CO04-branch-flags'],['条件码、有符号无符号条件转移、选择控制流']),
('4.3.3 ',['CO04-loop-complete','CO04-11'],['while/for/do循环、条件判断和回边']),
('4.3.4 ',['CO04-12','CO04-14','CO04-stack-complete'],['调用返回、参数寄存器、栈帧、递归阶乘和机器编码']),
('4.4 ',['CO04-07','CO04-08'],['CISC/RISC指令集倾向、复杂指令与流水实现条件'])],
'CO05':[
('5.1 ',['CO05-registers','CO05-state-complete'],['CPU功能、运算控制部件、寄存器与程序员可见状态']),
('5.2 ',['CO05-cycle','CO05-exception'],['指令机器时钟周期、取指间址执行中断、顺序与流水方案']),
('5.3_1',['CO05-datapath','CO05-datapath-complete','CO05-fetch-details'],['单总线微操作、暂存Y/Z、控制信号和节拍依赖']),
('5.3_2',['CO05-datapath','CO05-datapath-complete'],['专用通路、寄存器传送、访存和ALU连接']),
('5.4.1 ',['CO05-control','CO05-hardwired-design'],['硬布线输入、操作时间表、逻辑表达式与设计步骤']),
('5.4.2 ',['CO05-microsequence','CO05-microprogram-complete'],['CM/CMAR/CMDR、公共取指、操作码入口映射']),
('5.4.3 ',['CO05-example-4','CO05-example-5','CO05-microinstruction-design'],['直接/字段编码、互斥相容、水平垂直、下地址形成']),
('5.4.4 ',['CO05-microdesign-steps','CO05-microprogram-complete'],['微程序控制单元设计、静态动态毫微程序及比较']),
('5.6_1',['CO05-pipeline-performance','CO05-example-7','CO05-five-stage-details'],['时空图、延迟吞吐、加速比效率、理想公式条件']),
('5.6_2',['CO05-hazards','CO05-pipeline-types','CO05-issue'],['结构/数据/控制冒险、RAW/WAR/WAW、分类与处理']),
('5.6_3',['CO05-stage-registers','CO05-example-8','CO05-example-11','CO05-five-stage-details'],['五段LOAD/STORE/ALU/转移、转发、阻塞和最短调度']),
('5.7_1 多处理器基本概念.pdf',['CO05-flynn','CO05-multithread','CO05-thread-details'],['SISD/SIMD/MISD/MIMD、向量处理、共享/私有主存、多核']),
('5.7_1 多处理器基本概念骚图',['CO05-flynn','CO05-thread-details'],['共享地址空间、多计算机消息通信、多核集成维度']),
('5.7_2',['CO05-multithread','CO05-thread-details','CO05-thread-schedule'],['细粒度/粗粒度/SMT发射、线程状态与执行资源共享'])],
'CO06':[
('6.1.1~',['CO06-metrics','CO06-types-complete','CO06-organization-complete'],['总线特点、片内/系统/通信分类、信息方向、单多总线和桥']),
('6.1.5 ',['CO06-metrics','CO06-example-1','CO06-example-2'],['宽度/复用/根数、时钟与工作频率、带宽及单位']),
('6.2.0 ',['CO06-arbitration','CO06-arbitration-complete'],['拓展：链式/计数器/独立请求、分布式仲裁']),
('6.2.1~',['CO06-transaction','CO06-sync','CO06-async','CO06-timing-complete'],['事务四阶段、同步/异步/半同步/分离式、握手撤销条件']),
('6.3 ',['CO06-standards-complete'],['拓展：ISA/PCI/PCIe/USB/SATA等标准、串行替代并行的条件'])],
'CO07':[
('7.1.1+',['CO07-map','CO07-io-structure-complete'],['I/O软硬件、查询中断DMA通道、I/O指令与通道指令']),
('7.1.3 ',['CO07-devices','CO07-peripherals-complete'],['输入输出外存、显示器/打印机分类和性能']),
('7.2 ',['CO07-interface','CO07-io-structure-complete'],['接口端口、统一独立编址、数据状态控制寄存器和传送']),
('7.3.1 ',['CO07-query','CO07-query-complete','CO07-example-2'],['忙等/定时查询、速率缓冲期限和CPU占用']),
('7.3.2_1',['CO07-interrupt','CO07-entry','CO07-interrupt-complete'],['请求判优响应、中断隐指令、断点与现场恢复']),
('7.3.2_2',['CO07-mask','CO07-example-3','CO07-interrupt-complete'],['响应/处理优先级、屏蔽字、嵌套、NMI/INTR']),
('7.3.2_3',['CO07-example-4','CO07-overlap-example'],['中断I/O CPU预算、设备准备服务重叠和有限批次端点']),
('7.3.3 ',['CO07-dma','CO07-example-5','CO07-example-6','CO07-dma-complete'],['DMA控制器寄存器、预处理/传送/后处理、三种总线占用方式'])]}
for c,specs in rows.items():
 chapter=ROOT/'chapters'/c;s=(chapter/'content.md').read_text();anchors=set(re.findall(r'\{#([^}]+)',s));files=[f for f in records if f['chapter']==c and f['kind']=='lecture'];entries=[]
 for prefix,targets,topics in specs:
  matches=[f for f in files if Path(f['path']).name.startswith(prefix)]
  if len(matches)!=1:raise RuntimeError((c,prefix,[f['path'] for f in matches]))
  f=matches[0];assert set(targets)<=anchors,(c,set(targets)-anchors)
  entries.append({'path':f['path'],'pages':list(range(1,f['pdf_pages']+1)),'topics':topics,'targets':targets,'verification':'王道课件主题、知识回顾及有关例题与所列正文节对照；原始文本逐页建立索引，数值按独立模型复算。关键源图的视觉范围见author_report；此处页列表不是逐页人工视觉认证。','page_scope':'all file pages indexed; knowledge-group mapping'})
 assert len(entries)==len(files),(c,len(entries),len(files))
 figures=[]
 for name in re.findall(r'!\[[^\]]*\]\(([^)\s]+)',s):
  p=chapter/'figures'/Path(name).name
  if not p.exists():raise RuntimeError((c,name))
  figures.append({'id':p.stem,'targets':[],'source':'对应知识组的王道课件/教材示意，正文保留解释与约定','status':'editable_vector_available','svg':p.with_suffix('.svg').exists(),'png':p.with_suffix('.png').exists(),'visual_review':'pending final PDF figure inspection'})
 (chapter/'sources/course_coverage.json').write_text(json.dumps({'chapter':c,'primary_source':'王道计算机组成原理基础考点课件','lecture_files':entries,'figures':figures,'unresolved':[],'verification_boundary':'文件/页与知识组覆盖已登记；数值复算和最终PDF视觉证据另存，不能由映射数量推定全部原图已逐幅审定。'},ensure_ascii=False,indent=2))
 report=f'''# {c} 编写与核验记录\n\n主母本为项目内王道计算机组成原理课件。共{len(files)}份、{sum(f['pdf_pages'] for f in files)}个文件页；正文采用课件知识组和王道书术语，博客仅作表达参考。\n\n上一检查点已有实质扩写正文和新增矢量图，本轮逐课件核对主题、知识回顾及对应例题与正文位置，整理真实页码索引。覆盖以知识组登记，并非宣称每张动画页独立重写。关键数值由code/中的Python整数、分数、位级/IEEE模型复算，详细结果见numeric_checks.json、course_numeric_checks.json。\n\n扫描源的补充OCR只作阅读初稿，CO03 SSD与CO05硬件多线程按可读文本和关键渲染页核对。原始课件的全部图像尚未逐幅授予视觉结论；最终PDF全部页面及被引用教学图将单独审阅并绑定PDF指纹。\n\n正文、代码、图稿与来源映射就绪；PDF视觉审阅状态见visual_review.json与qa.json。\n'''
 (chapter/'sources/author_report.md').write_text(report)
 print(c,len(entries),len(figures))
