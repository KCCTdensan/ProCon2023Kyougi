#########################################################################
# solve3.py                                                             #
# 戦法                                                                  #
# 隣の職人の初期位置まで最短距離で移動しながら壁を建築する              #
#                                                                       #
# 隣の職人までの移動経路は                                              #
# 1.隣の職人から自分の位置まで幅優先探索を行う                          #
# 2.得られた距離が小さくなるように移動を行う                            #
#########################################################################

import simulator
import time

# 時計回りに隣の職人を見つける(はずの)関数
# res[移動する職人のid] = 移動先の職人のid
# idは0-index
def nextMason(initMasons,board):
    used = set()
    pair = dict()
    res = []
    for i in range(len(initMasons)):
        pair[i]=-1
    for i,mason1 in enumerate(initMasons):
        newDistance = board.distance(mason1)
        minCost = 10**9
        id = -1
        for j,mason2 in enumerate(initMasons):
            if i == j:
                continue
            if minCost>newDistance[mason2[0]][mason2[1]] and j not in used and pair[j] != i:
                minCost = newDistance[mason2[0]][mason2[1]]
                id = j
        res.append(id)
        used.add(id)
        pair[i] = id
    return res
            
def move(id,mason,initMasons,nextMasons,board):
    newDistance = board.distance(initMasons[nextMasons[id]])
    minCost = 10**9
    nextDir = 0
    x,y = mason[0],mason[1]
    for dir,dx,dy in simulator.directionSet:
        newX,newY = x+dx,y+dy
        if simulator.inField(board,newX,newY) :
            if minCost>newDistance[newX][newY] and newDistance[newX][newY] is not -1 and \
            board.masons[newX][newY] is 0:
                minCost = newDistance[newX][newY]
                nextDir = dir
    if minCost != 10**9:
        return [1, nextDir]
    else:
        return [0,0]
    
# [x,y]の周囲8マスに自分が建てた壁があるかを判定
def wallDitect(id,x,y,wallsId,board):
    for dir,dx,dy in simulator.directionSet:
        newX,newY = x+dx,y+dy
        if simulator.inField(board,newX,newY):
            if wallsId[newX][newY] == id:
                return True
    return False

def solve3(interface, solver):
    matchInfo = interface.getMatchInfo()
    initMasons = [] # 職人の初期位置
    nextMasons = [] # 隣の職人のid (0-index)
    oldDir = [] # 前のターンに壁を建てたかどうかをboolで格納
    wallsId = []
    while solver.isAlive() and matchInfo is not None and \
        interface.turn <= matchInfo.turns:
        board = matchInfo.board
        movement = []
        if not initMasons:
            initMasons = board.myMasons.copy()
        if not nextMasons:
            nextMasons = nextMason(initMasons,board)
            print("----------nextMasons----------")
            print(nextMasons)
            print("------------------------------")
        if not oldDir:
            oldDir = [False]*board.mason
        if not wallsId:
            wallsId = [[-1 for i in range(board.width)] for j in range(board.height)]
        for i,mason in enumerate(board.myMasons):
            if oldDir[i]:
                # 移動関連
                nextMove = move(i,mason,initMasons,nextMasons,board)
                movement.append(nextMove)
                if nextMove[0] == 1:
                    oldDir[i] = False
            else:
                x,y = mason[0],mason[1]
                flag = False
                for flag2 in range(2):
                    for dir,dx,dy in simulator.fourDirectionSet:
                        newX,newY = x+dx,y+dy
                        if simulator.inField(board,newX,newY):
                            if board.structures[newX][newY] != 2 and (wallDitect(i,newX,newY,wallsId,board) or flag2 == 1):
                                if board.walls[newX][newY] == 1:
                                    # oldDir[i] = True
                                    # flag = True
                                    # nextMove = move(i,mason,initMasons,nextMasons,board)
                                    # movement.append(nextMove)
                                    # if nextMove[0] != 0:
                                    #     oldDir[i] = False
                                    continue
                                elif board.walls[newX][newY] == 2:
                                    movement.append([3,dir])
                                    flag = True
                                    break
                                elif board.walls[newX][newY] == 0:
                                    movement.append([2,dir])
                                    wallsId[newX][newY] = i
                                    flag = True
                                    oldDir[i] = True
                                    break
                        if flag:
                            break
                    if flag:
                        break
                if not flag:
                    movement.append([0,0])


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
simulator.set("solve3", solve3)