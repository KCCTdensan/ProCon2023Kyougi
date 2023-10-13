import simulator
import evaluation
import time
import random
import queue
import copy

def buildAround(mason,blackList,board):
    if board.walls[mason] == 1:
        return []
    for dir,x,y in board.allDirection(mason,simulator.fourDirectionSet):
        if board.territories[x][y] != 1 and board.walls[x][y]!=1 and board.structures[x][y] != 2 and board.masons[x][y] == 0 and (x,y) not in blackList:
            if board.walls[x][y] == 0:
                return [2,dir]
            elif board.walls[x][y] == 2:
                return [3,dir]
            break
    return []

# いくつかの城が連結している場所を囲むための移動方法を探索する関数
# 動いてほしいなぁ...
def surroundCastel(mason,board):
    q = queue.Queue()
    q.put(mason)
    searched = [[-1 for i in range(board.height)]for j in range(board.width)]
    searched[mason[0]][mason[1]] = 0
    while not q.empty():
        now = q.get()
        buff = -1
        for dir,x,y in board.allDirection(now,simulator.directionSet):
            if board.structures[x][y] == 2 and searched[x][y] == -1:
                if searched[now[0]][now[1]] == 0:
                    searched[x][y] = dir
                else:
                    searched[x][y] = searched[now[0]][now[1]]
                q.put([x,y])
                if board.territories[x][y] != 1:
                    for x1,y1 in board.allDirection([x,y],simulator.fourDirectionList):
                        if board.walls[x1][y1] != 1 and board.structures[x1][y1] != 2 and board.masons[x][y] != 1:
                            if board.masons[x][y] == 2 and buff == -1:
                                buff = dir
                            elif board.masons[x][y] == 0:
                                return searched[x][y]
    return buff

def randomMove(mason,board):
    weight = []
    movement = []
    for dir,x,y in board.allDirection(mason,simulator.directionSet):
        if board.walls[x][y] == 2 and dir%2 == 1:
            continue
        if board.structures[x][y] != 1 and board.masons[x][y] == 0:
            weight.append(int(evaluation.evaluationPoints([x,y],board,3)))
            movement.append(dir)
    print("-------------------------")
    print("mason:",mason)
    print(weight)
    print("-------------------------")
    if len(movement) == 0:
        return -1
    else:
        return random.choices(movement,weights=weight)[0]

def makeBlackList(oldWalls,board):
    blackList = dict()
    for p,v in oldWalls.items():
        if (v == 0 and board.walls[p] == 2) or (v == 1 and board.walls[p] == 2):
            blackList[p] = 1
    return blackList

def oldWallsUpdate(mason,oldWalls,board):
    for x,y in board.allDirection(mason,simulator.fourDirectionList):
        oldWalls[(x,y)] = board.walls[x][y]
    return oldWalls

def boardUpdate(mason,movement,board):
    mode = movement[0]
    dir = movement[1]
    if mode == 0:
        return
    next = list(map(sum,zip(mason,simulator.eightDirectionList[dir-1])))
    match mode:
        case 1:
            id = board.masons[mason]
            board.masons[mason] = 0
            board.masons[next] = id
        case 2:
            board.walls[next] = 1
        case 3:
            board.walls[next] = 0
    return

def solve4(interface, solver):
    matchInfo = interface.getMatchInfo()
    oldWalls = dict()
    while solver.isAlive() and matchInfo is not None and \
        interface.turn <= matchInfo.turns:
        board = matchInfo.board
        movement = []
        blackList = makeBlackList(oldWalls,board)
        oldWalls = dict()
        buffBoard = copy.copy(board)
        for id,mason in enumerate(board.myMasons):
            oldWallsUpdate(mason,oldWalls,buffBoard)
            nextMovement = buildAround(mason,blackList,buffBoard)
            if  len(nextMovement) == 0:
                dir = surroundCastel(mason,buffBoard)
                if dir != -1:
                    nextMovement = [1,dir]
                else:
                    dir = randomMove(mason,buffBoard)
                    if dir == -1:
                        nextMovement = [0,0]
                    else:
                        nextMovement = [1,dir]
            movement.append(nextMovement)
            boardUpdate(mason,nextMovement,buffBoard)

        interface.postMovement(movement)
        turn = matchInfo.turn
        while turn == matchInfo.turn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        while matchInfo.myTurn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve4", solve4)
