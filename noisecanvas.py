from tkinter import *
import progressbar
import itertools

from templates import WorldState

canvas_width = 256
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

def draw_line_between_points(left_point, right_point, pointlist, canvas=w, world=world):
    leftx, lefty = world.cv(pointlist[left_point][0]), world.cv(pointlist[left_point][1], dim='y')
    rightx, righty = world.cv(pointlist[right_point][0]), world.cv(pointlist[right_point][1], dim='y')
    canvas.create_line(leftx, lefty, rightx, righty)

def draw_point(index, pointlist, radius=3, canvas=w, world=world):
    x, y = world.cv(pointlist[index][0]), world.cv(pointlist[index][1], dim='y')
    x, y = min(canvas_width-1, x), min(canvas_height-1, y)
    r, g, b = world.get_point_color(index)
    canvas.create_oval(x-radius,y-radius,x+radius,y+radius, fill=("#%02x%02x%02x" % (r, g, b)))

print("Rendering Polygons")
rbar = progressbar.ProgressBar()
for centroid, region in enumerate(rbar(world.get_regions())):
    if(len(region) == 0):
        continue
    vertcoords = [world.get_vertex(vert) for vert in region]
    coords = [world.cv(coord) for coord in vertcoords for coord in coord]
    r, g, b = world.get_point_color(centroid)
    w.create_polygon(*coords, activefill="#FFFF00", fill=("#%02x%02x%02x" % (r, g, b)))

# for index, _point in enumerate(world.get_points()):
#     draw_point(index, points)

w.update()
w.postscript(file="render.ps", colormode='color', width=canvas_width, height=canvas_height)

mainloop()
