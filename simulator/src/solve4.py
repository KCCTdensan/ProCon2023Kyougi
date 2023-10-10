import simulator
import evaluation
import time
import random
import queue

# 何回連続で同じところの壁をいじろうとしたら別の行動に移すようにするか
countLim = 3

def buildAround(mason,buffMv,countMv,board):
    for dir,x,y in board.allDirection(mason,simulator.fourDirectionSet):
        if board.walls[x][y]!=1 and board.structures[x][y] != 2 and board.masons[x][y] == 0:
            if board.walls[x][y] == 0 and (buffMv != [2,dir] or countMv < countLim):
                if buffMv == [2,dir]:
                    countMv+=1
                else:
                    buffMv = [2,dir]
                    countMv = 0
                return [2,dir]
            elif board.walls[x][y] == 2 and (buffMv != [3,dir] or countMv < countLim):
                if buffMv == [3,dir]:
                    countMv+=1
                else:
                    buffMv = [3,dir]
                    countMv = 0
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
    if len(movement) == 0:
        return -1
    else:
        return random.choices(movement,weights=weight)[0]

def solve4(interface, solver):
    matchInfo = interface.getMatchInfo()
    buffMv = []
    countMv = []
    while solver.isAlive() and matchInfo is not None and \
        interface.turn <= matchInfo.turns:
        board = matchInfo.board
        if len(buffMv) == 0:
            buffMv = [[-1,-1] for i in range(board.mason)] 
        if len(countMv) == 0:
            countMv = [0 for i in range(board.mason)]
        movement = []
        for id,mason in enumerate(board.myMasons):
            nextMovement = buildAround(mason,buffMv[id],countMv[id],board)
            if  len(nextMovement) != 0:
                movement.append(nextMovement)
                continue
            dir = surroundCastel(mason,board)
            if dir != -1:
                movement.append([1,dir])
                continue
            dir = randomMove(mason,board)
            if dir == -1:
                movement.append([0,0])
            else:
                movement.append([1,dir])

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
