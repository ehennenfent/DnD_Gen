import math
from scipy.spatial import Voronoi, voronoi_plot_2d
from categories import Terrain

def dist(_x, _y, _X, _Y):
    return math.sqrt((_x - _X)**2+(_y - _Y)**2)

def check_magnitude(point, world, tolerance=0.001):
    print("YOU'RE DEFINITELY NOT SUPPOSED TO BE CALLING THIS FUNCTION (IDIOT)")
    return True
    test = 0.5 - tolerance
    dist0 = math.sqrt((0.5 - (point[0] / world.width))**2)
    dist1 = math.sqrt((0.5 - (point[1] / world.height))**2)
    if (dist0 > test) or (dist1 > test):
        return False
    return True

def get_centroid(region_indices, point_list):
    print("YOU'RE DEFINITELY NOT SUPPOSED TO BE CALLING THIS FUNCTION (IDIOT)")
    if(len(region_indices) == 0):
        print("Got empty region!")
        return -1, -1
    centroid_x = sum(point_list[index][0] for index in region_indices if index != -1)
    centroid_y = sum(point_list[index][1] for index in region_indices if index != -1)
    centroid_x, centroid_y = centroid_x / len(region_indices), centroid_y / len(region_indices)
    # print("Region bounded by", region_indices, "has center at ({x},{y})".format(x=centroid_x, y=centroid_y))
    # for index in region_indices:
    #     print("   ", point_list[index])
    return centroid_x, centroid_y

def massage_to_canvas(point, world):
    print("YOU'RE DEFINITELY NOT SUPPOSED TO BE CALLING THIS FUNCTION (IDIOT)")
    out = [0, 0]
    if(point[0] > 0):
        out[0] = point[0]
    if(point[0] > world.width):
        point[0] = world.width - 1
    if(point[1] > 0):
        out[1] = point[1]
    if(point[1] > world.height):
        out[1] = point[1]
    return out

def produce_relaxed_points(points, num_iterations, world):
    print("YOU'RE DEFINITELY NOT SUPPOSED TO BE CALLING THIS FUNCTION (IDIOT)")
    centroids = points
    for _ in range(num_iterations):
        vor = Voronoi(centroids)
        centroids = [get_centroid(region, vor.vertices) for region in vor.regions if (len(region) > 0)]
    return [k for k in centroids if check_magnitude(k, world)]

def eligibility(cell, claimant=None):
    if(cell.terrain is Terrain.WATER):
        print("Attempting to Place in Water")
        return False
    if(claimant is not None):
        if (cell.owner is not claimant and cell.owner is not None):
            print("Cell is already claimed")
            return False
    if(cell.terrain is Terrain.CITY):
        print("This is already a city")
        return False

    return True

def histogram(iterable_thing):
    results = {}

    for thing in iterable_thing:
        if(thing not in results):
            results[thing] = 0
        results[thing] += 1

    return results
