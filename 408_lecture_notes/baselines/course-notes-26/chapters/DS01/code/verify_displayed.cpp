#include <cstdlib>
#include <cstdio>
#include <cassert>
#include <vector>
#include <deque>
#include <algorithm>
#include <random>
int func(int n) {
    int i=0, sum=0;
    while (sum<n) sum += ++i;
    return i;
}

bool maximum(int a[], int n, int &answer) {
    if (n <= 0) return false;
    int best = a[0];
    for (int i = 1; i < n; ++i)
        if (a[i] > best) best = a[i];
    answer = best;
    return true;
}

int main(){
 for(int n=0;n<10000;++n){int k=func(n);assert(k*(k+1)/2>=n);assert(k==0||(k-1)*k/2<n);}
 std::mt19937 g(2027); for(int n=0;n<1000;++n){std::vector<int>a(n);for(int&i:a)i=(int)(g()%20001)-10000;int ans=12345;bool ok=maximum(a.data(),n,ans);assert(ok==(n>0));if(n)assert(ans==*std::max_element(a.begin(),a.end()));else assert(ans==12345);}
 for(int n=1;n<10000;++n){int sum=0;for(int i=1;i<n;i*=2)for(int j=0;j<i;j++)sum++;int t=1;while(t<n)t*=2;assert(sum==t-1);}
 puts("DS01: 20999 checks passed");}
