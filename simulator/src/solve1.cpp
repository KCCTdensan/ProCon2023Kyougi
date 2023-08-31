#include "../include/solve1.h"
// movementType = 0(stay), 1(move), 2(build), 3(clear)
// field = 0(empty), 1(myWall), 2(enemyWall), 3(water), 4(castle)

vector<vector<int>> watchDistance(const vector<vector<int>>& field, Pos pos){
    vector<vector<int>> ans(field.size(), vector<int>(field[0].size(), -1));
    queue<Pos> targets;
    targets.push(pos);
    ans[pos.first][pos.second] = 0;
    
    Pos target;
    int r, c, d;
    while (!targets.empty()) {
        target = targets.front();
        targets.pop();
        d = ans[target.first][target.second] + 1;
        for (vector<int>& direction : directionSet) {
            tie(r, c) = target;
            r += direction[0];
            c += direction[1];
            if (r < 0 || height <= r || c < 0 || width <= c)
                continue;
            if (ans[r][c] == -1 && field[r][c] != 3) {
                ans[r][c] = d;
                targets.push(Pos(r, c));
            }
        }
    }
    return ans;
}

Pos nearestCastle(const vector<vector<int>>& field, const vector<vector<int>>& distance){
    Pos ans(-1, -1);
    int ansDistance = 999;
    for(int r = 0; r < height; r++){
        for(int c = 0; c < width; c++){
            if(field[r][c] == 4 && distance[r][c] < ansDistance && distance[r][c] != -1){
                ans = Pos(r, c);
                ansDistance = distance[r][c];
            }
        }
    }
    return ans;
}

void solve1(int requiredTime, const vector<vector<int>>& field, const vector<Person>& myPeople,
    const vector<Person>& enemyPeople, const system_clock::time_point& startTime, const bool& finishFlag,
    vector<Movement>& movements, int& writeAble)
{
    int r, c, newDistance;
    vector<vector<int>> distance;
    Pos castle;
    Movement movement;
    while (true) {
        while (writeAble != 1 && !finishFlag)
            ;
        if (finishFlag)
            break;
        movements = vector<Movement>(0);
        for(Person person : myPeople){
            distance = watchDistance(field, person.pos);
            castle = nearestCastle(field, distance);
            if(castle.first == -1) movement = Movement(0, 0);
            else if(distance[castle.first][castle.second] == 0){
                for(int i = 2; i <= 8; i += 2){
                    tie(r, c) = person.pos;
                    r += directionSet[i][0]; c += directionSet[i][1];
                    if(field[r][c] == 2) movement = Movement(3, i);
                    else if(field[r][c] != 1) movement = Movement(2, i);
                    else continue;
                    break;
                }
                if(field[r][c] == 1) movement = Movement(0, 0);
            } else {
                distance = watchDistance(field, castle);
                newDistance = 999;
                for(int i = 1; i <= 8; i++){
                    tie(r, c) = person.pos;
                    r += directionSet[i][0]; c += directionSet[i][1];
                    if(distance[r][c] < newDistance){
                        movement = Movement(1, i);
                        newDistance = distance[r][c];
                    }
                }
                if(newDistance == 999) movement = Movement(0, 0);
            }
            movements.push_back(movement);
        }
        writeAble = 0;
    }
}
