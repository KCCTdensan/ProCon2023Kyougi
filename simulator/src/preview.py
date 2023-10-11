import simulator
import view
import os
pastMatchInfoes = []
filePath = os.path.dirname(__file__)
pathSep = os.path.sep
fieldPath = f"{filePath}{pathSep}..{pathSep}fieldDatas{pathSep}"

def makeMatch(field, opponent, first):
    ans = {"id": 0, "turns": field[1], "turnSeconds": field[2],
           "bonus": {"wall": 10, "territory": 30, "castle": 100},
           "opponent": opponent, "first": first}
    with open(f"{fieldPath}{field[0]}.csv") as f:
        data = f
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
                    masons[-1].append(aMason)
                case "b":
                    structures[-1].append(0)
                    bMason += 1
                    masons[-1].append(-bMason)
    ans["board"] = {"width": len(data[0]), "height": len(data), "mason": aMason}
    ans["board"]["structures"] = structures
    ans["board"]["masons"] = masons
    return ans
    

def makeField(match):
    ans = {"id": 0, "turn": field[1], "logs": log}
    with open(f"{fieldPath}{field[0]}.csv") as f:
        data = f
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
                    masons[-1].append(aMason)
                case "b":
                    structures[-1].append(0)
                    bMason += 1
                    masons[-1].append(-bMason)
    ans["board"] = {"width": len(data[0]), "height": len(data), "mason": aMason}
    ans["board"]["walls"] = [[0]*len(data[0]) for _ in range(len(data))]
    ans["board"]["territories"] = [[0]*len(data[0]) for _ in range(len(data))]
    ans["board"]["structures"] = structures
    ans["board"]["masons"] = masons
    return ans

def restoration(log, field, opponent, first):
    global pastMatchInfoes
    pastMatchInfoes = []
    log = json.loads(log)
    field = makeField(field, log)
    for l in log: pass
        

def read(log=None):
    view.start()
    view.show()


def release():
    view.release()
if __name__ == "__main__":
    print("このプログラムは基本的にインタプリタで実行する形式です。")
    print("試合情報を読み込みたい場合はread関数を呼び出してください")
    print("使用方法を知りたい場合はhelp関数を呼び出してください")
    print("なお未完成です(重要)。")
