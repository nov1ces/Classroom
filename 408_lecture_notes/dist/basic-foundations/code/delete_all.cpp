void DeleteAll(SqList &L, int x) {
    int k = 0;
    for (int j = 0; j < L.length; ++j)
        if (L.data[j] != x)
            L.data[k++] = L.data[j];
    L.length = k;
}
