import simulator
from simulator import *
import time
def solve1(interface, solver):
    matchInfo = interface.getMatchInfo()
    while True:
        if matchInfo is None or not solver.isAlive(): return
        board = matchInfo.board
        distance = Distance(board)
        movement = []
        for mason in board.myMasons:
            castle, newDistance = None, 999
            for c in board.castles:
                if -1 < distance.watch(mason)[c[0]][c[1]] < newDistance:
                    castle, newDistance = c, distance.watch(mason)[c[0]][c[1]]
            if castle is None:
                movement.append([0, 0])
            elif mason == castle:
                for i, x, y in allDirection(board, fourDirectionSet, mason):
                    match board.walls[x][y]:
                        case 0: movement.append([2, i])
                        case 2: movement.append([3, i])
                        case _: continue
                    break
                else: movement.append([0, 0])
            else:
                ans, newDistance = None, distance[castle][mason[0]][mason[1]]
                for i, x, y in allDirection(board, directionSet, mason):
                    if -1 < distance.watch(castle)[x][y] < newDistance:
                        newDistance = distance.watch(castle)[x][y]
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
simulator.set("solve1", solve1)
