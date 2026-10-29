#include <cassert>
#include <string>
#include <vector>
#include <iostream>
#include <random>
#include <algorithm>
#include "ds04_displayed.cpp"
SString make(const std::string &s) {SString a={};assert(s.size()<MAXLEN);a.length=static_cast<int>(s.size());for(int i=1;i<=a.length;i++)a.ch[i]=s[i-1];return a;}
std::vector<int> brute_next(const std::string &p){std::vector<int> out(p.size()+1);for(size_t j=2;j<=p.size();j++){std::string pre=p.substr(0,j-1);size_t best=0;for(size_t k=1;k<pre.size();k++)if(pre.substr(0,k)==pre.substr(pre.size()-k))best=k;out[j]=static_cast<int>(best+1);}return out;}
std::vector<int> brute_nextval(const std::string &p,const std::vector<int>&n){std::vector<int> out(p.size()+1);for(size_t j=2;j<=p.size();j++){int k=n[j];out[j]=(p[j-1]==p[k-1])?out[k]:k;}return out;}
long countcheck=0;
void one(const std::string&s,const std::string&p){SString S=make(s),T=make(p);int n[MAXLEN]={},v[MAXLEN]={};get_next(T,n);get_nextval(T,v);std::vector<int>bn=brute_next(p),bv=brute_nextval(p,bn);for(size_t j=1;j<=p.size();j++){assert(n[j]==bn[j]);assert(v[j]==bv[j]);}size_t z=s.find(p);int expected=z==std::string::npos?0:static_cast<int>(z+1);assert(Index(S,T)==expected);assert(Index_KMP(S,T,n)==expected);assert(Index_KMP(S,T,v)==expected);countcheck++;}
int main(){std::vector<std::string>cases;for(int n=0;n<=7;n++)for(int x=0;x<(1<<n);x++){std::string s;for(int i=0;i<n;i++)s+=(x&(1<<i))?'a':'b';cases.push_back(s);}for(auto&s:cases)for(auto&p:cases)one(s,p);
std::mt19937 rng(20261026);for(int t=0;t<10000;t++){std::string a(rng()%80,'a'),b(rng()%30,'a');for(char&c:a)c='a'+rng()%4;for(char&c:b)c='a'+rng()%4;one(a,b);}one(std::string(MAXLEN-1,'a'),std::string(MAXLEN-1,'a'));one("abaabaabcabaabc","abaabc");one("googlogoogoogle","google");one("aaacaaaabdaaaab","aaaab");
SString a=make("abcdefg"),t=make("old");assert(SubString(t,a,8,0)&&t.length==0);t=make("old");assert(!SubString(t,a,9,0)&&t.length==3);assert(!SubString(t,a,0,1));assert(!SubString(t,a,7,2));assert(SubString(t,a,6,2)&&t.ch[1]=='f'&&t.ch[2]=='g');assert(Concat(a,a,make("h"))&&a.length==8&&a.ch[8]=='h');assert(StrCompare(make("a"),make("b"))<0);assert(StrCompare(make("aa"),make("a"))>0);std::cout<<"{\"actual_code_match_cases\":"<<countcheck<<",\"status\":\"pass\"}\n";}
