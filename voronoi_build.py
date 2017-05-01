from tkinter import *
import progressbar
from categories import Terrain
from templates import WorldState
from images import icons
from PIL import ImageTk
from scipy.spatial import Voronoi, Delaunay, voronoi_plot_2d
import ghalton
import matplotlib.pyplot as plt

canvas_width = 512
canvas_height = canvas_width
num_points = 64

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

# def draw_point(index, radius=3, canvas=w, world=world):
#     cell = world.get_cell(index)
#     x, y = cell.x, cell.y
#     color = world.get_point_color(index)
#     canvas.create_oval(x-radius,y-radius,x+radius,y+radius, fill=color)

sequencer = ghalton.Halton(2)
points = sequencer.get(num_points)
points = [[point[0] * canvas_width, point[1] * canvas_height] for point in points]

vor = Voronoi(points)

for index, point in enumerate(vor.points):
    region = vor.regions[vor.point_region[index]]
    print(point, region)
voronoi_plot_2d(vor)
plt.show()

# print("Rendering Polygons")
# rbar = progressbar.ProgressBar()
# for index, cell in enumerate(rbar(world.get_cells())):
#     vertcoords = [world.get_vertex(vert) for vert in cell.corners]
#     coords = [int(coord) for coord in vertcoords for coord in coord]
#     r, g, b = world.get_cell_color(index)
#     w.create_polygon(*coords, activefill="#FFFF00", fill=("#%02x%02x%02x" % (r, g, b)))

w.update()
w.postscript(file="test.ps", colormode='color', width=canvas_width, height=canvas_height)

mainloop()
