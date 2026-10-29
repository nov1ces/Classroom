#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>
constexpr int MaxSize = 100;
struct SqList {
    int data[MaxSize];
    int length = 0;
};

int LocateElem(const SqList &L, int x) {
    for (int j = 0; j < L.length; ++j)
        if (L.data[j] == x) return j + 1;
    return 0;
}

bool ListInsert(SqList &L, int i, int x) {
    if (i < 1 || i > L.length + 1
        || L.length == MaxSize) return false;
    for (int j = L.length; j >= i; --j)
        L.data[j] = L.data[j - 1];
    L.data[i - 1] = x;
    ++L.length;
    return true;
}

bool ListDelete(SqList &L, int i, int &x) {
    if (i < 1 || i > L.length) return false;
    x = L.data[i - 1];
    for (int j = i; j < L.length; ++j)
        L.data[j - 1] = L.data[j];
    --L.length;
    return true;
}
struct Node {
    int data;
    Node *next;
};
Node *GetElem(Node *L, int i) {
    if (i < 0) return nullptr;
    Node *p = L;
    for (int j = 0; p != nullptr && j < i; ++j)
        p = p->next;
    return p;
}

Node *LocateNode(Node *L, int x) {
    Node *p = L->next;
    while (p != nullptr && p->data != x)
        p = p->next;
    return p;
}

bool LinkedInsert(Node *L, int i, int x) {
    if (i < 1) return false;
    Node *p = GetElem(L, i - 1);
    if (p == nullptr) return false;
    Node *s = new Node{x, p->next};
    p->next = s;
    return true;
}

bool LinkedDelete(Node *L, int i, int &x) {
    if (i < 1) return false;
    Node *p = GetElem(L, i - 1);
    if (p == nullptr || p->next == nullptr)
        return false;
    Node *q = p->next;
    x = q->data;
    p->next = q->next;
    delete q;
    return true;
}

void BuildHead(Node *L, const int A[], int n) {
    for (int j = 0; j < n; ++j) {
        Node *s = new Node{A[j], L->next};
        L->next = s;
    }
}

void BuildTail(Node *L, const int A[], int n) {
    Node *rear = L;
    for (int j = 0; j < n; ++j) {
        Node *s = new Node{A[j], nullptr};
        rear->next = s;
        rear = s;
    }
}

void Destroy(Node *&L) {
    while (L != nullptr) {
        Node *q = L;
        L = L->next;
        delete q;
    }
}

struct DNode {
    int data;
    DNode *prior, *next;
};
// p has a valid predecessor; s is a new node.
void InsertBefore(DNode *p, DNode *s) {
    s->prior = p->prior;
    s->next = p;
    p->prior->next = s;
    p->prior = s;
}

void DeleteAll(SqList &L, int x) {
    int k = 0;
    for (int j = 0; j < L.length; ++j)
        if (L.data[j] != x)
            L.data[k++] = L.data[j];
    L.length = k;
}

void Reverse(Node *L) {
    Node *prev = nullptr, *cur = L->next;
    while (cur != nullptr) {
        Node *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    L->next = prev;
}

std::vector<int> vals(Node *L) {
    std::vector<int> a;
    for (Node *p=L->next;p;p=p->next) {
        assert(a.size()<200);
        a.push_back(p->data);
    }
    return a;
}
int main() {
    std::mt19937 rng(40802);
    SqList S;
    std::vector<int> a;
    Node *L=new Node{0,nullptr};
    for (int step=0;step<10000;++step) {
        int i=int(rng()%(a.size()+4))-1;
        if(rng()%2==0) {
            int x=int(rng()%9);
            bool legal=i>=1 && i<=int(a.size())+1 && a.size()<MaxSize;
            bool got=ListInsert(S,i,x);
            bool linked;
            if (a.size()==MaxSize && i>=1 && i<=int(a.size())+1)
                linked=LinkedInsert(L,-1,x);
            else linked=LinkedInsert(L,i,x);
            assert(got==legal && linked==legal);
            if(legal)a.insert(a.begin()+i-1,x);
        } else {
            int x=-999,y=-999;
            bool legal=i>=1 && i<=int(a.size());
            assert(ListDelete(S,i,x)==legal);
            assert(LinkedDelete(L,i,y)==legal);
            assert(x==y);
            if(legal){assert(x==a[i-1]);a.erase(a.begin()+i-1);}
        }
        assert(std::vector<int>(S.data,S.data+S.length)==a);
        assert(vals(L)==a);
        assert(GetElem(L,0)==L);
        assert(GetElem(L,-1)==nullptr);
        assert(GetElem(L,int(a.size())+1)==nullptr);
        for(int x=0;x<10;++x) {
            auto it=std::find(a.begin(),a.end(),x);
            int pos=it==a.end()?0:int(it-a.begin())+1;
            assert(LocateElem(S,x)==pos);
            Node *p=LocateNode(L,x);
            assert((p!=nullptr)==(pos!=0));
            if(p)assert(p==GetElem(L,pos));
        }
    }
    Destroy(L);assert(L==nullptr);
    for(int trial=0;trial<500;++trial) {
        int n=int(rng()%60);
        std::vector<int>b(n);
        for(int &x:b)x=int(rng()%7);
        for(int mode=0;mode<2;++mode) {
            L=new Node{0,nullptr};
            if(mode==0)BuildHead(L,b.data(),n);
            else BuildTail(L,b.data(),n);
            auto want=b;
            if(mode==0)std::reverse(want.begin(),want.end());
            assert(vals(L)==want);
            std::vector<Node*> nodes;
            for(Node*p=L->next;p;p=p->next)nodes.push_back(p);
            Reverse(L);std::reverse(want.begin(),want.end());
            assert(vals(L)==want);
            Node*p=L->next;
            for(auto it=nodes.rbegin();it!=nodes.rend();++it){assert(p==*it);p=p->next;}
            Destroy(L);assert(L==nullptr);
        }
        SqList T;T.length=n;std::copy(b.begin(),b.end(),T.data);
        int x=int(rng()%7);DeleteAll(T,x);
        b.erase(std::remove(b.begin(),b.end(),x),b.end());
        assert(std::vector<int>(T.data,T.data+T.length)==b);
    }
    DNode h{0,nullptr,nullptr},p{1,&h,nullptr},s{2,nullptr,nullptr};
    h.next=&p;InsertBefore(&p,&s);
    assert(h.next==&s && s.prior==&h && s.next==&p && p.prior==&s);
    std::cout<<"PASS: exact PDF code; 10000 paired list/array operations; 500 construction/reversal trials; empty/boundary and double-link checks.\n";
}
