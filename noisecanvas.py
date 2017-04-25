from noise import snoise2
from tkinter import Tk, mainloop, Canvas, PhotoImage
import numpy as np
from scipy.spatial import Voronoi
import math
from colorsys import hsv_to_rgb
from random import randint

canvas_width = 512
canvas_height = 512
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

master = Tk()


w = Canvas(master, width=canvas_width, height=canvas_height)
w.pack()

img = PhotoImage(width=canvas_width, height=canvas_height)
w.create_image((canvas_width/2, canvas_height/2), image=img, state="normal")

print("Generating Simplex Noise")
for x in range(canvas_width):
    for y in range(canvas_height):
        hScale = simplex_wrapper(x, y, height_offset)
        tScale = simplex_wrapper(x, y, temperature_offset)
        wScale = simplex_wrapper(x, y, water_offset)

        heightmap[x][y] = hScale
        temperature_map[x][y] = min(1, max(0, (tScale*.6 + .3) - 0.5*(dist(0, y, 0, canvas_height/2)/(canvas_height))))
        water_map[x][y] = min(1, wScale * .7 + (dist(x, y, canvas_width/2, canvas_height/2))/(canvas_width))

print("Rendering Bitmap")
for x in range(canvas_width):
    for y in range(canvas_height):
        r, g, b = get_color(heightmap[x][y], temperature_map[x][y], water_map[x][y])
        img.put("#%02x%02x%02x" % (r, g, b) , (x,y))

print("Generating Polygons")
points = np.random.random((num_poi, 2))
vor = Voronoi(points)

print("Normalizing Polygons")
for _ in range(normalization):
    points = []
    for region in vor.regions:
        if(len(region) == 0):
            continue
        newx = 0
        newy = 0
        for point in region:
            point = vor.vertices[point]
            newx += point[0]
            newy += point[1]
        newx /= len(region)
        newy /= len(region)
        points.append(list((newx, newy)))
    vor = Voronoi(points)

print("Rendering Polygons")
for ridge in vor.ridge_vertices:
    point1 = vor.vertices[ridge[0]]
    point2 = vor.vertices[ridge[1]]
    if -1 not in ridge:
        w.create_line(cv(point1[0]), cv(point1[1], dim='y'), cv(point2[0] ), cv(point2[1], dim='y'))

for point in vor.points:
    img.put("#%02x%02x%02x" % (255, 0, 0), (cv(point[0]), cv(point[1], dim='y')))

mainloop()
