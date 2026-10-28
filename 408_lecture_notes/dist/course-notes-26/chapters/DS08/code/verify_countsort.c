#include <assert.h>
#include <stdio.h>
void CountSort(int A[], int B[], int n, int k) {
    int i, C[k];
    for (i=0; i<k; ++i) C[i]=0;
    for (i=0; i<n; ++i) ++C[A[i]];
    for (i=1; i<k; ++i) C[i]+=C[i-1];
    for (i=n-1; i>=0; --i) {
        --C[A[i]];
        B[C[A[i]]]=A[i];
    }
}
int main(void){int A[]={4,2,2,0,3,1,4,0};int B[8];CountSort(A,B,8,5);int E[]={0,0,1,2,2,3,4,4};for(int i=0;i<8;++i)assert(B[i]==E[i]);CountSort(A,B,0,5);puts("C11 CountSort boundaries and duplicate keys passed");}
