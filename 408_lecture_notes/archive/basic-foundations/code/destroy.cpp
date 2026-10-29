void Destroy(Node *&L) {
    while (L != nullptr) {
        Node *q = L;
        L = L->next;
        delete q;
    }
}
