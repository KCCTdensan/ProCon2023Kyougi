import interface, view, simulator
import solveList as solveListPack
import pandas as pd
import sys, os, glob, platform, subprocess, threading, time, traceback
from collections import deque
from simulator import print
mode = 1
# 0: 本番用 1: 練習用 2: solverの管理 3: 結果確認
# solverは拡張子を含めた文字列を書いてください
# 拡張子が異なる同じ名前のファイルを作るとバグります
threadLen = 72
# 並列化処理のレベル
# 同時に実行する試合の最大数です
# 1試合につき3つ(試合終了時たまに6つ)のタスクを並列処理します
recordData = True
# サーバ通信のデータを記録するかどうか選べます
# 試合数が多いとかなりデータ量がとられます また、データ記録処理は結構時間がかかります
recordAll = True
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
        matchList = [["solve1.py","solve1.py"]]
        # フィールドの組み合わせ
        # A～C、11,13,15,17,21,25を指定可能
        # "all"を指定することで全ての組み合わせを試行する
        fieldList = ["all"]
        # ターン数の組み合わせ
        # [30, 90, 150, 200]を指定可能
        # "all"を指定することで全ての組み合わせを試行する
        turnList = ["all"]
        # Falseだと記録済みの組み合わせはスキップする Trueは上書き
        replace = True
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
        changedSolver = [["solve1.py", "all"], ["solve2.py", "all"],
                         ["solve3.py", "all"], ["solve4.py", "all"],
                         ["solve5.py", "all"], ["normalRandomWalk.py", "all"]]
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
allTimeList = [3, 8]
timeList = allTimeList

startPortNumber = 49152

class Result:
    def __init__(self, solver, *, update=False):
        self.name = solver.split('.')[0]
        self.result = {}
        for file in self.all():
            if update:
                self.result[file] = pd.DataFrame(index=allName,
                        columns=fieldList)
            else:
                self.result[file] = pd.read_csv(
                    f"{resultPath}{file}.csv", index_col=0)
                if list(self.result[file].index) != allName:
                    old = set(self.result[file].index)
                    new = [solver for solver in allName if solver in old]
                    self.result[file] = pd.concat([pd.DataFrame(index=allName),
                        self.result[file].loc[new]], axis=1)
            self.result[file] = self.result[file].astype('object')

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
                ans.append([data[0] == "WIN", *map(int, data[1].split(" - "))])
        return ans
    def set(self, other, field, point1, point2, result, *, first=True):
        self.result[f"{self.name}-{field[1]}-{field[2]}"].at[
            f"{other}-{'first' if first else 'second'}",field[0]] \
                = f"{'WIN' if result else 'LOSE'}: {point1} - {point2}"
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
            a = Result(solver[0], update=True); del a
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
            a = Result(solver[0], update=True); del a
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
    for solver in dS:
        for p in glob.glob(f"{resultPath}{solver.split('.')[0]}*.csv"):
            if os.path.isfile(p):
                os.remove(p)
    allList = [solver[0] for solver in [*solverList, *disabledList]]
    allName = sum([[f"{solver}-first", f"{solver}-second"] for solver \
                   in allList], start=[])
    newSolver = [solver[0] for solver in newSolver]
    for solver in newSolver:
        a = Result(solver, update=True); del a
    allList = [solver[0] for solver in [*solverList, *disabledList]]
    setCS = set(cS)
    targetList, allList = allList, []
    for solver in targetList:
        if solver not in setCS: allList.append(solver)
    allName = sum([[f"{solver}-first", f"{solver}-second"] for solver \
                   in allList], start=[])
    for solver in allList:
        a = Result(solver); del a
    
    allList = [solver[0] for solver in [*solverList, *disabledList]]
    allName = sum([[f"{solver}-first", f"{solver}-second"] for solver \
                   in allList], start=[])
    
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

interface.dataBool = recordAll
interface.recordBool = recordData

if mode == 1:
    results = dict([(solver[0], Result(solver[0])) for solver in solverList])

startupinfo = None
if os.name == "nt":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

