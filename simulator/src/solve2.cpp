#include "../include/solve2.h"

void solve2(int requiredTime, const vector<vector<int>>& field, const vector<Person>& myPeople,
    const vector<Person>& enemyPeople, const system_clock::time_point& startTime,
    const bool& finishFlag, vector<Movement>& movements, int& writeAble)
{
    while (true) {
        while (writeAble != 1 && !finishFlag)
            ;
        if (finishFlag)
            break;
        movements = vector<Movement>(myPeople.size(), Movement(0, -1));
        writeAble = 0;
    }
}