import interface, view, simulator
import solveList as solveListPack
import pandas as pd
import sys, os, platform, subprocess, threading, time, traceback
mode = 1
# 0: 本番用 1: 練習用 2: solverの管理 3: 結果確認
# solverは拡張子を含めた文字列を書いてください
# 拡張子が異なる同じ名前のファイルを作るとバグります
threadLen = 1
# 並列化処理のレベル
# 同時に実行する試合の最大数です
# 1試合につき3つ(試合終了時たまに6つ)のタスクを並列処理します
recordData = False
# サーバ通信のデータを完全に残すか否かを選べます
# データを完全に残すためにはかなり容量が必要になります(1試合9MB)
match mode:
    case 0:
        token = ""
        solver = ["solve1.py","solve2.py"]
        baseUrl = ""
    case 1:
        # solverを2つずつ入れた2次元配列
        # 0番目の要素が先手に設定される
        # [solver, "all"] と入れると全solverとの総当たり、
        # ["all", "all"] と入れると全ての組み合わせの試行を行う
        matchList = [["all", "all"]]
        # フィールドの組み合わせ
        # A～C、11,13,15,17,21,25を指定可能
        # "all"を指定することで全ての組み合わせを試行する
        fieldList = ["all"]
        # ターン数の組み合わせ
        # [30, 90, 150, 200]を指定可能
        # "all"を指定することで全ての組み合わせを試
        turnList = [30]
        # Falseだと記録済みの組み合わせはスキップする Trueは上書き
        replace = False
        # 観戦を行うか否か TrueでGUI表示します
        watch = True
    case 2:
        # 追加・変更の場合のみ[solver, type]の記述をしてください
        # (シミュレートの際に特定の種類のみ試行するようになります)
        # typeには"all"も記述可能です(どのフィールドでも動く解法)
        #   例) newSolver = [["solveX.py", "B"], ["solveKing.py", "all"], ...]
        #     -> solveXはBタイプフィールド専用, solveKingは全対応
        
        # 追加
        newSolver = []
        # 変更(記録をリセットする)
        changedSolver = [["solve1.py", "all"]]
        # 削除(記録を消去する) ファイルの削除は手動でやること
        deletedSolver = []
        # 無効化・有効化("all"に含まれなくなる)
        switchSolver = []
    case 3:
        solver = "solve1.py"
        # 特定のsolverに対しての結果を確認する

assert threadLen > 0, "threadLenが0以下なので何も実行出来ません！！"

filePath = os.path.dirname(__file__)


if platform.system() == "Windows":
    pathSep = "\\"
    serverName = f"{filePath}\\..\\server\\procon-server_win.exe"
elif platform.system() == "Linux":
    pathSep = "/"
    serverName = f"{filePath}/../server/procon-server_linux"
elif "AMD" in platform.machine().upper():
    pathSep = "/"
    serverName = f"{filePath}/../server/procon-server_darwin_amd"
else:
    pathSep = "/"
    serverName = f"{filePath}/../server/procon-server_darwin_arm"
resultPath = f"{filePath}{pathSep}result{pathSep}"
fieldPath = f"{filePath}{pathSep}..{pathSep}fieldDatas{pathSep}"

solverList, disabledList = None, None
while solverList is None:
    with open(f"{resultPath}solverList.txt", "r") as f:
        solverList = f.read().split("\n")
solverList = [solver.split(",") for solver in solverList if solver != ""]
solverDict = dict(solverList)
while disabledList is None:
    with open(f"{resultPath}disabledList.txt", "r") as f:
        disabledList = f.read().split("\n")
disabledList = [solver.split(",") for solver in disabledList if solver != ""]
allList = [solver[0] for solver in [*solverList, *disabledList]]
allName = sum([[f"{solver}-first", f"{solver}-second"] for solver in allList],
              start=[])

if mode != 1 or fieldList == "all" or fieldList == ["all"]:
    fieldList = []
    for c in "ABC":
        fieldList.extend([f"{c}{i}" for i in [11,13,15,17,21,25]])
allTurnList = [30,90,150,200]
if mode != 1 or turnList == "all" or turnList == ["all"]:
    turnList = allTurnList
allTimeList = [3]
timeList = allTimeList

