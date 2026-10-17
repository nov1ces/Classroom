#!/usr/bin/env python3
"""Regenerate editorial registers from fixed, reviewed OS chapter decisions."""
from pathlib import Path
import json,re,csv,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
coverage=json.load(open(ROOT/'editorial/scope/OS_coverage.json'))
errors=[r for r in json.load(open(ROOT/'editorial/errors/os_cn_errors.json')) if r['subject']=='OS']
source_inputs=json.load(open(HERE/'source_inputs.json'))
answers=source_inputs['answers']
index=json.load(open(ROOT/'editorial/full/sources/exam_question_index.json'))
index={(r['year'],r['question']):r for r in index}
sourcepdf='/workspace/study_analysis/v2/books/王道2027操作系统_高清带书签版.pdf'
chapter_files={int(p.name[:2]):p for p in (ROOT/'manuscript/OS').glob('*.md')}
# chapter, example, title, book section:question, year, national number, knowledge suffixes, teaching addition
spec=[
(1,1,'进程数与CPU利用率','1.2:20',2022,23,['01-01','01-02'],'识别资源竞争和并发收益的条件，反对无条件单调关系'),
(1,2,'系统调用硬件与软件分工','1.3:31',2022,31,['01-03','01-04','01-05'],'分别归属断点/PSW、通用寄存器、模式和服务代码'),
(1,3,'微内核收益与开销','1.6:21',2023,23,['01-08'],'保护域隔离、通信开销与性能结论条件'),
(1,4,'开机初始化与持久结构','1.6:20',2022,24,['01-09'],'区分本次运行中断入口和磁盘持久结构'),
(2,1,'主动让出CPU与就绪','2.1:71',2023,27,['02-02'],'事件等待、许可申请与主动让出三条分支'),
(2,2,'FCFS/SJF可选集合','2.2:45',2017,23,['02-08'],'只在t=2已到达集合内选择；题后HRRN改变优先量'),
(2,3,'抢占式优先级周转','2.2:53',2023,29,['02-06','02-07','02-08'],'保留剩余执行时间，完成时刻减各自到达时刻'),
(2,4,'调度次数与事件次数','2.2:52',2022,25,['02-07','02-08'],'到达不必分派，含首次与不计空闲的口径'),
(2,5,'二级反馈与剩余时间','2.2:48',2019,27,['02-08'],'从RR流入短进程队列后按剩余量选择'),
(2,6,'SRTF与RR逐段执行','2.2:BIG6',None,None,['02-06','02-07','02-08'],'补SRTF真正比较与RR同刻入队完整轨迹，非仅列算法名称'),
(4,1,'避免与检测的依据','2.4:39',2015,26,['04-02','04-03','04-04'],'未来最大需求与当前请求的差别'),
(4,2,'部分完成不代表安全','2.4:35',2011,27,['04-01','04-03'],'Work两步增长后仍卡住，区分不安全与已死锁'),
(4,3,'五进程四候选安全性','2.4:26',None,None,['04-03'],'逐分量检查与四候选独立初态；保留相关实际薄弱考法'),
(5,1,'共享页号与页框号','3.1:71',2023,30,['05-01','05-02'],'虚拟布局不同而物理共享对象相同'),
(5,2,'最佳适应当前空洞','3.1:61',2010,28,['05-03'],'分配8先用10，不能按首次适应或合并不相邻洞'),
(5,3,'二级页表目录规模','3.1:62',2010,29,['05-04','05-05'],'一页表可装项数→覆盖页数→目录项数'),
(5,4,'10+10+12地址字段','3.1:68',2019,31,['05-04','05-05'],'按二进制位宽分割，非整十六进制数字切分'),
(5,5,'LRU缺页与置换','3.2:53',2019,29,['05-08','05-09'],'每次命中更新最近顺序；空框装入不算置换'),
(5,6,'缺页后Clock与物理地址','3.2:55',2021,28,['05-04','05-07','05-09'],'存在位为0不能沿旧框号，重建换入映射'),
(5,7,'工作集窗口与去重','3.2:52',2016,29,['05-11'],'按6次引用取窗口再去重，非6个不同页'),
(6,1,'关闭与内存inode','4.2:67',2023,31,['06-01','06-02'],'开引用不等于磁盘硬链接；简化缓存释放模型限定'),
(6,2,'权限组合位数','4.2:60',2017,30,['06-03'],'每类五种权限独立开关，非类别编码加一种操作编码'),
(6,3,'混合索引路径','4.2:59',2015,29,['06-05'],'字节偏移→逻辑块→索引层次，计算1/3次访问'),
(6,4,'隐式链修改记录','4.2:25',None,None,['06-04','06-05'],'记录不跨块，先沿链读5再写回1'),
(6,5,'硬链接与打开状态','4.2:61',2017,31,['06-02','06-07'],'同一inode与独立打开位置的区分，保留原Ⅲ与选项'),
(6,6,'位图三层定位','4.3:14',2015,31,['06-09'],'位图相对块→绝对块→字节→位，零基编号'),
(7,1,'驱动程序的设备参数','5.2:40',2013,25,['07-03'],'传统CHS转换归驱动，与现代LBA范围区分'),
(7,2,'单双缓冲时间','5.2:38',2011,31,['07-05'],'输入/复制/分析资源占用与启动排空'),
(7,3,'CHS混合进位','5.3:16',None,None,['07-08'],'柱面64记录、盘面8记录、零基编号'),
(7,4,'逻辑格式化','5.3:30',2017,29,['07-08'],'文件系统根和空闲结构不同于分区与物理扇区'),
(7,5,'SCAN方向与距离','5.3:29',2015,32,['07-09'],'按向内方向先增，199端点后反向，服务完即停止')]
old=json.load(open(ROOT/'editorial/selection/sample_selection.json'))['items']
figs=json.load(open(HERE/'figures.json'))+json.load(open(ROOT/'editorial/figures/figure_manifest.json'))
byerror={(r['section'],r['source']['error_json_question_number']):r for r in errors}
def question_page(section,n):
    r=byerror.get((section,n))
    if r:return r['source']['question_pdf_page']
    return source_inputs['question_locations'].get(section+':'+str(n))

