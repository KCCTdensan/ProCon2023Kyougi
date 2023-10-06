import simulator
import evaluation
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
    while solver.isAlive() and matchInfo is not None and \
        interface.turn <= matchInfo.turns:
        board = matchInfo.board
        movement = []

        for mason in board.myMasons:
            nextMovement = buildAround(mason,board)
            if  len(nextMovement) != 0:
                movement.append(nextMovement)
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
simulator.set("solve4", solve4)