#include <cstdlib>
#include <cstdio>
#include <cassert>
#include <vector>
#include <deque>
#include <algorithm>
#include <random>
int F(int n) {
    if (n<=3) return 1;
    return F(n-2)+F(n-4)+1;
}
int factorial(int n) {
    if (n == 0 || n == 1) return 1;
    else return n * factorial(n - 1);
}
int Fib(int n) {
    if (n == 0) return 0;
    else if (n == 1) return 1;
    else return Fib(n - 1) + Fib(n - 2);
}

namespace structures {
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

typedef struct {
    ElemType data[MaxSize];
    int top0, top1;
} ShStack;
void InitStack(ShStack &S) {
    S.top0 = -1;
    S.top1 = MaxSize;
}

bool bracketCheck(char str[], int length) {
    SqStack S;
    InitStack(S);
    for (int i = 0; i < length; ++i) {
        char c = str[i];
        if (c == '(' || c == '[' || c == '{') {
            if (!Push(S, c)) return false;
        } else if (c == ')' || c == ']' || c == '}') {
            ElemType x;
            if (!Pop(S, x)) return false;
            if ((c == ')' && x != '(') ||
                (c == ']' && x != '[') ||
                (c == '}' && x != '{')) return false;
        }
    }
    return StackEmpty(S);
}

}
namespace nohead {using structures::ElemType;using structures::LinkNode;using structures::LinkQueue;
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
bool reference(const std::vector<char>&a){std::vector<char>s;for(char c:a){if(c=='('||c=='['||c=='{')s.push_back(c);else{if(s.empty())return false;char x=s.back();s.pop_back();if((c==')'&&x!='(')||(c==']'&&x!='[')||(c=='}'&&x!='{'))return false;}}return s.empty();}
int main(){using namespace structures;std::mt19937 g(2027);SqStack s;InitStack(s);std::vector<int>v;int x;for(int z=0;z<20000;++z){if(g()%2){int t=g()%100;bool ok=v.size()<100;assert(Push(s,t)==ok);if(ok)v.push_back(t);}else{bool ok=!v.empty();x=-999;assert(Pop(s,x)==ok);if(ok){assert(x==v.back());v.pop_back();}else assert(x==-999);}assert(StackEmpty(s)==v.empty());if(!v.empty()){assert(GetTop(s,x));assert(x==v.back());}}
 SqQueue q;InitQueue(q);std::deque<int>d;for(int z=0;z<20000;++z){if(g()%2){int t=g()%100;bool ok=d.size()<99;assert(EnQueue(q,t)==ok);if(ok)d.push_back(t);}else{bool ok=!d.empty();assert(DeQueue(q,x)==ok);if(ok){assert(x==d.front());d.pop_front();}}assert(QueueEmpty(q)==d.empty());assert((q.rear-q.front+100)%100==(int)d.size());}
 LiStack ls=NULL;v.clear();for(int z=0;z<10000;++z){if(g()%2){int t=g()%100;assert(Push(ls,t));v.push_back(t);}else{bool ok=!v.empty();assert(Pop(ls,x)==ok);if(ok){assert(x==v.back());v.pop_back();}}}while(Pop(ls,x)){}
 LinkQueue lq;InitQueue(lq);d.clear();for(int z=0;z<10000;++z){if(g()%2){int t=g()%100;EnQueue(lq,t);d.push_back(t);}else{bool ok=!d.empty();assert(DeQueue(lq,x)==ok);if(ok){assert(x==d.front());d.pop_front();}}assert((lq.front==lq.rear)==d.empty());}while(DeQueue(lq,x)){}assert(lq.rear==lq.front);free(lq.front);
 const char alphabet[]="()[]{}";for(int z=0;z<10000;++z){std::vector<char>a(g()%70);for(char &c:a)c=alphabet[g()%6];assert(bracketCheck(a.data(),(int)a.size())==reference(a));}

 {nohead::LinkQueue q;nohead::InitQueue(q);std::deque<int> ref;for(int z=0;z<15000;++z){if(g()%2){int t=g()%101;nohead::EnQueue(q,t);ref.push_back(t);}else{bool ok=!ref.empty();assert(nohead::DeQueue(q,x)==ok);if(ok){assert(x==ref.front());ref.pop_front();}}assert(nohead::IsEmpty(q)==ref.empty());if(ref.empty())assert(q.front==NULL&&q.rear==NULL);}while(nohead::DeQueue(q,x)){}assert(q.front==NULL&&q.rear==NULL);}
 int fact=1;for(int n=0;n<=12;++n){if(n)fact*=n;assert(factorial(n)==fact);}int a=0,b=1;for(int n=0;n<=20;++n){assert(Fib(n)==a);int c=a+b;a=b;b=c;}
 ShStack sh;InitStack(sh);assert(sh.top0==-1&&sh.top1==MaxSize);

 puts("DS03: 75000 random structure operations + 10000 bracket comparisons + factorial/Fibonacci/shared-state checks passed");}
