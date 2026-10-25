void BuildTail(Node *L, const int A[], int n) {
    Node *rear = L;
    for (int j = 0; j < n; ++j) {
        Node *s = new Node{A[j], nullptr};
        rear->next = s;
        rear = s;
    }
}
