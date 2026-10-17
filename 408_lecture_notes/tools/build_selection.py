#!/usr/bin/env python3
"""Editable teaching-task and question-selection records for the OS sample."""
from pathlib import Path
import csv,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'editorial/selection';OUT.mkdir(exist_ok=True)
METHODS=[
('M01','区分资源份数与相关临界区段数',['OS-03-01'],'ERR-OS-2.3-027','§3.1定义短例；保留原题默认的一进程一相关段条件'),
('M02','识别同一对进程的同步与互斥',['OS-03-01'],'ERR-OS-2.3-011','完整例3-1；与一次操作题对照，避免机械数信号量'),
('M03','构造反例检验互斥四项原则',['OS-03-02'],'TYP-OS-SW','三种软件方案各给一条决定性反例，不再凑重复选择题'),
('M04','根据flag与turn推演双方同时申请',['OS-03-02'],'TYP-OS-SW','Peterson给代码、单方/双方竞争与不能双进的推理'),
('M05','原子指令、锁范围与等待方式',['OS-03-03','OS-03-04'],'TYP-OS-HW','TS逻辑代码、Swap步骤及单核/多核屏蔽边界；典型实现模型'),
('M06','记录型信号量的值、队列与唤醒',['OS-03-05'],'MODEL-OS-SEM','初值2的连续P/V状态表；整数型计数语义另辨析'),
('M07','从初态确定许可初值',['OS-03-05'],'ERR-OS-2.3-018','完整例3-2；一次事件与已存在资源分开'),
('M08','前驱图中保留并发并删除已由线程保证的边',['OS-03-05'],'OS-EX-2022-46','完整例3-3；图和线程程序共同推导'),
('M09','单缓冲区一次读写与两次修改的最少量',['OS-03-01','OS-03-05','OS-03-07'],'OS-EX-2024-46','完整例3-4；三问改变活动范围，不套三信号量'),
('M10','从容量、产品与共享状态构造有限缓冲',['OS-03-07'],'TYP-OS-PC','经典模型完整代码，再用分类与整批真题迁移'),
('M11','区分许可预留与物理库存',['OS-03-05','OS-03-07'],'TYP-OS-PC','容量2、P后尚未放入的中间态；不另造替数字题'),
('M12','根据持有与等待找错误P顺序',['OS-03-05','OS-03-07'],'TYP-OS-PC；ERR-OS-2.3-039','给等待环图，真实错选并入模型边界；对照batch例与首读者例'),
('M13','按不同可取条件拆产品量',['OS-03-07'],'OS-EX-2009-45','完整例3-5；奇偶分开、空位共用，补明初态'),
('M14','整批消费者互斥与单次缓冲互斥',['OS-03-07'],'OS-EX-2014-47','完整例3-6；缺货时持batch但不持mutex'),
('M15','首读者/末读者控制整组访问权',['OS-03-08'],'TYP-OS-RW','完整代码与计数错误交错，允许读读并发'),
('M16','区别互斥正确、无死锁、无饥饿和公平',['OS-03-04','OS-03-08'],'TYP-OS-RW；TYP-OS-PHI','写者饥饿轨迹与gate条件；无证据不称高频'),
('M17','多人持多资源时断开循环等待',['OS-03-09'],'TYP-OS-PHI','五人等待环、room=4代码和全局资源排序证明'),
('M18','条件变量wait的职责及无等待者signal',['OS-03-06'],'OS-EX-2018-28；ERR-OS-2.3-029','完整真题例3-7；第29题的真实错选并入无等待者边界'),
('M19','等待时释放锁、通知后重检及丢失唤醒',['OS-03-06'],'TYP-OS-CV','Mesa/POSIX接口过程图与while；Hoare语义另说明条件'),
]

def save_csv(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})

