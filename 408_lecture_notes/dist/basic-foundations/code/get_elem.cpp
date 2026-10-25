Node *GetElem(Node *L, int i) {
    if (i < 0) return nullptr;
    Node *p = L;
    for (int j = 0; p != nullptr && j < i; ++j)
        p = p->next;
    return p;
}
