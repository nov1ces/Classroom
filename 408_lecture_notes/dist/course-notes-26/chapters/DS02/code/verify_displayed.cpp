#include <cstdlib>
#include <cstdio>
#include <cassert>
#include <vector>
#include <deque>
#include <algorithm>
#include <random>
namespace seq {
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
namespace dynamic {typedef int ElemType;
#define InitSize 100
typedef struct {
    ElemType *data;
    int MaxSize;
    int length;
} SeqList;
void InitList(SeqList &L) {
    L.data = (ElemType *)malloc(InitSize * sizeof(ElemType));
    L.length = 0;
    L.MaxSize = InitSize;
}
void IncreaseSize(SeqList &L, int len) {
    ElemType *p = L.data;
    L.data = (ElemType *)malloc(
        (L.MaxSize + len) * sizeof(ElemType));
    for (int i = 0; i < L.length; ++i)
        L.data[i] = p[i];
    L.MaxSize += len;
    free(p);
}

}
namespace link {typedef int ElemType;
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

void reverseList(LNode *L) {       // 带头结点
    LNode *prev=NULL, *cur=L->next;
    while (cur!=NULL) {
        LNode *nxt=cur->next;
        cur->next=prev;
        prev=cur;
        cur=nxt;
    }
    L->next=prev;
}

int searchK(LNode *list, int k) {
    if (k<=0) return 0;
    LNode *fast=list->next, *slow=list->next;
    for (int j=0; j<k; ++j) {
        if (fast==NULL) return 0;   // 表长不足 k
        fast=fast->next;
    }
    while (fast!=NULL) {
        fast=fast->next;
        slow=slow->next;
    }
    printf("%d", slow->data);
    return 1;
}

void reverse(int R[], int l, int r) {
    while (l<r) {
        int t=R[l]; R[l]=R[r]; R[r]=t;
        ++l; --r;
    }
}
void rotateLeft(int R[], int n, int p) {
    reverse(R,0,p-1);
    reverse(R,p,n-1);
    reverse(R,0,n-1);
}

LNode *commonSuffix(LNode *str1, LNode *str2) {
    int m=0,n=0;
    for (LNode *p=str1->next; p; p=p->next) ++m;
    for (LNode *q=str2->next; q; q=q->next) ++n;
    LNode *p=str1->next, *q=str2->next;
    while (m>n) { p=p->next; --m; }
    while (n>m) { q=q->next; --n; }
    while (p!=q) { p=p->next; q=q->next; }
    return p;                   // 无公共结点时二者同时为 NULL
}

int majority(int A[], int n) {
    int candidate=0, count=0;
    for (int i=0; i<n; ++i) {
        if (count==0) { candidate=A[i]; count=1; }
        else if (A[i]==candidate) ++count;
        else --count;
    }
    int actual=0;
    for (int i=0; i<n; ++i)
        if (A[i]==candidate) ++actual;
    return actual>n/2 ? candidate : -1;
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

bool ListInsert_NoHead(LinkList &L, int i, ElemType e) {
    if (i < 1) return false;
    if (i == 1) {
        LNode *s = (LNode *)malloc(sizeof(LNode));
        if (s == NULL) return false;
        s->data = e;
        s->next = L;
        L = s;
        return true;
    }
    LNode *p = L;
    int j = 1;
    while (p != NULL && j < i - 1) {
        p = p->next; ++j;
    }
    return InsertNextNode(p, e);
}

bool CreateList_Head(LinkList &L, ElemType a[], int n) {
    if (!InitList(L)) return false;
    for (int i = 0; i < n; ++i)
        if (!InsertNextNode(L, a[i])) return false;
    return true;
}
bool CreateList_Tail(LinkList &L, ElemType a[], int n) {
    if (!InitList(L)) return false;
    LNode *r = L;
    for (int i = 0; i < n; ++i) {
        if (!InsertNextNode(r, a[i])) return false;
        r = r->next;
    }
    return true;
}

typedef struct DNode {
    ElemType data;
    struct DNode *prior, *next;
} DNode, *DLinklist;
bool InsertNextDNode(DNode *p, DNode *s) {
    if (p == NULL || s == NULL) return false;
    s->next = p->next;
    if (p->next != NULL) p->next->prior = s;
    s->prior = p;
    p->next = s;
    return true;
}
bool DeleteNextDNode(DNode *p) {
    if (p == NULL || p->next == NULL) return false;
    DNode *q = p->next;
    p->next = q->next;
    if (q->next != NULL) q->next->prior = p;
    free(q);
    return true;
}

void eraseAll(LNode* L, int x) {
    LNode* p = L;
    while (p->next != NULL) {
        if (p->next->data == x) {
            LNode* q = p->next;
            p->next = q->next;
            free(q);
        } else {
            p = p->next;
        }
    }
}

}

void release(link::LinkList &l){while(l){link::LNode*p=l->next;free(l);l=p;}}
std::vector<int> values(link::LinkList l){std::vector<int>r;for(l=l->next;l;l=l->next)r.push_back(l->data);return r;}

std::vector<int> input_data; std::size_t input_pos=0;
int textbook_scanf(const char *, int *out) {
    if (input_pos == input_data.size()) return EOF;
    *out = input_data[input_pos++]; return 1;
}
#define scanf textbook_scanf
namespace textbook_input {
using link::LNode; using link::LinkList;
LinkList List_HeadInsert(LinkList &L) {
    LNode *s;
    int x;
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL;
    scanf("%d", &x);
    while (x != 9999) {
        s = (LNode *)malloc(sizeof(LNode));
        s->data = x;
        s->next = L->next;
        L->next = s;
        scanf("%d", &x);
    }
    return L;
}
LinkList List_TailInsert(LinkList &L) {
    int x;
    L = (LinkList)malloc(sizeof(LNode));
    LNode *s, *r = L;
    scanf("%d", &x);
    while (x != 9999) {
        s = (LNode *)malloc(sizeof(LNode));
        s->data = x;
        r->next = s;
        r = s;
        scanf("%d", &x);
    }
    r->next = NULL;
    return L;
}
}
#undef scanf

int main(){
 std::mt19937 g(2027); seq::SqList s;seq::InitList(s);std::vector<int>v;int e;
 for(int z=0;z<30000;++z){if(g()%2){int i=(int)(g()%(v.size()+3));int x=g()%101;bool expected=i>=1&&i<=(int)v.size()+1&&v.size()<100;assert(seq::ListInsert(s,i,x)==expected);if(expected)v.insert(v.begin()+i-1,x);}else{int i=(int)(g()%(v.size()+2));bool expected=i>=1&&i<=(int)v.size();e=-999;assert(seq::ListDelete(s,i,e)==expected);if(expected){assert(e==v[i-1]);v.erase(v.begin()+i-1);}else assert(e==-999);}assert(s.length==(int)v.size());for(int i=0;i<s.length;++i)assert(s.data[i]==v[i]);}
 dynamic::SeqList d;dynamic::InitList(d);assert(d.data!=NULL);d.length=5;for(int i=0;i<5;++i)d.data[i]=i*i;dynamic::IncreaseSize(d,7);assert(d.MaxSize==107);for(int i=0;i<5;++i)assert(d.data[i]==i*i);free(d.data);
 for(int n=0;n<200;++n){std::vector<int>a(n);for(int&i:a)i=(int)(g()%7);link::LinkList l;assert(link::CreateList_Tail(l,a.data(),n));assert(values(l)==a);assert(link::GetElem(l,0)==l);assert(link::GetElem(l,n+1)==NULL);for(int k=1;k<=n;++k)assert(link::GetElem(l,k)->data==a[k-1]);link::reverseList(l);std::reverse(a.begin(),a.end());assert(values(l)==a);link::eraseAll(l,3);a.erase(std::remove(a.begin(),a.end(),3),a.end());assert(values(l)==a);release(l);
 assert(link::CreateList_Head(l,a.data(),(int)a.size()));std::reverse(a.begin(),a.end());assert(values(l)==a);release(l);}
 link::LinkList l;assert(link::InitList(l));v.clear();for(int z=0;z<10000;++z){if(g()%2){int i=(int)(g()%(v.size()+3));int x=g()%100;bool expected=i>=1&&i<=(int)v.size()+1;assert(link::ListInsert(l,i,x)==expected);if(expected)v.insert(v.begin()+i-1,x);}else{int i=(int)(g()%(v.size()+2));bool expected=i>=1&&i<=(int)v.size();e=-999;assert(link::ListDelete(l,i,e)==expected);if(expected){assert(e==v[i-1]);v.erase(v.begin()+i-1);}else assert(e==-999);}assert(values(l)==v);}release(l);
 link::LinkList no=NULL;assert(link::ListInsert_NoHead(no,1,4));assert(link::ListInsert_NoHead(no,2,7));assert(no->data==4&&no->next->data==7);release(no);
 for(int n=1;n<100;++n){std::vector<int>a(n);for(int i=0;i<n;++i)a[i]=i;for(int k=1;k<n;++k){auto b=a;link::rotateLeft(b.data(),n,k);auto c=a;std::rotate(c.begin(),c.begin()+k,c.end());assert(b==c);}}
 for(int n=0;n<100;++n){std::vector<int>a(n);for(int&i:a)i=g()%5;int want=-1;for(int x=0;x<5;++x)if(std::count(a.begin(),a.end(),x)>n/2)want=x;assert(link::majority(a.data(),n)==want);}
 link::DNode *h=(link::DNode*)malloc(sizeof(link::DNode));h->next=NULL;h->prior=NULL;auto*q=(link::DNode*)malloc(sizeof(link::DNode));assert(link::InsertNextDNode(h,q));assert(h->next==q&&q->prior==h&&q->next==NULL);assert(link::DeleteNextDNode(h));assert(h->next==NULL);free(h);
 for(int n=0;n<50;++n){ input_data.clear();for(int i=0;i<n;++i)input_data.push_back(i+1);input_data.push_back(9999);input_pos=0;link::LinkList l=NULL;assert(textbook_input::List_TailInsert(l)==l);std::vector<int>want(input_data.begin(),input_data.end()-1);assert(values(l)==want);release(l);input_pos=0;assert(textbook_input::List_HeadInsert(l)==l);std::reverse(want.begin(),want.end());assert(values(l)==want);release(l);}
 puts("DS02: static 30000 + linked 10000 random operations, 200 build/reverse/filter groups, all rotations n<100 + 100 textbook interactive head/tail builds passed");}