chapters=[]
for c,p in sorted(chapter_files.items()):
    text=p.read_text();title=text.splitlines()[0].split('{')[0].lstrip('# ').strip()
    ks=[]
    for row in coverage:
        kid=row['知识点 ID']
        if int(kid.split('-')[1])!=c:continue
        num=int(kid.split('-')[2]);anchor=f'os-{c}-{num}'
        if c==3:anchor={1:'sec-concepts',2:'sec-locks',3:'sec-locks',4:'sec-locks',5:'sec-semaphore',6:'sec-monitor',7:'sec-buffer',8:'sec-readers',9:'sec-philosophers'}[num]
        assert '{#'+anchor+'}' in text,(kid,anchor)
        section_title=next(l.split('{')[0].lstrip('# ').strip() for l in text.splitlines() if '{#'+anchor+'}' in l)
        ks.append({'id':kid,'name':row['知识点'],'anchor':anchor,'location':f'第{c}章 {section_title}','manuscript':str(p.relative_to(ROOT)),'status':'已完成正文与语义审读；2027正式细目对照待核','learning_requirements':row['学习要求'],'source':'王道2027操作系统主资料；相关源题与解析已核读，非主书全页通读声明','methods':row['核心考法'],'conditions':row['重要条件与边界'],'outline_verification':'本地转录细目有去向，2027正式大纲全文尚未取得，不认证正式覆盖'})
    ch={'chapter':c,'title':title,'manuscript':str(p.relative_to(ROOT)),'characters':len(text),'knowledge':ks,'examples':[],'figures':[],'checks':{'content_review':'editorial/full/review/read_log.json；OS全部七章逐行语义审读，例2-6追加复核','computation':'editorial/full/OS/results.json；第3章并发模型见editorial/verification/model_results.json','pdf_visual':'由主编最终导出后逐页记录，不以计算验证替代','style':'标题定位任务；章内没有强制同一栏目；去除个人原作答和长题源；章节末自测明确原创'},'unresolved':[]}
    chapters.append(ch)
