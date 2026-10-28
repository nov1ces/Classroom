#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
texts={ch:(ROOT/'chapters'/ch/'content.md').read_text()for ch in ['DS05','DS07']}
blocks={ch:re.findall(r'^```cpp\n(.*?)^```',txt,re.M|re.S)for ch,txt in texts.items()}
head='''#include <cassert>\n#include <cstdlib>\n#include <vector>\n#include <algorithm>\n#include <random>\n#include <deque>\n#include <iostream>\nstd::vector<int> seen;\ntemplate<class T> void visit(T p){seen.push_back(p->data);}\n'''
body=head
for ch in texts:
 body+='namespace '+ch+' {\nusing ElemType=int;\n'+'\n'.join(blocks[ch])+'\n}\n'
body+=r'''
using DS05::BiTree;using DS05::BiTNode;using DS05::ThreadTree;using DS05::ThreadNode;
std::mt19937 rng(2026102705);int label=0;
BiTree tree(int n){if(!n)return NULL;int left=int(rng()%n);auto p=new BiTNode{label++,NULL,NULL};p->lchild=tree(left);p->rchild=tree(n-1-left);return p;}
void freeTree(BiTree p){if(p){freeTree(p->lchild);freeTree(p->rchild);delete p;}}
ThreadTree clone(BiTree p,std::vector<ThreadTree>&nodes){if(!p)return NULL;auto q=new ThreadNode{p->data,NULL,NULL,0,0};nodes.push_back(q);q->lchild=clone(p->lchild,nodes);q->rchild=clone(p->rchild,nodes);return q;}
std::vector<int> inorder(BiTree p){std::vector<int> out;std::vector<BiTree>st;while(p||!st.empty()){while(p){st.push_back(p);p=p->lchild;}p=st.back();st.pop_back();out.push_back(p->data);p=p->rchild;}return out;}
std::vector<int> preorder(BiTree p,bool rightfirst){std::vector<int>o;std::vector<BiTree>st;if(p)st.push_back(p);while(!st.empty()){p=st.back();st.pop_back();o.push_back(p->data);if(rightfirst){if(p->lchild)st.push_back(p->lchild);if(p->rchild)st.push_back(p->rchild);}else{if(p->rchild)st.push_back(p->rchild);if(p->lchild)st.push_back(p->lchild);}}return o;}
int depth(BiTree p){if(!p)return 0;std::deque<BiTree>q{p};int h=0;while(!q.empty()){auto n=q.size();while(n--){auto v=q.front();q.pop_front();if(v->lchild)q.push_back(v->lchild);if(v->rchild)q.push_back(v->rchild);}++h;}return h;}
void bstIn(DS07::BSTree p,std::vector<int>&o){if(p){bstIn(p->lchild,o);o.push_back(p->key);bstIn(p->rchild,o);}}
void freeBST(DS07::BSTree p){if(p){freeBST(p->lchild);freeBST(p->rchild);free(p);}}
int main(){int trees=0,heaps=0,unions=0,bsts=0;
 for(int n=0;n<=80;++n)for(int rep=0;rep<10;++rep){
  label=0;BiTree p=tree(n);auto in=inorder(p),pre=preorder(p,false),post=preorder(p,true);std::reverse(post.begin(),post.end());assert(DS05::TreeDepth(p)==depth(p));
  seen.clear();DS05::PreOrder(p);assert(seen==pre);seen.clear();DS05::InOrder(p);assert(seen==in);seen.clear();DS05::PostOrder(p);assert(seen==post);
  std::vector<ThreadTree>nodes;ThreadTree t=clone(p,nodes);DS05::CreateInThread(t);seen.clear();DS05::InOrderThread(t);assert(seen==in);
  if(t){auto q=DS05::Firstnode(t);for(int key:in){assert(q&&q->data==key);q=DS05::Nextnode(q);}assert(!q);}
  for(auto q:nodes){delete q;}freeTree(p);++trees;
 }
 for(int n=0;n<=160;++n)for(int rep=0;rep<20;++rep){std::vector<int>a(n+1);for(int i=1;i<=n;++i)a[i]=int(rng()%41)-20;
  for(int k=n/2;k>0;--k)DS05::HeadAdjust(a.data(),k,n);assert(std::is_heap(a.begin()+1,a.end()));
  for(int end=n;end>1;--end){std::swap(a[1],a[end]);DS05::HeadAdjust(a.data(),1,end-1);assert(std::is_heap(a.begin()+1,a.begin()+end));}
  assert(std::is_sorted(a.begin()+1,a.end()));++heaps;
 }
 for(int rep=0;rep<120;++rep){int n=int(rng()%80)+1;std::vector<int>s(n),labels(n);DS05::Initial(s.data(),n);for(int i=0;i<n;++i)labels[i]=i;
  for(int z=0;z<300;++z){int x=int(rng()%n),y=int(rng()%n),lx=labels[x],ly=labels[y];DS05::UnionBySize(s.data(),DS05::FindCompress(s.data(),x),DS05::FindCompress(s.data(),y));for(int i=0;i<n;++i)if(labels[i]==ly)labels[i]=lx;
   for(int i=0;i<n;++i){int root=DS05::FindCompress(s.data(),i);assert((root==DS05::FindCompress(s.data(),x))==(labels[i]==labels[x]));if(s[i]<0){int size=std::count(labels.begin(),labels.end(),labels[i]);assert(-s[i]==size);}}++unions;
  }
 }
 for(int rep=0;rep<500;++rep){DS07::BSTree t=NULL;std::vector<int>keys;for(int i=0;i<80;++i){int v=int(rng()%201)-100;bool exists=std::find(keys.begin(),keys.end(),v)!=keys.end();assert(DS07::BST_Insert(t,v)==!exists);if(!exists)keys.push_back(v);}std::sort(keys.begin(),keys.end());
  for(int key=-110;key<=110;++key){auto p=DS07::BST_Search(t,key);assert(bool(p)==std::binary_search(keys.begin(),keys.end(),key));if(p)assert(p->key==key);}
  std::vector<int>now;bstIn(t,now);assert(now==keys);if(t&&t->rchild){DS07::L_Rotate(t);now.clear();bstIn(t,now);assert(now==keys);}if(t&&t->lchild){DS07::R_Rotate(t);now.clear();bstIn(t,now);assert(now==keys);}freeBST(t);++bsts;
 }
 std::cout<<trees<<" random tree/thread cases; "<<heaps<<" heap builds/sorts; "<<unions<<" union/find rounds; "<<bsts<<" random BST/rotation cases passed\n";
}
'''
# Use braces in test-only compact loops to satisfy strict warning checks.
body=body.replace('for(int k=n/2;k>0;--k)DS05::HeadAdjust(a.data(),k,n);assert', 'for(int k=n/2;k>0;--k){DS05::HeadAdjust(a.data(),k,n);}\n  assert')
p=OUT/'ds_trees_displayed_test.cpp';p.write_text(body)
args=['g++','-std=c++11','-Wall','-Wextra','-Wpedantic','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-O1','-g',str(p),'-o',str(OUT/'ds_trees_displayed_test')]
a=subprocess.run(args,capture_output=True,text=True);assert a.returncode==0,a.stderr
b=subprocess.run([str(OUT/'ds_trees_displayed_test')],capture_output=True,text=True);assert b.returncode==0,b.stdout+b.stderr
(OUT/'ds_trees_results.json').write_text(json.dumps({'status':'passed','source':'DS05 and DS07 current cpp blocks extracted verbatim; independent randomized harness','compiler':'C++11 strict warnings ASan UBSan','output':b.stdout,'source_sha256':{c:hashlib.sha256(t.encode()).hexdigest()for c,t in texts.items()},'scope':'Recursive/iterative traversal and depth, inorder threading successor, heap downfilter, weighted union/path compression, BST search/insert/rotations. Excludes standalone handwritten pseudocode and image/coverage checks.'},ensure_ascii=False,indent=2));print(b.stdout)
