import interface, view
import solveList as solveListPack
import pandas as pd
import sys, platform, subprocess, threading, datetime

mode = 2
# 0: 本番用 1: 練習用 2: solverの管理 3: 結果確認
# solverは拡張子を含めた文字列を書いてください
# 拡張子が異なる同じ名前のファイルを作るとバグります
threadLen = 1
# 並列化処理のレベル
# 同時に実行する試合の最大数です
# 1試合につき3つのタスクを並列処理します
match mode:
    case 0:
        token = ""
        solver = ["solve1.py"]
        baseUrl = ""
    case 1:
        matchList = [["solve1.py", "solve2.py"]]
        # solverを2つずつ入れた2次元配列
        # [solver, "all"] と入れると全solverとの総当たり、
        # ["all", "all"] と入れると全ての組み合わせの試行を行う
    case 2:
        # 追加・変更の場合のみ[solver, type]の記述をしてください
        # (シミュレートの際に特定の種類のみ試行するようになります)
        # typeには"all"も記述可能です(どのフィールドでも動く解法)
        #   例) newSolver = [["solveX.py", "B"], ["solveKing.py", "all"], ...]
        #     -> solveXはBタイプフィールド専用, solveKingは全対応
        
        # 追加
        newSolver = []
        # 変更(記録をリセットする)
        changedSolver = []
        # 削除(記録を消去する) ファイルの削除は手動でやること
        deletedSolver = []
        # 無効化・有効化("all"に含まれなくなる)
        switchSolver = []
    case 3:
        solver = "solve1.cpp"
        # 特定のsolverに対しての結果を確認する

assert threadLen > 0, "threadLenが0以下なので何も実行出来ません！！"

solverList, disabledList = None, None
while solverList is None:
    with open("result\solverList.txt", "r") as f:
        solverList = f.read().split("\n")
solverList = [solver.split(",") for solver in solverList if solver != ""]
while disabledList is None:
    with open("result\disabledList.txt", "r") as f:
        disabledList = f.read().split("\n")
disabledList = [solver.split(",") for solver in disabledList if solver != ""]
allList = [solver[0] for solver in [*solverList, *disabledList]]
allDict = dict([*solverList, *disabledList])
fieldList = []
for c in "ABC":
    fieldList.extend([f"{c}{i}" for i in [11,13,15,17,21,25]])

if platform.system() == "Windows":
    target = r"..\server\procon-server_win.exe"
elif platform.system() == "Linux":
    target = r"..\server\procon-server_linux"
elif "AMD" in platform.machine().upper():
    target = r"..\server\procon-server_darwin_amd"
else:
    target = r"..\server\procon-server_darwin_arm"

class Result:
    def __init__(self, solver, *, new=False):
        self.file = f"result\{solver.split('.')[0]}.csv"
        if new: self.result = pd.DataFrame(index=allList,
                                           columns=fieldList)
        else:
            self.result = pd.read_csv(self.file, index_col=0)
            if list(self.result.index) != allList:
                old = set(self.result.index)
                new = [solver for solver in allList if solver in old]
                self.result = pd.concat([pd.DataFrame(index=allList), \
                                         self.result.loc[new]], axis=1)

    def match(self, opponent, field):
        ans = self.result.at[opponent][f"{field}.csv"].split(": ")
        return [ans[0] == "WIN", *map(int, ans[1].split("-"))]
    def set(self, opponent, field, point1, point2, result):
        self.result.at[opponent][f"{field}.csv"] = \
            f"{'WIN' if result else 'LOSE'}: {point1}-{point2}"
    def __del__(self):
        self.result.to_csv(self.file)

