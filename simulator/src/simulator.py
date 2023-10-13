from collections import deque, defaultdict
directionList = ((-1, 0), (0, 1), (1, 0), (0, -1), (1, -1),
                 (-1, -1), (1, 1), (-1, 1))
directionSet = ((2, -1, 0), (4, 0, 1), (6, 1, 0), (8, 0, -1),
                (1, -1, -1), (3, -1, 1), (5, 1, 1), (7, 1, -1))
fourDirectionList = ((-1, 0), (0, 1), (1, 0), (0, -1))
fourDirectionSet = ((2, -1, 0), (4, 0, 1), (6, 1, 0), (8, 0, -1))
eightDirectionList = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0),
                      (1, -1), (0, -1))
eightDirectionSet = ((1, -1, -1), (2, -1, 0), (3, -1, 1), (4, 0, 1), (5, 1, 1),
                     (6, 1, 0), (7, 1, -1), (8, 0, -1))

class Matrix(list):
    def __getitem__(self, target):
        if type(target) is int: return list.__getitem__(self, target)
        while len(target) == 1 and hasattr(target[0], '__len__'):
            target = target[0]
        if any(type(t) is not int for t in target):
            raise TypeError(f"{target}は正しい形式ではありません")
        if len(target) > 2 or len(target) == 0:
            raise IndexError(f"{len(target)}個の引数は許容されません")
        if len(target) == 1: return list.__getitem__(self, target)
        return list.__getitem__(self, target[0])[target[1]]
    def __setitem__(self, target, value):
        if type(target) is int: list.__setitem__(self, target, value)
        while len(target) == 1 and hasattr(target[0], '__len__'):
            target = target[0]
        if any(type(t) is not int for t in target):
            raise TypeError(f"{target}は正しい形式ではありません")
        if len(target) > 2 or len(target) == 0:
            raise IndexError(f"{len(target)}個の引数は許容されません")
        if len(target) == 1: list.__setitem__(self, target, value)
        list.__setitem__(self[target[0]], target[1], value)
    def __copy__(self):
        return Matrix([list(item) for item in self])
    def copy(self):
        return self.__copy__()

class Field:
    def __init__(self, wall, territory, structure, mason):
        self.wall, self.territory, self.structure, self.mason = \
                   wall, territory, structure, mason
    def __str__(self):
        return ",".join(["  MyEn"[self.wall*2:][:2],
                         "  MyEnXX"[self.territory*2:][:2],
                         "    pondfort"[self.structure*4:][:4],
                         f"{self.mason: >2}"])
    def __repr__(self):
        return "".join(["Field({wall: ",
                        ["None", "MyWall", "EnemyWall"][self.wall],
                        ", territory: ",
                        ["None", "MyField", "EnemyField",
                         "BothField"][self.territory],
                        ", structure: ",
                        ["None", "Pond", "Castle"][self.structure],
                        ", mason: ",
                        str(self.mason),
                        "})"])

