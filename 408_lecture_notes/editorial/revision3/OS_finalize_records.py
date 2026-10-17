#!/usr/bin/env python3
"""Finalize only OS revision-3 provenance; source books are never a runtime dependency."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
R3=ROOT/'editorial/revision3'
OS=ROOT/'editorial/full/OS'
BASE=R3/'baseline'

def read_json(path): return json.loads(path.read_text())
def dump(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

# These page numbers are physical PDF pages, not the book's printed folios.
BOOK='/workspace/study_analysis/v2/books/王道2027操作系统_高清带书签版.pdf'
SPECS=[
 dict(ch=2,no=7,year=2016,exam=46,section='2.2',book_no=10,qpages=[98,99],apages=[110],epage=11,
      title='把“等待越久越优先”写成动态优先数',knowledge=['OS-02-08'],questions=2,
      task='由值小优先确定运行与等待的符号，解释老化及饥饿边界',
      conditions='cpuTime与waitTime按执行/就绪状态清零；代入检查明确原创；公式不无条件推出固定等待界',
      answer='可用priority=nice+k1*cpuTime-k2*waitTime，k1、k2为正；waitTime使等待者逐渐提升优先级'),
 dict(ch=5,no=8,year=2009,exam=46,section='3.2',book_no=15,qpages=[246],apages=[260],epage=9,
      title='一次缺页要把“失败、调页、重试”全部计时',knowledge=['OS-05-05','OS-05-07','OS-05-08','OS-05-09'],questions=2,
      task='连续跟踪TLB、局部LRU、页框复用和缺页后原指令重试',
      conditions='TLB初空、驻留集固定2、LRU局部淘汰；缺页费含页表/TLB更新但不免除重试',
      answer='210ns、100000220ns、110ns；淘汰页0；1565H对应101565H'),
 dict(ch=5,no=9,year=2020,exam=46,section='3.2',book_no=21,qpages=[248],apages=[261,262],epage=11,
      title='数组偏移怎样逐级找到页表项',knowledge=['OS-05-04','OS-05-05','OS-05-07'],questions=3,
      task='行优先数组偏移、10+10+12拆位、逐级表项物理地址与局部性',
      conditions='按字节编址，目录项/页表项4B；下级页框00301H；未给最终页框或驻留集，不擅推目标物理地址或缺页次数',
      answer='VA10801008H；目录042H、页001H；目录项PA00201108H、页表项PA00301004H；虚拟连续、物理可离散；行遍历空间局部性较好'),
 dict(ch=6,no=7,year=2022,exam=45,section='4.2',book_no=15,qpages=[293,294],apages=[305],epage=9,
      title='同一索引节点怎样连接目录查找与文件扩展',knowledge=['OS-06-01','OS-06-02','OS-06-05','OS-06-06','OS-06-07'],questions=4,
      task='目录项、共享inode、打开读盘路径与6MB文件跨级索引',
      conditions='第4问跨物理p294；只给course目录缓存，目标inode/数据未另给命中；必要目录树和全部五行数据重绘保留',
      answer='stu含(course,2)、(doc,10)；x=30；读inode块和30号数据块共2块；1536数据块需一级及二级间接项'),
 dict(ch=6,no=8,year=2018,exam=46,section='4.2',book_no=14,qpages=[293],apages=[305],epage=10,
      title='先算地址覆盖，再比较inode与数据簇的上限',knowledge=['OS-06-01','OS-06-05'],questions=3,
      task='混合索引最大长度、inode/数据区双重文件数限制及末簇号定位',
      conditions='1M是2^20个簇；5600B文件占两个直接数据簇；第3问仅取末簇号，共同inode在内存/索引未缓存起点额外读盘0/1，不混为数据读取1/2',
      answer='(8+1024+1024^2+1024^3)*4096B；最多64M=67108864个图像；F1直接项、F2一级间接项'),
 dict(ch=7,no=6,year=2023,exam=46,section='5.2',book_no=3,qpages=[346],apages=[351,352],epage=10,
      title='一次键盘输入怎样使阻塞者重新获得运行资格',knowledge=['OS-02-02','OS-07-02','OS-07-03'],questions=4,
      task='系统调用等待、硬件输入与中断、驱动取字符、唤醒和返回的完整因果链',
      conditions='本题是键盘字符输入，不是磁盘/DMA题；P状态与CPU当前模式分开；题列相邻不表示指令紧邻；就绪不保证立即运行',
      answer='②⑥④③①⑤；①前③后⑤，⑥后④；②后离开P、①后可选P；③属驱动；中断入口P阻塞、CPU内核态'),
 dict(ch=7,no=7,year=2019,exam=44,section='5.3',book_no=7,qpages=[364],apages=[370],epage=8,
      title='把簇号转换成柱面，再逐步执行SSTF',knowledge=['OS-07-03','OS-07-08','OS-07-09'],questions=3,
      task='物理容量、簇转柱面、SSTF逐步重选、簇起始CHS及驱动职责',
      conditions='每簇2扇区、每柱面1000簇；按源解0基模型；目标簇100530含扇区60和61；不因两扇区加倍磁盘容量',
      answer='307200000B=300000KB；顺序100260,101660,110560,60005；起始CHS(100,5,60)，驱动完成转换')
]

d=read_json(OS/'chapter_records.json');baseline=read_json(BASE/'editorial/full/OS/chapter_records.json')
assert len(d['errors'])==133 and d['errors']==baseline['errors'],'Original 133 OS error records must stay byte-for-byte equivalent as JSON values'
chapters={c['chapter']:c for c in d['chapters']}
selections=[]
for s in SPECS:
 c=chapters[s['ch']];anchor=f'os-ex{s["ch"]}-{s["no"]}';eid=f'OS-FULL-{s["ch"]}-{s["no"]}'
 pngs=[f'editorial/revision3/OS_sources/book_p{p}.png' for p in sorted(set(s['qpages']+s['apages']))]
 epng=f'editorial/revision3/OS_sources/exam_{s["year"]}_q{s["exam"]}_p{s["epage"]}.png'
 source={'main_book':BOOK,'edition':'2027年操作系统考研复习指导，电子工业出版社，2026-01第1版',
         'section':s['section'],'question_type':'综合应用题','book_question_number':s['book_no'],
         'book_question_pdf_pages':s['qpages'],'book_answer_pdf_pages':s['apages'],
         'page_numbering':'物理PDF页；印刷页码为上述页码减12',
         'exam_year':s['year'],'exam_question_number':s['exam'],
         'exam_rebuild_pdf':f'editorial/sources/exams/exam_{s["year"]}_rebuild.pdf','exam_pdf_page':s['epage'],
         'evidence':pngs+[epng]}
 ex={'id':eid,'title':s['title'],'anchor':anchor,'location':f'例{s["ch"]}-{s["no"]}',
     'marker':f'【{s["year"]}】','category':'408真题','priority':1,'is_personal_error':False,'personal_error_ids':[],
     'knowledge_ids':s['knowledge'],'methods':[s['task']],'key_steps':s['task'],'conditions':s['conditions'],
     'difficulty':'综合应用；按完整设问连续推演','selection_reason':s['task'],
     'added_value':s['task'],'deletion_check':'删除将失去：'+s['task'],
     'source':source,'correct_answer':s['answer'],'subquestion_count':s['questions'],
     'verification':{'status':'完整题干、全部设问、必要数据/图与主书解答已图读，社区重建卷题面交叉；独立重写解析并执行复算',
                     'official_original':'未取得，不冒称官方原卷','official_answer':'未取得官方答案发布；主书答案与状态/数值复算交叉',
                     'author_read_role':'接续作者实际打开列出的PNG；不把前作者或独立审校的阅读冒作本人阅读',
                     'date':'2026-10-17','calculation':'editorial/full/OS/verification.py','results':'editorial/full/OS/results.json'},
     'changes':'保留原题全部设问、参数、单位及必要图数据；解析独立重写。原创代入和题后扩展另作说明。',
     'revision':3}
 c['examples']=[e for e in c['examples'] if e['id']!=eid]+[ex]
 selections.append({'id':f'OS-R3-{s["year"]}-{s["exam"]}','exam_year':s['year'],'exam_question_number':s['exam'],
                    'destination':'完整正文例题','manuscript':c['manuscript'],'anchor':anchor,
                    'complete_subquestions':s['questions'],'reason':s['task'],'source':source,
                    'personal_error_policy':'新增综合补充；不改原133条错题去向，不新增个人错题身份'})

comparison_changes={
 1:'宏/微内核：服务位置、通信边界、故障影响、扩展与性能代价；无机械扩张表格',
 2:'进程/线程资源与现场；ULT/KLT管理、调度、切换及内核可见性；映射表保留；新增例2-7',
 4:'预防/避免/检测的时机、依据、风险请求、保证与代价；区分Max/Need和当前Request',
 5:'基本/请求分页的驻留、映射字段、未命中/缺页分支、重试；新增例5-8/5-9，不重复页段表',
 6:'目录项、磁盘inode、内存inode、打开状态四层比较；新增例6-7/6-8及必要目录图，不重复文件分配表',
 7:'磁盘六算法的选择/方向、端点/折返、回跳服务和等待边界；新增例7-6/7-7，原I/O控制比较保留'}
figs=read_json(OS/'figures.json')
newfig=next(f for f in figs if f['id']=='OS_file_directory_2022')
chapters[6]['figures']=[f for f in chapters[6]['figures'] if f['id']!=newfig['id']]+[newfig]
for num,c in chapters.items():
 p=ROOT/c['manuscript'];text=p.read_text();c['characters']=len(text);c['sha256']=sha(p)
 c['question_count']=len(c['examples'])
 if num==3:
  assert p.read_bytes()==(BASE/c['manuscript']).read_bytes(),'Sync sample manuscript must remain unchanged'
  c['checks']['revision3_content']='正文与基线SHA相同；本轮未重写同步样章，也未将哈希核对记作语义重读'
 else:
  c['revision3_changes']=comparison_changes[num]
  c['checks']['revision3_content']='本轮改动、源题与新增解析自审已完成；独立内容审校见editorial/revision3/review，不以旧PASS代替本轮结论'
  c['checks']['revision3_reading_scope']='第6/7章全文读；其余非样章核本轮比较及新增题相关段落，未宣称本轮整章逐行重读'
 for key in ['PDF_visual','pdf_visual']:
  c['checks'][key]='第三轮未进行讲义PDF版式、分页或裁切检查；历史结果仅对应旧版'
 c['checks']['computation']='editorial/full/OS/results.json：66项（原37保留、第三轮新增29）；同步样章模型不在本轮重复执行'

summary=d['summary'];summary.update({'numbered_complete_examples':sum(len(c['examples']) for c in d['chapters']),
 'numbered_exam_examples':sum(e['category']=='408真题' for c in d['chapters'] for e in c['examples']),
 'numbered_typical_examples':sum(e['category']=='王道典型题' for c in d['chapters'] for e in c['examples']),
 'new_figures':len(figs),'new_calculation_checks':66,'revision3_added_complete_examples':7,
 'revision3_added_subquestions':sum(s['questions'] for s in SPECS),'revision3_added_figures':1,'revision3_added_calculation_checks':29})
assert summary['numbered_complete_examples']==45 and summary['personal_mistakes']==133
results=read_json(OS/'results.json');oldresults=read_json(BASE/'editorial/full/OS/results.json')
assert results['count']==66 and results['checks'][:37]==oldresults['checks'],'Keep the original 37 results intact'
d.update({'status':'第三轮内容审阅稿；七道综合题、七处必要比较及66项复算已落盘，独立审校结论另记',
          'author_stage_status':'六个非同步样章保留旧题与编号；新增7道完整综合题；原133错题记录及去向不变；OS03正文不变；本轮未检查讲义PDF版式',
          'revision3':{'changes':'editorial/revision3/OS_revision.md','selection_destinations':'editorial/revision3/OS_selection_destinations.json',
                       'sources':'editorial/revision3/OS_sources/source_manifest.json','results':'editorial/revision3/OS_results.json',
                       'new_question_count':7,'new_subquestion_count':21,'old_checks_retained':37,'new_checks':29,
                       'layout_status':'NOT_PERFORMED','independent_review':'结论以editorial/revision3/review的本轮报告为准'},
          'final_pdf_review':{'status':'NOT_PERFORMED_FOR_REVISION3','reason':'本任务只作内容；不以V1/V2视觉记录认证第三轮正文'},
          'manuscript_sha256':{c['manuscript']:c['sha256'] for c in d['chapters']}})
dump(OS/'chapter_records.json',d)
rejected=[
 {'id':'OS-R3-2016-47','destination':'本轮不选入正文','reason':'已记录的版本冲突：主书file1第5000字节，社区file第50字节；书题11对应解编号13亦须定位，不能声称完全一致',
  'replacement':'2018年第46题，例6-8','evidence':'editorial/revision3/review/01_initial_findings.md；OS_sources/exam_2016_q47_p12.png与book_p292/293/305.png',
  'reading_scope':'承接前作者/独立审校已记录的排除结论；接续作者未冒称逐页复读此候选完整题源'},
 {'id':'OS-R3-2010-45','destination':'本轮不选入正文','reason':'C-SCAN/C-LOOK名称与端点规则存在题源解释歧义，不选为新完整代表题；按明确端点定义补共同维度比较',
  'replacement':'2019年第44题，例7-7','evidence':'editorial/revision3/review/01_initial_findings.md；5.3_2_磁盘调度算法.txt p10至14',
  'reading_scope':'承接排除结论；本轮完整读保存的磁盘课件选页转录，并按具体规则明确区分四种扫描'}]
dump(R3/'OS_selection_destinations.json',{'subject':'OS','revision':3,'selected':selections,'not_selected':rejected,
 'limits':'只记录实际本轮选题及已讨论的排除项；未宣称遍历全部题库；来源交叉不是官方原卷/答案认证',
 'original_errors_preserved':{'count':133,'equal_to_revision3_baseline':True}})

book_pages=sorted({p for s in SPECS for p in s['qpages']+s['apages']})
read_pngs={f'book_p{p}.png' for p in book_pages}|{f'exam_{s["year"]}_q{s["exam"]}_p{s["epage"]}.png' for s in SPECS}
source_entries=[]
for p in sorted((R3/'OS_sources').glob('*.png')):
 source_entries.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),
   'reading_status':'接续作者实际打开图读，核完整题面/相关解答' if p.name in read_pngs else '已有承接材料；接续作者本轮未逐页打开，不计本人实读',
   'page_numbering':'book_p指物理PDF页；exam文件指社区重建卷物理页'})
slides=read_json(R3/'OS_sources/slide_read_selections.json')
for entry in slides:
 p=ROOT/entry['extracted_text'];entry['sha256']=sha(p)
 entry['reading_status']='接续作者已完整读取此保存的选页转录；不是整套课件逐页图读或全书通读声明'
manifest={'subject':'OS','revision':3,'primary_book':{'file':BOOK,'role':'正文源题与书解来源；复算和重绘只依赖交付的本地model_data，不要求此绝对路径存在',
 'actual_visual_read_physical_pages':book_pages,'actual_visual_read_printed_pages':[p-12 for p in book_pages]},
 'community_rebuilds':{'role':'七题完整题面交叉核对；非官方原卷认证','actual_read':len(SPECS)},
 'images':source_entries,'slide_selected_transcripts':slides,
 'source_conditions_not_copied_blindly':['课件大/微内核结构示意不推出任意实现性能结论，也不把具体操作系统简单定性作通则',
  '线程课件的阻塞/多核结论限纯多对一，正文分开管理方式与映射方式',
  '死锁检测用当前未满足Request，银行家安全性用未来Need；不把相似化简写成同义',
  '磁盘课件p14的SCAN/LOOK、C-SCAN/C-LOOK同名约定不作无条件定义；正文按端点/回跳规则区分',
  '磁盘课件p11给250/9的近似数值存在误算，本轮未照抄该数；新2019题另逐步执行SSTF',
  '课件读文件页的“read完成写操作”文字不沿用；正文按读/写分别解释'],
 'new_figure':{'file':'figures/OS_file_directory_2022.svg','png':'figures/OS_file_directory_2022.png',
 'model':'editorial/full/OS/model_data.json:directory_2022','generator':'tools/draw_os_figures.py --revision3-only',
 'semantic_read':'接续作者实际打开PNG核目录四条包含边及五行完整数据；未打开讲义PDF'},
 'review_limits':'本轮只对列明源页/选页转录及改动段落负责；OS03仅核基线不变；未取得2027正式大纲全文、官方原卷或官方答案'}
dump(R3/'OS_sources/source_manifest.json',manifest)
shutil.copyfile(OS/'results.json',R3/'OS_results.json')
print(json.dumps({'numbered_examples':summary['numbered_complete_examples'],'exam_examples':summary['numbered_exam_examples'],
 'original_errors':len(d['errors']),'checks':results['count'],'new_checks':results['revision3_added'],'book_source_pages_actually_opened':len(book_pages)},ensure_ascii=False))
