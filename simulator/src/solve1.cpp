#include "../include/solve1.h"

void solve1(int requiredTime, const vector<vector<int>>& field, const vector<Person>& myPeople,
    const vector<Person>& enemyPeople, const system_clock::time_point& startTime, const bool& finishFlag,
    vector<Movement>& movements, int& writeAble)
{
    int commandI = -1;
    int commands[3] = { 2, 3, 1 };
    Direction right = Right;
    while (true) {
        while (writeAble != 1 && !finishFlag)
            ;
        if (finishFlag)
            break;
        commandI++;
        movements = vector<Movement>(myPeople.size(), Movement(commands[commandI % 3], right));
        writeAble = 0;
    }
}
