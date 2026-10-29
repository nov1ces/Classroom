bool ListInsert(SqList &L, int i, int x) {
    if (i < 1 || i > L.length + 1
        || L.length == MaxSize) return false;
    for (int j = L.length; j >= i; --j)
        L.data[j] = L.data[j - 1];
    L.data[i - 1] = x;
    ++L.length;
    return true;
}
