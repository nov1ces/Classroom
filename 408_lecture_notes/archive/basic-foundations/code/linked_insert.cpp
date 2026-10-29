bool LinkedInsert(Node *L, int i, int x) {
    if (i < 1) return false;
    Node *p = GetElem(L, i - 1);
    if (p == nullptr) return false;
    Node *s = new Node{x, p->next};
    p->next = s;
    return true;
}
