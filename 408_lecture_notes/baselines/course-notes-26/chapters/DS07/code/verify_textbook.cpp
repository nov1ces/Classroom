#include <cstdlib>
#include <cassert>
#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
using ElemType=int;
std::vector<int> visited_values;
template<class T> void visit(T p){visited_values.push_back(p->data);}
typedef struct {
    ElemType *elem;
    int TableLen;
} SSTable;
int Search_Seq(SSTable ST, ElemType key) {
    ST.elem[0]=key;
    int i;
    for (i=ST.TableLen; ST.elem[i]!=key; --i) ;
    return i;
}

int Binary_Search(SSTable L, ElemType key) {
    int low=0, high=L.TableLen-1, mid;
    while (low<=high) {
        mid=(low+high)/2;
        if (L.elem[mid]==key) return mid;
        else if (L.elem[mid]>key) high=mid-1;
        else low=mid+1;
    }
    return -1;
}

typedef struct BSTNode {
    int key;
    struct BSTNode *lchild, *rchild;
} BSTNode, *BSTree;
BSTNode *BST_Search(BSTree T, int key) {
    while (T!=NULL && key!=T->key) {
        if (key<T->key) T=T->lchild;
        else T=T->rchild;
    }
    return T;
}
int BST_Insert(BSTree &T, int k) {
    if (T==NULL) {
        T=(BSTree)malloc(sizeof(BSTNode));
        T->key=k;
        T->lchild=T->rchild=NULL;
        return 1;
    } else if (k==T->key) return 0;
    else if (k<T->key) return BST_Insert(T->lchild,k);
    else return BST_Insert(T->rchild,k);
}
void Create_BST(BSTree &T, int str[], int n) {
    T=NULL;
    for (int i=0; i<n; ++i) BST_Insert(T,str[i]);
}

void R_Rotate(BSTree &p) {
    BSTNode *lc=p->lchild;
    p->lchild=lc->rchild;
    lc->rchild=p;
    p=lc;
}
void L_Rotate(BSTree &p) {
    BSTNode *rc=p->rchild;
    p->rchild=rc->lchild;
    rc->lchild=p;
    p=rc;
}

void clearBST(BSTree t){if(!t)return;clearBST(t->lchild);clearBST(t->rchild);free(t);}
int main(){
 std::mt19937 g(407);for(int n=0;n<100;++n){std::vector<int>a(n+1);for(int i=1;i<=n;++i)a[i]=i*2;SSTable t{a.data(),n};for(int k=-2;k<=2*n+2;++k){int r=Search_Seq(t,k);assert((r!=0)==(k>=2&&k<=2*n&&k%2==0));}std::vector<int>b(n);for(int i=0;i<n;++i)b[i]=i*2;SSTable v{b.data(),n};for(int k=-2;k<=2*n+2;++k){int r=Binary_Search(v,k);assert((r>=0)==(k>=0&&k<2*n&&k%2==0));}}
 BSTree t=NULL;int a[]={50,66,60,26,21,30,70,68};Create_BST(t,a,8);assert(BST_Search(t,68)->key==68);assert(BST_Search(t,100)==NULL);assert(BST_Insert(t,68)==0);int root=t->key;R_Rotate(t);assert(t->key==26);L_Rotate(t);assert(t->key==root);clearBST(t);
 std::cout<<"sentinel/empty/binary bounds, BST insertion and reference rotations passed\n";
}