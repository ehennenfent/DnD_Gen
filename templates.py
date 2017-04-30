from random import choice
import numpy as np
from scipy.spatial import Voronoi, Delaunay
from noise import snoise2
from colorsys import hsv_to_rgb
from random import randint, choice
import progressbar
import util
import math
import itertools
from dice import d6, d20
from categories import colors, Terrain

class Cell(object):

    def __init__(self, index, x, y, h, t, w, corners=None):
        self.index = index
        self.neighbors = []
        self.temperature = t
        self.height = h
        self.water = w
        self.x = x
        self.y = y
        self.corners = corners
        self.owner = None
        self.terrain = None

    def add_neighbor(self, neighbor_index):
        if neighbor_index not in self.neighbors:
            self.neighbors.append(neighbor_index)

    def claim(self, claimant):
        if self.owner is not None:
            return False
        self.owner = claimant
        return(True)

    def set_terrain(self, terrain):
        self.terrain = terrain

    def __repr__(self):
        return "Cell {p} at ({x}, {y})".format(p=self.index, x=self.x, y=self.y)

class WorldState(object):

    def __init__(self, canvas_width=2048, canvas_height=2048):
        self.width = canvas_width
        self.height = canvas_height

        self.height_map, self.temperature_map, self.water_map = np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height)), np.zeros((canvas_width, canvas_height))
        self.height_offset, self.temperature_offset, self.water_offset = randint(0, canvas_width*128), randint(0, canvas_width*128), randint(0, canvas_width*128)

        self.num_points = int(256 * math.log(max(canvas_width, canvas_height), 2))
        self.cells = []
        self.regions = []

        self.water_threshhold = 0.9
        self.freezing_temp = 0.1
        self.normalization_steps = 7
        self.mountain_threshhold = 0.8
        self.states = []
        self.num_kingdoms = d6()
        self.cities_per_kingdom = d6()
        self.num_curois = d20()
        self.num_city_states = max(0, randint(-3, 3))
        self.num_city_states = 1 # changeme

    def generate_world(self):
        print("Generating Simplex Noise")
        xbar = progressbar.ProgressBar()
        for x in xbar(range(self.width)):
            for y in range(self.height):
                hScale = self.simplex_wrapper(x, y, self.height_offset)
                tScale = self.simplex_wrapper(x, y, self.temperature_offset)
                wScale = self.simplex_wrapper(x, y, self.water_offset)

                self.height_map[x][y] = hScale
                self.temperature_map[x][y] = min(1, max(0, (tScale*.6 + .3) - 0.5*(util.dist(0, y, 0, self.height/2)/(self.height))))
                self.water_map[x][y] = min(1, wScale * .7 + (util.dist(x, y, self.width/2, self.height/2))/(self.width))

        print("Generating Polygons")
        points = np.random.random((self.num_points, 2))
        self.voronoi = Voronoi(points)

        print("Normalizing Polygons")
        for _ in range(self.normalization_steps):
            _points = []
            for region in self.voronoi.regions:
                if(len(region) == 0):
                    continue
                newx, newy = self.get_centroid(region)
                _points.append(list((newx, newy)))
            self.voronoi = Voronoi(_points)

        centroids = []
        index = 0
        print("Building Cells")
        rbar = progressbar.ProgressBar()
        for region in rbar(self.voronoi.regions):
            if(len(region) == 0):
                continue
            x, y = self.get_centroid(region)
            centroids.append([x, y])
            x, y = self.cv(x), self.cv(y, dim='y')
            _x, _y = min(self.width-1, x), min(self.height-1, y)
            cell = Cell(index, x, y, self.height_map[_x][_y], self.temperature_map[_x][_y], self.water_map[_x][_y], corners=region)
            cell.set_terrain(self.determine_terrain(cell))
            self.cells.append(cell)
            index += 1

        self.adjacency_matrix = np.zeros((len(self.cells), len(self.cells)))

        triangles = Delaunay(centroids)
        abar = progressbar.ProgressBar()
        print("Building Adjacency Graph")
        for item in abar(triangles.simplices):
            for pair in itertools.combinations(item, 2):
                cell0 = self.cells[pair[0]]
                cell1 = self.cells[pair[1]]
                cell0.add_neighbor(pair[1])
                cell1.add_neighbor(pair[0])
                self.adjacency_matrix[pair[0]][pair[1]] = util.dist(cell0.x, cell1.x, cell0.y, cell1.y)
                self.adjacency_matrix[pair[1]][pair[0]] = util.dist(cell0.x, cell1.x, cell0.y, cell1.y)

        if(self.num_city_states > 0):
            print("Placing city states")
            for i in range(self.num_city_states):
                cap = choice(self.cells)
                while(cap.terrain == Terrain.WATER or cap.owner is not None):
                    cap = choice(self.cells)
                cap.set_terrain(Terrain.CITY)
                cap.claim(i)
                state = State(cap, i, self)
                state.expand_territory()
                self.states.append(state)

    def simplex_wrapper(self, _x, _y, offset):
        return (snoise2((_x + offset) / (self.width / 2), (_y + offset) / (self.height / 2)) + 1) / 2

    def cv(self, float_val, dim='x'):
        if(dim=='y'):
            return max(0, min(self.height, int(float_val * self.height)))
        return max(0, min(self.width, int(float_val * self.width)))

    def determine_terrain(self, cell):
        if(cell.water > self.water_threshhold):
            return Terrain.WATER
        if(cell.height >= self.mountain_threshhold):
            return Terrain.MOUNTAIN
        return Terrain.PLAIN

    def get_color(self, height, temperature, water):
        if(temperature < self.freezing_temp):
            return 255, 255, 255
        if(water > self.water_threshhold):
            return 50, 50, 255
        _r, _g, _b = hsv_to_rgb((50+60*(1-height))/ 360, (temperature + 1)/2, 165/240)
        return int(_r*255), int(_g*255), int(_b*255)

    def get_centroid(self, _region):
        if(len(_region) == 0):
            return -1, -1
        _newx = 0
        _newy = 0
        for _point in _region:
            _point = self.voronoi.vertices[_point]
            _newx += _point[0]
            _newy += _point[1]
        _newx /= len(_region)
        _newy /= len(_region)
        return _newx, _newy

    def get_vertex(self, vertex_index):
        return self.voronoi.vertices[vertex_index]

    def get_cell(self, pointindex):
        return self.cells[pointindex]

    def get_point_color(self, cell_index):
        return 255, 0, 255

    def get_cell_color(self, cell_index):
        cell = self.cells[cell_index]
        return self.get_color(cell.height, cell.temperature, cell.water)

    def get_cells(self):
        return self.cells

class State(object):

    def __init__(self, capitol, index, world):
        self.capitol = capitol
        self.territory = [capitol.index]
        self.index = index
        self.color = colors[index]
        self.name = "Kingdom {0}".format(index)
        self.world = world

    def expand_territory(self):
        print(self.name,"holds",self.territory)
        newterritory = []
        for cellnum in self.territory:
            cell = self.world.get_cell(cellnum)
            print("Bordering", cell.neighbors)
            for neighbor in cell.neighbors:
                if neighbor not in self.territory:
                    print("Claiming",neighbor)
                    neighborcell = self.world.get_cell(neighbor)
                    if(neighborcell.claim(self.index)):
                        newterritory.append(neighbor)
        self.territory = self.territory + newterritory

    def __repr__(self):
        return self.name + " has its capitol at cell" + str(self.capitol) + " and controls " + str(len(self.territory)) + " cells"

class Settlement(object):

    def __init__(self):
        self.dickbutt = 0
