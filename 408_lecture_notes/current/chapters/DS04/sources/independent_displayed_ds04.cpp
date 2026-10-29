#define MAXLEN 255
typedef struct {
    char ch[MAXLEN];
    int length;
} SString;

bool SubString(SString &Sub, SString S, int pos, int len) {
    if (pos < 1 || pos > S.length + 1 || len < 0 ||
        len > S.length - pos + 1)
        return false;
    for (int i = pos; i < pos + len; ++i)
        Sub.ch[i - pos + 1] = S.ch[i];
    Sub.length = len;
    return true;
}
int StrCompare(SString S, SString T) {
    for (int i = 1; i <= S.length && i <= T.length; ++i)
        if (S.ch[i] != T.ch[i])
            return (unsigned char)S.ch[i] -
                   (unsigned char)T.ch[i];
    return S.length - T.length;
}

bool Concat(SString &T, SString S1, SString S2) {
    if (S1.length + S2.length >= MAXLEN) return false;
    for (int i = 1; i <= S1.length; ++i)
        T.ch[i] = S1.ch[i];
    for (int i = 1; i <= S2.length; ++i)
        T.ch[S1.length + i] = S2.ch[i];
    T.length = S1.length + S2.length;
    return true;
}

int Index(SString S, SString T) {
    if (T.length == 0) return 1;
    int i = 1, j = 1;
    while (i <= S.length && j <= T.length) {
        if (S.ch[i] == T.ch[j]) {
            ++i; ++j;
        } else {
            i = i - j + 2;
            j = 1;
        }
    }
    if (j > T.length) return i - T.length;
    return 0;
}

int Index_KMP(SString S, SString T, int next[]) {
    if (T.length == 0) return 1;
    int i = 1, j = 1;
    while (i <= S.length && j <= T.length) {
        if (j == 0 || S.ch[i] == T.ch[j]) {
            ++i;
            ++j;
        } else {
            j = next[j];
        }
    }
    if (j > T.length) return i - T.length;
    return 0;
}

void get_next(SString T, int next[]) {
    if (T.length == 0) return;
    int i = 1, j = 0;
    next[1] = 0;
    while (i < T.length) {
        if (j == 0 || T.ch[i] == T.ch[j]) {
            ++i; ++j;
            next[i] = j;
        } else {
            j = next[j];
        }
    }
}

void get_nextval(SString T, int nextval[]) {
    if (T.length == 0) return;
    int i = 1, j = 0;
    nextval[1] = 0;
    while (i < T.length) {
        if (j == 0 || T.ch[i] == T.ch[j]) {
            ++i; ++j;
            if (T.ch[i] != T.ch[j])
                nextval[i] = j;
            else
                nextval[i] = nextval[j];
        } else {
            j = nextval[j];
        }
    }
}

#include <string>
#include <vector>
#include <cassert>
#include <iostream>
SString pack(std::string a){SString s{};s.length=a.size();for(int i=1;i<=s.length;i++)s.ch[i]=a[i-1];return s;}
int main(){
 std::vector<std::string> a(1,"");
 for(int n=1;n<=7;n++)for(int v=0;v<(1<<n);v++){std::string s;for(int j=0;j<n;j++)s+=((v>>j)&1)?'a':'b';a.push_back(s);}
 int count=0;
 for(auto s:a)for(auto t:a){
  auto S=pack(s),T=pack(t);int ne[MAXLEN]{},nv[MAXLEN]{};get_next(T,ne);get_nextval(T,nv);
  for(int j=2;j<=T.length;j++){int l=0;auto pre=t.substr(0,j-1);for(int k=1;k<j-1;k++)if(pre.substr(0,k)==pre.substr(pre.size()-k))l=k;assert(ne[j]==l+1);assert(nv[j]==(t[j-1]!=t[ne[j]-1]?ne[j]:nv[ne[j]]));}
  auto at=s.find(t);int expected=at==std::string::npos?0:at+1;
  assert(Index(S,T)==expected);assert(Index_KMP(S,T,ne)==expected);assert(Index_KMP(S,T,nv)==expected);
  SString out{};assert(Concat(out,S,T));assert(out.length==int(s.size()+t.size()));
  for(int pos=0;pos<=int(s.size())+2;pos++)for(int len=-1;len<=int(s.size())+1;len++)assert(SubString(out,S,pos,len)==(pos>=1&&pos<=int(s.size())+1&&len>=0&&len<=int(s.size())-pos+1));
  ++count;
 }
 auto big=pack(std::string(MAXLEN-1,'x'));int ne[MAXLEN],nv[MAXLEN];get_next(big,ne);get_nextval(big,nv);assert(Index_KMP(big,big,nv)==1);SString out;assert(!Concat(out,big,pack("y")));
 std::cout<<count<<" pattern pairs; substring boundaries and maximum declared capacity passed\n";
}
