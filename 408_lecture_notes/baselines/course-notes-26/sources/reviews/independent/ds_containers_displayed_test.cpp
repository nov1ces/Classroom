#include <cstdlib>
#include <cassert>
#include <deque>
#include <vector>
#include <random>
#include <algorithm>
#include <iostream>
namespace seq {
typedef int ElemType;
#define MaxSize 100
typedef int ElemType;
typedef struct {
    ElemType data[MaxSize];
    int length;
} SqList;

void InitList(SqList &L) { L.length = 0; }
ElemType GetElem(SqList L, int i) {
    return L.data[i - 1];  // 前提：1 <= i <= L.length
}
int LocateElem(SqList L, ElemType e) {
    for (int i = 0; i < L.length; ++i)
        if (L.data[i] == e) return i + 1;
    return 0;
}

bool ListInsert(SqList &L, int i, ElemType e) {
    if (i < 1 || i > L.length + 1) return false;
    if (L.length >= MaxSize) return false;
    for (int j = L.length; j >= i; --j)
        L.data[j] = L.data[j - 1];
    L.data[i - 1] = e;
    ++L.length;
    return true;
}
bool ListDelete(SqList &L, int i, ElemType &e) {
    if (i < 1 || i > L.length) return false;
    e = L.data[i - 1];
    for (int j = i; j < L.length; ++j)
        L.data[j - 1] = L.data[j];
    --L.length;
    return true;
}

}
#undef MaxSize
namespace link {
typedef int ElemType;
typedef struct LNode {
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;
bool InitList(LinkList &L) {
    L = (LNode *)malloc(sizeof(LNode));
    if (L == NULL) return false;
    L->next = NULL;
    return true;
}

LNode *GetElem(LinkList L, int i) {
    if (i < 0) return NULL;
    int j = 0;
    LNode *p = L;
    while (p != NULL && j < i) {
        p = p->next;
        ++j;
    }
    return p;
}
LNode *LocateElem(LinkList L, ElemType e) {
    LNode *p = L->next;
    while (p != NULL && p->data != e) p = p->next;
    return p;
}

bool InsertNextNode(LNode *p, ElemType e) {
    if (p == NULL) return false;
    LNode *s = (LNode *)malloc(sizeof(LNode));
    if (s == NULL) return false;
    s->data = e;
    s->next = p->next;
    p->next = s;
    return true;
}
bool ListInsert(LinkList &L, int i, ElemType e) {
    if (i < 1) return false;
    LNode *p = GetElem(L, i - 1);
    return InsertNextNode(p, e);
}
bool ListDelete(LinkList &L, int i, ElemType &e) {
    if (i < 1) return false;
    LNode *p = GetElem(L, i - 1);
    if (p == NULL || p->next == NULL) return false;
    LNode *q = p->next;
    e = q->data;
    p->next = q->next;
    free(q);
    return true;
}

}
#undef MaxSize
namespace sq {
typedef int ElemType;
#define MaxSize 100
typedef int ElemType;
typedef struct {
    ElemType data[MaxSize];
    int top;
} SqStack;
void InitStack(SqStack &S) { S.top = -1; }
bool StackEmpty(SqStack S) { return S.top == -1; }
bool Push(SqStack &S, ElemType x) {
    if (S.top == MaxSize - 1) return false;
    S.data[++S.top] = x;
    return true;
}
bool Pop(SqStack &S, ElemType &x) {
    if (S.top == -1) return false;
    x = S.data[S.top--];
    return true;
}
bool GetTop(SqStack S, ElemType &x) {
    if (S.top == -1) return false;
    x = S.data[S.top];
    return true;
}

typedef struct {
    ElemType data[MaxSize];
    int front, rear;
} SqQueue;
void InitQueue(SqQueue &Q) { Q.front = Q.rear = 0; }
bool QueueEmpty(SqQueue Q) { return Q.front == Q.rear; }
bool EnQueue(SqQueue &Q, ElemType x) {
    if ((Q.rear + 1) % MaxSize == Q.front) return false;
    Q.data[Q.rear] = x;
    Q.rear = (Q.rear + 1) % MaxSize;
    return true;
}
bool DeQueue(SqQueue &Q, ElemType &x) {
    if (Q.front == Q.rear) return false;
    x = Q.data[Q.front];
    Q.front = (Q.front + 1) % MaxSize;
    return true;
}
bool GetHead(SqQueue Q, ElemType &x) {
    if (Q.front == Q.rear) return false;
    x = Q.data[Q.front];
    return true;
}

}
#undef MaxSize
namespace linked {
typedef int ElemType;
typedef struct Linknode {
    ElemType data;
    struct Linknode *next;
} *LiStack;
bool Push(LiStack &S, ElemType x) {
    LiStack p = (LiStack)malloc(sizeof(struct Linknode));
    if (p == NULL) return false;
    p->data = x;
    p->next = S;
    S = p;
    return true;
}
bool Pop(LiStack &S, ElemType &x) {
    if (S == NULL) return false;
    LiStack p = S;
    x = p->data;
    S = p->next;
    free(p);
    return true;
}

typedef struct LinkNode {
    ElemType data;
    struct LinkNode *next;
} LinkNode;
typedef struct {
    LinkNode *front, *rear;
} LinkQueue;
void InitQueue(LinkQueue &Q) {
    Q.front = Q.rear = (LinkNode *)malloc(sizeof(LinkNode));
    Q.front->next = NULL;
}
bool IsEmpty(LinkQueue Q) { return Q.front == Q.rear; }
void EnQueue(LinkQueue &Q, ElemType x) {
    LinkNode *s = (LinkNode *)malloc(sizeof(LinkNode));
    s->data = x;
    s->next = NULL;
    Q.rear->next = s;
    Q.rear = s;
}
bool DeQueue(LinkQueue &Q, ElemType &x) {
    if (Q.front == Q.rear) return false;
    LinkNode *p = Q.front->next;
    x = p->data;
    Q.front->next = p->next;
    if (Q.rear == p) Q.rear = Q.front;
    free(p);
    return true;
}

}
#undef MaxSize
namespace nohead {
typedef int ElemType;
typedef struct LinkNode {
    ElemType data;
    struct LinkNode *next;
} LinkNode;
typedef struct {
    LinkNode *front, *rear;
} LinkQueue;
void InitQueue(LinkQueue &Q) {
    Q.front = Q.rear = NULL;
}
bool IsEmpty(LinkQueue Q) { return Q.front == NULL; }
void EnQueue(LinkQueue &Q, ElemType x) {
    LinkNode *s = (LinkNode *)malloc(sizeof(LinkNode));
    s->data = x;
    s->next = NULL;
    if (Q.front == NULL)
        Q.front = Q.rear = s;
    else {
        Q.rear->next = s;
        Q.rear = s;
    }
}
bool DeQueue(LinkQueue &Q, ElemType &x) {
    if (Q.front == NULL) return false;
    LinkNode *p = Q.front;
    x = p->data;
    Q.front = p->next;
    if (Q.rear == p) Q.rear = NULL;
    free(p);
    return true;
}

}
#undef MaxSize

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
  if(lqr.empty()){assert(lq.front==lq.rear);}
  if(nqr.empty()){assert(nq.front==NULL&&nq.rear==NULL);}
  checks+=5;
 }
 int out;while(linked::Pop(ls,out)){}while(linked::DeQueue(lq,out)){}free(lq.front);while(nohead::DeQueue(nq,out)){}
 std::cout<<checks<<" paired container operation rounds passed\n";
}
