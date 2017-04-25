from noise import snoise2
from tkinter import *
import numpy as np
from scipy.spatial import Voronoi
import math
from colorsys import hsv_to_rgb
from random import randint
import progressbar

canvas_width = 2048
canvas_height = canvas_width
freq = canvas_width / 2
num_poi = int(256 * math.log(max(canvas_width, canvas_height), 2))
water_threshhold = 0.9
freezing = 0.1
normalization = 7

heightmap, temperature_map, water_map = np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height))
height_offset, temperature_offset, water_offset = randint(0, canvas_width*128), randint(0, canvas_width*128), randint(0, canvas_width*128)

def cv(float_val, dim='x'):
    if(dim=='y'):
        return max(0, min(canvas_height, int(float_val * canvas_height)))
    return max(0, min(canvas_width, int(float_val * canvas_width)))

def dist(_x, _y, _X, _Y):
    return math.sqrt((_x - _X)**2+(_y - _Y)**2)

def get_color(height, temperature, water):
    if(temperature < freezing):
        return 255, 255, 255
    if(water > water_threshhold):
        return 50, 50, 255
    _r, _g, _b = hsv_to_rgb((50+60*height)/ 360, (temperature + 1)/2, 165/240)
    return int(_r*255), int(_g*255), int(_b*255)

def simplex_wrapper(_x, _y, offset):
    return (snoise2((_x + offset) / freq, (_y + offset) / freq) + 1) / 2

def get_centroid(_region):
    _newx = 0
    _newy = 0
    for _point in _region:
        _point = vor.vertices[_point]
        _newx += _point[0]
        _newy += _point[1]
    _newx /= len(_region)
    _newy /= len(_region)
    return _newx, _newy

master = Tk()
frame = Frame(master)
frame.grid(row=0,column=0)
frame.pack()
w = Canvas(frame, width=canvas_width, height=canvas_height, scrollregion=(0,0,canvas_width,canvas_height))
hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=w.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=w.yview)
w.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
w.pack(side=LEFT,expand=True, in_=frame)

img = PhotoImage(width=canvas_width, height=canvas_height)
w.create_image((canvas_width/2, canvas_height/2), image=img, state="normal")

print("Generating Simplex Noise")
xbar = progressbar.ProgressBar()
for x in xbar(range(canvas_width)):
    for y in range(canvas_height):
        hScale = simplex_wrapper(x, y, height_offset)
        tScale = simplex_wrapper(x, y, temperature_offset)
        wScale = simplex_wrapper(x, y, water_offset)

        heightmap[x][y] = hScale
        temperature_map[x][y] = min(1, max(0, (tScale*.6 + .3) - 0.5*(dist(0, y, 0, canvas_height/2)/(canvas_height))))
        water_map[x][y] = min(1, wScale * .7 + (dist(x, y, canvas_width/2, canvas_height/2))/(canvas_width))

print("Generating Polygons")
points = np.random.random((num_poi, 2))
vor = Voronoi(points)

print("Normalizing Polygons")
for _ in range(normalization):
    points = []
    for region in vor.regions:
        if(len(region) == 0):
            continue
        newx, newy = get_centroid(region)
        points.append(list((newx, newy)))
    vor = Voronoi(points)

print("Rendering Polygons")
for region in vor.regions:
    if(len(region) == 0):
        continue
    vertcoords = [vor.vertices[vert] for vert in region]
    coords = [cv(coord) for coord in vertcoords for coord in coord]
    x, y = get_centroid(region)
    x, y = min(canvas_width - 1, cv(x)), min(canvas_height - 1, cv(y, dim=y))
    r, g, b = get_color(heightmap[x][y], temperature_map[x][y], water_map[x][y])
    w.create_polygon(*coords, activefill="#FFFF00", fill=("#%02x%02x%02x" % (r, g, b)))

for point in vor.points:
    img.put("#%02x%02x%02x" % (255, 0, 0), (cv(point[0]), cv(point[1], dim='y')))

w.update()
w.postscript(file="render.ps", colormode='color', width=canvas_width, height=canvas_height)

mainloop()
