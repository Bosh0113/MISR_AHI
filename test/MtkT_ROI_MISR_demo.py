# python 3.6
from MisrToolkit import MtkRegion, path_time_range_to_orbit_list, orbit_to_time_range
import os
import json


start_t = '2015-07-01T00:00:00Z'
end_t = '2017-06-01T23:59:59Z'


def get_extent(polygon_points):
    ullat = polygon_points[0][1]
    ullon = polygon_points[0][0]
    lrlat = polygon_points[0][1]
    lrlon = polygon_points[0][0]

    for pt in polygon_points:
        lat = pt[1]
        lon = pt[0]
        if ullat < lat:
            ullat = lat
        if lrlat > lat:
            lrlat = lat
        # all polygon in eastern Earth
        if ullon > lon:
            ullon = lon
        if lrlon < lon:
            lrlon = lon
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    return [ullat, ullon, lrlat, lrlon]


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220526\MISR_AHI_ROIs'
    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    all_paths = []
    for vza in MISR_vza:
        folder = ws + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                filename = folder + '/' + file
                with open(filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
                    roi_extent = get_extent(polygon_pts)

                    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
                    pathList = roi_r.path_list
                    orbit_t = []
                    for path in pathList:
                        if path not in all_paths:
                            all_paths.append(path)
                        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
                        for orbit in orbits:
                            # print(orbit_to_time_range(orbit))
                            orbit_t.append(orbit)
                    print('--->', vza, file.split('.')[0], ':', len(orbit_t))
    all_paths.sort()
    print(all_paths)