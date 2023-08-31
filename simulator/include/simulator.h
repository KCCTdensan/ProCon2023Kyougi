#pragma once

#include <chrono>
#include <vector>
#include <iostream>
#include <queue>
#include <set>
#include <map>
#include <unordered_set>
#include <unordered_map>
#include <string>

#define debugPrint false
#if (debugPrint == true)
#define _printAll printAll()
#else
#define _printAll
#endif

using namespace std;
using namespace std::chrono;

#define Movement pair<int, int>
// pair<type, direction>
//   type = 0(stay), 1(move), 2(build), 3(clear)
//   [type = 0]     direction = 0(stay)
//   [type = 1]     direction = 1(right) - 8(right-up)
//   [type = 2, 3]  direction = 2(up), 4(right), 6(down), 8(left)
typedef enum {
    NoDirection,
    LeftUp,
    Up,
    RightUp,
    Right,
    RightDown,
    Down,
    LeftDown,
    Left,
} Direction;
#define Pos pair<int, int> // r, c
struct Person {
    Pos pos;
    vector<Movement> movement; // history
};

#define solveDatas int, const vector<vector<int>>&, const vector<Person>&, const vector<Person>&, const system_clock::time_point&, const bool&, vector<Movement>&, int&

typedef void (*SolveFunction)(solveDatas);

extern int height, width;

pair<int, int> personFind(Pos pos);
extern vector<vector<int>> directionSet;
extern vector<vector<int>> fourDirection;