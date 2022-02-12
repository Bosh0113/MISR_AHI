# python 3.6
from MisrToolkit import *


if __name__ == "__main__":
    ahi_r = MtkRegion(60, 85, -60, -155)
    start_t = '2016-05-01T00:00:00Z'
    end_t = '2016-05-31T23:59:59Z'
    pathList = ahi_r.path_list
    orbit_t = []
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
        for orbit in orbits:
            orbit_t.append(orbit)
    print(len(orbit_t))