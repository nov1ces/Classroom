void BuildHead(Node *L, const int A[], int n) {
    for (int j = 0; j < n; ++j) {
        Node *s = new Node{A[j], L->next};
        L->next = s;
    }
}