for c,n,title,key,year,q,ids,purpose in spec:
    sec,num=key.split(':');big=num.startswith('BIG');no=int(num.replace('BIG',''));anchor=f'os-ex{c}-{n}'
    assert '{#'+anchor+'}' in chapter_files[c].read_text()
    if big:
        b=source_inputs['big_2_2_6']
        book_question_pages=[x['page'] for x in b['crops']];answer_pages=[x['page'] for x in b['answer']['crops']];correct={'SRTF_mean':13,'RR_mean':19.25}
    else:
        a=answers['OS:'+key];book_question_pages=[];answer_pages=sorted(set(x['page'] for x in a['crops']));correct=a['answer']
    nativepage=question_page(sec,no) if not big else None
    evidence=[f'editorial/full/OS/source_checks/answer_{sec}_{no}.png'] if not big else ['editorial/full/OS/source_checks/srtf_question_98.png','editorial/full/OS/source_checks/srtf_answer_108.png','editorial/full/OS/source_checks/srtf_answer_109.png']
    r=byerror.get((sec,no)) if not big else None
    ex={'id':f'OS-FULL-{c}-{n}','title':title,'anchor':anchor,'location':f'例{c}-{n}','marker':f'【{year}】' if year else f'〖{sec}-{no:03d}〗','category':'408真题' if year else '王道典型题','priority':1 if year else 2,'is_personal_error':bool(r),'personal_error_ids':[r['id']] if r else [],'knowledge_ids':['OS-'+i for i in ids],'methods':[purpose],'key_steps':purpose,'conditions':'见本例及紧邻机制说明，原题数据和选项保留；解析中新增假设与题后变式单独说明','difficulty':'基础至中等；以实际执行过程为准','selection_reason':purpose,'added_value':purpose,'deletion_check':'删除将失去：'+purpose,'source':{'main_book':sourcepdf,'edition':'2027年操作系统考研复习指导，电子工业出版社，2026-01第1版','section':sec,'question_type':'综合应用题' if big else '单项选择题','book_question_number':no,'book_question_pdf_pages':book_question_pages,'book_answer_pdf_pages':answer_pages,'horizontal_question_pdf':'/workspace/Classroom/03_操作系统/【横版】27王道操作系统选择题做题本.pdf','horizontal_question_pdf_page':nativepage,'exam_year':year,'exam_question_number':q,'evidence':evidence},'correct_answer':correct,'verification':{'status':'已核对完整题干/选项/所需图表及主书答案，解析独立重写；二手交叉核验','official_original':'未取得，不冒称官方原卷','official_answer':'未取得官方答案发布；主书答案与独立推理核对','date':'2026-10-16'},'changes':'题意、数据、选项未改；原图可重绘，解析原创。题后变式另标原创。'}
    if year:
        ix=index[(year,q)];ex['source']['exam_rebuild_pdf']=ix['full_pdf'];ex['source']['exam_pdf_page']=ix['pdf_page'];ex['source']['evidence'].append(f'editorial/full/OS/source_checks/exam_{year}_p{ix["pdf_page"]}.png')
        if year==2010 and q==29:ex['source']['exam_continued_page']=4
    if c==2 and n==2:
        ex['source']['book_question_pdf_pages']=[94,95];ex['source']['evidence'].append('editorial/full/OS/source_checks/book_p94.png');ex['source']['conflict_resolution']='王道J4=3/1，neville复原误排3/4。独立学府PDF及希赛表格均3/1支持主书，正文按1。详source_conflicts.json。'
    if c==6 and n==1:ex['conditions']='最后关闭释放内存inode为本题简化模型；实际系统可保留缓存。'
    chapters[c-1]['examples'].append(ex)
