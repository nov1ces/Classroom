#!/usr/bin/env python3
from pathlib import Path
import re,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sources={c:(ROOT/'chapters'/c/'content.md').read_text()for c in ['DS02','DS03']}
blocks={c:re.findall(r'^```(?:cpp|c)\n(.*?)^```',t,re.M|re.S)for c,t in sources.items()}
def find(c,p):
 r=[x for x in blocks[c]if re.search(p,x)]
 assert len(r)==1,(c,p,len(r));return r[0]
seq='\n'.join(find('DS02',p)for p in [r'} SqList;',r'void InitList\(SqList',r'bool ListInsert\(SqList'])
link='\n'.join(find('DS02',p)for p in [r'} LNode, \*LinkList;',r'LNode \*GetElem\(',r'bool InsertNextNode\('])
sq='\n'.join(find('DS03',p)for p in [r'} SqStack;',r'} SqQueue;'])
linked='\n'.join(find('DS03',p)for p in [r'} \*LiStack;',r'} LinkQueue;'])
nohead=find('DS03',r'Q.front = Q.rear = NULL;')
# The unheaded variant shares the printed node/queue definitions, not its headed functions.
node_defs=linked[linked.index('typedef struct LinkNode'):linked.index('void InitQueue(LinkQueue')]
program='''#include <cstdlib>\n#include <cassert>\n#include <deque>\n#include <vector>\n#include <random>\n#include <algorithm>\n#include <iostream>\n'''
for name,body in [('seq',seq),('link',link),('sq',sq),('linked',linked),('nohead',node_defs+nohead)]:
 program+='namespace '+name+' {\ntypedef int ElemType;\n'+body+'\n}\n#undef MaxSize\n'
