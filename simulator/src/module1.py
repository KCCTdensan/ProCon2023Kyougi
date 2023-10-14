import simulator
from simulator import *
import time
from collections import deque

class Solve1:
    def __init__(self, interface, solver):
        # init
        pass
    def postMovement(self, interface, solver):
        self.matchInfo = interface.getMatchInfo()
        self.board = self.matchInfo.board
        turn = self.matchInfo.turns
        movement = []
        castles = []
        for castle in self.board.castles:
            if self.board.territories[castle]&1 == 0:
                castles.append(castle)
        walls = self.board.outline(castles, fourDirectionList)
        targetWall = []
        for target in walls:
            if self.board.walls[target] != 1:
                targetWall.append(target)
        targets = self.board.around(targetWall, fourDirectionList)
        for mason in self.board.myMasons:
            target = self.board.nearest(mason, targets, destroy=True)
            if target is None:
                movement.append([0, 0])
                continue
            elif mason == target:
                for i, x, y in self.board.allDirection(mason, fourDirectionSet):
                    if self.board.walls[x][y] == 1 or self.board.structures[x][y] == 2:
                        continue
                    for x1, y1 in self.board.allDirection(x, y, fourDirectionList):
                        if self.board.structures[x1][y1] == 2: break
                    else: continue
                    match self.board.walls[x][y]:
                        case 0: movement.append([2, i])
                        case 2: movement.append([3, i])
                        case _: continue
                    break
                else: movement.append([0, 0])
            else:
                ans = self.board.firstMovement(mason, target)
                if ans is None: movement.append([0, 0])
                else: movement.append(ans)
        return movement