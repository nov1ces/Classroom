int sum = 0;
for (int i = 1; i < n; i *= 2)
    for (int j = 0; j < i; ++j)
        ++sum;
