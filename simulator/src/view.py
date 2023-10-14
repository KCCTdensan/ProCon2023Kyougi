import tkinter as tk
import threading
from simulator import eightDirectionList
from collections import deque
finishBool = False
data = None
size, height, width, mouseX, mouseY = 850, 850, 950, 0, 0
x0, lenght, mode = 50, 0, 0
moveLimit = None
nowText = "データ指定"
infoText = ""
controlData = []
viewPos = []
def getGUIControl(mason, pos):
    return None
def changeMatch():
    pass

def drawField(canvas, field, x, y, x0, length):
    global controlData
    if max(field.territory, field.structure, field.wall, abs(field.mason)) == 0:
        if (y, x) in controlData:
            canvas.create_line(x0+(x+0.15)*length+2, 50+(y+0.85)*length-2,
                               x0+(x+0.85)*length-2, 50+(y+0.15)*length-2,
                               fill="green2", width = 6)
            canvas.create_line(x0+(x+0.15)*length+2, 50+(y+0.15)*length-2,
                               x0+(x+0.85)*length-2, 50+(y+0.85)*length-2,
                               fill="green2", width = 6)
        if len(controlData) > 0 and \
           (y, x) == data[0].board.myMasons[controlData[0]-1]:
            canvas.create_oval(x0+(x+0.3)*length+2, 50+(y+0.3)*length+2,
                           x0+(x+0.7)*length-2, 50+(y+0.7)*length-2,
                           fill="green2", outline="green2")
        if (y, x) in viewPos:
            canvas.create_oval(x0+(x+0.3)*length+2, 50+(y+0.3)*length+2,
                           x0+(x+0.7)*length-2, 50+(y+0.7)*length-2,
                           fill="pink", outline="pink")
        return

    match field.territory:
        case 0: line="#eee"
        case 1: line="tomato"
        case 2: line="RoyalBlue1"
        case 3: line="green"
    match field.structure:
        case 0: color="#eee"
        case 1: color="cyan2"
        case 2: color="yellow"
    canvas.create_rectangle(x0+x*length+1, 50+y*length+1, x0+(x+1)*length-1,
                            50+(y+1)*length-1, fill=color, outline=line,
                            width=4)
    match field.wall:
        case 1: color="tomato"
        case 2: color="RoyalBlue1"
        case _: color=None
    if color is not None:
        canvas.create_polygon(x0+x*length, 50+(y+0.5)*length,
                              x0+(x+0.5)*length, 50+y*length,
                              x0+(x+1)*length, 50+(y+0.5)*length,
                              x0+(x+0.5)*length, 50+(y+1)*length,
                              fill=color, outline=color, width=0)
    if field.mason > 0:
        if color == "tomato": color = "red"
        else: color="tomato"
    elif field.mason < 0:
        if color == "RoyalBlue1": color = "blue"
        else: color="RoyalBlue1"
    else: return
    canvas.create_oval(x0+(x+0.15)*length+2, 50+(y+0.15)*length+2,
                       x0+(x+0.85)*length-2, 50+(y+0.85)*length-2,
                       fill=color, outline=color)
    if (y, x) in controlData:
        canvas.create_line(x0+(x+0.15)*length+2, 50+(y+0.85)*length-2,
                           x0+(x+0.85)*length-2, 50+(y+0.15)*length-2,
                           fill="green2", width = 6)
        canvas.create_line(x0+(x+0.15)*length+2, 50+(y+0.15)*length-2,
                           x0+(x+0.85)*length-2, 50+(y+0.85)*length-2,
                           fill="green2", width = 6)
    if len(controlData) > 0 and \
       (y, x) == data[0].board.myMasons[controlData[0]-1]:
        canvas.create_oval(x0+(x+0.3)*length+2, 50+(y+0.3)*length+2,
                       x0+(x+0.7)*length-2, 50+(y+0.7)*length-2,
                       fill="green2", outline="green2")
    if (y, x) in viewPos:
        canvas.create_oval(x0+(x+0.3)*length+2, 50+(y+0.3)*length+2,
                       x0+(x+0.7)*length-2, 50+(y+0.7)*length-2,
                       fill="pink", outline="pink")
    

