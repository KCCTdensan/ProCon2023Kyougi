#define GL

#ifdef GL
#include "../include/display.h"
#endif

#include "../include/simulator.h"
#include <chrono>
#include <iostream>
#include <queue>
#include <random>
#include <thread>
#include <unordered_set>
#include <vector>
#include <unordered_map>

#include <string>
#include <fstream>
#include <sstream>

using namespace std;
using namespace std::chrono;

#include "../include/solveList.h"
#include "../include/solveList2.h"

extern vector<pair<string, SolveFunction>> solveList;

void solver(const SolveFunction _solve, int requiredTime,
    const vector<vector<int>>& field, const vector<Person>& myPeople,
    const vector<Person>& enemyPeople, const system_clock::time_point& startTime,
    const bool& finishFlag, vector<Movement>& movements, int& writeAble)
{
    _solve(requiredTime, field, myPeople, enemyPeople, startTime, finishFlag, movements, writeAble);
}

std::mt19937 randint;

int height, width;
vector<vector<bool>> originField;
vector<vector<int>> fieldData1, fieldData2;

int peopleLen;
vector<Person> people1;
vector<Person> people2;

pair<int, int> setNewPos()
{
    int r = randint() % height, c = randint() % width;
    while (fieldData1[r][c] != 0) {
        r = randint() % height;
        c = randint() % width;
    }
    return Pos(r, c);
}

void setWater(int r, int c, int phase)
{
    if (fieldData1[r][c] != 0)
        return;
    fieldData1[r][c] = 3;
    if (phase >= 4)
        return;
    phase++;
    if (r != 0 && randint() % 3 != 0)
        setWater(r - 1, c, phase);
    if (r != height - 1 && randint() % 3 != 0)
        setWater(r + 1, c, phase);
    if (c != 0 && randint() % 3 != 0)
        setWater(r, c - 1, phase);
    if (c != width - 1 && randint() % 3 != 0)
        setWater(r, c + 1, phase);
}
void setWater(Pos pos)
{
    setWater(pos.first, pos.second, 0);
}

void printField()
{
    for (vector<int>& column : fieldData1) {
        for (int i = 0; i < width; i++) {
            cout << (i != 0 ? " " : "") << column[i];
        }
        cout << endl;
    }
}

void printMovements(vector<Movement>& movements)
{
    for (int i = 0; i < (int)movements.size(); i++) {
        cout << ((i != 0) ? " " : "") << movements[i].first
             << " " << movements[i].second;
    }
    cout << endl;
}

pair<int, int> personFind(Pos pos)
{
    for (int i = 0; i < peopleLen; i++) {
        if (people1[i].pos == pos)
            return pair<int, int>(1, i);
    }
    for (int i = 0; i < peopleLen; i++) {
        if (people2[i].pos == pos)
            return pair<int, int>(2, i);
    }
    return pair<int, int>(-1, -1);
}

void printAll()
{
    int t;
    for (int r = 0; r < height; r++) {
        for (int c = 0; c < width; c++) {
            cout << (c != 0 ? " " : "");
            t = personFind(Pos(r, c)).first;
            cout << (t == -1 ? " " : (t == 1 ? "a" : "b")) << fieldData1[r][c];
        }
        cout << endl;
    }
}

vector<vector<int>> directionSet = {
    { 0, 0 }, { -1, -1 }, { -1, 0 }, { -1, 1 }, { 0, 1 }, { 1, 1 }, { 1, 0 }, { 1, -1 }, { 0, -1 }
};
vector<vector<int>> fourDirection = {
    { -1, 0 }, { 0, 1 }, { 1, 0 }, { 0, -1 }
};
Movement stay(0, -1);
vector<int> typeOrder = { 3, 2, 1 };

