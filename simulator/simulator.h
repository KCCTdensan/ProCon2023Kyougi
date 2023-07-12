#pragma once

#include <chrono>
#include <vector>

#define debugPrint false
#if(debugPrint == true)
  #define _printAll printAll()
#else
  #define _printAll 
#endif

using namespace std;
using namespace std::chrono;

#define Movement pair<int, int>
// pair<type, direction>
//   type = 0(stay), 1(move), 2(build), 3(clear)
//   [type = 0]     direction = -1(stay)
//   [type = 1]     direction = 0(right) - 7(right-up)
//   [type = 2, 3]  direction = 0(right) - 3(up)
typedef enum 
{
	Right,
	Down,
	Left,
	Up,
	RightDown,
	LeftDown,
	LeftUp,
	RightUp,
} Direction;
#define Pos pair<int, int> //r, c
struct Person{
    Pos pos;
    vector<Movement> movement; //history
};

#define solveDatas int, const vector<vector<int>>&, const vector<Person>&, const vector<Person>&, const system_clock::time_point&, const bool&, vector<Movement>&, int&

typedef void (* SolveFunction)(solveDatas);