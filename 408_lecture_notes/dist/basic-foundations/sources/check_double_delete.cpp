#include <cassert>
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

void CheckedDelete(DNode *p) {
p->prior->next = p->next;
p->next->prior = p->prior;
delete p;

}
int main(){DNode h{0,nullptr,nullptr},t{0,nullptr,nullptr}; DNode *p=new DNode{1,&h,&t}; h.next=p;t.prior=p; CheckedDelete(p);assert(h.next==&t && t.prior==&h);}