# Reuse previously verified complete sample questions, maintaining identities and exact national numbers.
for n,oid,anchor in [(1,'ERR-OS-2.3-011','ex-err11'),(2,'ERR-OS-2.3-018','ex-err18'),(3,'OS-EX-2022-46','ex-2022'),(4,'OS-EX-2024-46','ex-2024'),(5,'OS-EX-2009-45','ex-2009'),(6,'OS-EX-2014-47','ex-2014'),(7,'ERR-OS-2.3-054','ex-2018')]:
    # The archive may name selected error entries with a prefixed id. Keep all original metadata in trace.
    candidate=next((x for x in old if x['id']==oid or oid in str(x)),{})
    year={3:2022,4:2024,5:2009,6:2014,7:2018}.get(n)
    eid={1:'ERR-OS-2.3-011',2:'ERR-OS-2.3-018',7:'ERR-OS-2.3-054'}.get(n)
    chapters[2]['examples'].append({'id':f'OS-FULL-3-{n}','title':f'同步样章例3-{n}','anchor':anchor,'location':f'例3-{n}','marker':f'【{year}】' if year else f'〖2.3-{11 if n==1 else 18:03d}〗','category':'408真题' if year else '王道典型题','priority':1 if year else 2,'is_personal_error':eid is not None,'personal_error_ids':[eid] if eid else [],'knowledge_ids':['OS-03-'+('01' if n==1 else '05' if n in [2,3] else '06' if n==7 else '07')],'source':{'archived_complete_records':'editorial/selection/sample_selection.json','archive_id':oid,'details':candidate,'verification_evidence':'editorial/sources/os_exam_checks；editorial/errors/os_cn_checks'},'verification':{'status':'首轮完整核题并复算，本轮按已确认短标记与无原作答修订','official_original':'未取得官方原始卷/答案，不声称官方核验'},'methods':[candidate.get('key_steps','见完整样章原选题台账')],'selection_reason':candidate.get('reason','保留原样章的独立教学任务'),'deletion_check':candidate.get('deletion_check','删除将失去本例的同步/互斥边界或过程'),'changes':'最新仅改题源展示及去除个人原选，不改题意；奇数判断!=0仍符合原题正整数。'})
# Full unnumbered treatments and concise merged question fragments are registered separately.
extras=[
(2,'OS-MERGED-2023-26','os-2-10','【2023】','题目摘要并入',2023,26,'2.1:70','模式切换与上下文切换区别'),
(5,'OS-UNNUM-2016-28','os-5-6','【2016】','完整未编号例题',2016,28,'3.1:65','段偏移超界先检查再算地址'),
(5,'OS-UNNUM-3.2-012','os-5-11','〖3.2-012〗','完整未编号例题',None,None,'3.2:12','数组行列顺序映射到页引用串，单数据页框'),
(5,'OS-MERGED-3.2-014','os-5-5','〖3.2-014〗','题目摘要并入',None,None,'3.2:14','TLB命中与二级遍历分支'),
(5,'OS-MERGED-3.2-020','os-5-4','王道书§3.2','题目摘要并入',None,None,'3.2:20','页号/偏移拆分与物理地址'),
(6,'OS-MERGED-4.2-010','os-6-6','王道书§4.2','模型辨析并入',None,None,'4.2:10','目录线性查找精确期望与近似')]
for c,eid,anchor,marker,typ,year,q,key,method in extras:
    sec,no=key.split(':');r=byerror.get((sec,int(no)));a=answers.get('OS:'+key,{})
    chapters[c-1].setdefault('merged_or_unnumbered',[]).append({'id':eid,'anchor':anchor,'marker':marker,'category':typ,'source':{'book':sourcepdf,'section':sec,'question':int(no),'answer_pages':[x['page'] for x in a.get('crops',[])],'exam_year':year,'exam_question':q},'is_personal_error':bool(r),'personal_error_ids':[r['id']] if r else [],'teaching_task':method,'count_policy':'不计完整编号代表题；完整未编号另计','added_conditions':'数组题显式说明4B整数、页对齐、数据空初态；目录期望显式等概率并区分原书近似。'})
for ch in chapters:
    text=chapter_files[ch['chapter']].read_text()
    ch['figures']=[f for f in figs if f['id']+'.png' in text or Path(f.get('png','')).name in text]
    ch['question_count']=len(ch['examples'])