if mode == 2:
    changedSolver = dict(changedSolver)
    newSolverList, newDisabledList = [], []
    nS, cS, dS, sS = newSolver.copy(), [], [], []
    for solver in solverList:
        if solver[0] in changedSolver:
            a = Result(solver[0], new=True); del a
            cS.append(solver[0])
            solver[1] = changedSolver.pop(solver[0])
        if solver[0] in deletedSolver:
            dS.append(solver[0]); deletedSolver.remove(solver[0])
            continue
        if solver[0] in switchSolver:
            newDisabledList.append(solver)
            sS.append(solver[0]); switchSolver.remove(solver[0])
            continue
        newSolverList.append(solver)
    for solver in disabledList:
        if solver[0] in changedSolver:
            a = Result(solver[0], new=True); del a
            cS.append(solver[0])
            solver[1] = changedSolver.pop(solver[0])
        if solver[0] in deletedSolver:
            dS.append(solver[0]); deletedSolver.remove(solver[0])
            continue
        if solver[0] in switchSolver:
            newSolverList.append(solver)
            sS.append(solver[0]); switchSolver.remove(solver[0])
            continue
        newDisabledList.append(solver)
    newSolverList.extend(newSolver)
    solverList = newSolverList
    disabledList = newDisabledList
    newSolverList = [",".join(solver) for solver in newSolverList]
    newDisabledList = [",".join(solver) for solver in newDisabledList]
    while newSolverList is not None:
        with open("result\solverList.txt", "w") as f:
            f.write("\n".join(newSolverList))
            newSolverList = None
    while newDisabledList is not None:
        with open("result\disabledList.txt", "w") as f:
            f.write("\n".join(newDisabledList))
            newDisabledList = None
    allList = [solver[0] for solver in [*solverList, *disabledList]]
    newSolver = [solver[0] for solver in newSolver]
    for solver in newSolver:
        a = Result(solver, new=True); del a
    print("処理を終了しました")
    if len(newSolver) != 0:
        print("\n以下のデータが新規に追加されました")
        print(*newSolver, sep="\n")
    if len(cS) != 0:
        print("\n以下のデータの記録をリセットしました")
        print(*cS, sep="\n")
    if len(dS) != 0:
        print("\n以下のデータの記録を消去しました")
        print(*dS, sep="\n")
    if len(sS) != 0:
        print("\n以下のデータを有効化/無効化しました")
        print(*sS, sep="\n")
    if len(changedSolver)+len(deletedSolver)+len(switchSolver) != 0:
        print("\n以下のデータは見つからなかったため、処理を行いませんでした")
        print(*changedSolver, *deletedSolver, *switchSolver, sep="\n")
    print("\n現在の有効なsolverは以下の通りです")
    for solver in solverList:
        if solver[1] == "all": print(solver[0])
        else: print(f"{solver[0]}: {solver[1]}タイプ専用")
    print("\n現在無効化されているsolverは以下の通りです")
    for solver in disabledList:
        if solver[1] == "all": print(solver[0])
        else: print(f"{solver[0]}: {solver[1]}タイプ専用")
    sys.exit()

if mode == 3:
    pd.set_option('display.width', None)
    print(Result(solver).result)
    sys.exit()

if mode == 1:
    results = dict([(solver[0].split(".")[0], Result(solver[0])) \
                    for solver in solverList])

class Solver:
    def __init__(self, solver):
        self.thread = []
        if solver[0][-3:] == ".py": self.lang = "python"
        else: self.lang = "c++"
        self.name = solver[0].split(".")[0]
        if solver[1] == "all": self.target = False
        else: self.target = obj[1]
        if self.lang == "python":
            self.solver = solveListPack.getSolver(obj[0][:-3])
            assert self.solver is not None, f"{obj[0]}が見つかりません"
    def threading(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self.thread.append(thread)
        thread.start()
        return thread
    def start(self, interface):
        if self.lang == "python":
            self.main = self.threading(self.solver, interface)
    def targetAs(self, target):
        return not self.target or target[0] == self.target
    def isAlive(self):
        if self.lang == "python":
            return self.main.is_alive()

class Match(object):
    def __init__(self):
        self.thread = []
    def interfaceStart(self, interface, matchId, token, **kwargs):
        interface.__init__(token, **kwargs)
        interface.setTo(matchId)
    def threading(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self.thread.append(thread)
        thread.start()
        return thread
    def show(self):
        if not self.isAlive(): return False
        view.show(self.interface.getMatchInfo()["board"])
        return True
    def __del__(self):
        for thread in self.threads:
            thread.join()

class Real(Match):
    def __init__(self, solver, matchId):
        super().__init__()
        self.interface = interface.Interface(check=False)
        self.interface1 = interface.Interface(check=False)
        self.threading(
          self.interfaceStart, self.interface, matchId, token, baseUrl=baseUrl)
        thread = self.threading(
          self.interfaceStart, self.interface1, matchId, token, baseUrl=baseUrl)
        self.solver = solver
        self.mode="real"
        thread.join()
        solver.start(self.interface1)
    def isAlive(self):
        return self.solver.isAlive()
    def __del__(self):
        super().__del__()
        self.solver.release()

class Practice(Match):
    def __init__(self, solver1, solver2, field, port):
        super().__init__()
        subprocess.run([target, "-c", f"..\\fieldDatas\\{field}.txt", "-l",
                        f":{port}"])
        self.field = field
        self.interface = interface.Interface(check=False)
        self.interface1 = interface.Interface(check=False)
        self.interface2 = interface.Interface(check=False)
        self.threading(
            self.interfaceStart, self.interface, 10, "token1", port=port)
        thread1 = self.threading(
            self.interfaceStart, self.interface1, 10, "token1", port=port)
        thread2 = self.threading(
            self.interfaceStart, self.interface2, 10, "token2", port=port)
        
        self.solver1 = solver1
        self.solver2 = solver2
        self.mode="practice"
        thread1.join()
        thread2.join()
        solver1.start(self.interface1)
        solver2.start(self.interface2)
    def isAlive(self):
        return self.solver1.isAlive() and self.solver2.isAlive()
    def __del__(self):
        super().__del__()
        solver1, solver2 = self.solver1, self.solver2
        results[solver1.name].set(solver2.name, self.field, solver1.point,
                                  solver2.point, solver1.result)
        results[solver2.name].set(solver1.name, self.field, solver2.point,
                                  solver1.point, solver2.result)
        solver1.release()
        solver2.release()

