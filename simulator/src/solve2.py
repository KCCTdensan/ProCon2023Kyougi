import simulator
from simulator import *
import time
def solve2(interface, solver):
    while solver.isAlive(): time.sleep(0.1)
simulator.set("solve2", solve2)