# Personal mistakes: retain original answer evidence internally, no invented reasoning or psychological causes.
selected={eid:(ch,ex) for ch in chapters for ex in ch['examples']+ch.get('merged_or_unnumbered',[]) for eid in ex.get('personal_error_ids',[])}
merged={
'ERR-OS-1.1-003':'os-1-1','ERR-OS-1.1-010':'os-1-5','ERR-OS-2.1-022':'os-1-7','ERR-OS-2.2-009':'os-2-10',
'ERR-OS-2.3-027':'sec-concepts','ERR-OS-2.3-029':'sec-monitor','ERR-OS-2.3-039':'sec-buffer',
'ERR-OS-2.4-023':'sec-readers','ERR-OS-2.4-028':'os-4-3','ERR-OS-3.1-009':'os-1-6',
'ERR-OS-3.1-031':'os-5-1','ERR-OS-3.1-041':'os-5-1','ERR-OS-3.2-018':'os-5-1','ERR-OS-3.2-019':'os-5-4',
'ERR-OS-3.2-029':'os-5-11','ERR-OS-4.2-026':'os-6-5','ERR-OS-4.2-028':'os-6-5',
'ERR-OS-4.2-037':'os-6-2','ERR-OS-4.2-039':'os-6-2','ERR-OS-4.2-064':'os-6-2','ERR-OS-4.3-012':'os-6-10',
'ERR-OS-5.1-016':'os-7-3','ERR-OS-5.1-020':'os-7-2','ERR-OS-5.2-012':'os-7-5','ERR-OS-5.2-018':'os-1-2',
'ERR-OS-5.2-020':'os-7-7','ERR-OS-5.2-023':'os-7-7','ERR-OS-5.3-003':'os-7-1','ERR-OS-5.3-005':'os-7-9',
'ERR-OS-5.3-008':'os-7-8','ERR-OS-5.3-025':'os-7-10'}
exception={
'ERR-OS-1.3-011':'选项把访管指令与内核可执行指令的关系限定在教材抽象；实际ISA规则不同，正文不无条件排除用户态可执行的非特权指令。',
'ERR-OS-3.1-011':'原JSON作答C与书答案C一致，错题身份不能等同确认做错；不编个人错因。',
'ERR-OS-3.2-013':'题干未指定替换算法，FIFO/LRU2048与OPT1917不同；保留原题条件疑点，不作为唯一答案正式代表题。',
'ERR-OS-5.3-017':'r为秒/转且整轨成簇的原选项需区分跨轨次数及旋转等待模型；正文改讲单位和单轨标准分解，原题保留为条件练习。'}
anchorinfo={k['id']:(ch,k) for ch in chapters for k in ch['knowledge']}
errout=[]
for r in errors:
    eid=r['id'];kid=r.get('knowledge_ids',[''])[0];ch,k=anchorinfo[kid];anchor=k['anchor'];dest='复习练习';reason='原题保留用于回查；正文已讲对应模型，与已选代表题比较后不重复完整题面。新增训练点：'+r['question_specific_correction']
    if eid in selected:
        ch,ex=selected[eid];anchor=ex['anchor'];dest='正文例题' if ex.get('location') else ('正文未编号例题' if ex.get('category')=='完整未编号例题' else '并入正文辨析');reason=ex.get('selection_reason',ex.get('teaching_task','对应过程'))
    elif eid in merged:
        anchor=merged[eid];ch=next(c for c in chapters if '{#'+anchor+'}' in chapter_files[c['chapter']].read_text());dest='并入已有题或知识辨析';reason=r['question_specific_correction']+'；不重复已选同模型完整例题。'
    if eid in exception:dest='复习练习/条件核验保留';reason=exception[eid]
    errout.append({'id':eid,'subject':'OS','knowledge_ids':r['knowledge_ids'],'core_method':r['core_method'],'source':r['source'],'exam_identity':r['exam_identity'],'original_answer_information':r['actual_answer_information'],'confirmed_personal_error_cause':None,'destination':dest,'manuscript':ch['manuscript'],'anchor':anchor,'location':f'第{ch["chapter"]}章 #{anchor}','reason':reason,'correction':r['question_specific_correction'],'reading_status':'首轮已读题干/选项和原JSON作答、已看书答案行；本轮仅对实际入选和列证据者进一步核完整解析与卷页','student_text_policy':'不显示个人原选、ERR身份或做题本；内部台账保留原证据','verification_limits':r.get('unresolved_or_missing',[])})
