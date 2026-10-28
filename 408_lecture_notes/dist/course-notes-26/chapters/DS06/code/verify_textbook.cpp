#include <cstdlib>
#include <cassert>
#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
using ElemType=int;
std::vector<int> visited_values;
template<class T> void visit(T p){visited_values.push_back(p->data);}
using VertexType=int;using EdgeType=int;
#define MaxVertexNum 100
typedef struct {
    VertexType Vex[MaxVertexNum];
    EdgeType Edge[MaxVertexNum][MaxVertexNum];
    int vexnum, arcnum;
} MGraph;

typedef struct ArcNode {
    int adjvex;
    struct ArcNode *next;
    // 带权图在此补充权值域
} ArcNode;
typedef struct VNode {
    VertexType data;
    ArcNode *first;
} VNode, AdjList[MaxVertexNum];
typedef struct {
    AdjList vertices;
    int vexnum, arcnum;
} ALGraph;
using Graph=MGraph;
int FirstNeighbor(Graph G,int v){for(int w=0;w<G.vexnum;++w)if(G.Edge[v][w])return w;return -1;}
int NextNeighbor(Graph G,int v,int old){for(int w=old+1;w<G.vexnum;++w)if(G.Edge[v][w])return w;return -1;}
void visit(int v){visited_values.push_back(v);}
struct SqQueue{int data[MaxVertexNum+1];int front,rear;};
void InitQueue(SqQueue &q){q.front=q.rear=0;}
bool QueueEmpty(SqQueue q){return q.front==q.rear;}
void EnQueue(SqQueue &q,int x){int nr=(q.rear+1)%(MaxVertexNum+1);assert(nr!=q.front);q.data[q.rear]=x;q.rear=nr;}
void DeQueue(SqQueue &q,int &x){assert(!QueueEmpty(q));x=q.data[q.front];q.front=(q.front+1)%(MaxVertexNum+1);}

bool visited[MaxVertexNum];
void DFS(Graph G, int v) {
    visit(v);
    visited[v]=true;
    for (int w=FirstNeighbor(G,v); w>=0;
         w=NextNeighbor(G,v,w))
        if (!visited[w]) DFS(G,w);
}
void DFSTraverse(Graph G) {
    for (int v=0; v<G.vexnum; ++v) visited[v]=false;
    for (int v=0; v<G.vexnum; ++v)
        if (!visited[v]) DFS(G,v);
}
void BFS(Graph G, int v) {
    SqQueue Q;
    InitQueue(Q);
    visit(v);
    visited[v]=true;
    EnQueue(Q,v);
    while (!QueueEmpty(Q)) {
        DeQueue(Q,v);
        for (int w=FirstNeighbor(G,v); w>=0;
             w=NextNeighbor(G,v,w)) {
            if (!visited[w]) {
                visit(w);
                visited[w]=true;
                EnQueue(Q,w);
            }
        }
    }
}
void BFSTraverse(Graph G) {
    for (int v=0; v<G.vexnum; ++v) visited[v]=false;
    for (int v=0; v<G.vexnum; ++v)
        if (!visited[v]) BFS(G,v);
}

int main(){Graph G{};G.vexnum=6;int edges[][2]={{0,1},{0,2},{0,4},{1,4},{2,5},{3,5},{3,4}};for(auto &e:edges)G.Edge[e[0]][e[1]]=G.Edge[e[1]][e[0]]=1;
 DFSTraverse(G);assert((visited_values==std::vector<int>{0,1,4,3,5,2}));visited_values.clear();BFSTraverse(G);assert((visited_values==std::vector<int>{0,1,2,4,5,3}));
 Graph D{};D.vexnum=5;D.Edge[0][1]=1;D.Edge[1][2]=1;D.Edge[2][0]=1;visited_values.clear();BFSTraverse(D);assert(visited_values.size()==5);
 std::cout<<"DFS/BFS order, cycles, disconnected and directed traversal passed\n";
}