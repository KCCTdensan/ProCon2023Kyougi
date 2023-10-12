import simulator as sim

def wallsPoints(pos,board):
    count = 0
    pointDict = dict([(0,50),(1,1000),(2,800),(3,100),(4,20),(5,10),(6,1),(7,1),(8,0)])
    for x,y in board.allDirection(pos,sim.directionList):
        if board.walls[x][y] == 1 or board.territories[x][y] == 1:
            count+=1
    return pointDict[count]

def isCastel(pos,board):
    if board.structures[pos[0]][pos[1]] == 2 and board.territories[pos[0]][pos[1]] != 1:
        return 5000
    else:
        return 0

def isTerritorie(pos,board):
    if board.walls[pos[0]][pos[0]] == 1 or board.territories[pos[0]][pos[1]] == 1:
        return 0
    else:
        return 500
    
def lakeStop(pos,board):
    for i in range(4):
        x1 = sim.fourDirectionList[i%4][0]+pos[0]
        y1 = sim.fourDirectionList[i%4][1]+pos[1]
        x2 = sim.fourDirectionList[(i+1)%4][0]+pos[0]
        y2 = sim.fourDirectionList[(i+1)%4][1]+pos[1]
        if sim.inField(board,x1,y1) and sim.inField(board,x2,y2):
            if board.structures[x1][y1] == 1 and board.structures[x2][y2] == 1:
                    return 2000
    return 0
    
EFList = [wallsPoints,isCastel,isTerritorie,lakeStop]

def evaluationPoints(pos,board,num = 0):
    res = 0
    for func in EFList:
        res += func(pos,board)
    if num >0:
        for x,y in board.allDirection(pos,sim.directionList):
            if board.structures[x][y] != 1 and board.walls[x][y] != 2:
                res += evaluationPoints([x,y],board,num-1)*0.3
    return res