#include <cstdlib>
#include <cassert>
#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
using ElemType=int;
std::vector<int> visited_values;
template<class T> void visit(T p){visited_values.push_back(p->data);}
typedef struct BiTNode {
    ElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;

int TreeDepth(BiTree T) {
    if (T==NULL) return 0;
    int hl=TreeDepth(T->lchild), hr=TreeDepth(T->rchild);
    return 1+(hl>hr ? hl : hr);
}

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

void destroy(BiTree p){if(!p)return;destroy(p->lchild);destroy(p->rchild);delete p;}
int main(){
 BiTree a=new BiTNode{1,NULL,NULL}; a->lchild=new BiTNode{2,NULL,NULL};a->rchild=new BiTNode{3,NULL,NULL};
 assert(TreeDepth(a)==2);PreOrder(a);assert((visited_values==std::vector<int>{1,2,3}));visited_values.clear();
 InOrder(a);assert((visited_values==std::vector<int>{2,1,3}));visited_values.clear();PostOrder(a);assert((visited_values==std::vector<int>{2,3,1}));destroy(a);
 ThreadTree t=new ThreadNode{1,NULL,NULL,0,0};t->lchild=new ThreadNode{2,NULL,NULL,0,0};t->rchild=new ThreadNode{3,NULL,NULL,0,0};
 CreateInThread(t);visited_values.clear();InOrderThread(t);assert((visited_values==std::vector<int>{2,1,3}));
 assert(Nextnode(t->lchild)==t);assert(Nextnode(t->rchild)==NULL);delete t->lchild;delete t->rchild;delete t;
 std::mt19937 gen(408);int S[100],label[100];Initial(S,100);for(int i=0;i<100;++i)label[i]=i;
 for(int z=0;z<4000;++z){int a1=gen()%100,b=gen()%100;int la=label[a1],lb=label[b];UnionBySize(S,FindCompress(S,a1),FindCompress(S,b));for(int i=0;i<100;++i)if(label[i]==lb)label[i]=la;for(int j=0;j<100;++j)assert((FindCompress(S,a1)==FindCompress(S,j))==(label[a1]==label[j]));}
 int P[4];Initial(P,4);Union(P,0,1);assert(Find(P,1)==0);int H[]={0,1,8,7};HeadAdjust(H,1,3);assert(H[1]==8 && H[2]==1);
 std::cout<<"tree traversal, threading boundaries, 4000 union/find operations passed\n";
}