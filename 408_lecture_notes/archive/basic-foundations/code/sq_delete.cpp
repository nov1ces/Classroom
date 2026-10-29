bool ListDelete(SqList &L, int i, int &x) {
    if (i < 1 || i > L.length) return false;
    x = L.data[i - 1];
    for (int j = i; j < L.length; ++j)
        L.data[j - 1] = L.data[j];
    --L.length;
    return true;
}