class Board:
    def __init__(self, board):
        self.walls = Matrix(board["walls"])
        self.territories = Matrix(board["territories"])
        self.width = board["width"]
        self.height = board["height"]
        self.mason = board["mason"]
        self.structures = Matrix(board["structures"])
        self.masons = Matrix(board["masons"])
        self.all = Matrix([Field(*data) for data in zip(*datas)] for datas \
            in zip(self.walls, self.territories, self.structures, self.masons))
        self.myMasons = [None]*self.mason
        self.otherMasons = [None]*self.mason
        self.castles = []
        for x, row in enumerate(self.all):
            for y, ans in enumerate(row):
                if ans.mason > 0: self.myMasons[ans.mason-1] = (x, y)
                if ans.mason < 0: self.otherMasons[-ans.mason-1] = (x, y)
                if ans.structure == 2: self.castles.append((x, y))
    
        self.log_distance = defaultdict(lambda: defaultdict(dict))
        
    def inField(self, x, y=None):
        if y is None: x, y = x
        return 0 <= x < self.height and 0 <= y < self.width

    def allDirection(self, x, y, directions = None):
        if directions is None: x, y, directions = (*x, y)
        for d in directions:
            pos = (x+d[-2], y+d[-1])
            if not self.inField(*pos): continue
            if len(d) == 2: yield pos
            if len(d) == 3: yield (d[0], *pos)
        
    def distance(self, x, y = None, *, destroy=False):
        if y is None: x, y = x
        if not self.inField(x, y): return None
        if destroy not in self.log_distance[x][y]:
            ans = [[-1]*self.width for _ in range(self.height)]
            ans[x][y] = 0
            targets = deque([[x, y]])
            while len(targets) > 0:
                target = targets.popleft()
                now = ans[target[0]][target[1]]+1
                for pos in self.allDirection(target, directionList):
                    field = self.all[pos]
                    if ans[pos[0]][pos[1]] == -1 and field.wall != 2 and \
                       field.structure != 1:
                        ans[pos[0]][pos[1]] = now
                        targets.append(pos)
                if not destroy: continue
                for pos in self.allDirection(target, fourDirectionList):
                    field = self.all[pos]
                    if ans[pos[0]][pos[1]] == -1 and field.wall == 2 and \
                       field.structure != 1:
                        ans[pos[0]][pos[1]] = now+1
                        targets.append(pos)
            ans = tuple(tuple(a) for a in ans)
            self.log_distance[x][y][destroy] = ans
        return Matrix(self.log_distance[x][y][destroy])
        
    def reverseDistance(self, x, y = None):
        if y is None: x, y = x
        if not self.inField(x, y): return None
        if "reverse" not in self.log_distance[x][y]:
            ans = [[-1]*self.width for _ in range(self.height)]
            ans[x][y] = 0
            targets = deque([[x, y]])
            while len(targets) > 0:
                target = targets.popleft()
                now = ans[target[0]][target[1]]+1
                if self.walls[target] == 2:
                    for pos in self.allDirection(target, fourDirectionList):
                        field = self.all[pos]
                        if not(-1 < ans[pos[0]][pos[1]] < now+1) and \
                               field.structure != 1:
                            ans[pos[0]][pos[1]] = now+1
                            targets.append(pos)
                else:
                    for pos in self.allDirection(target, directionList):
                        field = self.all[pos]
                        if ans[pos[0]][pos[1]] == -1 and field.structure != 1:
                            ans[pos[0]][pos[1]] = now
                            targets.append(pos)
            ans = tuple(tuple(a) for a in ans)
            self.log_distance[x][y]["reverse"] = ans
        return Matrix(self.log_distance[x][y]["reverse"])

    def reachAble(self, pos, targets, directions=directionSet, mason=False):
        distance = self.reverseDistance(pos)
        if distance is None: return None
        ans = [target for target in targets if distance[target] != -1 and \
                (not mason or self.masons[target] == 0)]
        if pos not in ans and pos in targets: ans.append(pos)
        return ans

    def nearest(self, *args, destroy=False):
        if hasattr(args[0], '__len__'): pos, targets = args[0], args[1:]
        else: pos, targets = args[:2], args[2:]
        if len(targets) == 1: targets = targets[0]
        if len(targets) == 0: return None
        if not hasattr(targets[0], '__len__'): targets = (targets, )
        ans, newDistance = None, 999
        if destroy: distance = self.reverseDistance(pos)
        else: distance = self.distance(pos)
        if distance is None: return None
        for target in targets:
            if -1 < distance[target] < newDistance:
                ans = target
                newDistance = distance[target]
        return ans

    def outline(self, targets, directions):
        ans = []
        targetBool = [[False]*self.width for _ in range(self.height)]
        for x, y in targets:
            targetBool[x][y] = True
        for target in targets:
            for t in self.allDirection(target, directions):
                if not targetBool[t[-2]][t[-1]]: ans.append(t[-2:])
        return ans

    def around(self, targets, directions):
        ans = []
        targetBool = [[True]*self.width for _ in range(self.height)]
        for target in targets:
            for t in self.allDirection(target, directions):
                if targetBool[t[-2]][t[-1]]: ans.append(t[-2:])
                targetBool[t[-2]][t[-1]] = False
        return ans

    def frame(self, targets, directions):
        ans = []
        targetBool = [[False]*self.width for _ in range(self.height)]
        for x, y in targets:
            targetBool[x][y] = True
        for target in targets:
            poses = list(self.allDirection(target, directions))
            if len(poses) == len(directions):
                for t in poses:
                    if not targetBool[t[-2]][t[-1]]: break
                else: continue
            ans.append(target)
        return ans

    def area(self, outline, directions):
        ans = []
        reached = [[False]*self.width for _ in range(self.height)]
        for x, y in outline:
            reached[x][y] = True
        allPos = ((x, y) for x in range(self.height) for y in range(self.width))
        while True:
            for pos in allPos:
                if not reached[pos[0]][pos[1]]: break
            else: break
            ans.append([])
            targets = deque([pos])
            reached[pos[0]][pos[1]] = True
            ans[-1].append(pos)
            while len(targets) > 0:
                target = targets.popleft()
                for pos in self.allDirection(target, directions):
                    if not reached[pos[-2]][pos[-1]]:
                        targets.append(pos[-2:])
                        ans[-1].append(pos[-2:])
                        reached[pos[-2]][pos[-1]] = True
        return ans

    def route(self, pos, target, directions=directionSet, destroy=True):
        if destroy: distance = self.reverseDistance(target)
        else: distance = self.distance(target)
        if distance[pos] == -1: return None
        ans = []
        while pos != target:
            newDistance = distance[pos]
            nextPos = targetI = None
            for i, x, y in self.allDirection(pos, directions):
                if -1 < distance[x][y] < newDistance:
                    newDistance = distance[x][y]
                    nextPos = (x, y)
                    targetI = i
            if self.walls[nextPos] == 2: ans.append([3, targetI])
            ans.append([1, targetI])
            pos = nextPos
        return ans

    def firstMovement(self, pos, target, directions=directionSet, destroy=True):
        if destroy: distance = self.reverseDistance(target)
        else: distance = self.distance(target)
        if distance[pos] == -1: return None
        ans = nextPos = None
        newDistance = distance[pos]
        for i, x, y in self.allDirection(pos, directions):
            if -1 < distance[x][y] < newDistance:
                newDistance = distance[x][y]
                nextPos = (x, y)
                ans = i
        if self.walls[nextPos] == 2: return [3, ans]
        return [1, ans]

    def calcPoint(self):
        ans = [0, 0, 0]
        other = [0, 0, 0]
        for row in self.all:
            for field in row:
                point = 100 if field.structure == 2 else 30
                if field.territory % 2 == 1:
                    ans[0] += point
                    ans[1+(field.structure!=2)] += point
                if field.territory >= 2:
                    other[0] += point
                    other[1+(field.structure!=2)] += point
                match field.wall:
                    case 1: ans[0] += 10
                    case 2: other[0] += 10
        return [ans, other]
    
    def __str__(self):
        return "[\n  [{}]\n]".format(
            "],\n  [".join("|".join([*map(str, line)]) for line in self.all))
    def __repr__(self):
        return "[{}]".format(",\n".join(map(repr, self.all)))

