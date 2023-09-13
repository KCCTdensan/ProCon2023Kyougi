import tkinter as tk
import threading
from simulator import directionList
from collections import deque
finishBool = False
data = None

def drawField(canvas, field, x, y, x0, length):
    match field.territory:
        case 0: line="white"
        case 1: line="red"
        case 2: line="blue"
        case 3: line="green"
    match field.structure:
        case 0: color="white"
        case 1: color="cyan2"
        case 2: color="yellow"
    canvas.create_rectangle(x0+x*length, 50+y*length, x0+(x+1)*length-2,
                            50+(y+1)*length-2, fill=color, outline=line,
                            width=2)
    match field.wall:
        case 1: color="red"
        case 2: color="blue"
        case _: color=None
    if color is not None:
        canvas.create_polygon(x0+x*length, 50+(y+0.5)*length,
                              x0+(x+0.5)*length, 50+y*length,
                              x0+(x+1)*length, 50+(y+0.5)*length,
                              x0+(x+0.5)*length, 50+(y+1)*length,
                              fill=color, outline=color)
    if field.mason > 0: color="red"
    elif field.mason < 0: color="blue"
    else: return
    canvas.create_oval(x0+(x+0.15)*length, 50+(y+0.15)*length,
                            x0+(x+0.85)*length, 50+(y+0.85)*length,
                            fill=color, outline=color)

def main():
    root = tk.Tk()
    root.geometry("600x700")
    canvas = tk.Canvas(root, width=600, height=700)
    canvas.place(x=0, y=0)
    def update():
        global data, finishBool
        canvas.delete("all")
        if data is not None:
            board = data[0].board
            length = 500//board.height
            x0 = (600-board.height*length)/2
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
                    dif = directionList[action["dir"]-1]
                    if log["turn"]%2 == 0 ^ data[0].first:
                        myMasons[i] = list(map(sum, zip(myMasons[i], dif)))
                        myHistory[i].appendleft(myMasons[i])
                    else:
                        otherMasons[i] = list(map(sum, zip(otherMasons[i], dif)))
                        otherHistory[i].appendleft(otherMasons[i])
            for h in myHistory:
                if len(h) == 1: continue
                args = []
                for p in h:
                    args.append(x0+(p[1]+0.5)*length)
                    args.append(50+(p[0]+0.5)*length)
                canvas.create_line(*args, fill = "tomato",
                                   activewidth = 7, width = 3, arrow=tk.LAST)
            for h in otherHistory:
                if len(h) == 1: continue
                args = []
                for p in h:
                    args.append(x0+(p[1]+0.5)*length)
                    args.append(50+(p[0]+0.5)*length)
                canvas.create_line(*args, fill = "RoyalBlue1",
                                   activewidth = 7, width = 3, arrow=tk.LAST)

            if len(data) == 2:
                canvas.create_text(300, 650, text=f"{data[1]}を実行中")
            if len(data) == 4:
                canvas.create_text(300, 630, text=f"{data[1]} vs {data[2]}")
                canvas.create_text(300, 670, text=f"{data[3]}  "
                                   f"turn{data[0].turn}")
        if finishBool: root.destroy()
        else: root.after(200, update)
    update()
    root.mainloop()
thread = None
def start():
    global thread
    if thread is not None: return
    thread = threading.Thread(target=main)
    thread.start()
def show(*new):
    global data
    data = new
def release():
    global finishBool, thread
    finishBool = True
    thread.join()
