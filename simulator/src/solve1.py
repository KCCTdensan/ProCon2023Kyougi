import simulator
from simulator import *
import time
from collections import deque
def solve1(interface, solver):
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        board = matchInfo.board
        movement = []
        castles = []
        for castle in board.castles:
            if board.territories[castle] != 1:
                castles.append(castle)
        walls = board.outline(castles, fourDirectionList)
        targetWall = []
        for target in walls:
            if board.walls[target] != 1:
                targetWall.append(target)
        targets = board.around(targetWall, fourDirectionList)
        for mason in board.myMasons:
            target = board.nearest(mason, targets, destroy=True)
            if target is None:
                movement.append([0, 0])
                continue
            elif mason == target:
                for i, x, y in board.allDirection(mason, fourDirectionSet):
                    if board.walls[x][y] == 1: continue
                    for x1, y1 in board.allDirection(x, y, fourDirectionList):
                        if board.structures[x1][y1] == 2: break
                    else: continue
                    match board.walls[x][y]:
                        case 0: movement.append([2, i])
                        case 2: movement.append([3, i])
                        case _: continue
                    break
                else: movement.append([0, 0])
            else:
                ans = board.route(mason, target)
                if ans is None: movement.append([0, 0])
                else: movement.append(ans[0])
        interface.postMovement(movement)
        turn = matchInfo.turn
        while turn == matchInfo.turn:
            time.sleep(0.1)
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.set("solve1", solve1)
