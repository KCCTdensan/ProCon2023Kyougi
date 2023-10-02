import simulator
from simulator import *
import time
def solve2(interface, solver):
    matchInfo = interface.getMatchInfo()
    frame = []
    for i in range(matchInfo.board.height):
        frame.append([i, 0])
        frame.append([i, 1])
        frame.append([i, matchInfo.board.width-2])
        frame.append([i, matchInfo.board.width-1])
    for i in range(2, matchInfo.board.width-2):
        frame.append([0, i])
        frame.append([1, i])
        frame.append([matchInfo.board.height-2, i])
        frame.append([matchInfo.board.height-1, i])
    
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        board = matchInfo.board
        movement = []
        for mason in board.myMasons:
            targets = []
            for target in frame:
                for x, y in board.allDirection(target, fourDirectionList):
                    if 0 < x < board.height-1 and 0 < y < board.width-1:
                        continue
                    if board.walls[x][y] != 1: break
                else: continue
                targets.append(target)
            target = board.nearest(mason, targets)
            if target is None:
                movement.append([0, 0])
            elif mason == target:
                for i, x, y in board.allDirection(mason, fourDirectionSet):
                    if 0 < x < board.height-1 and 0 < y < board.width-1:
                        continue
                    match board.walls[x][y]:
                        case 0: movement.append([2, i])
                        case 2: movement.append([3, i])
                        case _: continue
                    break
                else: movement.append([0, 0])
            else:
                ans = None
                newDistance = board.distance(target)[mason[0]][mason[1]]
                for i, x, y in board.allDirection(mason, directionSet):
                    if -1 < board.distance(target)[x][y] < newDistance:
                        newDistance = board.distance(target)[x][y]
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
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.set("solve2", solve2)
