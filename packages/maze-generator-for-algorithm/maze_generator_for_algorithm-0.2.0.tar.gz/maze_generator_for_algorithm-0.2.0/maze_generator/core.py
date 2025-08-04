# maze_generator/core.py

import random
import turtle
import time
import json
import pyautogui
from PIL import Image

def listsum(input):
    return sum(sum(row) for row in input)

def generate_maze(sizex, sizey):
    Walls=[[[1,1,1,1] for a in range(sizex)] for b in range(sizey)]
    x=0
    y=0
    visitsum=0
    currentnode=[x,y]
    visited=[[0 for a in range(sizex)] for b in range(sizey)]
    visited[x][y]=1
    visitn=[[x,y]]
    n=0
    while visitsum!=(sizex*sizey):#check to see if finished
        options=[0,0,0,0]
        if x!=0:
            if visited[y][x-1]==0:
                options[0]=1
        if y!=sizey-1:
            if visited[y+1][x]==0:
                options[1]=1
        if x!=sizex-1:
            if visited[y][x+1]==0:
                options[2]=1
        if y!=0:
            if visited[y-1][x]==0:
                options[3]=1

        if options==[0,0,0,0]:
            currentnode=visitn[n-1]
            x=currentnode[0]
            y=currentnode[1]
            n=n-1
        else:
            nodefound=False
            while nodefound==False:
                randomint=random.randint(0,3)
                if options[randomint]==1:
                    if randomint==0:
                        oppisitenode=[currentnode[0]-1,currentnode[1]]
                        Walls[currentnode[1]][currentnode[0]][0]=0
                        Walls[oppisitenode[1]][oppisitenode[0]][2]=0
                    elif randomint==1:
                        oppisitenode=[currentnode[0],currentnode[1]+1]
                        Walls[currentnode[1]][currentnode[0]][1]=0
                        Walls[oppisitenode[1]][oppisitenode[0]][3]=0
                    elif randomint==2:
                        oppisitenode=[currentnode[0]+1,currentnode[1]]
                        Walls[currentnode[1]][currentnode[0]][2]=0
                        Walls[oppisitenode[1]][oppisitenode[0]][0]=0
                    else:
                        oppisitenode=[currentnode[0],currentnode[1]-1]
                        Walls[currentnode[1]][currentnode[0]][3]=0
                        Walls[oppisitenode[1]][oppisitenode[0]][1]=0
                    n=n+1
                    visitn.insert(n,oppisitenode)
                    currentnode=oppisitenode
                    visited[currentnode[1]][currentnode[0]]=1
                    x=currentnode[0]
                    y=currentnode[1]
                    nodefound=True
        visitsum=listsum(visited)
    return(Walls)

def print_maze(sizex, sizey, Walls):
    startx = -380
    starty = -startx
    gridsize = (2 * (-startx)) / sizex
    turtle.clear()
    turtle.speed(0)
    for y in range(sizey):
        for x in range(sizex):
            cell_x = startx + gridsize * x
            cell_y = -starty + gridsize * y
            if Walls[y][x][0] == 1:
                turtle.penup()
                turtle.goto(cell_x, cell_y)
                turtle.pendown()
                turtle.setheading(90)
                turtle.forward(gridsize)
            if Walls[y][x][1] == 1:
                turtle.penup()
                turtle.goto(cell_x, cell_y + gridsize)
                turtle.pendown()
                turtle.setheading(0)
                turtle.forward(gridsize)
            if Walls[y][x][2] == 1:
                turtle.penup()
                turtle.goto(cell_x + gridsize, cell_y)
                turtle.pendown()
                turtle.setheading(90)
                turtle.forward(gridsize)
            if Walls[y][x][3] == 1:
                turtle.penup()
                turtle.goto(cell_x, cell_y)
                turtle.pendown()
                turtle.setheading(0)
                turtle.forward(gridsize)
            turtle.penup()
            turtle.goto(cell_x + gridsize / 2, cell_y + gridsize / 2)
            turtle.pendown()
            turtle.write(f"{y},{x}", align="center", font=("Arial", 10, "normal"))

def apply_wall_config(Walls, path="wall_config.json"):
    try:
        with open(path) as f:
            wall_overrides = json.load(f)
            for key, value in wall_overrides.items():
                row, col = map(int, key.split(','))
                Walls[row][col] = value
        print("Custom wall configuration loaded.")
    except FileNotFoundError:
        print("No custom wall_config.json found.")
    return Walls

def export_images(Walls, sizex, sizey, eps_name="maze_output.eps", png_name="maze_generated_output.png"):
    print_maze(sizex, sizey, Walls)
    ts = turtle.getscreen()
    canvas = ts.getcanvas()
    canvas.postscript(file=eps_name)
    print(f"Maze saved as {eps_name}")
    time.sleep(2)
    root = canvas.winfo_toplevel()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    screenshot = pyautogui.screenshot()
    maze_img = screenshot.crop((x, y, x + w, y + h))
    maze_img.save(png_name)
    print(f"Maze saved as {png_name}")
    turtle.bye()