def main():
    methods=[dict(id='OS-'+i,task=t,knowledge_ids=k,representative=q,handling=h,
                  status='样章已讲解；原正式大纲细目待核',frequency_basis=None)
             for i,t,k,q,h in METHODS]
    (OUT/'考法清单.json').write_text(json.dumps(methods,ensure_ascii=False,indent=2));save_csv(OUT/'考法清单.csv',methods)
    items=[]
    def add(i,kind,priority,personal,source,method,steps,boundary,difficulty,reason,added,deletion,destination,change='题意和数据未修改；解析重新编写'):
        items.append(dict(id=i,category=kind,priority=priority,is_personal_error=personal,
            source_and_location=source,methods=method,key_steps=steps,boundaries=boundary,
            teaching_difficulty=difficulty,reason=reason,added_value=added,deletion_check=deletion,
            destination=destination,changes=change,review_state='本轮已检查；官方原卷/官方答案未取得时不声称官方核验'))
    exams=json.loads((ROOT/'editorial/sources/os_exam_candidates.json').read_text())['questions']
    detail={q['id']:q for q in exams}
    true_data=[
      ('OS-EX-2022-46','OS-M08','线程内顺序先保留；只传A完成与C完成两种跨线程通知','不得增加D到E/F的边','中等','图到程序的完整转换','线程归属使五条边只需两次跨线程通知','失去前驱图的完整真题演示','正文例3-3'),
      ('OS-EX-2024-46','OS-M09','三情境分开；一次先后done=0，两修改者mutex=1','各一次；只有题给操作；修改不清空分组','基础至中等','同对象但活动范围不同，纠正固定背量数','同步本身已排除一次读写重叠的边界','失去最少量与执行次数的辨析','正文例3-4'),
      ('OS-EX-2009-45','OS-M13','empty共用，odd/even按可取类别分开；锁内取放，锁外统计','原题没写初态，解答显式按空；可推广a奇b偶','中等','在标准模型上加不同的等待条件','有产品不等于有本进程能取的产品','失去分类许可模型','正文例3-5'),
      ('OS-EX-2014-47','OS-M14','batch锁整批；mutex只锁单次；空位逐件归还','消费者缺货可等；不能阻止生产者补货','综合','锁范围由连续10件条件决定','一批中的消费者排他与生产并发同时成立','失去批次约束改变锁范围的迁移','正文例3-6'),
      ('OS-EX-2025-45','OS-M10；OS-M13','空坑配额、阶段产物和共享铁锹分别建量','树坑按尚未放苗空坑理解；丙独用水桶','综合','可用于后续阶段流水线综合','新增三阶段工具共享，但当前单元主要模型已由四题与典型模型完成','本轮删除不损失当前主要考法；保留到后续综合章','备用，未收入样章'),
    ]
    for i,m,st,b,di,r,a,de,dest in true_data:
        q=detail[i]
        add(i,'408真题（教材+社区完整重建卷二手交叉核验）',1,False,
            {'detail':'editorial/sources/os_exam_candidates.json','id':i,'book':q['book']},m,st,b,di,r,a,de,dest)
    for i,num,ex,method,steps,boundary,reason,added in [
      ('ERR-OS-2.3-011',11,'正文例3-1','OS-M02','先写后读为同步，访问共享缓冲区为互斥','不能从关系分类机械推出必须几个量','处理实际错选B；用一题建立两类约束','同一对进程可能同时受两类约束'),
      ('ERR-OS-2.3-018',18,'正文例3-2','OS-M07','初值从实际初态求，不由名称决定','D不是任意取值；0仅覆盖部分初态','处理实际错选B；题目直接检验初值泛化','同步量不一律从0开始'),
      ('ERR-OS-2.3-027',27,'并入§3.1定义','OS-M01','资源对象与各进程代码段分别计数','题目默认每个进程一个相关段','实际错选A，不能被其他缓冲题替掉','相关代码区段数不同于资源份数'),
      ('ERR-OS-2.3-029',29,'并入§3.8条件变量辨析','OS-M18','检查无等待者时signal是否留许可','D按教材语法模块语境，不推广成所有对象无法实例化','保留实际错选D与正确C的边界纠正','相对2018题补无等待者signal边界'),
      ('ERR-OS-2.3-039',39,'并入§3.5模型边界','OS-M12','模型解决同步互斥；错误代码可能制造死锁','正确生产消费不自动保证公平','真实错选C并入模型解释，避免重复完整题','区分建模任务与死锁/饥饿保证'),
    ]:
        add(i,'个人错题；王道典型选择题',2,True,
            f'做题本§2.3第{num}题；完整原题/选项/原错选/扫描答案位置见editorial/errors/错误题总台账.json，id={i}',
            method,steps,boundary,'基础辨析',reason,added,'删除或合并后仍须保留该实际错误选项的具体纠正',ex)
    add('OS-EX-2018-28','408真题+个人错题',1,True,
        '2018重建卷第28题；做题本§2.3第54题p271；王道答案PDF144；ERR-OS-2.3-054',
        'OS-M18','调用前判断共享状态；wait入队阻塞并让出管程','条件变量不是整数资源数，wait不自行判值','基础辨析',
        '同考法有已核身份真题且是实际错题，优先完整讲','实际错选C直接暴露选项职责混淆，机制处纠正',
        '失去条件等待的真题与实际错选；不能用泛讲替掉','正文例3-7')
    typical=[
      ('TYP-OS-SW','王道OS §2.3.2，印100–101/PDF112–113','OS-M03；OS-M04','三种失败法的决定交错与Peterson代码/证明','共享读写原子、顺序一致、两进程','软件互斥的机制不能由缓冲PV题代替'),
      ('TYP-OS-HW','王道OS §2.3.2–3，印102–104/PDF114–116','OS-M05','TS原子取旧置真、Swap申请/退出步骤，区分自旋与阻塞','原子性不是普通C赋值；屏蔽仅本CPU；公平需另定','补足信号量前置和锁实现条件'),
      ('MODEL-OS-SEM','王道信号量机制课件2.3.4_1 PDF5–7；主书印104–105','OS-M06','初值2，四次P两次V的有符号队列轨迹','为追踪显式假定FIFO；唤醒不重复P、不等于运行','用最小状态序列讲清机制，非另编独立练习题'),
      ('TYP-OS-PC','王道OS §2.3.5，印107–108/PDF119–120','OS-M10；OS-M11；OS-M12','容量/产品/锁三量；具体持锁等待反例','许可已预留时不同于物理库存；P顺序规则有范围','标准代码作为分类与批次真题的前置模型'),
      ('TYP-OS-RW','王道OS §2.3.5，印109–111/PDF121–123','OS-M15；OS-M16','首读者取rw，末读者放rw；计数判断整体保护；gate入口','FIFO/进度/有限访问是公平性结论的条件','共享读者组的模型未由生产消费题覆盖'),
      ('TYP-OS-PHI','王道OS §2.3.5，印111–112/PDF123–124','OS-M17；OS-M16','五人等待环；room=4完整代码；资源排序反证','限制申请人数不同于同时进餐；无死锁不自动无饥饿','多资源循环等待与断环的不同方法'),
      ('TYP-OS-CV','王道OS §2.3.6印112–114；Oracle Using Condition Variables例18–20','OS-M19','wait释放并重取锁；while重检；缓冲模块完整接口','明确Mesa/POSIX式；条件变量不保存许可','将管程概念接到可执行等待过程，补教材语义省略'),
    ]
    for i,source,m,st,b,r in typical:
        add(i,'可信资料中的典型模型讲解（不计为编号完整例题）',2,False,source,m,st,b,'机制理解至执行',r,r,
            '删除会失去所列机制、状态或成立条件；与完整真题分工，未另堆同模型数值题','正文相应知识段',
            '叙述与伪代码重新编排，变量按全章统一；TYP-OS-CV将Oracle occupied/more/less改称count/notEmpty/notFull并省略C接口、索引与assert，保留等待/通知逻辑；不声称逐字原例题')
    for n,(source,task,changed) in enumerate([
        ('MODEL-OS-SEM；ERR-OS-2.3-018','检查P后0、V后0两个不同边界','抽取原机制边界作三问'),
        ('OS-EX-2022-46','检查延迟通知是否增加原题没有的顺序','把signal位置移到D后，作为错误代码辨析'),
        ('OS-EX-2009-45','检查原题未明初态时怎样参数化','解答改按已有a奇b偶，原题未静默添数据'),
        ('OS-EX-2014-47','检查批内缺货时的持有与等待','观察已取3件的中间态'),
        ('TYP-OS-PHI','区别四人申请与二人可同时进餐','回顾既有模型，不改五根筷子条件'),
        ('ERR-OS-2.3-029','检查无等待者的通知边界','回顾本章已纠正选项的最小判断'),
    ],1):
        add(f'OS-RECALL-{n:02}','原创章内回顾设问',3,False,source,'对应已选主例题/模型的局部自查',
            task,'以正文已经说明的条件为准','短辨析/迁移',
            '补充目的：允许遮住正文答案检验关键中间状态；主要模型已优先用真题、错题和典型模型讲解',
            task,'不计作新增代表模型；若后续增加同任务的独立练习，合并此回顾以免重复','§3.10，答案集中在节末',changed)
    payload=dict(date='2026-10-15',selection_rule='已核验真题优先；个人错题与典型例题同等；原创只用于章内回顾自查。',
        numbering='完整编号例题7道；5道真题（其中1道兼个人错题）+2道其他个人错题；另3道个人错题并入。模型讲解与6个原创回顾设问不计作完整代表题数量。',
        items=items)
    (OUT/'sample_selection.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2));save_csv(OUT/'sample_selection.csv',items)
    lines=['# 同步样章考法与选题说明','',payload['numbering'],'',
           '实际先从本单元需要处理的机制、主要约束与重要边界列任务，再比较可用题源；此表将正文中的这些决定固化为可恢复台账。没有由题目年份或数量推导考频。','',
           '| 考法ID | 教学任务 | 对应题或模型 | 处理 |','| --- | --- | --- | --- |']
    lines += [f"| {r['id']} | {r['task']} | {r['representative']} | {r['handling']} |" for r in methods]
    lines += ['', '逐题完整来源、优先级、个人错题身份、关键步骤、条件、定性难度、增量价值与删除检查，见sample_selection.csv/json。',
              '', '2025年第45题已核验但未选入本样章，留给后续综合主题；不为增加近年年份重复叠题。六道同步错题均有去向，没有统一转移到附录。',
              '', '原作答与书答案的差异可确认，个人心理原因不可由字母倒推。完整例题中的个性化说明只分析实际错选的选项内容。']
    (OUT/'考法与选题说明.md').write_text('\n'.join(lines)+'\n')
    print('19 teaching tasks; selection ledger written')

if __name__=='__main__':main()
