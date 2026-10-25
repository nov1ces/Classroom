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