void turnProcessing(vector<Movement>& movements, vector<Person>& people,
    vector<vector<int>>& fieldData, int team)
{
    int r, c, t, direction, f, _t, j;
    bool w;
    unordered_set<int> cantMove(0);
    printMovements(movements);
    for (int type : typeOrder) {
        for (int i = 0; i < peopleLen; i++) {
            tie(t, direction) = movements[i];
            if (t != type)
                continue;
            if (direction < 1 || direction > 8 || (t != 1 && direction % 2 == 1)) {
                movements[i] = stay;
                continue;
            }
            tie(r, c) = people[i].pos;
            r += directionSet[direction][0];
            c += directionSet[direction][1];
            if (r < 0 || height <= r || c < 0 || width <= c) {
                movements[i] = stay;
                continue;
            }
            f = fieldData[r][c];
            w = originField[r][c];
            // type = 0(stay), 1(move), 2(build), 3(clear)
            // f = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)
            switch (type) {
            case 1:
                if (w || f == 2)
                    break;
                tie(_t, j) = personFind(Pos(r, c));
                if (_t == team)
                    cantMove.insert(j);
                if (_t != -1)
                    break;
                people[i].pos = Pos(r, c);
                continue;
            case 2:
                if (f == 2 || f == 4)
                    break;
                tie(_t, j) = personFind(Pos(r, c));
                if (_t != -1 && _t != team)
                    break;
                fieldData[r][c] = 1;
                continue;
            case 3:
                if (f != 1 && f != 2)
                    break;
                fieldData[r][c] = w ? 3 : 0;
                continue;
            }
            movements[i] = stay;
        }
    }
    for (int i : cantMove) {
        tie(t, direction) = movements[i];
        if (t != 1)
            continue;
        tie(r, c) = people[i].pos;
        r += directionSet[(direction+3)%8+1][0];
        c += directionSet[(direction+3)%8+1][1];
        people[i].pos = Pos(r, c);
        movements[i] = stay;
    }
    for (int i = 0; i < peopleLen; i++)
        people[i].movement.push_back(movements[i]);
}

vector<vector<int>> fieldReplace(vector<vector<int>>& fieldData)
{
    vector<vector<int>> ans(height, vector<int>(width));
    for (int c = 0; c < height; c++) {
        for (int r = 0; r < width; r++) {
            if (fieldData[c][r] == 1)
                ans[c][r] = 2;
            else if (fieldData[c][r] == 2)
                ans[c][r] = 1;
            else
                ans[c][r] = fieldData[c][r];
        }
    }
    return ans;
}

void waitSolve(int target, const int& flag, const system_clock::time_point& startTime, int requiredTime)
{
    system_clock::time_point now;
    int msec;
    while (flag == target) {
        now = system_clock::now();
        msec = duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if (msec > requiredTime)
            break;
    }
}

void fieldUpdate(vector<vector<int>>& pointField1, vector<vector<int>>& pointField2, const vector<vector<int>>& fieldData1, const vector<vector<int>>& fieldData2)
{
    for (vector<int>& column : pointField1) {
        for (int& r : column) {
            if (r == 1)
                r = 2;
        }
    }
    for (vector<int>& column : pointField2) {
        for (int& r : column) {
            if (r == 1)
                r = 2;
        }
    }
    queue<Pos> targets;
    vector<vector<bool>> reached(height, vector<bool>(width));
    int r, c;
    for (r = 1; r < height - 1; r++) {
        if (fieldData1[r][0] != 1) {
            targets.push(Pos(r, 0));
            reached[r][0] = true;
        }
        if (fieldData1[r][width - 1] != 1) {
            targets.push(Pos(r, width - 1));
            reached[r][width - 1] = true;
        }
    }
    for (c = 0; c < width; c++) {
        if (fieldData1[0][c] != 1) {
            targets.push(Pos(0, c));
            reached[0][c] = true;
        }
        if (fieldData1[height - 1][c] != 1) {
            targets.push(Pos(height - 1, c));
            reached[height - 1][c] = true;
        }
    }

    Pos target;
    while (!targets.empty()) {
        target = targets.front();
        targets.pop();
        for (vector<int>& direction : fourDirection) {
            tie(r, c) = target;
            r += direction[0];
            c += direction[1];
            if (r < 0 || height <= r || c < 0 || width <= c)
                continue;
            if (!reached[r][c] && fieldData1[r][c] != 1) {
                reached[r][c] = true;
                targets.push(Pos(r, c));
            }
        }
    }

    for (r = 0; r < height; r++) {
        for (c = 0; c < width; c++) {
            if (!reached[r][c]) {
                pointField1[r][c] = 1;
                pointField2[r][c] = 0;
            }
            if (fieldData1[r][c] == 1)
                pointField1[r][c] = 0;
        }
    }

    reached = vector<vector<bool>>(height, vector<bool>(width));
    for (r = 1; r < height - 1; r++) {
        if (fieldData2[r][0] != 1) {
            targets.push(Pos(r, 0));
            reached[r][0] = true;
        }
        if (fieldData2[r][width - 1] != 1) {
            targets.push(Pos(r, width - 1));
            reached[r][width - 1] = true;
        }
    }
    for (c = 0; c < width; c++) {
        if (fieldData2[0][c] != 1) {
            targets.push(Pos(0, c));
            reached[0][c] = true;
        }
        if (fieldData2[height - 1][c] != 1) {
            targets.push(Pos(height - 1, c));
            reached[height - 1][c] = true;
        }
    }

    while (!targets.empty()) {
        target = targets.front();
        targets.pop();
        for (vector<int>& direction : fourDirection) {
            tie(r, c) = target;
            r += direction[0];
            c += direction[1];
            if (r < 0 || height <= r || c < 0 || width <= c)
                continue;
            if (!reached[r][c] && fieldData2[r][c] != 1) {
                reached[r][c] = true;
                targets.push(Pos(r, c));
            }
        }
    }

    for (r = 0; r < height; r++) {
        for (c = 0; c < width; c++) {
            if (!reached[r][c]) {
                pointField2[r][c] = 1;
                pointField1[r][c] &= 1;
            }
            if (fieldData2[r][c] == 1)
                pointField2[r][c] = 0;
        }
    }
}

