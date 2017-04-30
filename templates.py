from random import choice
import numpy as np
from scipy.spatial import Voronoi, Delaunay
from noise import snoise2
from colorsys import hsv_to_rgb
from random import randint
import progressbar
from util import dist
import math

class Cell(object):

    def __init__(self, x, y, t, h, w, corners=None):
        self.point = point
        self.neighbors = []
        self.temperature = t
        self.height = h
        self.water = w
        self.x = x
        self.y = y
        self.corners = corners

    def __repr__(self):
        return "Cell {p} at ({x}, {y})".format(p=self.point, x=self.x, y=self.y)

class WorldState(object):

    def __init__(self, canvas_width=2048, canvas_height=2048, water_threshhold=0.9, freezing_temp=0.1, normalization_steps=7):
        self.width = canvas_width
        self.height = canvas_height

        self.heightmap, self.temperature_map, self.water_map = np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height))
        self.height_offset, self.temperature_offset, self.water_offset = randint(0, canvas_width*128), randint(0, canvas_width*128), randint(0, canvas_width*128)

        self.num_points = int(256 * math.log(max(canvas_width, canvas_height), 2))
        self.adjacency_matrix = np.zeros((self.num_points, self.num_points))
        self.cells = []

        self.water_threshhold = water_threshhold
        self.freezing_temp = freezing_temp
        self.normalization_steps = normalization_steps

    def simplex_wrapper(self, _x, _y, offset):
        return (snoise2((_x + offset) / (self.width / 2), (_y + offset) / (self.height / 2)) + 1) / 2

    def cv(self, float_val, dim='x'):
        if(dim=='y'):
            return max(0, min(self.height, int(float_val * self.height)))
        return max(0, min(self.width, int(float_val * self.width)))

    def generate_world(self):
        print("Generating Simplex Noise")
        xbar = progressbar.ProgressBar()
        for x in xbar(range(self.width)):
            for y in range(self.height):
                hScale = self.simplex_wrapper(x, y, self.height_offset)
                tScale = self.simplex_wrapper(x, y, self.temperature_offset)
                wScale = self.simplex_wrapper(x, y, self.water_offset)

                self.heightmap[x][y] = hScale
                self.temperature_map[x][y] = min(1, max(0, (tScale*.6 + .3) - 0.5*(dist(0, y, 0, self.height/2)/(self.height))))
                self.water_map[x][y] = min(1, wScale * .7 + (dist(x, y, self.width/2, self.height/2))/(self.width))

        print("Generating Polygons")
        self.points = np.random.random((self.num_points, 2))
        self.voronoi = Voronoi(self.points)

        print("Normalizing Polygons")
        for _ in range(self.normalization_steps):
            _points = []
            for region in self.voronoi.regions:
                if(len(region) == 0):
                    continue
                newx, newy = self.get_centroid(region)
                _points.append(list((newx, newy)))
            self.voronoi = Voronoi(_points)
        self.points = _points

        # triangles = Delaunay(self.points)
        # abar = progressbar.ProgressBar()
        # print("Building Adjacency Graph")
        # for item in abar(triangles.simplices):
        #     for pair in itertools.combinations(item, 2):
        #         draw_line_between_points(pair[0], pair[1], points)


    def get_color(self, height, temperature, water):
        if(temperature < self.freezing_temp):
            return 255, 255, 255
        if(water > self.water_threshhold):
            return 50, 50, 255
        _r, _g, _b = hsv_to_rgb((50+60*height)/ 360, (temperature + 1)/2, 165/240)
        return int(_r*255), int(_g*255), int(_b*255)

    def get_centroid(self, _region):
        _newx = 0
        _newy = 0
        for _point in _region:
            _point = self.voronoi.vertices[_point]
            _newx += _point[0]
            _newy += _point[1]
        _newx /= len(_region)
        _newy /= len(_region)
        return _newx, _newy

    def get_regions(self):
        return self.voronoi.regions

    def get_vertex(self, vertex_index):
        return self.voronoi.vertices[vertex_index]

    def get_point_color(self, point_index):
        return self.get_color(0.5, 0.5, 0.5)


class Settlement(object):

    def __init__(self):
        self.dickbutt = 0
