from pathlib import Path
import json,csv,collections
R=Path('/workspace/408_lecture_notes/editorial/errors');p=R/'ds_co_errors.json';d=json.load(open(p));rs=d['records'];m={}
def sec(sub,s,ids):
 for x in rs:
  if x['subject']==sub and x['section']==s:m[x['id']]=ids.split()
def each(sub,s,nos,ids):
 for n in nos.split():m[f'ERR-{sub}-{s}-{int(n):03}']=ids.split()
sec('DS','1.1','DS-01-01');sec('DS','1.2','DS-01-03');each('DS','1.2','2','DS-01-02 DS-01-03 DS-01-04')
sec('DS','2.3','DS-02-04');each('DS','2.3','3','DS-01-01 DS-02-03');each('DS','2.3','12','DS-02-02 DS-02-03')
sec('DS','3.1','DS-03-01');each('DS','3.1','1','DS-01-01 DS-03-01 DS-03-02');each('DS','3.1','8','DS-03-04');each('DS','3.1','25','DS-03-03');each('DS','3.1','26','DS-03-01 DS-03-02')
sec('DS','3.2','DS-03-04');each('DS','3.2','5 6 9','DS-03-03');sec('DS','3.3','DS-03-07');sec('DS','3.4','DS-03-06');sec('DS','4.2','DS-04-03');sec('DS','5.1','DS-05-01');sec('DS','5.2','DS-05-03');each('DS','5.2','7','DS-05-02');sec('DS','5.3','DS-05-04');each('DS','5.3','23 29','DS-05-05');sec('DS','5.4','DS-05-06 DS-05-07');sec('DS','5.5','DS-05-09');sec('DS','6.1','DS-06-01');sec('DS','6.2','DS-06-02');sec('DS','6.3','DS-06-04');each('DS','6.3','13','DS-06-01');sec('DS','6.4','DS-06-07');each('DS','6.4','19 36','DS-06-08');each('DS','6.4','31','DS-06-09');each('DS','6.4','41','DS-06-04 DS-06-08');sec('DS','7.2','DS-07-03');each('DS','7.2','2','DS-07-01 DS-07-02');sec('DS','7.3','DS-07-05');each('DS','7.3','29','DS-07-04 DS-07-05');sec('DS','7.4','DS-07-07');sec('DS','7.5','DS-07-09');sec('DS','8.2','DS-08-05');each('DS','8.2','15','DS-08-01 DS-08-05');sec('DS','8.3','DS-08-06');sec('DS','8.4','DS-05-11 DS-08-07');each('DS','8.4','1','DS-08-04');sec('DS','8.5','DS-08-09');each('DS','8.5','3','DS-01-04 DS-08-06 DS-08-08 DS-08-11');sec('DS','8.6','DS-08-11');sec('DS','8.7','DS-08-10');each('DS','8.7','1','DS-08-01 DS-08-10')
sec('CO','1.2','CO-01-01 CO-01-02');each('CO','1.2','8 11','CO-01-02 CO-04-05');sec('CO','1.3','CO-01-03');each('CO','1.3','8','CO-01-03 CO-02-02');sec('CO','2.1','CO-02-03');each('CO','2.1','1','CO-02-01');each('CO','2.1','16','CO-02-02');sec('CO','2.2','CO-02-05');each('CO','2.2','18','CO-02-04 CO-02-05');each('CO','2.2','22','CO-02-03 CO-02-05');each('CO','2.2','24','CO-02-06');sec('CO','2.3','CO-02-07');each('CO','2.3','7','CO-02-02 CO-02-07');each('CO','2.3','8','CO-02-08');each('CO','2.3','20 24','CO-02-03 CO-02-07');each('CO','2.3','21 30 45','CO-04-03');sec('CO','3.1','CO-03-01');sec('CO','3.2','CO-03-02 CO-03-03');each('CO','3.2','26','');sec('CO','3.3','CO-03-05');each('CO','3.3','12','CO-03-03 CO-03-05');sec('CO','3.4','CO-03-06');sec('CO','3.5','CO-03-07');each('CO','3.5','12 35','CO-03-08');each('CO','3.5','23 24','CO-03-07 CO-07-02');each('CO','3.5','30','CO-03-08 CO-03-09');each('CO','3.5','31 34','CO-03-08 CO-03-10');sec('CO','3.6','CO-03-12');each('CO','3.6','2','CO-03-11');each('CO','3.6','5','CO-03-11 CO-03-12');each('CO','3.6','14','CO-03-10 CO-03-12');sec('CO','4.1','CO-04-01');sec('CO','4.2','CO-04-02');each('CO','4.2','11 19','CO-04-02 CO-04-03');each('CO','4.2','15','CO-04-01 CO-04-02');each('CO','4.2','20','CO-04-01');each('CO','4.2','21','CO-02-05 CO-04-06');sec('CO','4.3','CO-04-07');each('CO','4.3','6','CO-02-05 CO-04-06');sec('CO','4.4','CO-04-04');sec('CO','5.1','CO-05-01');each('CO','5.1','21','CO-05-02 CO-05-03');sec('CO','5.2','CO-05-02');sec('CO','5.3','CO-05-03');sec('CO','5.4','CO-05-04');each('CO','5.4','1','CO-05-02 CO-05-03');each('CO','5.4','18','CO-05-01 CO-05-04');sec('CO','5.5','CO-05-05');sec('CO','5.6','CO-06-03');each('CO','5.6','8','CO-06-02');each('CO','5.6','18','CO-06-04');each('CO','5.6','26','CO-05-03 CO-06-02');each('CO','5.6','33','CO-05-01 CO-05-04 CO-06-03');sec('CO','5.7','CO-06-06');each('CO','5.7','12','CO-06-05 CO-06-06');sec('CO','6.1','CO-07-01');sec('CO','6.2','CO-07-02');each('CO','6.2','11','CO-08-01 CO-07-02');each('CO','6.2','17','CO-07-01');sec('CO','7.2','CO-08-01');each('CO','7.2','10','CO-03-06 CO-08-01');sec('CO','7.3','CO-08-03');each('CO','7.3','3 19 38','CO-08-03 CO-08-04');each('CO','7.3','20','CO-08-02');each('CO','7.3','21 44 47 53','CO-08-04');each('CO','7.3','50','CO-05-05 CO-08-03')
assert set(m)==set(x['id'] for x in rs)
known={}
for sub in ['DS','CO']:
 for x in json.load(open(R.parent/'scope'/f'{sub}_coverage.json')):known[x['知识点 ID']]=x['知识点']