processes = []
runningThreads = deque([])
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
            print(traceback.format_exc(), file=sys.stderr)
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
        self.returned = None
    def interfaceStart(self, interface, matchId, token, **kwargs):
        try:
            interface.__init__(token, **kwargs)
            interface.setTo(matchId)
        except AssertionError:
            if self.mode == "practice": self.portFailed = True
            else: print(traceback.format_exc(), file=sys.stderr)
        except KeyboardInterrupt: raise KeyboardInterrupt
        except: print(traceback.format_exc(), file=sys.stderr)
    def threading(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        self.thread.append(thread)
        thread.start()
        return thread
    def keep(self, func, *args, **kwargs):
        self.returned = func(*args, **kwargs)
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
        self.mode="real"
        self.cantStart = False
        self.interface = interface.Interface(check=False)
        self.interface1 = interface.Interface(check=False)
        thread = self.threading(self.interfaceStart, self.interface, matchId, token,
                       baseUrl=baseUrl)
        thread1 = self.threading(self.interfaceStart, self.interface1, matchId,
                                token, baseUrl=baseUrl)
        self.solver = solver
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
        self.mode="practice"
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
        self.cantRecord = self.cantStart = self.portFailed = False
        self.process = subprocess.Popen([serverName, "-c",
            f"{fieldPath}{field[2]}{pathSep}{field[0]}-{field[1]}-"
                        f"{field[2]}.txt",
            "-l", f":{port}", "-start", "0s"], startupinfo=startupinfo)
        processes.append(self.process)
        self.field = field
        self.interfaceStart(self.interface, 10, "token1", port=port)
        self.interfaceStart(self.interface1, 10, "token1", port=port)
        self.interfaceStart(self.interface2, 10, "token2", port=port)
        
        self.allTurn = None
        if not self.interface.checked or not self.interface1.checked or \
           not self.interface2.checked:
            self.cantRecord = True
            return
        while self.interface.getMatchInfo() is None:
            if self.interface.released: return
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
    def release(self, *, safety=False):
        self.solver1.release()
        self.solver2.release()
        if safety:
            self.threading(lambda: self.interface.release())
            self.threading(lambda: self.interface1.release())
            self.threading(lambda: self.interface2.release())
        else:
            self.interface.release(safety=False)
            self.interface1.release(safety=False)
            self.interface2.release(safety=False)
    def __del__(self):
        if self.cantStart:
            super().__del__()
            return
        solver1, solver2 = self.solver1, self.solver2
        returned = None
        if not self.cantRecord: returned = self.interface.getMatchInfo()
        self.release(safety=True)
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

matches = []
match1 = None
def practiceStart(target, po):
    global matches, match1
    matches.append([Practice(Solver(target[0]),
                    Solver(target[1]), target[2:], po), po])
    if po == startPortNumber: match1 = matches[-1][0]

try:
    if mode == 1:
        queue, p = iter(matchList), iter([])
        port = set()
        failedPort = set()
        failedMatch = deque([])
        matchesLen = 0
        targetLen = 50
        finishLen = 0
        preFinish = 0
        if watch: view.start()
        while True:
            if watch and match1 is not None: match1.show()
            while len(runningThreads) > 0 and not runningThreads[0].is_alive():
                runningThreads.popleft()
            matchesLen = len(runningThreads) + len(matches)
            if matchesLen < threadLen and matchesLen < targetLen:
                if len(failedMatch) > 0: target = failedMatch.popleft()
                else:
                    target = next(p, None)
                    if target is None:
                        target = next(queue, None)
                        if target is None: break
                        p = pattern(*target)
                        continue
                if replace or not results[target[0][0]].match(target[1][0],
                                                              target[2:])[0]:
                    for po in range(startPortNumber, startPortNumber+10000):
                        if po not in failedPort and po not in port: break
                    runningThreads.append(threading.Thread(
                        target=practiceStart, args=(target, po)))
                    runningThreads[-1].start()
                    port.add(po)
                continue
            matchesLen = len(runningThreads) + len(matches)
            if matchesLen < threadLen:
                print(f"現在の試合数: {matchesLen}")
                print("試合の再読み込み中…")
            aliveDict = {}
            for m in matches:
                aliveDict[m[1]] = m[0].threading(m[0].keep, m[0].isAlive)
            for i, m in enumerate(matches):
                if m[1] not in aliveDict: continue
                aliveDict[m[1]].join()
                if not m[0].returned:
                    if m[0].portFailed:
                        failedPort.add(m[1])
                        solver1 = m[0].solver1.name
                        solver2 = m[0].solver2.name
                        failedMatch.append([[solver1, solverDict[solver1]],
                                            [solver2, solverDict[solver2]],
                                            *m[0].field])
                    port.discard(m[1])
                    if m[1] == startPortNumber: match1 = None
                    del m, matches[i]
                    finishLen += 1
            targetLen = len(runningThreads) + len(matches)
            targetLen -= targetLen%50
            targetLen += 50
            if finishLen >= preFinish+100:
                print("結果を自動保存中…")
                for result in results.values():
                    result.release()
    while len(matches) > 0 or len(runningThreads) > 0:
        if watch and match1 is not None: match1.show()
        while len(runningThreads) > 0 and not runningThreads[0].is_alive():
            runningThreads.popleft()
        for i, m in enumerate(matches):
            if not m[0].isAlive(): del m, matches[i]
        time.sleep(0.1)
        if (len(matches)+len(runningThreads)) % 10 == 0:
            print(f"現在の試合数: {len(matches)+len(runningThreads)}")
    print("正常終了しました。")
except KeyboardInterrupt: print("終了します")
finally:
    try:
        for thread in runningThreads:
            thread.join()
        for m in matches: m[0].cantRecord = True
        m = None
        if match1 is not None: del match1
        del matches
        matches = []
        for result in results.values():
            result.release()
        if watch: view.release()
    except KeyboardInterrupt: print("\nKeyboardInterrupt\n", end="")
    except: print(traceback.format_exc(), file=sys.stderr)
    finally:
        for match in matches: match[0].release(safety=False)
        for p in processes:
            if p.poll() is None: p.kill()
        interface.release()
        if watch: view.release()
