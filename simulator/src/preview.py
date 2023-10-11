from simulator import *
import view
import os
import copy
import json
from collections import deque
pastMatchInfoes = []
filePath = os.path.dirname(__file__)
pathSep = os.path.sep
resultPath = f"{filePath}{pathSep}result{pathSep}"
fieldPath = f"{filePath}{pathSep}..{pathSep}fieldDatas{pathSep}"
value = []
nowTurn = 0

def makeMatch(field, opponent, first):
    ans = {"id": 0, "turns": field[1], "turnSeconds": field[2],
           "bonus": {"wall": 10, "territory": 30, "castle": 100},
           "opponent": opponent, "first": first}
    with open(f"{fieldPath}{field[0]}.csv") as f:
        data = f.read()
    data = [x.split(",") for x in data.split("\n")][:-1]
    structures, masons = [], []
    aMason = 0
    bMason = 0
    for x in data:
        structures.append([])
        masons.append([])
        for d in x:
            match d:
                case "0":
                    structures[-1].append(0)
                    masons[-1].append(0)
                case "1":
                    structures[-1].append(1)
                    masons[-1].append(0)
                case "2":
                    structures[-1].append(2)
                    masons[-1].append(0)
                case "a":
                    structures[-1].append(0)
                    aMason += 1
                    if first: masons[-1].append(aMason)
                    else: masons[-1].append(-aMason)
                case "b":
                    structures[-1].append(0)
                    bMason += 1
                    if first: masons[-1].append(-bMason)
                    else: masons[-1].append(bMason)
    ans["board"] = {"width": len(data[0]), "height": len(data), "mason": aMason}
    ans["board"]["structures"] = structures
    ans["board"]["masons"] = masons
    return ans

def makeField(info):
    ans = {"id": info["id"], "turn": 0, "logs": []}
    ans["board"] = copy.deepcopy(info["board"])
    ans["board"]["walls"] = [[0]*info["board"]["width"] \
                             for _ in range(info["board"]["height"])]
    ans["board"]["territories"] = \
        [[0]*info["board"]["width"] for _ in range(info["board"]["height"])]
    return ans

def inBreadth(walls, withOut):
    height, width = len(walls), len(walls[0])
    targets = deque([])
    targets.extend([[0, i] for i in range(0, width)])
    targets.extend([[height-1, i] for i in range(0, width)])
    targets.extend([[i, 0] for i in range(1, height-1)])
    targets.extend([[i, width-1] for i in range(0, height-1)])
    ans = Matrix([[True]*width for _ in range(height)])
    for pos in targets:
        ans[pos] = False
    board = pastMatchInfoes[-1].board
    while len(targets) > 0:
        x, y = targets.popleft()
        if walls[x][y] == withOut: continue
        for newTarget in board.allDirection(x, y, fourDirectionList):
            if ans[newTarget]:
                ans[newTarget] = False
                targets.append(newTarget)
    return ans

def territories(walls, preData):
    ans = [[0]*len(walls[0]) for _ in range(len(walls))]
    ans = copy.deepcopy(preData)
    team1 = inBreadth(walls, 1)
    team2 = inBreadth(walls, 2)
    for x in range(len(walls)):
        for y in range(len(walls[0])):
            if not team1[x][y] and not team2[x][y]: continue
            i = 0
            if team1[x][y]: i |= 1
            if team2[x][y]: i |= 2
            ans[x][y] = i
    return ans

def restoration(log, field, opponent, first):
    global pastMatchInfoes
    info = makeMatch(field, opponent, first)
    data = makeField(info)
    pastMatchInfoes = [MatchInfo(data, info)]
    for l in log:
        data = copy.deepcopy(data)
        turn = data["turn"] = l["turn"]
        preData = pastMatchInfoes[-1]
        if turn%2 == int(first): team = 1
        else: team = 2
        for i, action in enumerate(l["actions"], 1):
            if not action["succeeded"] or action["type"] == 0: continue
            if team == 1: pos = preData.board.myMasons[i-1]
            else:
                pos = preData.board.otherMasons[i-1]
                i *= -1
            direction = eightDirectionList[action["dir"]-1]
            newPos = tuple(map(sum, zip(pos, direction)))
            match action["type"]:
                case 1:
                    data["board"]["masons"][pos[0]][pos[1]] = 0
                    data["board"]["masons"][newPos[0]][newPos[1]] = i
                case 2:
                    data["board"]["walls"][newPos[0]][newPos[1]] = team
                case 3:
                    data["board"]["walls"][newPos[0]][newPos[1]] = 0
        data["board"]["territories"] = territories(data["board"]["walls"],
                                            preData.board.territories)
        data["logs"].append(l)
        pastMatchInfoes.append(MatchInfo(data, info))

def read(log=None):
    global nowTurn, value
    if log is None:
        solver1 = input("先手：")
        solver2 = input("後手：")
        field = input("フィールド：")
        turn = int(input("ターン数："))
        turnTime = int(input("ターン時間："))
        print("先手として試合を見ますか、後手として試合を見ますか？")
        first = None
        while first not in ["y", "n"]:
            first = input("先手: y, 後手: n >>> ").lower()
        first = first == "y"
        if first: my, opponent = solver1, solver2
        else: my, opponent = solver2, solver1
        with open(f"{resultPath}{solver1}{pathSep}{solver2}{pathSep}"
                  f"{field}-{turn}-{turnTime}.txt") as f:
            log = json.load(f)
        value = [my, opponent, [field, turn, turnTime]]
    else:
        opponent = "他チーム"
        log = json.loads(log)
        field = input("フィールド：")
        turn = len(log)
        turnTime = 3
        print("先手として試合を見ますか、後手として試合を見ますか？")
        first = None
        while first not in ["y", "n"]:
            first = input("先手: y, 後手: n >>> ").lower()
        first = first == "y"
        value = ["自チーム"]
    restoration(log, [field, turn, turnTime], opponent, first)
    view.start()
    nowTurn = turn
    view.show(pastMatchInfoes[-1], *value)

def setTurn(turn):
    global nowTurn
    if len(pastMatchInfoes) <= turn:
        print("ターン数が無効です")
        return
    nowTurn = turn
    view.show(pastMatchInfoes[turn], *value)

def getMatchInfo(turn = None):
    if turn is None: turn = nowTurn
    if len(pastMatchInfoes) <= turn:
        print("ターン数が無効です")
        return None
    return pastMatchInfoes[turn]

def release():
    view.release()

def help():
    print("read関数: 過去の試合のデータを呼び出して表示します。")
    print("引数にログデータの文字列を貼り付けることで"
          "保存されていないデータも呼び出せます。")
    print("setTurn関数: ターン数を指定するとそのターン数まで盤面を移動します。")
    print("getMatchInfo関数: 現在の盤面でのMatchInfoを返します。")
    print("ターン数を指定するとそのターン数でのMatchInfoを返します。")

if __name__ == "__main__":
    print("このプログラムは基本的にインタプリタで実行する形式です。")
    print("試合情報を読み込みたい場合はread関数を呼び出してください")
    print("使用方法を知りたい場合はhelp関数を呼び出してください")
