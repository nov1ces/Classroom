int LocateElem(const SqList &L, int x) {
    for (int j = 0; j < L.length; ++j)
        if (L.data[j] == x) return j + 1;
    return 0;
}
