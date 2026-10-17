import json,csv,re,collections,hashlib
from pathlib import Path
out=Path(__file__).parent;dest=out.parent
raw=json.load(open(out/'os_cn_raw_read.json'));meta={r['id']:r for r in csv.DictReader(open(out/'os_cn_annotations.tsv'),delimiter='\t')};calc={r['id']:r for r in json.load(open(out/'os_cn_calculation_log.json'))['records']}
fig={
'ERR-OS-2.2-052':{'columns':['进程','进入就绪队列时刻ms','优先级（值小优先）','CPU时间ms'],'rows':[['P0',0,15,100],['P1',10,20,60],['P2',10,10,20],['P3',15,6,10]]},
'ERR-OS-2.4-023':{'initial':'Semaphore x1=x2=y=1; int c1=c2=0;','P1':'while(1){P(x1); if(++c1==1)P(y); V(x1); computer(A); P(x1); if(--c1==0)V(y); V(x1);}','P2':'while(1){P(x2); if(++c2==1)P(y); V(x2); computer(B); P(x2); if(--c2==0)V(y); V(x2);}'},
'ERR-OS-2.4-026':{'processes':['P0','P1','P2','P3','P4'],'resources':['A','B','C'],'Allocation':[[0,0,3],[1,0,0],[1,3,5],[0,0,2],[0,0,1]],'Max':[[0,0,4],[1,7,5],[2,3,5],[0,6,4],[0,6,5]],'Available':['x','y','z'],'candidates':{'I':[1,4,0],'II':[0,6,2],'III':[1,1,1],'IV':[0,4,7]}},
'ERR-OS-2.4-028':{'symbols':'k≥1；最大需求量之和nk；选项C为nk<m+n'},
'ERR-OS-3.1-062':{'page_bytes':'2^10 B','PTE_bytes':2,'logical_space_pages':'2^16','address_fields':['页目录号','页号','页内偏移量']},
'ERR-OS-3.1-068':{'address_fields':[['页目录号',10],['页号',10],['页内偏移',12]],'virtual_address':'20501225H'},
'ERR-OS-3.2-012':{'code':'int a[128][128];\nfor(int i=0;i<128;i++)\n  for(int j=0;j<128;j++)\n    a[j][i]=0;'},
'ERR-OS-3.2-013':{'code':'int X[64][64];\nfor(int j=0;j<64;j++)\n  for(int i=0;i<64;i++)\n    X[i][j]=0;'},
'ERR-OS-3.2-016':{'option_D':'min(m,n)'},
'ERR-OS-3.2-052':{'shown_reference_sequence':[1,3,4,5,6,0,3,2,3,2,4,0,4,0,3,2,9,2,1],'t_after_access_index_1based':10,'window_before_t':[6,0,3,2,3,2],'source_note':'题源加入[注意：抖动和工作集已从最新大纲中删除]；此非题干条件且年度不明，不能据此确认考试范围。'},
'ERR-OS-5.3-017':{'source_options_as_printed':{'A':'(r+T)b/N','B':'b/NT','C':'(b/N+T)r','D':'bT/N+r'},'unit_r':'秒/转','unit_T':'秒','track_bytes':'N','requested_bytes':'b','cluster':'一整磁道'},
'ERR-CN-3.6-031':{'topology':'A(MAC_A) —无线— AP1(BSSID1) — 路由器(MAC1,MAC2) — AP2(BSSID2) —无线— B(MAC_B)','asked_hop':'AP2→B','correct_addresses':['MAC_B','BSSID2','MAC_A']},
'ERR-CN-3.8-013':{'topology':'学院交换机分别接A/B/C三个系交换机、Web服务器、邮件服务器及互联网路由器；各系交换机各接3主机','links_Mbps':100,'sources':{'hosts':9,'servers':2},'counterpart_changes':['各级均交换机','仅A/B/C换Hub','所有交换机换Hub']},
'ERR-CN-4.2-045':{'topology':'H1、H2与Router接Switch；Switch接Hub，Hub接H3/H4','addresses':{'H1':'192.168.3.2','H2':'192.168.3.3','H3':'192.168.3.251','H4':'192.168.3.252','R1':'192.168.3.1','R2':'192.168.3.254'},'configuration':{'H1_H2':{'gateway':'192.168.3.1','mask':'255.255.255.0'},'H3_H4':{'gateway':'192.168.3.254','mask':'255.255.255.128'}},'initial_ARP':'全部为空'},
'ERR-CN-4.2-072':{'server_IP':'192.168.5.1','sequence':[{'direction':'server→H','message':'DHCPOFFER','yiaddr':'192.168.5.9'},{'direction':'H→server','message':'DHCPREQUEST','yiaddr':'192.168.5.9'}]},
'ERR-CN-4.7-018':{'edges':[['R1','R2',4],['R1','R3',4],['R2','R4',2],['R2','R5',2],['R3','R6',2],['R3','R7',2],['R4','H1',1],['R4','H2',1],['R5','H3',1],['R5','H4',1],['R6','H5',1],['R6','H6',1],['R7','H7',1],['R7','H8',1]],'bandwidth_unit':'Mb/s','duplex':'全双工'},
'ERR-CN-5.3-060':{'timeline':[{'from':'甲','to':'乙','seq':2001,'data_B':1000},{'from':'甲','to':'乙','seq':3001,'data_B':1000},{'from':'乙','to':'甲','seq':4001,'ack_seq':3001,'rcvwnd_B':4000}],'t1':'甲收到图中确认时','initial_cwnd_B':2000,'ssthresh_B':8000,'MSS_B':1000},
'ERR-CN-6.2-014':{'local_LAN':['H','本地域名服务器','路由器'],'Internet_servers':['根域名服务器','com顶级域名服务器','abc.com权威域名服务器','www.abc.com'],'RTT_to_Internet_ms':10,'local_DNS_service':'递归','other_DNS_service':'迭代'},
}
full_view={'ERR-OS-3.1-011','ERR-OS-2.1-022','ERR-OS-4.3-012','ERR-OS-4.2-028'}
# 六题已读原书解析全文；其他题只以答案行核读为默认，避免把索引当解析核验。
six={r['id'] for r in raw if r['subject']=='OS' and r['section']=='2.3'}
severe={'ERR-OS-2.1-022','ERR-OS-2.4-028','ERR-OS-3.2-013','ERR-OS-4.2-010','ERR-CN-4.1-003'}
rows=[]
for n,r in enumerate(raw):
 i=r['id'];m=meta[i];a=r['answer_index'];text=r['raw_question_text'];match=re.search(r'^([0-9]+)\.\s',text,re.M);printed=int(match.group(1)) if match else None
 if match:text=text[match.start():]
 source_note=[]
 if i=='ERR-OS-3.2-052':
  note='[注意：抖动和工作集已从最新大纲中删除]';source_note.append(note);text=text.replace(note,'')
 text=text.replace('x.wait(\n)','x.wait()')
 corrections=[]
 for old,new in ({'210B':'2^10 B','216 页':'2^16 页'} if i=='ERR-OS-3.1-062' else {'232MB':'2^32 MB','232B':'2^32 B'} if i=='ERR-OS-3.2-018' else {'27\n':'2^7\n','216\n':'2^16\n','223\n':'2^23\n','232':'2^32'} if i=='ERR-OS-3.2-019' else {'http:⎳':'http://'} if i=='ERR-CN-6.2-014' else {}).items():
  if old in text:text=text.replace(old,new);corrections.append({'raw':old,'normalized':new,'basis':'原PDF字形/题义核读；指数或URL字符修复'})
 year=re.search(r'【(\d{4})\s*年?\s*统考真题】',text);year=int(year.group(1)) if year else None
 correct='B,D,C,A,B' if i=='ERR-CN-1.2-023' else a['answer'] if a else None
 mismatch='原作答与书答案不同；未见原推理，不能确认具体个人错因'
 if i=='ERR-OS-3.1-011':mismatch='JSON标为错题且错选C，但书答案C；错题登记与答案一致，须保留此矛盾，不能认定确实答错'
 if i=='ERR-CN-1.2-023':mismatch='第1—4空与书答案相同；仅第5空错选A，书答案B'
 if i=='ERR-OS-2.1-022':mismatch='按书三段模型：第1空D→B，第2空C→D，第3空C→D，第4空D→C；第5、6空原答正确。书模型把赋值数据并入正文段，须另作术语说明'
 reading=['已读原始错题JSON作答字段','已从原做题本对应页重新提取题干与选项并逐条语义核读','已在原书扫描PDF图像中核读题号和答案行']
 if i in fig or i in six or i in full_view:reading.append('已查看原题页面/题文裁图')
 if i in six or i in full_view:reading.append('已查看王道答案解析全文图像')
 if i in calc:reading.append('已用独立程序计算过程/数值；见复算状态与假设')
 if i in six:reading.append('已独立按定义和机制核对选项')
 qimage=(out/(i+'_question.png'))
 if i in six:qimage=out/f"OS_2.3_{r['question_number']:03}_question_{r['source_pdf_page']}.png"
 subject_name={'OS':'操作系统','CN':'计算机网络'}[r['subject']]
 article={'id':i,'subject':r['subject'],'subject_name':subject_name,'chapter':r['chapter'],'section':r['section'],'section_name_in_json':r['section_name'],'knowledge_point':m['knowledge_point'],'core_method':m['core_method'],'source':{'error_json':f"/workspace/Classroom/{'03_操作系统/操作系统' if r['subject']=='OS' else '04_计算机网络/计算机网络'}错题精简.json",'question_pdf':r['question_source'],'question_pdf_page':r['source_pdf_page'],'error_json_question_number':r['question_number'],'printed_question_number':printed,'question_location':f"§{r['section']}，JSON第{r['question_number']}题，做题本PDF p{r['source_pdf_page']}，印刷题号{printed}",'book_answer_pdf':a['book'] if a else None,'book_answer_pdf_pages':sorted(set(z['page'] for z in a['crops'])) if a else [],'book_answer_number':a['num'] if a else None,'answer_crops':a['crops'] if a else []},'question_category':['我的错题','王道标注统考真题（身份待交叉核验）' if year else '王道典型选择题'],'selection_priority':'第一优先：已交叉核对真题题意、年号与题号' if i=='ERR-OS-2.3-054' else '第一优先候选：真题身份尚待核验' if year else '第二优先：我的错题与典型例题同等重要','is_personal_error':True,'exam_identity':{'book_tag_year':year,'national_question_number':28 if i=='ERR-OS-2.3-054' else None,'status':'已交叉核对2018第三方重建卷p3—4第28题完整题干与选项；书答案和独立原理均为D；未取得官方答案发布页' if i=='ERR-OS-2.3-054' else '仅核读做题本的统考年份标签；未取得并逐题交叉核对原卷，不标已核验真题' if year else '未标统考真题，按王道典型题登记'},'raw_question_text':r['raw_question_text'],'question_text':text,'normalization':corrections,'figure_or_code_data':fig.get(i),'figure_flags':r['graphic_flags'],'source_editorial_notes':source_note,'actual_answer_information':{'chosen_option':r['original_choice'],'provided_reasoning':None,'provided_teacher_annotation':None,'provided_wrong_reason':None,'personal_evidence':'原始错题JSON中的“错选”；没有个人演算或教师文字批注','book_correct_answer':correct,'book_answer_index_raw':a['answer'] if a else None,'book_answer_visual_check':'已核读答案行；不是官方答案发布的核验','observed_answer_discrepancy':mismatch},'confirmed_personal_error_cause':None,'cause_limit':'未见原始解题过程，不推测当时为何选择该项。知识点及纠正建议依据题干和实际错选定位。','initial_destination':m['initial_destination'],'selection_reason_and_deletion_check':m['additional_value_or_boundary'],'question_specific_correction':m['additional_value_or_boundary'],'unresolved_or_missing':(['未提供个人演算/批改；此项不影响正确解法，不列为需用户重新提供的默认任务']+([m['additional_value_or_boundary']] if i in severe or i=='ERR-OS-3.1-011' else [])),'reading_level':reading,'verification_status':'已读取并归类；题源条件待编辑核准' if i in severe else '已读取并归类；错题身份有矛盾待复核' if i=='ERR-OS-3.1-011' else '已读取并归类；选题初拟，正式入选待考法去重与真题源核验','independent_calculation':calc.get(i),'evidence':{'read_log':str(out/'os_cn_read_log.json'),'answer_header_contact_sheet':str(out/f'answer_headers_{n//60+1}.png'),'answer_header_cell_1based':n%60+1,'original_question_image':str(qimage) if qimage.exists() else None,'question_image_status':'已查看' if qimage.exists() else '文本逐条已读，未逐页图像精读'},'read_date':'2026-10-15'}
 rows.append(article)