program+=r'''
int main(){
 std::mt19937 gen(20261027);int checks=0;
 seq::SqList sl;seq::InitList(sl);std::vector<int> ref;
 link::LinkList ll;assert(link::InitList(ll));
 for(int z=0;z<100000;++z){
  int pos=int(gen()%(ref.size()+4))-1,x=int(gen()%31)-15,old=-123456;
  if(gen()%2){
   bool valid=pos>=1&&pos<=int(ref.size())+1;
   bool a=seq::ListInsert(sl,pos,x);bool b=link::ListInsert(ll,pos,x);
   assert(a==(valid&&ref.size()<100));assert(b==valid);
   if(b){if(!a){int dummy;assert(link::ListDelete(ll,pos,dummy));}else ref.insert(ref.begin()+pos-1,x);}
  }else{
   bool valid=pos>=1&&pos<=int(ref.size());int aout=old,bout=old;
   assert(seq::ListDelete(sl,pos,aout)==valid);assert(link::ListDelete(ll,pos,bout)==valid);
   if(valid){assert(aout==ref[pos-1]&&bout==ref[pos-1]);ref.erase(ref.begin()+pos-1);}else assert(aout==old&&bout==old);
  }
  assert(sl.length==int(ref.size()));auto p=ll->next;
  for(int i=0;i<int(ref.size());++i){assert(sl.data[i]==ref[i]);assert(p&&p->data==ref[i]);p=p->next;}
  assert(!p);assert(link::GetElem(ll,0)==ll);assert(link::GetElem(ll,-1)==NULL);assert(link::GetElem(ll,int(ref.size())+1)==NULL);++checks;
 }
 while(ll){auto p=ll;ll=ll->next;free(p);}
 sq::SqStack ss;sq::InitStack(ss);std::vector<int> sr;
 sq::SqQueue qq;sq::InitQueue(qq);std::deque<int> qr;
 linked::LiStack ls=NULL;std::vector<int> lr;
 linked::LinkQueue lq;linked::InitQueue(lq);std::deque<int> lqr;
 nohead::LinkQueue nq;nohead::InitQueue(nq);std::deque<int> nqr;
 for(int z=0;z<150000;++z){
  int x=int(gen()),out=-17;bool push=gen()%2;
  if(push){bool valid=sr.size()<100;assert(sq::Push(ss,x)==valid);if(valid)sr.push_back(x);}
  else{bool valid=!sr.empty();assert(sq::Pop(ss,out)==valid);if(valid){assert(out==sr.back());sr.pop_back();}else assert(out==-17);}
  assert(sq::StackEmpty(ss)==sr.empty());out=-17;assert(sq::GetTop(ss,out)==!sr.empty());if(!sr.empty())assert(out==sr.back());else assert(out==-17);
  if(push){bool valid=qr.size()<99;assert(sq::EnQueue(qq,x)==valid);if(valid)qr.push_back(x);}
  else{out=-17;bool valid=!qr.empty();assert(sq::DeQueue(qq,out)==valid);if(valid){assert(out==qr.front());qr.pop_front();}else assert(out==-17);}
  assert(sq::QueueEmpty(qq)==qr.empty());assert((qq.rear-qq.front+100)%100==int(qr.size()));out=-17;assert(sq::GetHead(qq,out)==!qr.empty());if(!qr.empty())assert(out==qr.front());else assert(out==-17);
  if(push){assert(linked::Push(ls,x));lr.push_back(x);linked::EnQueue(lq,x);lqr.push_back(x);nohead::EnQueue(nq,x);nqr.push_back(x);}
  else{
   out=-17;assert(linked::Pop(ls,out)==!lr.empty());if(!lr.empty()){assert(out==lr.back());lr.pop_back();}else assert(out==-17);
   out=-17;assert(linked::DeQueue(lq,out)==!lqr.empty());if(!lqr.empty()){assert(out==lqr.front());lqr.pop_front();}else assert(out==-17);
   out=-17;assert(nohead::DeQueue(nq,out)==!nqr.empty());if(!nqr.empty()){assert(out==nqr.front());nqr.pop_front();}else assert(out==-17);
  }
  assert(linked::IsEmpty(lq)==lqr.empty());assert(nohead::IsEmpty(nq)==nqr.empty());
  if(lqr.empty())assert(lq.front==lq.rear);if(nqr.empty())assert(nq.front==NULL&&nq.rear==NULL);checks+=5;
 }
 int out;while(linked::Pop(ls,out)){}while(linked::DeQueue(lq,out)){}free(lq.front);while(nohead::DeQueue(nq,out)){}
 std::cout<<checks<<" paired container operation rounds passed\n";
}
'''
# Avoid a misleading-indentation warning in the independent harness itself.
program=program.replace('if(nqr.empty())assert(nq.front==NULL&&nq.rear==NULL);checks+=5;', 'if(nqr.empty()){assert(nq.front==NULL&&nq.rear==NULL);}\n  checks+=5;')
program=program.replace('if(lqr.empty())assert(lq.front==lq.rear);if(nqr.empty())','if(lqr.empty()){assert(lq.front==lq.rear);}\n  if(nqr.empty())')
p=OUT/'ds_containers_displayed_test.cpp';p.write_text(program)
cmd=['g++','-std=c++11','-Wall','-Wextra','-Wpedantic','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-O1','-g',str(p),'-o',str(OUT/'ds_containers_displayed_test')]
a=subprocess.run(cmd,text=True,capture_output=True);assert a.returncode==0,a.stderr
b=subprocess.run([str(OUT/'ds_containers_displayed_test')],text=True,capture_output=True);assert b.returncode==0,b.stdout+b.stderr
result={'status':'passed','checks':'850000 paired container operation rounds plus getters, invalid position/output and allocation cleanup assertions','compiler':cmd[:-3],'output':b.stdout,'chapters_sha256':{c:hashlib.sha256(t.encode()).hexdigest()for c,t in sources.items()},'scope':'Verbatim displayed static sequence-list + headed-list updates; stack, circular queue, linked stack, headed and unheaded linked queues. Allocation-success textbook preconditions retained. Excludes input-driven builders and unrelated code blocks.'}
(OUT/'ds_containers_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(b.stdout)
