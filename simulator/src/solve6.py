import simulator
from simulator import *
import time
def solve6(interface, solver):
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        board = matchInfo.board
        movement = [[0,0]for i in range(board.mason)]
        if len(matchInfo.otherLogs) != 0:
            matchInfo.otherLogs[-1]["actions"]
            for i in range(board.mason):
                movement[board.mason - 1 - i] = [matchInfo.otherLogs[-1]["actions"][i]["type"],(matchInfo.otherLogs[-1]["actions"][i]["dir"]-1+4)%8+1]
        interface.postMovement(movement)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve6", solve6)