def inField(board, x, y=None):
    return board.inField(x, y)

def allDirection(board, *args):
    return board.allDirection(*args)

def distance(board, x, y=None):
    return board.distance(x, y)

def nearest(board, *targets):
    return board.nearest(*targets)

def calcPoint(board):
    return board.calcPoint()

class MatchInfo:
    def __init__(self, info, match):
        self.id = info["id"]
        self.turn = info["turn"]
        self.turns = match["turns"]
        self.board = Board(info["board"])
        self.logs = info["logs"]
        self.myTurn = info["turn"]%2 == 1 ^ match["first"]
        self.myLogs = info["logs"][1-int(match["first"])::2]
        self.otherLogs = info["logs"][match["first"]::2]
        self.first = match["first"]
        self.turnTime = match["turnSeconds"]
        self.other = match["opponent"]
    def __str__(self):
        return (f"id: {self.id}\n"
                f"turn: {self.turn}\n"
                 "board:\n"
                f"{self.board}\n"
                f"myTurn: {self.myTurn}\n"
                f"logs: {self.logs}\n"
                f"myLogs: {self.myLogs}\n"
                f"otherLogs: {self.otherLogs}")
    def __repr__(self):
        return "".join(["MatchInfo({id: ",
                        repr(self.id),
                        ", turn: ",
                        repr(self.turn),
                        ", myTurn: ",
                        repr(self.myTurn),
                        ",\nlogs: ",
                        repr(self.logs),
                        ",\nmyLogs: ",
                        repr(self.myLogs),
                        ",\notherLogs: ",
                        repr(self.otherLogs),
                        ",\nboard:\n",
                        repr(self.board)])

_print = print
def print(*args, sep=" ", end="\n", file=None):
    _print(sep.join(map(str, args))+end, end="", file=file)

solverList = {}
def solverSet(name, solver):
    solverList[name] = solver
