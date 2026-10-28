from pathlib import Path
import re,subprocess,json,hashlib
ch=Path(__file__).resolve().parents[1]
text=(ch/'content.md').read_text()
body=re.search(r'```c\n(int uniquely\(MGraph G\).*?)\n```',text,re.S).group(1)
source='''#include <cassert>
#include <algorithm>
#include <iostream>
#define MAXV 8
typedef struct { int numVertices,numEdges;char VerticesList[MAXV];int Edge[MAXV][MAXV]; } MGraph;
'''+body+'''
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
 std::cout<<cases<<" exhaustive directed graph / empty / self-loop topology cases passed\\n";
}
'''
p=ch/'code/verify_unique_topology.cpp';p.write_text(source)
exe=Path('/workspace/scratch/ds-finish-review/verify_unique_topology')
cmd=['g++','-std=c++11','-Wall','-Wextra','-Wpedantic','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(p),'-o',str(exe)]
subprocess.run(cmd,check=True)
r=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
(ch/'sources/unique_topology_verification.json').write_text(json.dumps({'source':'Displayed uniquely function extracted verbatim; separate type and permutation oracle','displayed_function_sha256':hashlib.sha256(body.encode()).hexdigest(),'output':r.stdout,'exit_code':r.returncode,'flags':cmd[1:8]},ensure_ascii=False,indent=2));print(r.stdout)
