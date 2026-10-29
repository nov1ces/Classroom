Node *LocateNode(Node *L, int x) {
    Node *p = L->next;
    while (p != nullptr && p->data != x)
        p = p->next;
    return p;
}
