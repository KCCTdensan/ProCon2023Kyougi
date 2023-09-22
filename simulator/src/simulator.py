from collections import deque, defaultdict
directionList = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                (0, -1))
directionSet = ((1, -1, -1), (2, -1, 0), (3, -1, 1), (4, 0, 1), (5, 1, 1),
                (6, 1, 0), (7, 1, -1), (8, 0, -1))
fourDirectionList = ((-1, 0), (0, 1), (1, 0), (0, -1))
fourDirectionSet = ((2, -1, 0), (4, 0, 1), (6, 1, 0), (8, 0, -1))
def inField(board, x, y=None):
    if y is None: x, y = x
    return 0 <= x < board.height and 0 <= y < board.width

def allDirection(board, directions, x, y=None):
    if y is None: x, y = x
    for d in directions:
        pos = (x+d[-2], y+d[-1])
        if not inField(board, *pos): continue
        if len(d) == 2: yield pos
        if len(d) == 3: yield (d[0], *pos)

def distance(board, x, y=None):
    return board.distance(x, y)

def nearest(board, *targets):
    if hasattr(board, 'nearest'): return board.nearest(*targets)
    distance = board
    if len(targets) == 1: targets = targets[0]
    if not hasattr(targets[0], '__len__'): targets = (targets, )
    ans, newDistance = None, 999
    for target in targets:
        if -1 < distance[target[0]][target[1]] < newDistance:
            ans = target
            newDistance = distance[target[0]][target[1]]
    return ans

def calcPoint(board):
    ans = [0, 0, 0]
    other = [0, 0, 0]
    for row in board.all:
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
        self.walls = board["walls"]
        self.territories = board["territories"]
        self.width = board["width"]
        self.height = board["height"]
        self.mason = board["mason"]
        self.structures = board["structures"]
        self.masons = board["masons"]
        self.all = [[Field(*data) for data in zip(*datas)] for datas \
            in zip(self.walls, self.territories, self.structures, self.masons)]
        self.myMasons = [None]*self.mason
        self.otherMasons = [None]*self.mason
        self.castles = []
        for x, row in enumerate(self.all):
            for y, ans in enumerate(row):
                if ans.mason > 0: self.myMasons[ans.mason-1] = [x, y]
                if ans.mason < 0: self.otherMasons[-ans.mason-1] = [x, y]
                if ans.structure == 2: self.castles.append([x, y])
    
        self.log_distance = defaultdict(dict)
        
    def inField(self, x, y=None):
        if y is None: x, y = x
        return 0 <= x < self.height and 0 <= y < self.width

    def allDirection(self, *args):
        return allDirection(self, *args)

    def nearest(self, *args):
        if hasattr(args[0], '__len__'): pos, targets = args[0], args[1:]
        else: pos, targets = args[:2], args[2:]
        if len(targets) == 1: targets = targets[0]
        if not hasattr(targets[0], '__len__'): targets = (targets, )
        ans, newDistance, distance = None, 999, self.distance(pos)
        if distance is None: return None
        for target in targets:
            if -1 < distance[target[0]][target[1]] < newDistance:
                ans = target
                newDistance = distance[target[0]][target[1]]
        return ans
        
    def distance(self, x, y = None):
        if y is None: x, y = x
        if not self.inField(x, y): return None
        if y not in self.log_distance[x]:
            ans = [[-1]*self.width for _ in range(self.height)]
            ans[x][y] = 0
            targets = deque([[x, y]])
            while len(targets) > 0:
                target = targets.popleft()
                now = ans[target[0]][target[1]]+1
                for x, y in self.allDirection(directionList, target):
                    field = self.all[x][y]
                    if ans[x][y] == -1 and field.wall != 2 and \
                       field.structure != 1:
                        ans[x][y] = now
                        targets.appendleft([x, y])
            ans = tuple(tuple(a) for a in ans)
            self.log_distance[x][y] = ans
        return self.log_distance[x][y]

    def calcPoint(self):
        return calcPoint(self)
    
    def __str__(self):
        return "[\n  [{}]\n]".format(
            "],\n  [".join("|".join([*map(str, line)]) for line in self.all))
    def __repr__(self):
        return "[{}]".format(",\n".join(map(repr, self.all)))

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

solverList = {}
def set(name, solver):
    solverList[name] = solver
