#include <cassert>
#include <algorithm>
#include <iostream>
#define MAXV 8
typedef struct { int numVertices,numEdges;char VerticesList[MAXV];int Edge[MAXV][MAXV]; } MGraph;
int uniquely(MGraph G) {
    int n=G.numVertices, indeg[MAXV]={0};
    bool used[MAXV]={false};
    for (int u=0; u<n; ++u)
        for (int v=0; v<n; ++v)
            if (G.Edge[u][v]) ++indeg[v];
    for (int step=0; step<n; ++step) {
        int pick=-1;
        for (int v=0; v<n; ++v)
            if (!used[v] && indeg[v]==0) {
                if (pick!=-1) return 0; // 至少两个候选
                pick=v;
            }
        if (pick==-1) return 0;         // 剩余部分有环
        used[pick]=true;
        for (int v=0; v<n; ++v)
            if (G.Edge[pick][v]) --indeg[v];
    }
    return 1;
}
int main(){
 int cases=0;
 for(int n=0;n<=4;++n){
  const int bits=n*(n-1);
  for(int mask=0;mask<(1<<bits);++mask){
   MGraph g{};g.numVertices=n;int b=0;
   for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(u!=v)g.Edge[u][v]=(mask>>(b++))&1;
   int p[MAXV];for(int i=0;i<n;++i)p[i]=i;
   int ways=0;
   do{int pos[MAXV];for(int i=0;i<n;++i)pos[p[i]]=i;bool ok=true;
      for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(g.Edge[u][v]&&pos[u]>=pos[v])ok=false;
      ways+=ok;
   }while(std::next_permutation(p,p+n));
   assert(uniquely(g)==(ways==1));++cases;
  }
 }
 MGraph self{};self.numVertices=1;self.Edge[0][0]=1;assert(uniquely(self)==0);++cases;
 std::cout<<cases<<" exhaustive directed graph / empty / self-loop topology cases passed\n";
}
