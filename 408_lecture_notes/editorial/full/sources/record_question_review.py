from pathlib import Path
import json,hashlib,re
ROOT=Path('/workspace/408_lecture_notes');BASE=ROOT/'editorial/full/sources';WORK=BASE/'current_review'
a=json.loads((WORK/'selected_evidence.json').read_text())
reviewed_ids={'CO2-7','CO2-8','CO2-9',*[f'CO3-{i}' for i in range(1,11)],'CO6-1','CO6-3','CO6-4',*[f'CO7-{i}' for i in range(1,5)],'CN3-1','CN3-2','CN3-3','CN3-4','CN3-5','CN3-7','CN3-8','CN3-9','CN3-11','CN4-1','CN4-2','CN4-3','CN4-4','CN4-5','CN4-7','CN4-8','CN4-9',*[f'CN5-{i}' for i in range(1,8)]}
reviewed_ids.update({'CN6-1','CN6-2','CN6-3','CN6-4','CN6-6','CN6-7'})
assert {r['id'] for r in a}==reviewed_ids
cache={}
def sha(p):
 p=Path(p)
 if str(p) not in cache:cache[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[str(p)]
fig_map={'CN4-7':'CN13_dhcp_2025.png','CN5-6':'CN10_tcp_window_2025.png','CO3-9':'正文页表','CN4-1':'正文距离向量表','CO6-3':'正文代码序列','CN6-1':'CN14_dns_topology_2016.png','CN6-6':'CN11_dns_web_2020.png'}
calc={}
for name,key in [('review_calculation_results.json','results'),('new_chapter_calculation_results.json','checks')]:
 for x in json.loads((BASE/name).read_text())[key]:calc.setdefault(x['question'],[]).append(name)
calc['CN5-6']=['source_calculation_results.json']
calc['CN6-1']=['source_calculation_results.json']
calc['CN6-6']=['source_calculation_results.json']
records=[]
for r in a:
 p=Path(r['manuscript']);s=p.read_text();exam=ROOT/f'editorial/sources/exams/exam_{r["year"]}_rebuild.pdf';w=r['wangdao_location'];book=r['book_answer']['book']
 row={'id':r['id'],'review_date':'2026-10-16','subject':r['id'][:2],'manuscript':str(p),'manuscript_sha256_at_review':sha(p),'exam_year':r['year'],'exam_question_number':r['exam_question'],'reader_source_mark':f'【{r["year"]}】','source_checks':{'complete_rebuild_pdf':str(exam),'rebuild_sha256':sha(exam),'rebuild_question_start_pdf_page':r['exam_page'],'rebuild_kind':'社区二手复原，非官方原始发布','provided_question_text_source':'用户提供王道横版题文；实际提取读取题干和四个选项并与完整卷比较','provided_question_section':w['section'],'provided_question_number':w['question_number'],'provided_horizontal_pdf_page':w['horizontal_page'],'main_book_answer_pdf':book,'main_book_sha256':sha(book),'main_book_answer_pages':sorted({c['page'] for c in r['book_answer']['crops']}),'main_book_answer_images_actually_viewed':r['answer_images'],'main_book_answer':r['book_answer']['answer'],'official_answer_publication_obtained':False},'actual_reading_scope':['正文该题完整题干、选项与连续解析','完整二手卷对应题文与题号/年份','用户提供王道对应题干与选项','王道主书答案及解析的原页裁剪图'],'comparison_result':'题意、已知数据与A—D选项保持一致；未见未经标注的条件/数值/设问改编','calculation_checks':sorted(set(calc.get(r['id'],[]))),'figure_table_code_review':fig_map.get(r['id'],'该题无决定答案的原题图示；正文表/公式按实际数据核对'),'issues':[],'status':'本记录所列题文与书答已交叉；非全库逐题核验'}
 if r['id']=='CN3-9':
  row['issues'].append({'item':'CTS后NAV图注','found':'初稿将CTS结束后的剩余区间写三个SIFS，正文计算为两个','action':'已通知作者；当前稿件图注已改两个SIFS，解析NAV354μs一致','status':'已修正并复读当前文字'})
  row['issues'].append({'item':'复原卷原始误排和版本分歧','found':'复原PDF p4本身写DIFS=128s、SIFS≥28μs；王道题/答及N诺题文为128μs、28μs。PGCode和csgraduates另记DIFS120μs','action':'按主书采用128μs、28μs；记录二手卷错误与版本差异。DIFS不进入CTS后NAV计算','status':'主书题文本和计算已核；原始发布卷中DIFS字段待原始扫描进一步核对','evidence':['current_review/CN3-9_exam_p4.png','https://noobdream.com/Practice/exam_solution/41996/','https://pgcode.cn/exams/408/years/2024/preview']})
  row['comparison_result']='主书题文保持；二手复原卷自身的单位/比较符误排已辨明，不把其错误当成原题成立条件'
 if r['id']=='CN4-7':
  row['actual_reading_scope']+=['完整复原卷2025 p4图示、王道主书p171图示及p186答案','IETF RFC2131 §4.3.2、§4.4表5一手字段规则']
  row['issues'].append({'item':'原题图DHCPREQUEST字段标签','found':'复原卷与王道图均把待申请192.168.5.9标为yiaddr；规范客户端该字段为0','action':'正文保留原图标注并在解析说明Requested IP Address与尚未取得使用权，避免无标注修改真题','status':'正文辨析已读；CN13重绘成图与原题字值/箭头逐项一致，最终PDF另检','primary_source':'https://datatracker.ietf.org/doc/html/rfc2131'})
 if r['id']=='CN5-6':
  row['actual_reading_scope']+=['复原2025 p5与主书p264—265原题图、p274答案的seq/ack_seq/rcvwnd方向数值逐项图读']
  row['issues'].append({'item':'重绘图稿','action':'原图及重绘PNG数据已核（2001/3001/4001、ack3001、rwnd4000、每段1000B）；返回斜线穿rwnd标签已通知作者调整','status':'图稿数据已核；标签压线待改后复看'})
 if r['id']=='CO3-9':row['actual_reading_scope']+=['复原2022 p2页表原图：十进制虚页82/129/130、十六进制页框024/180/018、存在0/1/1']
 records.append(row)
report={'schema_version':'1.0','date':'2026-10-16','scope':'独立审校实际所读50道正文真题；不代表四科全部题、大纲覆盖或最终PDF视觉检查','read_count':len(records),'files_sha256':cache,'records':records,'not_reviewed_by_this_log':['其他正文/自测题不得从本表自动升级已核','全部846个下载题号只是定位，非人工审校总数','最终CN重绘题图/全书PDF尚待独立视觉检查'],'follow_up':['原卷DIFS字段仍有120/128二手版本分歧；主书128并不影响该题354μs答案','CN13 DHCP、CN10 TCP窗PNG已与原题逐项检查；CN10/CN05标签压线待改后复看，最终PDF另检']}
(BASE/'full_question_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('recorded',len(records),'questions',len(cache),'actual input hashes')
