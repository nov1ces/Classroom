#include <cassert>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <random>
#include <deque>
#include <iostream>
std::vector<int> seen;
template<class T> void visit(T p){seen.push_back(p->data);}
namespace DS05 {
using ElemType=int;
typedef struct BiTNode {
    ElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;

void PreOrder(BiTree T) {
    if (T!=NULL) {
        visit(T);
        PreOrder(T->lchild);
        PreOrder(T->rchild);
    }
}
void InOrder(BiTree T) {
    if (T!=NULL) {
        InOrder(T->lchild);
        visit(T);
        InOrder(T->rchild);
    }
}
void PostOrder(BiTree T) {
    if (T!=NULL) {
        PostOrder(T->lchild);
        PostOrder(T->rchild);
        visit(T);
    }
}

typedef struct ThreadNode {
    ElemType data;
    struct ThreadNode *lchild, *rchild;
    int ltag, rtag;  // 0：孩子；1：线索
} ThreadNode, *ThreadTree;

void InThread(ThreadTree p, ThreadTree &pre) {
    if (p!=NULL) {
        InThread(p->lchild, pre);
        if (p->lchild==NULL) {
            p->lchild=pre;
            p->ltag=1;
        }
        if (pre!=NULL && pre->rchild==NULL) {
            pre->rchild=p;
            pre->rtag=1;
        }
        pre=p;
        InThread(p->rchild, pre);
    }
}
void CreateInThread(ThreadTree T) {
    ThreadTree pre=NULL;
    if (T!=NULL) {
        InThread(T, pre);
        pre->rchild=NULL;
        pre->rtag=1;
    }
}

ThreadNode *Firstnode(ThreadNode *p) {
    while (p->ltag==0) p=p->lchild;
    return p;
}
ThreadNode *Nextnode(ThreadNode *p) {
    if (p->rtag==0) return Firstnode(p->rchild);
    return p->rchild;
}
void InOrderThread(ThreadNode *T) {
    if (T==NULL) return;
    for (ThreadNode *p=Firstnode(T); p!=NULL; p=Nextnode(p))
        visit(p);
}

#define MAX_TREE_SIZE 100
typedef struct {
    ElemType data;
    int parent;
} PTNode;
typedef struct {
    PTNode nodes[MAX_TREE_SIZE];
    int n;
} PTree;

typedef struct CSNode {
    ElemType data;
    struct CSNode *firstchild, *nextsibling;
} CSNode, *CSTree;

void Initial(int S[], int n) {
    for (int i=0; i<n; ++i) S[i]=-1;
}
int Find(int S[], int x) {
    while (S[x]>=0) x=S[x];
    return x;
}
void Union(int S[], int Root1, int Root2) {
    if (Root1==Root2) return;
    S[Root2]=Root1;
}

void UnionBySize(int S[], int Root1, int Root2) {
    if (Root1==Root2) return;
    if (S[Root2]>S[Root1]) {
        S[Root1]+=S[Root2];
        S[Root2]=Root1;
    } else {
        S[Root2]+=S[Root1];
        S[Root1]=Root2;
    }
}
int FindCompress(int S[], int x) {
    int root=x;
    while (S[root]>=0) root=S[root];
    while (x!=root) {
        int t=S[x];
        S[x]=root;
        x=t;
    }
    return root;
}

void HeadAdjust(int A[], int k, int len) {
    A[0]=A[k];
    for (int i=2*k; i<=len; i*=2) {
        if (i<len && A[i]<A[i+1]) ++i;
        if (A[0]>=A[i]) break;
        A[k]=A[i]; k=i;
    }
    A[k]=A[0];
}

}
namespace DS07 {
using ElemType=int;
typedef struct {
    ElemType *elem;
    int TableLen;
} SSTable;
int Search_Seq(SSTable ST, ElemType key) {
    ST.elem[0]=key;
    int i;
    for (i=ST.TableLen; ST.elem[i]!=key; --i) ;
    return i;
}

int Binary_Search(SSTable L, ElemType key) {
    int low=0, high=L.TableLen-1, mid;
    while (low<=high) {
        mid=(low+high)/2;
        if (L.elem[mid]==key) return mid;
        else if (L.elem[mid]>key) high=mid-1;
        else low=mid+1;
    }
    return -1;
}

typedef struct BSTNode {
    int key;
    struct BSTNode *lchild, *rchild;
} BSTNode, *BSTree;
BSTNode *BST_Search(BSTree T, int key) {
    while (T!=NULL && key!=T->key) {
        if (key<T->key) T=T->lchild;
        else T=T->rchild;
    }
    return T;
}
int BST_Insert(BSTree &T, int k) {
    if (T==NULL) {
        T=(BSTree)malloc(sizeof(BSTNode));
        T->key=k;
        T->lchild=T->rchild=NULL;
        return 1;
    } else if (k==T->key) return 0;
    else if (k<T->key) return BST_Insert(T->lchild,k);
    else return BST_Insert(T->rchild,k);
}
void Create_BST(BSTree &T, int str[], int n) {
    T=NULL;
    for (int i=0; i<n; ++i) BST_Insert(T,str[i]);
}

void R_Rotate(BSTree &p) {
    BSTNode *lc=p->lchild;
    p->lchild=lc->rchild;
    lc->rchild=p;
    p=lc;
}
void L_Rotate(BSTree &p) {
    BSTNode *rc=p->rchild;
    p->rchild=rc->lchild;
    rc->lchild=p;
    p=rc;
}

}

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
  for(int k=n/2;k>0;--k){DS05::HeadAdjust(a.data(),k,n);}
  assert(std::is_heap(a.begin()+1,a.end()));
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
