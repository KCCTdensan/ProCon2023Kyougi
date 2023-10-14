from module1 import *
from module4 import *

def solve4_2(interface, solver):
    solve1 = Solve1(interface,solver)
    solve4 = Solve4(interface,solver)
    matchInfo = interface.getMatchInfo()
    while solver.isAlive() and matchInfo is not None and \
          interface.turn <= matchInfo.turns:
        while not matchInfo.myTurn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
        preTime = time.time()
        turn = matchInfo.turn
        mode = 1 if turn<30 else 4
        match mode:
            case 1: movement = solve1.postMovement(interface, solver)
            case 4: movement = solve4.postMovement(interface, solver)
        
        interface.postMovement(movement)
        turn = matchInfo.turn
        time.sleep(preTime+matchInfo.turnTime*2-0.2-time.time())
        while turn == matchInfo.turn:
            matchInfo = interface.getMatchInfo()
            if matchInfo is None or not solver.isAlive(): return
    if matchInfo is None: return
    while solver.isAlive(): time.sleep(0.1)
simulator.solverSet("solve4_2", solve4_2)