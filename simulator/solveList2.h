#include "simulator.h"
#include "solveList.h"
vector<SolveFunction> solveList(0);
void makeList(){
    solveList.push_back(solve1);
    solveList.push_back(solve2);
}