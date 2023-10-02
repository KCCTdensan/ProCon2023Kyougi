import tkinter as tk
import threading
from simulator import eightDirectionList
from collections import deque
finishBool = False
data = None

def drawField(canvas, field, x, y, x0, length):
    if max(field.territory, field.structure, field.wall, abs(field.mason)) == 0:
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
                            width=2)
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

def main():
    root = tk.Tk()
    root.geometry("600x700")
    canvas = tk.Canvas(root, width=600, height=700, bg="#eee")
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
                    dif = eightDirectionList[action["dir"]-1]
                    if log["turn"]%2 == 0 ^ data[0].first:
                        myMasons[i] = [myMasons[i][0]-dif[0],
                                       myMasons[i][1]-dif[1]]
                        myHistory[i].appendleft(myMasons[i])
                    else:
                        otherMasons[i] = [otherMasons[i][0]-dif[0],
                                          otherMasons[i][1]-dif[1]]
                        otherHistory[i].appendleft(otherMasons[i])
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

            x1, y1 = 600-x0+4, 50+board.width*length+4
            canvas.create_line(x0-4, 46, x1, 46, x1, y1, x0-4, y1, x0-4, 46,
                               fill = "#ddd", width = 4)
            if len(data) == 2:
                canvas.create_text(300, 650, text=f"{data[1]}を実行中")
            if len(data) == 4:
                canvas.create_text(300, 630, text=f"{data[1]} vs {data[2]}")
                canvas.create_text(300, 670, text=f"{data[3][0]}   {data[3][1]}"
                    f" turns  {data[3][2]} seconds   turn {data[0].turn}")
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
    data = new
def release():
    global finishBool, thread
    finishBool = True
    thread.join()
