from tkinter import *
import progressbar
from categories import Terrain, Color
from templates import WorldState
from images import icons, update_icon_size
from PIL import ImageTk, Image
import util

canvas_width = 2048
canvas_height = int(canvas_width * (9.0 / 16.0))

icons = update_icon_size(max(1, canvas_width // 1024))

world = WorldState(canvas_width, canvas_height)
world.generate_world()

master = Tk()
frame = Frame(master)
frame.pack()
w = Canvas(
    frame,
    width=canvas_width,
    height=canvas_height,
    scrollregion=(0, 0, canvas_width, canvas_height),
)
hbar = Scrollbar(frame, orient=HORIZONTAL)
hbar.pack(side=BOTTOM, fill=X)
hbar.config(command=w.xview)
vbar = Scrollbar(frame, orient=VERTICAL)
vbar.pack(side=RIGHT, fill=Y)
vbar.config(command=w.yview)
w.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
w.pack(side=LEFT, expand=True, in_=frame)


def draw_line_between_points(left_point, right_point, canvas=w, world=world):
    left, right = world.get_cell(left_point), world.get_cell(right_point)
    canvas.create_line(left.x, left.y, right.x, right.y)
    # canvas.create_text((left.x + right.x)/2, (left.y + right.y)/2, text=world.get_weight_str(left_point, right_point))


def draw_point(index, radius=3, canvas=w, world=world):
    cell = world.get_cell(index)
    x, y = cell.x, cell.y
    color = world.get_point_color(index)
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)


number_of_regions = len(world.get_cells())

print("Rendering Polygons")
rbar = progressbar.ProgressBar()
for index, cell in enumerate(rbar(world.get_cells())):
    vertcoords = [world.get_vertex(vert) for vert in cell.corners if vert != -1]
    coords = [int(coord) for coord in vertcoords for coord in coord]
    r, g, b = world.get_cell_color(index)
    w.create_polygon(*coords, activefill="#FFFF00", fill=("#%02x%02x%02x" % (r, g, b)))

for index, cell in enumerate(world.get_cells()):
    # if(cell.owner is not None and cell.terrain is Terrain.PLAIN and cell.icon is None):
    #     draw_point(index)
    # for neighbor in cell.neighbors:
    # draw_line_between_points(index, neighbor)
    if cell.terrain == Terrain.CITY:
        cell.photo = ImageTk.PhotoImage(icons[cell.icon.value])
        w.create_image(cell.x, cell.y, image=cell.photo)
    elif cell.icon is not None:
        cell.photo = ImageTk.PhotoImage(icons[cell.icon.value])
        w.create_image(cell.x, cell.y, image=cell.photo)
    elif cell.terrain == Terrain.MOUNTAIN:
        cell.photo = ImageTk.PhotoImage(icons["mountain"])
        w.create_image(cell.x, cell.y, image=cell.photo)

for path in world.roads:
    for cell1, cell2 in zip(path[:-1], path[1:]):
        if cell1 < 0 or cell2 < 0:
            continue
        draw_line_between_points(cell1, cell2)

cornersize = canvas_width // 16
w.create_polygon(0, 0, cornersize, 0, 0, cornersize, fill=Color.BROWN.value)
w.create_polygon(
    canvas_width,
    0,
    canvas_width - cornersize,
    0,
    canvas_width,
    cornersize,
    fill=Color.BROWN.value,
)
w.create_polygon(
    canvas_width,
    canvas_height,
    canvas_width - cornersize,
    canvas_height,
    canvas_width,
    canvas_height - cornersize,
    fill=Color.BROWN.value,
)
w.create_polygon(
    0,
    canvas_height,
    cornersize,
    canvas_height,
    0,
    canvas_height - cornersize,
    fill=Color.BROWN.value,
)

w.update()
w.postscript(
    file="render.ps", colormode="color", width=canvas_width, height=canvas_height
)

details = str(world)
print(details)

mainloop()

print("Converting Image")
i = Image.open("render.ps")
i.save("render.png")

with open("world.txt", "w") as outputfile:
    outputfile.write(details)
