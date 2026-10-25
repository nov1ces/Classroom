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
