// Matched BFS/DFS reachability benchmark
// Repository: https://github.com/tltmgnt/TruthAI-Benchmark-Lab
// Standalone C++17, offline, synthetic reference model.
// Build: c++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp_model/model.cpp -o model
// Run: ./model    (runs built-in assertions and prints a bounded demo result)
// Research-only: no trained AI, independent validation, external actions or approval.
#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
namespace model {
bool bfs_reachable(const std::vector<std::vector<int>>&g,int s,int t){std::queue<int>q;std::vector<bool>seen(g.size());q.push(s);seen[s]=true;while(!q.empty()){int u=q.front();q.pop();if(u==t)return true;for(int v:g[u])if(!seen[v]){seen[v]=true;q.push(v);}}return false;}
bool dfs_reachable(const std::vector<std::vector<int>>&g,int s,int t){std::vector<int> st={s};std::vector<bool>seen(g.size());while(!st.empty()){int u=st.back();st.pop_back();if(u==t)return true;if(seen[u])continue;seen[u]=true;for(int v:g[u])if(!seen[v])st.push_back(v);}return false;}
void demo(){std::vector<std::vector<int>> g={{1,2},{3},{3},{}};bool a=bfs_reachable(g,0,3),b=dfs_reachable(g,0,3);require(a&&b,"matched reachability");std::cout<<"bfs_reachable="<<a<<" dfs_reachable="<<b<<" performance_superiority_claim=0";}
} // namespace model
int main(){try{std::cout<<std::boolalpha;model::demo();std::cout<<'\n';return 0;}catch(const std::exception&e){std::cerr<<"model test failed: "<<e.what()<<'\n';return 1;}}
