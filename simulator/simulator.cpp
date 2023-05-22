#include <iostream>
#include <bits/stdc++.h>
#include <random>
#include <thread>
#include <chrono>

using namespace std;
using namespace std::chrono;

#define debugPrint false
#if(debugPrint == true)
  #define _printAll printAll()
#else
  #define _printAll 
#endif

#define Movement pair<int, int>
// pair<type, direction>
//   type = 0(stay), 1(move), 2(build), 3(clear)
//   [type = 0]     direction = -1(stay)
//   [type = 1]     direction = 0(right) - 7(right-up)
//   [type = 2, 3]  direction = 0(right) - 3(up)
#define Pos pair<int, int> //r, c
struct Person{
    Pos pos;
    vector<Movement> movement; //history
};

// field[r][c] = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)
// writeAble = 0(never or return answer), 1(writeAble), -1(wait)
void solve1(int requiredTime, vector<vector<int>>& field, vector<Person>& myPeople,
            vector<Person>& enemyPeople, vector<Movement>& movements,
            int& writeAble, system_clock::time_point& startTime,
            bool& finishFlag){
    int commandI = -1;
    int commands[3] = {2, 3, 1};
    while(true){
        while(writeAble != 1 && !finishFlag);
        if(finishFlag) break;
        commandI++;
        movements = vector<Movement>(myPeople.size(), Movement(commands[commandI%3], 0));
        writeAble = 0;
    }
}
// field[r][c] = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)
// writeAble = 0(never or return answer), 1(writeAble), -1(wait)
void solve2(int requiredTime, vector<vector<int>>& field, vector<Person>& myPeople,
            vector<Person>& enemyPeople, vector<Movement>& movements,
            int& writeAble, system_clock::time_point& startTime,
            bool& finishFlag){
    while(true){
        while(writeAble != 1 && !finishFlag);
        if(finishFlag) break;
        movements = vector<Movement>(myPeople.size(), Movement(0, -1));
        writeAble = 0;
    }
}

std::mt19937 randint;

int height, width;
vector<vector<bool>> originField;
vector<vector<int>> fieldData1;
vector<vector<int>> fieldData2;

int peopleLen;
vector<Person> people1;
vector<Person> people2;

pair<int, int> setNewPos(){
    int r = randint() % height, c = randint() % width;
    while(fieldData1[r][c] != 0){ r = randint() % height; c = randint() % width; }
    return Pos(r, c);
}

void setWater(int r, int c, int phase){
    if(fieldData1[r][c] != 0) return;
    fieldData1[r][c] = 3;
    originField[r][c] = true;
    if(phase >= 4) return;
    phase++;
    if(r != 0 && randint() % 3 != 0) setWater(r-1, c, phase);
    if(r != height-1 && randint() % 3 != 0) setWater(r+1, c, phase);
    if(c != 0 && randint() % 3 != 0) setWater(r, c-1, phase);
    if(c != width-1 && randint() % 3 != 0) setWater(r, c+1, phase);
}
void setWater(Pos pos){
    setWater(pos.first, pos.second, 0);
}

void printField(){
    for(vector<int>& column: fieldData1){
        for (int i = 0; i < column.size(); i++) {
            cout << (i != 0 ? " " : "") << column[i];
        }
        cout << endl;
    }
}

void printMovements(vector<Movement>& movements){
    for (int i = 0; i < movements.size(); i++) {
        cout << ((i != 0) ? " " : "") << movements[i].first
             << " " << movements[i].second;
    }
    cout << endl;
}

pair<int, int> personFind(Pos pos){
    for(int i = 0; i < peopleLen; i++){
        if(people1[i].pos == pos) return pair<int, int>(1, i);
    }
    for(int i = 0; i < peopleLen; i++){
        if(people2[i].pos == pos) return pair<int, int>(2, i);
    }
    return pair<int, int>(-1, -1);
}

void printAll(){
    int t;
    for(int r = 0; r < height; r++){
        for (int c = 0; c < width; c++) {
            cout << (c != 0 ? " " : "");
            t = personFind(Pos(r, c)).first;
            cout << (t == -1 ? " " : (t == 1 ? "1" : "2")) << fieldData1[r][c];
        }
        cout << endl;
    }
}

