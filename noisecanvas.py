from tkinter import *
import progressbar
from categories import Terrain
from templates import WorldState
from images import icons
from PIL import ImageTk

canvas_width = 1024
canvas_height = canvas_width

world = WorldState(canvas_width, canvas_height)
world.generate_world()

master = Tk()
frame = Frame(master)
frame.pack()
w = Canvas(frame, width=canvas_width, height=canvas_height, scrollregion=(0,0,canvas_width,canvas_height))
hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=w.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=w.yview)
w.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
w.pack(side=LEFT, expand=True, in_=frame)

def draw_line_between_points(left_point, right_point, canvas=w, world=world):
    left, right = world.get_cell(left_point), world.get_cell(right_point)
    canvas.create_line(left.x, left.y, right.x, right.y)

def draw_point(index, radius=3, canvas=w, world=world):
    cell = world.get_cell(index)
    x, y = cell.x, cell.y
    r, g, b = world.get_point_color(index)
    canvas.create_oval(x-radius,y-radius,x+radius,y+radius, fill=("#%02x%02x%02x" % (r, g, b)))

number_of_regions = len(world.get_cells())

print("Rendering Polygons")
rbar = progressbar.ProgressBar()
for index, cell in enumerate(rbar(world.get_cells())):
    if(len(cell.corners) == 0):
        centroid -= 1
        continue
    vertcoords = [world.get_vertex(vert) for vert in cell.corners]
    coords = [world.cv(coord) for coord in vertcoords for coord in coord]
    r, g, b = world.get_cell_color(index)
    w.create_polygon(*coords, activefill="#FFFF00", fill=("#%02x%02x%02x" % (r, g, b)))

for index, cell in enumerate(world.get_cells()):
    if(cell.owner is not None and cell.terrain is not Terrain.CITY):
        draw_point(index)
    # for neighbor in cell.neighbors:
        # draw_line_between_points(index, neighbor)
    if(cell.terrain == Terrain.CITY):
        cell.photo = ImageTk.PhotoImage(icons['tower'])
        w.create_image(cell.x, cell.y, image=cell.photo)
    elif(cell.terrain == Terrain.MOUNTAIN):
        cell.photo = ImageTk.PhotoImage(icons['mountain'])
        w.create_image(cell.x, cell.y, image=cell.photo)

w.update()
w.postscript(file="render.ps", colormode='color', width=canvas_width, height=canvas_height)

mainloop()