class Result:
    def __init__(self, solver, *, new=False):
        self.name = solver.split('.')[0]
        self.result = {}
        for file in self.all():
            if new: self.result[file] = pd.DataFrame(index=allName,
                        columns=fieldList, dtype=object)
            else:
                self.result[file] = pd.read_csv(
                    f"{resultPath}{file}.csv", index_col=0)
                if list(self.result[file].index) != allName:
                    old = set(self.result[file].index)
                    new = [solver for solver in allName if solver in old]
                    self.result = pd.concat([pd.DataFrame(index=allName,
                        dtype=object), self.result[file].loc[new]], axis=1)

    def all(self):
        for turn in allTurnList:
            for time in allTimeList:
                yield f"{self.name}-{turn}-{time}"

    def match(self, other, field):
        ans = []
        for text in [f"{other}-first", f"{other}-second"]:
            data = self.result[f"{self.name}-{field[1]}-{field[2]}"].at[
                text,field[0]]
            if pd.isnull(data): ans.append(None)
            else:
                data = data.split(": ")
                ans.append([data[0] == "WIN", *map(int, data[1].split("-"))])
        return ans
    def set(self, other, field, point1, point2, result, *, first=True):
        self.result[f"{self.name}-{field[1]}-{field[2]}"].at[
            f"{other}-{'first' if first else 'second'}",field[0]] \
                = f"{'WIN' if result else 'LOSE'}: {point1}-{point2}"
    def release(self):
        for file in self.all():
            self.result[file].to_csv(f"{resultPath}{file}.csv")
    def __del__(self):
        for file in self.all():
            self.result[file].to_csv(f"{resultPath}{file}.csv")

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
        with open(f"{resultPath}solverList.txt", "w") as f:
            f.write("\n".join(newSolverList))
            newSolverList = None
    while newDisabledList is not None:
        with open(f"{resultPath}disabledList.txt", "w") as f:
            f.write("\n".join(newDisabledList))
            newDisabledList = None
    allList = [solver[0] for solver in [*solverList, *disabledList]]
    allName = sum([[f"{solver}-first", f"{solver}-second"] for solver \
                   in allList], start=[])
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
    result = Result(solver)
    for file in result.all():
        print("f========{file}========")
        print(Result(solver)[file].result)
    sys.exit()

interface.dataBool = recordData

if mode == 1:
    results = dict([(solver[0], Result(solver[0])) for solver in solverList])
