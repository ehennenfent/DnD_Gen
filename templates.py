from random import choice
import numpy as np
from scipy.spatial import Voronoi, Delaunay, voronoi_plot_2d
from scipy.sparse.csgraph import shortest_path
from noise import snoise2
from colorsys import hsv_to_rgb
from random import randint, choice
import progressbar
import util
import math
import itertools
from dice import d4, d6, d20, d100
from categories import colors, Terrain, religions, Icon, organizations
import matplotlib.pyplot as plt
import ghalton
from names import nameGen

np.set_printoptions(precision=4)
nameGenerator = nameGen()


class Cell(object):
    def __init__(self, index, x, y, h, t, w, region_index, corners=None):
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
        self.icon = None
        self.region_index = region_index

    def add_neighbor(self, neighbor_index):
        if neighbor_index not in self.neighbors:
            self.neighbors.append(neighbor_index)

    def claim(self, claimant):
        if self.owner is not None:
            return False
        self.owner = claimant
        return True

    def set_terrain(self, terrain):
        self.terrain = terrain

    def set_icon(self, icon):
        self.icon = icon

    def __repr__(self):
        return "Cell {p} at ({x}, {y})".format(p=self.index, x=self.x, y=self.y)


class WorldState(object):
    def __init__(self, canvas_width=2048, canvas_height=2048):
        self.width = canvas_width
        self.height = canvas_height

        self.height_map, self.temperature_map, self.water_map = (
            np.zeros((canvas_width, canvas_height)),
            np.zeros((canvas_width, canvas_height)),
            np.zeros((canvas_width, canvas_height)),
        )
        self.height_offset, self.temperature_offset, self.water_offset = (
            randint(0, canvas_width * 128),
            randint(0, canvas_width * 128),
            randint(0, canvas_width * 128),
        )

        self.num_points = int(256 * math.log(max(canvas_width, canvas_height), 2))
        self.cells = []
        self.regions = []
        self.roads = []
        self.curiosities = []
        self.societies = set([choice(organizations) for _ in range(d4() - 1)])

        self.water_threshhold = 0.9
        self.freezing_temp = 0.1
        self.normalization_steps = 7
        self.mountain_threshhold = 0.8
        self.distance_threshold = 1.5
        self.states = []
        self.num_kingdoms = d6()
        self.cities_per_kingdom = d6()
        self.num_curios = int(math.log(max(canvas_width, canvas_height), 2)) + d20()
        self.num_city_states = max(0, randint(-2, 3))
        self.pantheon = choice(religions)

        self.name = nameGenerator.get_place()

    def __repr__(self):
        kingdomstring = self.states[0].name
        if len(self.states) > 2:
            for k in self.states[1:-1]:
                kingdomstring += ", " + k.name
            kingdomstring += " and " + self.states[-1].name
        if len(self.states) == 2:
            kingdomstring += " and " + self.states[-1].name

        out = "Behold the kingdom of {name}, home to the kingdoms of {kingdoms}\n\n".format(
            name=self.name.upper(), kingdoms=kingdomstring
        )

        out += "World Size: %s cells\n" % len(self.cells)
        out += "Religious State: %s\n" % self.pantheon.value
        out += "Clandestine Organizations:\n"
        for org in self.societies:
            out += "\t" + org.value + "\n"

        out += "\n"
        out += "Kingdoms:\n"
        for kingdom in self.states:
            out += str(kingdom) + "\n"
            for city in kingdom.cities:
                out += "\t\t" + str(city)

        out += "\n"
        out += "Points of Interest:\n"
        for poi in self.curiosities:
            out += "\t" + str(poi) + "\n"

        return out

    def generate_world(self):
        print("Generating Simplex Noise")
        xbar = progressbar.ProgressBar()
        for x in xbar(range(self.width)):
            for y in range(self.height):
                hScale = self.simplex_wrapper(x, y, self.height_offset)
                tScale = self.simplex_wrapper(x, y, self.temperature_offset)
                wScale = self.simplex_wrapper(x, y, self.water_offset)

                self.height_map[x][y] = hScale
                self.temperature_map[x][y] = min(
                    1,
                    max(
                        0,
                        (tScale * 0.6 + 0.3)
                        - 0.5 * (util.dist(0, y, 0, self.height / 2) / (self.height)),
                    ),
                )
                self.water_map[x][y] = min(
                    1,
                    wScale * 0.7
                    + (util.dist(x, y, self.width / 2, self.height / 2)) / (self.width),
                )

        print("Generating Polygons")
        sequencer = ghalton.Halton(2)
        points = sequencer.get(self.num_points + 100)[d100() :]
        points = [
            [int(point[0] * self.width), int(point[1] * self.height)]
            for point in points
        ]

        self.voronoi = Voronoi(points)

        print("Building Cells")
        rbar = progressbar.ProgressBar()
        for index, point in rbar(enumerate(self.voronoi.points)):
            region = self.voronoi.regions[self.voronoi.point_region[index]]
            x, y = int(point[0]), int(point[1])
            cell = Cell(
                index,
                x,
                y,
                self.height_map[x][y],
                self.temperature_map[x][y],
                self.water_map[x][y],
                self.voronoi.point_region[index],
                corners=region,
            )
            cell.set_terrain(self.determine_terrain(cell))
            self.cells.append(cell)

        print("Sorting out Water Cells")
        dry_cells = []
        wet_cells = []
        for cell in self.cells:
            if cell.terrain is Terrain.WATER:
                wet_cells.append(cell)
            else:
                cell.index = len(dry_cells)
                dry_cells.append(cell)
        num_dry_cells = len(dry_cells)
        for i, wet_cell in enumerate(wet_cells):
            wet_cell.index = i + num_dry_cells
        self.cells = dry_cells + wet_cells

        self.adjacency_matrix = np.zeros((num_dry_cells, num_dry_cells))

        calc_over = [[cell.x, cell.y] for cell in self.cells[:num_dry_cells]]
        print("Running Delaunay's Algorithm")
        triangles = Delaunay(calc_over)
        abar = progressbar.ProgressBar()
        print("Calculating Distances")
        distances = []
        for item in abar(triangles.simplices):
            for pair in itertools.combinations(item, 2):
                cell0, cell1 = self.cells[pair[0]], self.cells[pair[1]]
                d1 = util.terrain_dist(cell0, cell1)
                distances.append(d1)

        self.dist_mean, self.dist_std = np.mean(distances), np.std(distances)
        print("Distances - mean:", self.dist_mean, "std:", self.dist_std)

        print("Building Adjacency Matrix")
        abar = progressbar.ProgressBar()
        for item in abar(triangles.simplices):
            for pair in itertools.combinations(item, 2):
                cell0, cell1 = self.cells[pair[0]], self.cells[pair[1]]
                cell0.add_neighbor(pair[1])
                cell1.add_neighbor(pair[0])
                d1 = util.terrain_dist(cell0, cell1)
                if d1 > (self.dist_mean + self.distance_threshold * self.dist_std):
                    d1 = d1 ** 3
                self.adjacency_matrix[pair[0]][pair[1]] = d1
                self.adjacency_matrix[pair[1]][pair[0]] = d1

        if self.num_city_states > 0:
            print("Placing {0} city states".format(self.num_city_states))
            for i in range(self.num_city_states):
                cap = choice(self.cells)
                while cap.terrain == Terrain.WATER or cap.owner is not None:
                    cap = choice(self.cells)
                cap.set_terrain(Terrain.CITY)
                cap.set_icon(Icon.CSTATE)
                cap.claim(i)
                state = State(cap, i, self)
                state.cities.append(Settlement(cap, state, state))
                state.expand_territory()
                self.states.append(state)

        print("Creating {0} Kingdoms".format(self.num_kingdoms))
        for i in range(self.num_kingdoms):
            cap = choice(self.cells)
            while cap.terrain == Terrain.WATER or cap.owner is not None:
                cap = choice(self.cells)
            cap.set_terrain(Terrain.CITY)
            cap.set_icon(Icon.CAPITOL)
            cap.claim(len(self.states))
            state = State(cap, len(self.states), self)
            state.cities.append(Settlement(cap, state, state))
            state.expand_territory()
            self.states.append(state)

        print("Growing Kingdoms")
        unclaimed = True
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        counter = 0
        while unclaimed:
            iteration = False
            for kingdom in self.states[self.num_city_states :]:
                res = kingdom.expand_territory()
                iteration = iteration or res
            unclaimed = iteration
            counter += 1
            bar.update(counter)

        print()
        print("Calculating Shortest Paths")
        dist_matrix, self.path_matrix = shortest_path(
            self.adjacency_matrix, return_predecessors=True
        )
        print("Building roads between capitols")
        capitols = [kingdom.capitol for kingdom in self.states]
        for cap1, cap2 in itertools.combinations(capitols, 2):
            path = self.path_between(cap1.index, cap2.index)
            self.roads.append(path)

        print("Placing Cities")
        for kingdom in self.states[self.num_city_states :]:
            for citynum in range(self.cities_per_kingdom):
                location = choice(kingdom.territory)
                cell = self.cells[location]
                if not util.eligibility(cell, claimant=kingdom.index):
                    continue
                bigcity = Settlement(cell, kingdom.cities[0], kingdom)
                cell.set_terrain(Terrain.CITY)
                cell.set_icon(choice([Icon.CITY, Icon.CASTLE, Icon.CATHEDRAL]))
                self.roads.append(self.path_between(kingdom.capitol.index, cell.index))
                kingdom.cities.append(bigcity)

                for subordinate_num in range(d4() - 1):
                    location = choice(self.dual_neighbors(cell.index))
                    subcell = self.cells[location]
                    if not util.eligibility(subcell, claimant=kingdom.index):
                        continue
                    city = Settlement(subcell, bigcity, kingdom)
                    subcell.set_terrain(Terrain.CITY)
                    subcell.set_icon(Icon.VILLAGE)
                    self.roads.append(self.path_between(subcell.index, cell.index))
                    kingdom.cities.append(city)

        print(util.histogram([cell.terrain for cell in self.cells]))
        # print("Placing {0} Points of Interest".format(self.num_curios))
        # for k in range(self.num_curios):
        #     location = choice(self.cells)
        #     if not util.eligibility(location):
        #         continue
        #     poi = POI(location)
        #     ic = choice([Icon.DRAGON, Icon.AXE, Icon.CRYPT, Icon.FOREST, Icon.GRIFFIN, Icon.HELMET, Icon.HYDRA, Icon.MANTICORE, Icon.OGRE, Icon.SWORDS])
        #     location.set_icon(ic)
        #     self.curiosities.append(poi)

    def path_between(self, cell1, cell2):
        path = []
        start = cell1
        while start != cell2:
            path.append(start)
            start = self.path_matrix[cell2][start]
        path.append(cell2)
        return path

    def dual_neighbors(self, cell_index):
        out = []
        for n_index in self.cells[cell_index].neighbors:
            out.append(n_index)
            for k_index in self.cells[n_index].neighbors:
                out.append(k_index)
        return out

    def simplex_wrapper(self, _x, _y, offset):
        return (
            snoise2((_x + offset) / (self.width / 2), (_y + offset) / (self.height / 2))
            + 1
        ) / 2

    def cv(self, float_val, dim="x"):
        if dim == "y":
            return max(0, min(self.height, int(float_val * self.height)))
        return max(0, min(self.width, int(float_val * self.width)))

    def determine_terrain(self, cell):
        if cell.water > self.water_threshhold:
            return Terrain.WATER
        if cell.height >= self.mountain_threshhold:
            return Terrain.MOUNTAIN
        return Terrain.PLAIN

    def get_color(self, height, temperature, water):
        if temperature < self.freezing_temp:
            return 255, 255, 255
        if water > self.water_threshhold:
            return 50, 50, 255
        _r, _g, _b = hsv_to_rgb(
            (50 + 60 * (1 - height)) / 360, (temperature + 1) / 2, 165 / 240
        )
        return int(_r * 255), int(_g * 255), int(_b * 255)

    def get_vertex(self, vertex_index):
        return self.voronoi.vertices[vertex_index]

    def get_cell(self, pointindex):
        return self.cells[pointindex]

    def get_point_color(self, cell_index):
        cell = self.get_cell(cell_index)
        if cell.owner is not None:
            return colors[cell.owner].value
        return colors[-1].value

    def get_cell_color(self, cell_index):
        cell = self.cells[cell_index]
        return self.get_color(cell.height, cell.temperature, cell.water)

    def get_cells(self):
        return self.cells

    def get_weight_str(self, left, right):
        return str(int(self.adjacency_matrix[left][right]))

    def get_weighted_dist(self, celli1, celli2):
        return self.adjacency_matrix[celli1][celli2]