for x in rs:
 x['knowledge_ids']=m[x['id']];x['knowledge_group_names']=[known[z] for z in x['knowledge_ids']];x['knowledge_link_status']='按已读题意与覆盖组的同名概念/明确机制人工匹配；本题来源条件核验状态另列。' if x['knowledge_ids'] else '待章节核：当前覆盖表未明确单体多字存储器的去向，不将它直接等同多模块交叉存储器。'
 x['knowledge_point_id_status']='逐题分类锚点保留；与总覆盖表的关联使用knowledge_ids。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
# Update the CSV to expose coverage links next to detailed classifications.
cp=R/'ds_co_errors.csv';head=next(csv.reader(cp.open(encoding='utf-8-sig')));head=head[:head.index('knowledge_point')]+['knowledge_ids','knowledge_group_names','knowledge_link_status']+head[head.index('knowledge_point'):]
with cp.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=head,extrasaction='ignore');w.writeheader()
 for x in rs:
  y={k:x.get(k) for k in head}
  for k,v in list(y.items()):
   if isinstance(v,(dict,list)):y[k]=json.dumps(v,ensure_ascii=False)
  w.writerow(y)
print('linked',sum(bool(x['knowledge_ids']) for x in rs),'pending',[x['id'] for x in rs if not x['knowledge_ids']])
print('groups',len(set(z for x in rs for z in x['knowledge_ids'])))