assert len(errout)==133
fullcount=sum(len(x['examples']) for x in chapters)
obj={'subject':'OS','date':'2026-10-16','status':'七章正文完成、语义审校与37项新增计算核验；最终PDF视觉由主编接续','scope_limits':'以既有64稳定知识组和本地转录细目组织；2027正式大纲全文未取得，正式细目覆盖仍待核。书与复原卷交叉不等于官方原卷/官方答案认证。','source_label_policy':'正文真题【年份】，非真题〖节号-三位题号〗；个人原选及详细来源只在内部台账。','chapters':chapters,'errors':errout,'summary':{'chapters':7,'knowledge_groups':sum(len(c['knowledge']) for c in chapters),'numbered_complete_examples':fullcount,'numbered_exam_examples':sum(e['category']=='408真题' for c in chapters for e in c['examples']),'numbered_typical_examples':sum(e['category']=='王道典型题' for c in chapters for e in c['examples']),'personal_mistakes':len(errout),'destinations':{d:sum(r['destination']==d for r in errout) for d in sorted(set(r['destination'] for r in errout))},'new_figures':11,'existing_sample_figures':8,'new_calculation_checks':37},'unresolved':[{'id':'SCOPE-2027','status':'待核验','detail':'2027正式全文未获；不宣称官方覆盖全部核验'},{'id':'SOURCE-OFFICIAL','status':'来源级别限制','detail':'真题核对依赖王道与公开复原卷及其他独立转载；未获得官方原始发布与官方答案'},{'id':'OS-3.2-013','status':'条件不足，不入正式代表题','detail':exception['ERR-OS-3.2-013']},{'id':'OS-1.3-011','status':'术语条件边界，保留','detail':exception['ERR-OS-1.3-011']}],'original_supplements':'自测为原创回顾设问，不替换已选真题。原创最小机制例/变式补“现存量不足以证明安全”、Clock扫描中间状态、数组次序迁移、访问时间单位；未宣称遍历全部题库证明无题可选。'}
(HERE/'chapter_records.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
# Review practice navigation stays internal and never exposes the original choices in the lecture.
lines=['# 操作系统错题复习去向','内部材料。133条逐条登记；原作答只在JSON台账中。未推测个人心理错因。','']
for ch in chapters:
 lines += [f'## 第{ch["chapter"]}章 {ch["title"]}','']
 for r in errout:
  if r['manuscript']==ch['manuscript']:lines.append(f'- {r["id"]}：{r["destination"]}；[{r["anchor"]}](../../../{r["manuscript"]}#{r["anchor"]})；{r["reason"]}')
(HERE/'错题复习去向.md').write_text('\n'.join(lines)+'\n')
conflicts=[{'question':'2017第23题/王道§2.2选择45','book_pdf_pages':[94,95],'book_data':'J4到达3、运行1','neville_data':'J4到达3、运行4','resolution':'正文采用主书1；已实际打开的独立学府PDF和希赛表格均1，neville此处误排不用于改动原题。','support_urls':['https://officialxuefucom.oss-cn-beijing.aliyuncs.com/u/cms/beijing/202007/03163140uwyh.pdf','https://www.educity.cn/kyyy/5106735.html'],'support_record':'editorial/full/sources，由scope_sources保存实际读取证据','impact':'t2时J4未到达，答案D未变；数据仍按原题核正。'}, {'question':'OS§2.1-022','resolution':'初始化全局变量属数据区，不照抄正文段混写。'}, {'question':'OS§2.4-028','resolution':'nk<m+n是任意分配最坏总量界，不是银行家可运行必要条件；章4明确反例。'}, {'question':'OS§4.2-010','resolution':'等概率50目录块+1个inode的精确期望26.5，原书N/2近似26分别标明。'}, {'question':'OS§4.2-028','resolution':'FAT总规模一般由卷簇数而非单文件最大值决定，正文保留条件而不把书答128KB无条件推广。'}, {'question':'OS§4.2-067','resolution':'最后close释放内存inode仅按考题简化；现实可缓存，区分打开引用与磁盘硬链接。'}]
(HERE/'source_conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2))
print(json.dumps(obj['summary'],ensure_ascii=False))
