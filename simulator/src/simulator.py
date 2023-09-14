from collections import deque, defaultdict
directionList = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                (0, -1))
directionSet = ((1, -1, -1), (2, -1, 0), (3, -1, 1), (4, 0, 1), (5, 1, 1),
                (6, 1, 0), (7, 1, -1), (8, 0, -1))
fourDirectionList = ((-1, 0), (0, 1), (1, 0), (0, -1))
fourDirectionSet = ((2, -1, 0), (4, 0, 1), (6, 1, 0), (8, 0, -1))
def inField(board, x, y=None):
    if y is None: x, y = x
    if not(0 <= x < board.height and 0 <= y < board.width): return False
    return True

def allDirection(board, directions, x, y=None):
    if y is None: x, y = x
    for d in directions:
        pos = (x+d[-2], y+d[-1])
        if not inField(board, *pos): continue
        if len(d) == 2: yield pos
        if len(d) == 3: yield (d[0], *pos)

def distance(board, x, y=None):
    if not inField(board, x, y): return None
    if y is None: x, y = x
    ans = [[-1]*board.width for _ in range(board.height)]
    ans[x][y] = 0
    targets = deque([[x, y]])
    while len(targets) > 0:
        target = targets.pop()
        now = ans[target[0]][target[1]]+1
        for x, y in allDirection(board, directionList, target):
            field = board.all[x][y]
            if ans[x][y] == -1 and field.wall != 2 and field.structure != 1:
                ans[x][y] = now
                targets.appendleft([x, y])
    ans = tuple(tuple(a) for a in ans)
    return ans

class Distance:
    def __init__(self, board, *, inside = -1):
        self.inside = inside
        if inside != -1:
            self.parent = board
            return
        self.board = board
        self.results = defaultdict(dict)
        self.children = {}
    def watch(self, *pos):
        if self.inside != -1:
            return self.parent.watch(self.inside, *pos)
        if len(pos) == 1: pos = pos[0]
        if not hasattr(pos, '__len__') or len(pos) != 2:
            if not hasattr(pos, '__len__'):
                raise IndexError(f"watch({pos})は適切ではありません。")
            pos = tuple(pos)
            raise IndexError(f"watch{pos}は適切ではありません。")
        x, y = pos
        if y in self.results[x]: return self.results[x][y]
        self.results[x][y] = distance(self.board, *pos)
        return self.results[x][y]
    def __getitem__(self, pos):
        if self.inside == -1 and type(pos) == int:
            if pos != -1 and pos not in self.children:
                self.children[pos] = Distance(self, inside=pos)
            return self.children[pos]
        if type(pos) is not tuple: pos = (pos, )
        if not self.watch(*pos): raise IndexError(f"{pos}は範囲外です")
        return self.watch(*pos)
    def __str__(self):
        if self.inside != -1: return f"{self.parent}[{self.inside}]"
        return f"Distance(\n{self.board}\n)"
    def __repr__(self):
        if self.inside != -1: return f"{repr(self.parent)}[{self.inside}]"
        return f"Distance(\n{repr(self.board)}\n)"

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

solverList = {}
def set(name, solver):
    solverList[name] = solver