processes = []
class Solver:
    def __init__(self, solver):
        self._isAlive, self.main, self.dead = False, None, False
        self.thread = []
        if solver[0][-3:] == ".py": self.lang = "python"
        else: self.lang = "c++"
        self.name = solver[0]
        if solver[1] == "all": self.target = False
        else: self.target = solver[1]
        if self.lang == "python":
            self.solver = solveListPack.getSolver(solver[0][:-3])
            assert self.solver is not None, f"{solver[0]}が見つかりません"
    def threading(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self.thread.append(thread)
        thread.start()
        return thread
    def solve(self, func, *args, **kwargs):
        try: func(*args, **kwargs)
        except:
            self.dead = True
            traceback.print_exc()
    def start(self, interface):
        self._isAlive = True
        if self.lang == "python":
            self.main = self.threading(self.solve, self.solver, interface, self)
    def targetAs(self, target):
        return not self.target or target[0] == self.target
    def isAlive(self):
        if self.lang == "python" and self.main is not None:
            self._isAlive &= self.main.is_alive()
        return self._isAlive
    def release(self):
        self._isAlive = False
    def __del__(self):
        for thread in self.thread:
            try: thread.join()
            except RuntimeError: pass

class Match(object):
    def __init__(self):
        self.thread = []
        self.process = None
    def interfaceStart(self, interface, matchId, token, **kwargs):
        try:
            interface.__init__(token, **kwargs)
            interface.setTo(matchId)
        except: traceback.print_exc()
    def threading(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self.thread.append(thread)
        thread.start()
        return thread
    def show(self):
        if not self.isAlive(): return False
        if self.mode == "real":
            view.show(self.interface.getMatchInfo(), self.solver.name)
        if self.mode == "practice":
            view.show(self.interface.getMatchInfo(), self.solver1.name,
                      self.solver2.name, self.field)
        return True
    def __del__(self):
        for thread in self.thread:
            try: thread.join()
            except RuntimeError: pass

class Real(Match):
    def __init__(self, solver, matchId):
        super().__init__()
        self.cantStart = False
        self.interface = interface.Interface(check=False)
        self.interface1 = interface.Interface(check=False)
        thread = self.threading(self.interfaceStart, self.interface, matchId, token,
                       baseUrl=baseUrl)
        thread1 = self.threading(self.interfaceStart, self.interface1, matchId,
                                token, baseUrl=baseUrl)
        self.solver = solver
        self.mode="real"
        try:
            thread.join()
            thread1.join()
        except RuntimeError: pass
        if not self.interface1.checked:
            self.cantStart = True
            return
        while self.interface.getMatchInfo() is None: pass
        solver.start(self.interface1)
    def isAlive(self):
        return self.solver.isAlive()
    def __del__(self):
        if self.cantStart: return False
        self.solver.release()
        self.threading(lambda: self.interface.release())
        self.threading(lambda: self.interface1.release())
        super().__del__()

class Practice(Match):
    def __init__(self, solver1, solver2, field, port):
        super().__init__()
        if not(solver1.targetAs(field) and solver2.targetAs(field)):
            self.cantStart = True
            return
        print(f"start {solver1.name} - {solver2.name} match in {field[0]}-"
              f"{field[1]}-{field[2]} at port {port}")
        
        self.solver1 = solver1
        self.solver2 = solver2
        self.interface = interface.Interface(check=False)
        self.interface1 = interface.Interface(check=False)
        self.interface2 = interface.Interface(check=False)
        self.cantRecord = self.cantStart = False
        self.process = subprocess.Popen([serverName, "-c",
            f"{fieldPath}{field[0]}-{field[1]}-{field[2]}.txt",
            "-l", f":{port}", "-start", "1s"])
        processes.append(self.process)
        time.sleep(1)
        self.field = field
        thread = self.threading(
            self.interfaceStart, self.interface, 10, "token1", port=port)
        thread1 = self.threading(
            self.interfaceStart, self.interface1, 10, "token1", port=port)
        thread2 = self.threading(
            self.interfaceStart, self.interface2, 10, "token2", port=port)
        
        self.mode="practice"
        self.allTurn = None
        try:
            thread.join()
            thread1.join()
            thread2.join()
        except RuntimeError: pass
        if not self.interface1.checked or not self.interface2.checked:
            self.cantRecord = True
            return
        while self.interface.getMatchInfo() is None: pass
        solver1.start(self.interface1)
        solver2.start(self.interface2)
    def isAlive(self):
        if self.cantStart: return False
        if self.cantRecord: return False
        if self.allTurn is None:
            returned = self.interface.getMatches()
            if returned: self.allTurn = returned[0]["turns"]
            else: self.cantRecord = True
        returned = self.interface.getMatchInfo()
        if not self.interface.checked: pass
        if not returned: self.cantRecord = True
        elif returned.turn == self.allTurn: return False
        if self.cantRecord: return False
        return not self.solver1.dead and not self.solver2.dead
    def __del__(self):
        if self.cantStart:
            super().__del__()
            return
        solver1, solver2 = self.solver1, self.solver2
        solver1.release()
        solver2.release()
        self.threading(lambda: self.interface1.release())
        self.threading(lambda: self.interface2.release())
        returned = None
        if not self.cantRecord: returned = self.interface.getMatchInfo()
        self.threading(lambda: self.interface.release())
        if returned:
            point = simulator.calcPoint(returned.board)
            if solver1.dead: point[0] = [-1, -1, -1]
            if solver2.dead: point[1] = [-1, -1, -1]
            result = point[0] >= point[1]
            results[solver1.name].set(solver2.name, self.field, point[0][0],
                                      point[1][0], result)
            results[solver2.name].set(solver1.name, self.field, point[1][0],
                                      point[0][0], not result, first=False)
            print(f"recorded {solver1.name} - {solver2.name} match "
                  f"in {self.field[0]}-{self.field[1]}-{self.field[2]}")
        else:
            print(f"failed {solver1.name} - {solver2.name} match "
                  f"in {self.field[0]}-{self.field[1]}-{self.field[2]}")
        super().__del__()
        if self.process.poll() is None: self.process.kill()

def pattern(solver1, solver2):
    if solver1 != "all" and solver1 not in solverDict:
        print(f"{solver1}は存在しません")
        return
    if solver2 != "all" and solver2 not in solverDict:
        print(f"{solver2}は存在しません")
        return
    if solver1 == "all":
        for solver1 in solverList:
            for p in pattern(solver1[0], solver2): yield p
        return 
    if solver2 == "all":
        for solver2 in solverList:
            for p in pattern(solver1, solver2[0]): yield p
        return
    solver1 = [solver1, solverDict[solver1]]
    solver2 = [solver2, solverDict[solver2]]
    for field in fieldList:
        for turn in turnList:
            for time in timeList:
                yield [solver1, solver2, field, turn, time]

try:
    if mode == 1:
        queue, p = iter(matchList), iter([])
        matches = []
        port = set()
        match1 = None
        if watch: view.start()
        while True:
            if watch and match1 is not None: match1.show()
            for i, m in enumerate(matches):
                if not m[0].isAlive():
                    port.discard(m[1])
                    if m[1] == 3000: match1 = None
                    del m, matches[i]
            if len(matches) < threadLen:
                target = next(p, None)
                if target is None:
                    target = next(queue, None)
                    if target is None: break
                    p = pattern(*target)
                    continue
                if replace or not results[target[0][0]].match(target[1][0],
                                                              target[2:])[0]:
                    for po in range(3000, 4000):
                        if po not in port: break
                    matches.append([Practice(Solver(target[0]),
                                    Solver(target[1]), target[2:], po), po])
                    port.add(po)
                    if po == 3000: match1 = matches[-1][0]
                continue
            time.sleep(0.1)
    while len(matches) > 0:
        for i, m in enumerate(matches):
            if not m[0].isAlive(): del m, matches[i]
        time.sleep(0.1)
    print("正常終了しました。")
except KeyboardInterrupt: print("終了します")
finally:
    for m in matches: m[0].cantRecord = True
    if match1 is not None: del match1, m
    del matches
    for result in results.values():
        result.release()
    for p in processes:
        if p.poll() is None: p.kill()
    if watch: view.release()
    interface.release()
