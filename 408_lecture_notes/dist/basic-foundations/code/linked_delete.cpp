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
