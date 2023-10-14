import simulator, view
from simulator import *
import time
from collections import deque
from itertools import product
boolean = True
def solve7(interface, solver):
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        movement = {}
        board = matchInfo.board

        masons = []
        for masonId, mason in enumerate(board.myMasons, 1):
            value = 0
            for m in board.otherMasons:
                value += board.distance(mason, destroy=True)[m]*4*board.height
            for pos in product(range(board.height), range(board.width)):
                if board.walls[pos] == 2 or board.territories[pos] == 2:
                    value += board.distance(mason, destroy=True)[pos]
            masons.append([value, masonId, mason])
        masons.sort()
        if len(masons) < 2: attackMason, defendMason = [], masons
        elif len(masons) < 4: attackMason, defendMason = masons[:1], masons[1:]
        else: attackMason, defendMason = masons[:2], masons[2:]
        attackMason = [mason[1:] for mason in attackMason]
        defendMason = [mason[1:] for mason in defendMason]
        view.viewPos = [mason[1] for mason in attackMason]

        otherWalls = [p for p in product(range(
                board.height), range(board.width)) if board.walls[p] == 2]
        otherCastles = [castle for castle in
                board.castles if board.territories[castle] == 2]
        for masonId, mason in attackMason:
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
                                        movement[masonId] = [2, i]
                                        solver.flag[masonId] = None
                                    case 2:
                                        movement[masonId] = [3, i]
                                    case 1:
                                        solver.flag[masonId] = None
                                        break
                        else: continue
                    else: solver.flag[masonId] = None
                else:
                    ans = board.firstMovement(mason, target, destroy=True)
                    if ans is not None: movement[masonId] = ans
                    else: movement[masonId] = [0, 0]
                    continue
            targetWalls = board.reachAble(mason, otherWalls, mason=True)
            cursedCastles = board.reachAble(mason, otherCastles, mason=True)
            nearestCastle = board.nearest(mason, cursedCastles, destroy=True)
            if nearestCastle and \
               -1 < board.distance(mason, destroy=True)[nearestCastle] < 4:
                targets, targetWalls = deque([nearestCastle]), []
                while len(targets) > 0:
                    target = targets.popleft()
                    for pos in board.allDirection(target, fourDirectionList):
                        if board.structures[pos] == 2: targets.append(pos)
                        else: targetWalls.append(pos)
            target = board.nearest(mason, *board.around(targetWalls,
                                    fourDirectionList), destroy=True)
            if mason == target:
                for i, x, y in board.allDirection(mason, fourDirectionSet):
                    if board.walls[x][y] == 1 or \
                       board.structures[x][y] == 2:
                        continue
                    for pos in board.allDirection(x, y, fourDirectionList):
                        if board.structures[pos] == 2: break
                    else: continue
                    match board.walls[x][y]:
                        case 0: movement[masonId] = [2, i]
                        case 2: movement[masonId] = [3, i]
                        case _: continue
                    break
                else: defendMason.append([masonId, mason])
            elif target is not None:
                ans = board.firstMovement(mason, target)
                if ans is None: defendMason.append([masonId, mason])
                else: movement[masonId] = ans
            else:
                target = board.nearest(mason, board.otherMasons, destroy=True)
                if target is None: defendMason.append([masonId, mason])
                else:
                    ans = board.firstMovement(mason, target)
                    if ans is None: defendMason.append([masonId, mason])
                    else: movement[masonId] = ans
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
        for masonId, mason in defendMason:
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
                                        movement[masonId] = [2, i]
                                        solver.flag[masonId] = None
                                    case 2:
                                        movement[masonId] = [3, i]
                                    case 1:
                                        solver.flag[masonId] = None
                                        break
                        else: continue
                    else: solver.flag[masonId] = None
                else:
                    ans = board.firstMovement(mason, target, destroy=True)
                    if ans is not None: movement[masonId] = ans
                    else: movement[masonId] = [0, 0]
                    continue
            if target is None:
                movement[masonId] = [0, 0]
                continue
            elif mason == target:
                for i, x, y in board.allDirection(mason, fourDirectionSet):
                    if board.walls[x][y] == 1 or board.structures[x][y] == 2:
                        continue
                    for x1, y1 in board.allDirection(x, y, fourDirectionList):
                        if board.structures[x1][y1] == 2: break
                    else: continue
                    match board.walls[x][y]:
                        case 0: movement[masonId] = [2, i]
                        case 2: movement[masonId] = [3, i]
                        case _: continue
                    break
                else: movement[masonId] = [0, 0]
            else:
                ans = board.firstMovement(mason, target)
                if ans is None: movement[masonId] = [0, 0]
                else: movement[masonId] = ans
        ans = []
        for i in range(1, len(board.myMasons)+1):
            ans.append(movement.get(i, [0, 0]))
        interface.postMovement(ans)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve7", solve7)