def selecting():
    global mode, mouseX, mouseY, size, nowText, infoText, controlData, height, \
           width, length, data, flag, getGUIControl
    board = data[0].board
    match mode:
        case 0:
            if width/2+25 <= mouseX <= width/4*3-25 and \
               height-90 <= mouseY <= height-60:
                controlData = []
                infoText = "職人を指定してください"
                nowText = "キャンセル"
                mode = 1
            if width/4*3+25 <= mouseX <= width-25 and \
               height-90 <= mouseY <= height-60:
                controlData = []
                infoText = "表示する試合を変更しました"
                changeMatch()
        case 1:
            if width/2+25 <= mouseX <= width/4*3-25 and \
               height-90 <= mouseY <= height-60:
                infoText = "キャンセルしました"
                nowText = "データ指定"
                mode = 0
            if x0 <= mouseX < width-x0 and \
               50 <= mouseY < 50+board.height*length:
                pos = ((mouseY-50)//length, int(mouseX-x0)//length)
                if board.masons[pos] > 0:
                    controlData.append(board.masons[pos])
                    flag = getGUIControl()
                    controlData.append(flag[controlData[0]])
                    infoText = "対象の地点を指定してください"
                    nowText = "キャンセル"
                    mode = 2
        case 2:
            if width/2+25 <= mouseX <= width/4*3-25 and \
               height-90 <= mouseY <= height-60:
                infoText = "キャンセルしました"
                nowText = "データ指定"
                mode = 0
            elif x0 <= mouseX < width-x0 and \
               50 <= mouseY < 50+board.height*length:
                controlData[1] = ((mouseY-50)//length, int(mouseX-x0)//length)
                flag = getGUIControl()
                flag[controlData[0]] = controlData[1]
                infoText = "送信しました"
                nowText = "データ指定"
                mode = 0
            else:
                flag[controlData[0]] = None
                controlData.pop()
                infoText = "この職人の目的地を消去しました"
                nowText = "データ指定"
                mode = 0

def main():
    global height, width
    root = tk.Tk()
    height, width = size+100, size
    root.geometry(f"{width}x{height}")
    canvas = tk.Canvas(root, width=width, height=height, bg="#eee")
    canvas.place(x=0, y=0)
    def mouseReload(event):
        global mouseX, mouseY
        mouseX, mouseY = event.x, event.y
    def mouseClicked(event):
        selecting()
    canvas.bind("<Motion>", mouseReload)
    canvas.bind("<Button-1>", mouseClicked)
    def update():
        global data, finishBool, nowText, infoText, x0, length
        canvas.delete("all")
        if data is not None:
            board = data[0].board
            length = (width-100)//board.height
            x0 = (width-board.height*length)/2
            for y, row in enumerate(board.all):
                for x, field in enumerate(row):
                    drawField(canvas, field, x, y, x0, length)
            myMasons = board.myMasons.copy()
            myHistory = [deque([pos]) for pos in myMasons]
            otherMasons = board.otherMasons.copy()
            otherHistory = [deque([pos]) for pos in otherMasons]
            for log in data[0].logs[::-1]:
                for i, action in enumerate(log["actions"]):
                    if not action["succeeded"] or action["type"] != 1: continue
                    dif = eightDirectionList[action["dir"]-1]
                    if log["turn"]%2 == 0 ^ data[0].first:
                        myMasons[i] = [myMasons[i][0]-dif[0],
                                       myMasons[i][1]-dif[1]]
                        myHistory[i].appendleft(myMasons[i])
                    else:
                        otherMasons[i] = [otherMasons[i][0]-dif[0],
                                          otherMasons[i][1]-dif[1]]
                        otherHistory[i].appendleft(otherMasons[i])
            if moveLimit is not None and moveLimit != -1:
                myHistory = myHistory[:moveLimit]
                otherHistory = otherHistory[:moveLimit]
            for h in myHistory:
                if len(h) == 1: continue
                args = []
                for p in h:
                    args.append(x0+(p[1]+0.5)*length)
                    args.append(50+(p[0]+0.5)*length)
                canvas.create_line(*args, fill = "orange",
                                   activewidth = 7, width = 3, arrow=tk.LAST)
            for h in otherHistory:
                if len(h) == 1: continue
                args = []
                for p in h:
                    args.append(x0+(p[1]+0.5)*length)
                    args.append(50+(p[0]+0.5)*length)
                canvas.create_line(*args, fill = "SlateBlue2",
                                   activewidth = 7, width = 3, arrow=tk.LAST)

            x1, y1 = width-x0+4, 50+board.width*length+4
            canvas.create_line(x0-4, 46, x1, 46, x1, y1, x0-4, y1, x0-4, 46,
                               fill = "#ddd", width = 4)
            if not hasattr(data, '__len__') or len(data) == 0: pass
            elif data[-1] == "real" and len(data) == 3:
                canvas.create_text(width/4, height-70,
                    text=f"{data[1]} vs {data[0].other}")
                points = board.calcPoint()
                canvas.create_text(width/4, height-50,
                    text=f"{points[0][0]} - {points[1][0]}")
                canvas.create_text(width/4, height-30,
                    text=f"{data[0].turns} turns  "
                         f"{data[0].turnTime} seconds   turn {data[0].turn}")
                canvas.create_rectangle(width/2+25, height-90,
                                        width/4*3-25, height-60, fill="green3",
                                        outline="green3", activefill="green2")
                canvas.create_rectangle(width/4*3+25, height-90,
                                        width-25, height-60, fill="red3",
                                        outline="red3", activefill="red2")
                canvas.create_text(width/8*7, height-75, text="変更")
                
            elif data[-1] == "preview" and len(data) == 3:
                canvas.create_text(width/2, height-70,
                    text=f"{data[1]} vs {data[0].other}")
                points = board.calcPoint()
                canvas.create_text(width/2, height-50,
                    text=f"{points[0][0]} - {points[1][0]}")
                canvas.create_text(width/2, height-30,
                    text=f"{data[0].turns} turns  "
                         f"{data[0].turnTime} seconds   turn {data[0].turn}")
            elif len(data) == 5:
                canvas.create_text(width/2, height-70, text=f"{data[1]} vs {data[2]}")
                points = board.calcPoint()
                canvas.create_text(width/2, height-50,
                    text=f"{points[0][0]} - {points[1][0]}")
                canvas.create_text(width/2, height-30,
                    text=f"{data[3][0]}   {data[3][1]} turns  "
                         f"{data[3][2]} seconds   turn {data[0].turn}")
        if not hasattr(data, '__len__') or len(data) == 0: pass
        elif data[-1] == "real" and len(data) == 3:
            canvas.delete("control")
            canvas.create_text(width/8*5, height-75, text=nowText,
                               tag="control")
            canvas.create_text(width/4*3, height-25, text=infoText,
                               tag="control")
        if finishBool: root.destroy()
        else: root.after(200, update)
    update()
    root.mainloop()
thread = None
def start():
    global thread, finishBool
    if thread is not None and thread.is_alive(): return
    finishBool = False
    thread = threading.Thread(target=main)
    thread.start()
def show(*new):
    global data
    if new[0] is None: return
    data = new
def release():
    global finishBool, thread
    finishBool = True
    if thread is not None: thread.join()
