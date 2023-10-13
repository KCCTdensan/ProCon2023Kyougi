import simulator
from simulator import *
import time
from collections import deque, defaultdict
from itertools import product
import view

def building(board, mason, notProtectedCastles, targets, alreadyTarget):
    target = board.nearest(mason, [target for target in board.around(targets,
            fourDirectionList) if target not in alreadyTarget], destroy=True)
    if target is None:
        # solve1
        target = board.nearest(mason,
            board.around(board.around(notProtectedCastles, fourDirectionList),
                         fourDirectionList),
                               destroy=True)
        if target is None: return [0, 0]
        if mason == target:
            for i, x, y in board.allDirection(mason, fourDirectionSet):
                if board.walls[x][y] == 1 or board.structures[x][y] == 2:
                    continue
                for x1, y1 in board.allDirection(x, y, fourDirectionList):
                    if board.structures[x1][y1] == 2: break
                else: continue
                match board.walls[x][y]:
                    case 0: return [2, i]
                    case 2: return [3, i]
            return [0, 0]
        ans = board.firstMovement(mason, target)
        if ans is None: return [0, 0]
        return ans
    if mason == target:
        alreadyTarget.append(target)
        for i, x, y in board.allDirection(mason, fourDirectionSet):
            if (x, y) not in targets: continue
            match board.walls[x][y]:
                case 0: return [2, i]
                case 2: return [3, i]
        return [0, 0]
    ans = board.firstMovement(mason, target)
    if ans is not None:
        alreadyTarget.append(target)
        return ans
    return [0, 0]

def solve5(interface, solver):
    matchInfo = interface.getMatchInfo()
    board = matchInfo.board
    field = []
    for x in range(board.height):
        for y in range(board.width):
            if board.structures[x][y] != 1: field.append([x, y])
    outline = board.outline(field, fourDirectionList)
    areas = board.area(outline, fourDirectionList)
    areaIndex = Matrix([[-1]*board.width for _ in range(board.height)])
    pointPos = []
    for i, area in enumerate(areas):
        for pos in area:
            if board.structures[pos] != 1: areaIndex[pos] = i

    cantProtectArea = set()
    for i, area in enumerate(areas):
        pointPos.append([])
        for pos in area:
            for x, y in board.allDirection(pos, directionList[4:]):
                if areaIndex[x][y] != -1 and areaIndex[x][y] != i:
                    if board.structures[pos] == 2: cantProtectArea.add(i)
                    else:
                        for pos1 in board.allDirection(pos, fourDirectionList):
                            if board.structures[pos1] != 1: break
                        else: cantProtectArea.add(i)
                        break
            else: continue
            pointPos[-1].append(pos)
    
    protectedArea = set()
    
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        board = matchInfo.board
        
        otherAreas = set()
        for mason in board.otherMasons:
            otherAreas.add(areaIndex[mason])
            
        for i, j in enumerate(pointPos):
            if i not in protectedArea:
                for mason in board.otherMasons:
                    for pos in areas[i]:
                        if board.distance(mason, destroy=True,
                                          other=True)[pos] != -1: break
                    else: continue
                    break
                else: protectedArea.add(i)
        
        nowPointPoses = []
        for i, p in enumerate(pointPos):
            if i in otherAreas or i in protectedArea or i in cantProtectArea:
                continue
            targets = []
            for target in p:
                if board.walls[target] != 1: targets.append(target)
            nowPointPoses.extend(targets)

        protectedAreas = []
        notProtectedCastles = []
        for pos in product(range(board.height), range(board.width)):
            for pos1 in board.allDirection(pos, fourDirectionList):
                for mason in board.otherMasons:
                    if board.distance(mason, destroy=True,
                        other=True)[pos1] != -1: break
                else: continue
                break
            else:
                protectedAreas.append(pos)
                continue
            if board.structures[pos] == 2 and board.territories[pos]&1 == 0:
                notProtectedCastles.append(pos)
        targetArea = []
        for pos in protectedAreas:
            for pos1 in board.allDirection(pos, fourDirectionList):
                for mason in board.myMasons:
                    if board.distance(mason, destroy=True)[pos1] != -1: break
                else: continue
                break
            else: continue
            targetArea.append(pos)
        targetWall = board.frame(targetArea, fourDirectionList)
        targets = []
        for target in targetWall:
            if board.walls[target] != 1: targets.append(target)
        
        broken = defaultdict(set)
        cantMoveTo = defaultdict(set)
        for mason in board.myMasons:
            cantMoveTo[mason[0]].add(mason[1])
        movement = []
        alreadyTarget = []
        for mason in board.myMasons:
            if matchInfo.turn < matchInfo.turns/2:
                i = areaIndex[mason]
                target, value = None, 1 << 60
                for t in board.reachAble(mason,
                        board.around(nowPointPoses, fourDirectionList),
                                         mason=True):
                    v = 1 << 30
                    v *= 1+board.distance(mason, destroy=True)[t]**2
                    for m in board.otherMasons:
                        if board.reverseDistance(t)[m] == -1: continue
                        v /= 1+min(10, board.reverseDistance(t)[m])
                    for x in alreadyTarget:
                        if board.distance(t, destroy=True)[x] == -1: continue
                        v /= 1+min(10, board.distance(t, destroy=True)[x])**0.25
                    if v < value:
                        value = v
                        target = t
                if target is None:
                    movement.append(building(board, mason, notProtectedCastles,
                                    targets, alreadyTarget))
                else:
                    alreadyTarget.append(target)
                    if mason == target:
                        for j, x, y in board.allDirection(mason,
                                                          fourDirectionSet):
                            if (x, y) in nowPointPoses:
                                if board.walls[x][y] == 2 and \
                                   y not in broken[x]:
                                    movement.append([3, j])
                                    broken[x].add(y)
                                    break
                                elif board.walls[x][y] != 1:
                                    movement.append([2, j])
                                    break
                        else: movement.append([0, 0])
                    else:
                        ans = board.firstMovement(mason, target)
                        if ans is None: movement.append([0, 0])
                        else: movement.append(ans)
            else: movement.append(building(board, mason, notProtectedCastles,
                                           targets, alreadyTarget))
            t, d = movement[-1]
            if t == 1:
                d = eightDirectionList[d-1]
                x, y = d[0]+mason[0], d[1]+mason[1]
                if y in cantMoveTo[x]: movement[-1] = [0, 0]
                else: cantMoveTo[x].add(y)
        
        interface.postMovement(movement)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve5", solve5)
