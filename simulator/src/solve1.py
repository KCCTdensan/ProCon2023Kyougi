import simulator
from simulator import *
import time
from collections import deque
boolean = True
def solve1(interface, solver):
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        board = matchInfo.board
        movement = []
        castles = []
        for castle in board.castles:
            if board.territories[castle]&1 == 0:
                castles.append(castle)
        walls = board.outline(castles, fourDirectionList)
        targetWall = []
        for target in walls:
            if board.walls[target] != 1:
                targetWall.append(target)
        targets = board.around(targetWall, fourDirectionList)
        for masonId, mason in enumerate(board.myMasons, 1):
            target = board.nearest(mason, targets, destroy=True)
            if solver.flag[masonId] is not None:
                if boolean: target = board.nearest(mason, *board.allDirection(
                                solver.flag[masonId], fourDirectionList),
                                                   destroy=True)
                else: target = solver.flag[masonId]
                if target == mason:
                    if boolean:
                        for i, x, y in board.allDirection(mason,
                                                          fourDirectionSet):
                            if solver.flag[masonId] == (x, y):
                                match board.walls[x][y]:
                                    case 0:
                                        movement.append([2, i])
                                        solver.flag[masonId] = None
                                    case 2:
                                        movement.append([3, i])
                                    case 1:
                                        solver.flag[masonId] = None
                                        break
                        else: continue
                    else: solver.flag[masonId] = None
                else:
                    ans = board.firstMovement(mason, target, destroy=True)
                    if ans is not None: movement.append(ans)
                    else: movement.append([0, 0])
                    continue
            if target is None:
                movement.append([0, 0])
                continue
            elif mason == target:
                for i, x, y in board.allDirection(mason, fourDirectionSet):
                    if board.walls[x][y] == 1 or board.structures[x][y] == 2:
                        continue
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
                ans = board.firstMovement(mason, target)
                if ans is None: movement.append([0, 0])
                else: movement.append(ans)
        interface.postMovement(movement)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve1", solve1)