vector<int> calcPoints(vector<vector<int>>& pointField, const vector<vector<int>>& fieldData){
    vector<int> ans(3, 0);
    for (int r = 0; r < height; r++) {
        for (int c = 0; c < width; c++) {
            if (pointField[r][c] != 0) {
                if (fieldData[r][c] == 4) {
                    ans[0] += 100;
                    ans[1] += 100;
                } else {
                    ans[0] += 30;
                    ans[2] += 30;
                }
            }
            if (fieldData[r][c] == 1)
                ans[0] += 10;
        }
    }
    return ans;
}

void judgeSystem(int requiredTurn, int requiredTime, bool& finishFlag,
    vector<Person>& people1, vector<Person>& people2,
    vector<Movement>& movements1, vector<Movement>& movements2,
    vector<vector<int>>& fieldData1, vector<vector<int>>& fieldData2,
    int& writeAble1, int& writeAble2,
    system_clock::time_point& startTurn1, system_clock::time_point& startTurn2, int& ans)
{
    vector<vector<int>> pointField1(height, vector<int>(width));
    vector<vector<int>> pointField2(height, vector<int>(width));
    for (int turn = 0; turn < requiredTurn; turn++) {
        startTurn1 = system_clock::now();
        writeAble1 = 1;
        waitSolve(1, writeAble1, startTurn1, requiredTime);
        turnProcessing(movements1, people1, fieldData1, 1);
        writeAble1 = 0;
        fieldData2 = fieldReplace(fieldData1);
        fieldUpdate(pointField1, pointField2, fieldData1, fieldData2);
        _printAll;

        waitSolve(-1, writeAble2, startTurn1, requiredTime);

        startTurn2 = system_clock::now();
        writeAble2 = 1;
        waitSolve(1, writeAble2, startTurn2, requiredTime);
        turnProcessing(movements2, people2, fieldData2, 2);
        fieldData1 = fieldReplace(fieldData2);
        fieldUpdate(pointField1, pointField2, fieldData1, fieldData2);
        _printAll;

        waitSolve(-1, writeAble1, startTurn2, requiredTime);
    }
    vector<int> point1 = calcPoints(pointField1, fieldData1);
    vector<int> point2 = calcPoints(pointField2, fieldData2);
    printAll();
    cout << "team1: " << point1[0] << ", " << point1[1] << ", " << point1[2] << endl;
    cout << "team2: " << point2[0] << ", " << point2[1] << ", " << point2[2] << endl;
    if (point1[0] > point2[0])
        ans = 1;
    else if (point1[0] < point2[0])
        ans = 2;
    else if (point1[1] > point2[1])
        ans = 1;
    else if (point1[1] < point2[1])
        ans = 2;
    else if (point1[2] > point2[2])
        ans = 1;
    else if (point1[2] < point2[2])
        ans = 2;
    finishFlag = true;
}

#define AllFieldData tuple<vector<vector<int>>, vector<Person>, vector<Person>>

AllFieldData create(int seed){
    if (seed == -1) {
        std::random_device rnd;
        seed = rnd();
    }
    cout << "seed: " << seed << endl;
    randint = std::mt19937(seed);

    height = 11 + randint() % 15;
    width = 11 + randint() % 15;
    fieldData1 = vector<vector<int>>(height, vector<int>(width));

    int r, c;
    for (int i = randint() % 3; i > 0; i--)
        setWater(setNewPos());
    for (int i = randint() % 2; i >= 0; i--) {
        tie(r, c) = setNewPos();
        fieldData1[r][c] = 4;
    }

    peopleLen = 2 + randint() % 5;
    people1 = vector<Person>(peopleLen);
    people2 = vector<Person>(peopleLen);
    for (Person& person : people1) {
        tie(r, c) = setNewPos();
        person.pos = Pos(r, c);
        fieldData1[r][c] = -1;
    }
    for (Person& person : people2) {
        tie(r, c) = setNewPos();
        person.pos = Pos(r, c);
        fieldData1[r][c] = -1;
    }
    for (vector<int>& column : fieldData1) {
        for (int i = 0; i < width; i++) {
            if (column[i] == -1)
                column[i] = 0;
        }
    }
    return AllFieldData(fieldData1, people1, people2);
}

