from collections import deque
directionList = ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1),
                (-1, 0))
directionSet = ((1, -1, -1), (2, 0, -1), (3, 1, -1), (4, 1, 0), (5, 1, 1),
                (6, 0, 1), (7, -1, 1), (8, -1, 0))
fourDirectionList = ((0, -1), (1, 0), (0, 1), (-1, 0))
fourDirectionSet = ((2, 0, -1), (4, 1, 0), (6, 0, 1), (8, -1, 0))
def inField(board, x, y=None):
    if y is None: x, y = x
    if not(0 <= x < board.height and 0 <= y < board.width): return False
    return True

def distance(board, x, y=None):
    if y is None: x, y = x
    ans = [[-1]*board.width for _ in range(board.height)]
    ans[x][y] = 0
    targets = deque([[x, y]])
    while len(targets) > 0:
        target = targets.pop()
        now = ans[target[0]][target[1]]+1
        for dx, dy in directionList:
            x, y = target[0]+dx, target[1]+dy
            if not inField(board, x, y): continue
            field = board.all[x][y]
            if ans[x][y] == -1 and field.wall != 2 and field.structure != 1:
                ans[x][y] = now
                targets.appendleft([x, y])
    return ans

def calcPoint(board):
    ans = [0, 0, 0]
    opponent = [0, 0, 0]
    for row in board.all:
        for field in row:
            point = 100 if field.structure == 2 else 30
            if field.territory % 2 == 1:
                ans[0] += point
                ans[1+(field.structure!=2)] += point
            if field.territory >= 2:
                opponent[0] += point
                opponent[1+(field.structure!=2)] += point
            match field.wall:
                case 1: ans[0] += 10
                case 2: opponent[0] += 10
    return [ans, opponent]

solverList = {}
def set(name, solver):
    solverList[name] = solver
