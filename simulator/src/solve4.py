import simulator
import evaluation
import time
import random
import queue
import copy

countLim = 12
waitTurn = 6

def countFlag(pos,count,countor):
    if len(countor) == 0:return True
    if count - countor[pos[0]][pos[1]] >= countLim or countor[pos[0]][pos[1]] == -1:
        countor[pos[0]][pos[1]] = count
        return True
    else:
        return False

def buildAround(mason,blackList,board):
    if board.walls[mason] == 1:
        return []
    for dir,x,y in board.allDirection(mason,simulator.fourDirectionSet):
        if board.territories[x][y] & 1 == 0 and board.walls[x][y]!=1 and board.structures[x][y] != 2 and board.masons[x][y] == 0 and (x,y) not in blackList:
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
                if board.territories[x][y] & 1 == 0:
                    for x1,y1 in board.allDirection([x,y],simulator.fourDirectionList):
                        if board.walls[x1][y1] != 1 and board.structures[x1][y1] != 2 and board.masons[x][y] != 1:
                            if board.masons[x][y] == 2 and buff == -1:
                                buff = dir
                            elif board.masons[x][y] == 0:
                                return searched[x][y]
    return buff

def randomMove(mason,count,countor,board):
    weight = []
    movement = []
    for dir,x,y in board.allDirection(mason,simulator.directionSet):
        if (board.walls[x][y] == 2 and dir%2 == 1):
            continue
        if board.structures[x][y] != 1 and board.masons[x][y] == 0 and countFlag([x,y],count,countor) == True:
            weight.append(int(evaluation.evaluationPoints([x,y],board,3)))
            movement.append(dir)
    # print("-------------------------")
    # print("mason:",mason)
    # print(weight)
    # print("-------------------------")
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

def flagMove(mason,gorl,board):
    newDistance = board.distance(gorl)
    minCost = 10**9
    nextDir = 0
    x,y = mason[0],mason[1]
    for dir,dx,dy in simulator.directionSet:
        newX,newY = x+dx,y+dy
        if simulator.inField(board,newX,newY) :
            if minCost>newDistance[newX][newY] and newDistance[newX][newY] != -1 and \
            board.masons[newX][newY] == 0:
                minCost = newDistance[newX][newY]
                nextDir = dir
    if minCost != 10**9:
        return [1, nextDir]
    else:
        return [0,0]
        

def solve4(interface, solver):
    oldWalls = dict()
    countor = []
    count = []
    wait = []
    befourPoints = [] 
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        board = matchInfo.board
        turn = matchInfo.turns
        movement = []
        blackList = makeBlackList(oldWalls,board)
        oldWalls = dict()
        buffBoard = copy.copy(board)
        if len(count) == 0:
            count = [0 for i in range(board.mason)]
        if len(countor) == 0:
            countor = [[-1 for i in range(board.height)]for j in range(board.width)]
        if len(wait) == 0:
            wait = [0 for i in range(board.mason)]
        if len(befourPoints) == 0:
            for mason in board.myMasons:
                befourPoints.append(mason)
        for id,mason in enumerate(board.myMasons):
            oldWallsUpdate(mason,oldWalls,buffBoard)
            nextMovement = []
            if befourPoints[id] == mason:
                wait[id]+=1
            else:
                befourPoints[id] = mason
                wait[id] = 0
            if wait[id] < waitTurn:nextMovement = buildAround(mason,blackList,buffBoard)
            if  len(nextMovement) == 0:
                f = False
                if solver.flag[(id-1)%board.mason] is not None:
                    nextMovement = flagMove(mason,solver.flag[(id-1)%board.mason],buffBoard)
                    print(nextMovement)
                    f = True
                    if nextMovement[0] == 0:
                        f = False
                        solver.flag[id] = None
                if f == False:
                    dir = -1
                    if wait[id] < waitTurn:dir = surroundCastel(mason,buffBoard)
                    if dir != -1:
                        nextMovement = [1,dir]
                    else:
                        dir = randomMove(mason,count[id],countor,buffBoard)
                        if dir == -1:
                            tmp = list()
                            dir = randomMove(mason,count[id],tmp,buffBoard)
                            if dir == -1:
                                nextMovement = [0,0]
                            else:
                                nextMovement = [1,dir]
                        else:
                            nextMovement = [1,dir]
            movement.append(nextMovement)
            if nextMovement[0] == 1:
                count[id]+=1
            boardUpdate(mason,nextMovement,buffBoard)

        interface.postMovement(movement)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve4", solve4)

