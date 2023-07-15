#pragma once

#include "simulator.h"
// field[r][c] = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)
// writeAble = 0(never or return answer), 1(writeAble), -1(wait)
void solve2(int requiredTime, const vector<vector<int>>& field, const vector<Person>& myPeople,
    const vector<Person>& enemyPeople, const system_clock::time_point& startTime,
    const bool& finishFlag, vector<Movement>& movements, int& writeAble);