(dest/'os_cn_errors.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
fields=['稳定ID','科目','知识点','考法','原题PDF','PDF页','JSON题号','做题本印刷题号','完整题文','图示与代码数据','错选','原书答案','原书答案页','确认个人错因','实际差错记录','初拟去向','选题价值与边界','未解决项','读取层级','核验状态']
with open(dest/'os_cn_errors.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:
  s=r['source'];a=r['actual_answer_information'];w.writerow(dict(zip(fields,[r['id'],r['subject_name'],r['knowledge_point'],r['core_method'],s['question_pdf'],s['question_pdf_page'],s['error_json_question_number'],s['printed_question_number'],r['question_text'],json.dumps(r['figure_or_code_data'],ensure_ascii=False) if r['figure_or_code_data'] else '',a['chosen_option'],a['book_correct_answer'],','.join(map(str,s['book_answer_pdf_pages'])),'未能确认：无原解题过程',a['observed_answer_discrepancy'],r['initial_destination'],r['selection_reason_and_deletion_check'],'；'.join(r['unresolved_or_missing']),'；'.join(r['reading_level']),r['verification_status']])))
# 精确记录逐条读取与视觉核查层级，不以文件存在替代过程核验。
log=json.load(open(out/'os_cn_read_log.json'));log['semantic_reading']='本轮逐条读取全部230题题文，手工标注知识点、考法、去向；非仅统计JSON';log['answer_header_visual_check']={'count':230,'sheets':[f'answer_headers_{i}.png' for i in range(1,5)],'correction':'CN1.2-023的既有答案索引?改为实看B,D,C,A,B'};log['figure_or_formula_visual_check']={'flagged_count':18,'checked_ids':list(fig),'contact_sheets':[f'figures_{i}.png' for i in range(1,5)],'note':'figures_1另含OS3.1-011原题；六题同步独立合图另存'};log['computation_records']=len(calc);log['source_anomalies']=[r['id'] for r in rows if r['id'] in severe or r['id']=='ERR-OS-3.1-011'];log['final_outputs']={'json':str(dest/'os_cn_errors.json'),'csv':str(dest/'os_cn_errors.csv')};
p=out/'exam_2018_rebuild.pdf';log['exam_2018_check']={'url':'https://raw.githubusercontent.com/neville-studio/408-exam-paper/main/papers-rebuild/2018.pdf','access_date':'2026-10-15','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages_visually_checked':[3,4],'question_number':28,'official_source':False}
(out/'os_cn_read_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print('finalized',len(rows),collections.Counter(r['subject'] for r in rows),'book true tags',sum(r['exam_identity']['book_tag_year'] is not None for r in rows),'figures',len(fig),'calculations',len(calc))
