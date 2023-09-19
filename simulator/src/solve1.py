import simulator
from simulator import *
import time
def solve1(interface, solver):
    matchInfo = interface.getMatchInfo()
    while interface.turn <= matchInfo.turns:
        if matchInfo is None or not solver.isAlive(): return
        board = matchInfo.board
        movement = []
        for mason in board.myMasons:
            castle = board.nearest(mason, board.castles)
            if castle is None:
                movement.append([0, 0])
            elif mason == castle:
                for i, x, y in board.allDirection(fourDirectionSet, mason):
                    match board.walls[x][y]:
                        case 0: movement.append([2, i])
                        case 2: movement.append([3, i])
                        case _: continue
                    break
                else: movement.append([0, 0])
            else:
                ans = None
                newDistance = board.distance(castle)[mason[0]][mason[1]]
                for i, x, y in board.allDirection(directionSet, mason):
                    if -1 < board.distance(castle)[x][y] < newDistance:
                        newDistance = board.distance(castle)[x][y]
                        ans = i
                if ans is None: movement.append([0, 0])
                else: movement.append([1, ans])
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
    while solver.isAlive(): time.sleep(0.1)
simulator.set("solve1", solve1)
