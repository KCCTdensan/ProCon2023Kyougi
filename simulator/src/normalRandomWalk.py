#########################################################################
# normalRandomWalk.py                                                   #
# 戦法                                                                  #
# 4方向に壁を建てながらランダムウォークを行う                                #
#########################################################################

import simulator
import time
import random

def buildAround(mason,board):
    for dir,x,y in board.allDirection(mason,simulator.fourDirectionSet):
        if board.walls[x][y]!=1 and board.structures[x][y] != 2:
            if board.walls[x][y] == 0:
                return [2,dir]
            elif board.walls[x][y] == 2:
                return [3,dir]
            break
    return []

def normalRandomWalk(interface, solver):
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
        interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        board = matchInfo.board
        movement = []
        for mason in board.myMasons:
            nextMovement = buildAround(mason,board)
            if  len(nextMovement) != 0:
                movement.append(nextMovement)
                continue
            flag = False            
            x,y = mason
            dirSet = set(list(i for i in range(8)))
            while len(dirSet)>0:
                rnd = random.randint(0,len(dirSet)-1)
                dirList = list(dirSet)
                dx,dy = simulator.eightDirectionList[dirList[rnd]]
                newX = x+dx
                newY = y+dy
                if simulator.inField(board,newX,newY):
                    if board.walls[newX][newY] != 2 and board.structures[newX][newY] != 1 and board.masons[newX][newY] == 0:
                        flag = True
                        movement.append([1,dirList[rnd]+1])
                        break
                dirSet.remove(dirList[rnd])
            
            if not flag:
                movement.append([0,0])

        interface.postMovement(movement)
        turn = matchInfo.turn
        while turn == matchInfo.turn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.set("normalRandomWalk", normalRandomWalk)
