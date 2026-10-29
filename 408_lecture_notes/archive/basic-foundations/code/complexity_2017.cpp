int func(int n) {
    int i = 0, sum = 0;
    while (sum < n) sum += ++i;
    return i;
}
