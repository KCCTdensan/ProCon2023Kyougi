import simulator
from simulator import *
import time
from collections import deque, defaultdict

def building(board, mason, frame, targetPos, walls, targets):
    target = board.nearest(mason, targetPos, destroy=True)
    if target is None:
        # solve1
        target = board.nearest(mason, targets, destroy=True)
        if target is None: return [0, 0]
        if mason == target:
            for i, x, y in board.allDirection(mason, fourDirectionSet):
                if board.walls[x][y] == 1: continue
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
        for i, x, y in board.allDirection(mason, fourDirectionSet):
            if (x, y) not in frame: continue
            match board.walls[x][y]:
                case 0: return [2, i]
                case 2: return [3, i]
    ans = board.firstMovement(mason, target)
    if ans is not None: return ans
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
        for x, y in area:
            areaIndex[x][y] = i
    for i, area in enumerate(areas):
        pointPos.append([])
        for pos in area:
            for x, y in board.allDirection(pos, directionList[4:]):
                if areaIndex[x][y] != -1 and areaIndex[x][y] != i: break
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
        nowPointPos = dict()
        for i, p in enumerate(pointPos):
            targets = []
            for target in p:
                if board.walls[target] != 1: targets.append(target)
            nowPointPos[i] = targets
        if len(areas) != 1:
            for i, j in nowPointPos.items():
                if len(j) == 0: protectedArea.add(i)
        
        newAreas = []
        protectedAreas = []
        for i, area in enumerate(areas):
            if i in protectedArea: protectedAreas.extend(area)
            elif i not in otherAreas: newAreas.extend(area)
        frame = board.frame(protectedAreas, fourDirectionList)
        allFrame = []
        for pos in frame:
            if board.walls[pos] != 1: allFrame.append(pos)
        frameBool = [[False]*board.width for _ in range(board.height)]
        for x, y in allFrame: frameBool[x][y] = True
        frame = []
        for pos in allFrame:
            for x, y in board.allDirection(pos, fourDirectionList):
                if not frameBool[x][y] and board.structures[x][y] != 1: break
            else: continue
            frame.append(pos)
        targetPos = board.around(frame, fourDirectionList)

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

        broken = defaultdict(set)
        cantMoveTo = defaultdict(set)
        for mason in board.myMasons:
            cantMoveTo[mason[0]].add(mason[1])
        movement = []
        for mason in board.myMasons:
            if matchInfo.turn < matchInfo.turns/2 and len(areas) != 1:
                i = areaIndex[mason]
                target = board.nearest(mason,
                            board.around(nowPointPos[i], fourDirectionList),
                            destroy=True)
                target, value = None, 1 << 60
                for t in board.reachAble(mason,
                        board.around(nowPointPos[i], fourDirectionList),
                                         mason=True):
                    v = board.reverseDistance(mason)[t]
                    for m in board.otherMasons:
                        v *= min(10, board.reverseDistance(m)[t])
                    if v < value:
                        value = v
                        target = t
                print(target)
                if i in otherAreas or target is None:
                    if mason in newAreas: newAreas.remove(mason)
                    target = board.nearest(mason, newAreas, destroy=True)
                    if target is None: movement.append(building(board,
                        mason, frame, targetPos, walls, targets))
                    else: movement.append(board.firstMovement(mason, target))
                else:
                    if mason == target:
                        for j, x, y in board.allDirection(mason,
                                                          fourDirectionSet):
                            if (x, y) in nowPointPos[i]:
                                if board.walls[x][y] == 2 and \
                                   y not in broken[x]:
                                    movement.append([3, j])
                                    broken[x].add(y)
                                    break
                                elif board.walls[x][y] != 1:
                                    movement.append([2, j])
                                    nowPointPos[i].remove((x, y))
                                    break
                        else: movement.append([0, 0])
                    else:
                        ans = board.firstMovement(mason, target)
                        if ans is None: movement.append([0, 0])
                        else: movement.append(ans)
            else: movement.append(building(board, mason, frame, targetPos,
                                           walls, targets))
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