vector<vector<vector<int>>> directionSet = {
    {{0, 1}, {1, 0}, {0, -1}, {-1, 0}},
    {{0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}, {-1, -1}, {-1, 0}, {-1, 1}}};
vector<vector<int>> directions;
Movement stay(0, -1);
vector<int> typeOrder = {3, 2, 1};

void turnProcessing(vector<Movement>& movements, vector<Person>& people,
                    vector<vector<int>>& fieldData, int team){
    int r, c, t, direction, f, _t, j;
    bool w;
    unordered_set<int> cantMove(0);
    printMovements(movements);
    for(int type : typeOrder){
        directions = directionSet[type == 1];
        for(int i = 0; i < peopleLen; i++){
            tie(t, direction) = movements[i];
            if(t != type) continue;
            if(direction < 0 || directions.size() <= direction){
                movements[i] = stay; continue;
            }
            tie(r, c) = people[i].pos;
            r += directions[direction][0];
            c += directions[direction][1];
            if(r < 0 || height <= r || c < 0 || width <= c){
                movements[i] = stay; continue;
            }
            f = fieldData[r][c];
            w = originField[r][c];
            //type = 0(stay), 1(move), 2(build), 3(clear)
            //f = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)
            switch(type){
                case 1:
                    if(w || f == 2) break;
                    tie(_t, j) = personFind(Pos(r, c));
                    if(_t == team) cantMove.insert(j);
                    if(_t != -1) break;
                    people[i].pos = Pos(r, c);
                    continue;
                case 2:
                    if(f == 2 || f == 4) break;
                    tie(_t, j) = personFind(Pos(r, c));
                    if(_t != -1 && _t != team) break;
                    fieldData[r][c] = 1;
                    continue;
                case 3:
                    if(f != 1 && f != 2) break;
                    fieldData[r][c] = w ? 3 : 0;
                    continue;
            }
            movements[i] = stay;
        }
    }
    directions = directionSet[0];
    for(int i : cantMove){
        tie(t, direction) = movements[i];
        if(t != 1) continue;
        tie(r, c) = people[i].pos;
        r += directions[(direction+4)%8][0];
        c += directions[(direction+4)%8][1];
        people[i].pos = Pos(r, c);
        movements[i] = stay;
    }
}

vector<vector<int>> fieldReplace(vector<vector<int>> ans){
    for(vector<int>& column : ans){
        for(int& r : column){
            if(r == 1) r = 2;
            if(r == 2) r = 1;
        }
    }
    return ans;
}

void waitSolve(int target, int& flag, system_clock::time_point& startTime, int requiredTime){
    system_clock::time_point now;
    int msec;
    while(flag == target){
        now = system_clock::now();
        msec = duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if(msec > requiredTime) break;
    }
}