int simulate(AllFieldData data, int turn, int requiredTime, const SolveFunction _solve1,
    const SolveFunction _solve2)
{
    fieldData1 = get<0>(data);
    fieldData2 = fieldReplace(fieldData1);
    height = (int)fieldData1.size();
    width = (int)fieldData1.back().size();
    originField = vector<vector<bool>>(height, vector<bool>(width));
    for(int r = 0; r < height; r++){
        for(int c = 0; c < height; c++) originField[r][c] = fieldData1[r][c] == 3;
    }
    people1 = get<1>(data);
    people2 = get<2>(data);
    peopleLen = (int)people1.size();
    printAll();

#ifdef GL
    displayInit();
    drawDisplay(fieldData1);
#endif

    vector<thread> threads;
    bool finishFlag = false;
    int ans = 0;

    int writeAble1 = 0;
    vector<Movement> movements1(peopleLen, pair<int, int>(0, -1));

    int writeAble2 = 0;
    vector<Movement> movements2(peopleLen, pair<int, int>(0, -1));

    auto startTurn1 = system_clock::now();
    auto startTurn2 = system_clock::now();

    threads.push_back(thread(solver, _solve1, requiredTime, ref(fieldData1), ref(people1), ref(people2),
        ref(startTurn1), ref(finishFlag), ref(movements1), ref(writeAble1)));
    threads.push_back(thread(solver, _solve2, requiredTime, ref(fieldData2), ref(people2), ref(people1),
        ref(startTurn2), ref(finishFlag), ref(movements2), ref(writeAble2)));
    threads.push_back(thread(judgeSystem, turn, requiredTime, ref(finishFlag), ref(people1), ref(people2),
        ref(movements1), ref(movements2),
        ref(fieldData1), ref(fieldData2),
        ref(writeAble1), ref(writeAble2),
        ref(startTurn1), ref(startTurn2), ref(ans)));
    for (auto& t : threads)
        t.join();
    return ans;
}

unordered_map<string, AllFieldData> getAllFieldDatas() {
    unordered_map<string, AllFieldData> ans;
    vector<string> targets = {"A11", "A13", "A15", "A17", "A21", "A25", "B11", "B13", "B15", "B17", "B21", "B25", "C11", "C13", "C15", "C17", "C21", "C25"};
    string str_buf, str_conma_buf, input_csv_file_path;
    for(string& target : targets){
        AllFieldData newData;
        input_csv_file_path = "../fieldDatas/" + target + ".csv";
        std::ifstream ifs_csv_file(input_csv_file_path);
        vector<vector<int>>& data = get<0>(newData);
        vector<Person> &person1 = get<1>(newData), &person2 = get<2>(newData);
        int i = 0, j;
        while (getline(ifs_csv_file, str_buf)) {
            std::istringstream i_stream(str_buf);
            data.push_back(vector<int>(0));
            j = 0;
            while (getline(i_stream, str_conma_buf, ',')) {
                switch(str_conma_buf[0]){
                    case 'a':
                        data.back().push_back(0);
                        person1.push_back(Person());
                        person1.back().pos = Pos(i, j);
                        break;
                    case 'b':
                        data.back().push_back(0);
                        person2.push_back(Person());
                        person2.back().pos = Pos(i, j);
                        break;
                    case '0':
                        data.back().push_back(0);
                        break;
                    default:
                        data.back().push_back(str_conma_buf[0]-'0'+2);
                        break;
                }
                j++;
            }
            i++;
        }
        ans[target] = newData;
    }
    return ans;
}

int main(void)
{
    makeList();
    unordered_map<string, AllFieldData> allField = getAllFieldDatas();
    int winner = simulate(allField["A11"], 10, 3000, solveList[0].second, solveList[1].second);
    // simulate(allField["fieldName"], turn, timeOfTurn, solve1, solve2)
    //  -> 1: solve1 win   2: solve2 win   0: draw
    
    // simulate(create(seed), ...)
    //  seed = -1 --> random seed
    cout << "winner: " << winner << endl;

#ifdef GL
    displayOff();
#endif

    return 0;
}