class State(object):
    def __init__(self, capitol, index, world):
        self.capitol = capitol
        self.territory = [capitol.index]
        self.index = index
        self.color = colors[index]
        self.name = "Kingdom {0}".format(index)
        self.world = world
        self.cities = []

        self.ruler = nameGenerator.get_person()
        self.name = nameGenerator.get_place()

    def expand_territory(self):
        newterritory = []
        for cellnum in self.territory:
            cell = self.world.get_cell(cellnum)
            for neighbor in cell.neighbors:
                if neighbor not in self.territory and cell.terrain is not Terrain.WATER:
                    dist = self.world.get_weighted_dist(cellnum, neighbor)
                    should_continue = True
                    if (
                        dist
                        > self.world.dist_mean
                        + self.world.distance_threshold * self.world.dist_std
                    ):
                        should_continue = choice([True, False, False, False, False])
                    if should_continue:
                        neighborcell = self.world.get_cell(neighbor)
                        if neighborcell.claim(self.index):
                            newterritory.append(neighbor)
        self.territory = self.territory + newterritory
        if len(newterritory) == 0:
            return False
        return True

    def __repr__(self):
        out = (
            "\t"
            + self.name
            + ", led by "
            + self.ruler
            + ", has its capitol at cell ("
            + str(self.capitol.x)
            + ","
            + str(self.capitol.y)
            + ") and controls "
            + str(len(self.territory))
            + " cells, "
            + str(len(self.cities))
            + " cities"
        )

        return out


class Settlement(object):
    def __init__(self, cell, parent, kingdom):
        self.cell = cell
        self.parent = parent
        self.kingdom = kingdom

        self.ruler = nameGenerator.get_person()
        self.name = nameGenerator.get_place()

    def __repr__(self):
        if type(self.parent) == State:
            return (
                self.name
                + ", capitol of "
                + self.parent.name
                + ", located at ("
                + str(self.cell.x)
                + ", "
                + str(self.cell.y)
                + ")\n"
            )
        else:
            return (
                "\t"
                + self.name
                + ", dependant to "
                + self.parent.name
                + " in the kingdom of "
                + self.kingdom.name
                + ", located at ("
                + str(self.cell.x)
                + ", "
                + str(self.cell.y)
                + ")\n"
            )


class POI(object):
    def __init__(self, cell):
        self.cell = cell

        self.name = nameGenerator.get_person()

    def __repr__(self):
        return "({x}, {y}) -- {name}".format(
            x=self.cell.x, y=self.cell.y, name=self.name
        )