void judgeSystem(int requiredTurn, int requiredTime, bool& finishFlag,
                 vector<Person>& people1, vector<Person>& people2,
                 vector<Movement>& movements1, vector<Movement>& movements2,
                 vector<vector<int>>& fieldData1, vector<vector<int>>& fieldData2,
                 int& writeAble1, int& writeAble2,
                 system_clock::time_point& startTurn1, system_clock::time_point& startTurn2){
    int msec;
    vector<vector<int>> _fieldData;
    vector<Pos> _people1(people1.size()), _people2(people2.size());
    _fieldData = fieldData1;
    for(int i = 0; i < people1.size(); i++) _people1[i] = people1[i].pos;
    for(int i = 0; i < people2.size(); i++) _people2[i] = people2[i].pos;
    for(int turn = 0; turn < requiredTurn; turn++){
        startTurn1 = system_clock::now();
        writeAble1 = 1;
        waitSolve(1, writeAble1, startTurn1, requiredTime);
        if(fieldData1 != _fieldData){
            cout << "turn" << turn << "にてfieldData1への不正な書き込みが発生しました" << endl;
            break;
        }
        for(int i = 0; i < people1.size(); i++){
            finishFlag |= _people1[i] != people1[i].pos;
            finishFlag |= _people2[i] != people2[i].pos;
        }
        if(finishFlag){
            cout << "turn" << turn << "にてpeopleへの不正な書き込みが発生しました" << endl;
            break;
        }
        turnProcessing(movements1, people1, fieldData1, 1);
        writeAble1 = 0;
        fieldData2 = fieldReplace(fieldData1);
        _printAll;
        
        _fieldData = fieldData2;
        for(int i = 0; i < people1.size(); i++) _people1[i] = people1[i].pos;
        for(int i = 0; i < people2.size(); i++) _people2[i] = people2[i].pos;
        waitSolve(-1, writeAble2, startTurn1, requiredTime);
        turn++;
        
        startTurn2 = system_clock::now();
        writeAble2 = 1;
        waitSolve(1, writeAble2, startTurn2, requiredTime);
        if(fieldData2 != _fieldData){
            cout << "turn" << turn << "にてfieldData2への不正な書き込みが発生しました" << endl;
            break;
        }
        for(int i = 0; i < people1.size(); i++){
            finishFlag |= _people1[i] != people1[i].pos;
            finishFlag |= _people2[i] != people2[i].pos;
        }
        if(finishFlag){
            cout << "turn" << turn << "にてpeopleへの不正な書き込みが発生しました" << endl;
            break;
        }
        turnProcessing(movements2, people2, fieldData2, 2);
        fieldData1 = fieldReplace(fieldData2);
        _printAll;
        
        _fieldData = fieldData1;
        for(int i = 0; i < people1.size(); i++) _people1[i] = people1[i].pos;
        for(int i = 0; i < people2.size(); i++) _people2[i] = people2[i].pos;
        waitSolve(-1, writeAble1, startTurn2, requiredTime);
    }
    finishFlag = true;
}

void simulate(int seed, int turn, int requiredTime){
    if(seed == -1){
        std::random_device rnd;
        seed = rnd();
    }
    cout << "seed: " << seed << endl;
    randint = std::mt19937(seed);

    height = 11 + randint() % 15; width = 11 + randint() % 15;
    fieldData1 = vector<vector<int>>(height, vector<int>(width));
    originField = vector<vector<bool>>(height, vector<bool>(width));

    int r, c;
    for(int i = randint() % 3; i > 0; i--) setWater(setNewPos());
    for(int i = randint() % 2; i >= 0; i--){
        tie(r, c) = setNewPos();
        fieldData1[r][c] = 4;
    }

    peopleLen = 2 + randint() % 5;
    people1 = vector<Person>(peopleLen);
    people2 = vector<Person>(peopleLen);
    for(Person& person : people1) {
        tie(r, c) = setNewPos();
        person.pos = Pos(r, c);
        fieldData1[r][c] = -1;
    }
    for(Person& person : people2) {
        tie(r, c) = setNewPos();
        person.pos = Pos(r, c);
        fieldData1[r][c] = -1;
    }
    cout << people1.size() << " " << people2.size() << endl;
    for(vector<int>& column : fieldData1){
        for(int i = 0; i < width; i++){
            if(column[i] == -1) column[i] = 0;
        }
    }
    fieldData2 = fieldReplace(fieldData1);
    printAll();
    
    vector<thread> threads;
    bool finishFlag = false;
    
    int writeAble1 = 0;
    auto startTurn1 = system_clock::now();
    vector<Movement> movements1(peopleLen, pair<int, int>(0, -1));
    threads.push_back(thread(solve1, requiredTime, ref(fieldData1), ref(people1), ref(people2),
                             ref(movements1), ref(writeAble1), ref(startTurn1), ref(finishFlag)));
    
    int writeAble2 = 0;
    auto startTurn2 = system_clock::now();
    vector<Movement> movements2(peopleLen, pair<int, int>(0, -1));
    threads.push_back(thread(solve2, requiredTime, ref(fieldData2), ref(people2), ref(people1),
                             ref(movements2), ref(writeAble2), ref(startTurn2), ref(finishFlag)));
    threads.push_back(thread(judgeSystem, turn, requiredTime, ref(finishFlag), ref(people1), ref(people2),
                                          ref(movements1), ref(movements2),
                                          ref(fieldData1), ref(fieldData2),
                                          ref(writeAble1), ref(writeAble2),
                                          ref(startTurn1), ref(startTurn2)));
    for(auto& t : threads) t.join();
}

int main(void){
    simulate(0, 20, 3000);
    return 0;
}