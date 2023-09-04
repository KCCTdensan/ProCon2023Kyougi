#include "../include/solveList2.h"

vector<Solver> solveList;

void makeList()
{
    solveList.push_back(Solver("solve1", solve1));
    solveList.push_back(Solver("solve2", solve2));
}