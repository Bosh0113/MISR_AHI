# for python 3.6
from MisrToolkit import *
import math
import os
import json

# time range for our study
start_t = '2016-01-01T00:00:00Z'
end_t = '2016-12-31T23:59:59Z'
# data path
misr_folder = '/data/beichen/data/MISR4AHI'
roi_folder = '/data/beichen/data/MISR_AHI_ROIs'


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

    # angles of MISR cameras
    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    for vza in MISR_vza:
        # read roi geoinfo
        folder = roi_folder + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                filename = folder + '/' + file
                with open(filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
                    roi_extent = get_extent(polygon_pts)
                    
                    print('***ROI:', vza, '-', file.split('.')[0])
                    roi_misr_count = 0
                    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
                    pathList = roi_r.path_list
                    for path in pathList:
                        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
                        for orbit in orbits:
                            P = 'P' + (3-len(str(path)))*'0' + str(path)
                            O = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
                            F = 'F' + '07'
                            v = '0022'
                            hdf_file = 'MISR_AM1_AS_LAND_' + P + '_' + O + '_' + F + '_' + v + '.hdf'
                            hdf_filename = misr_folder + '/' + hdf_file
                            if os.path.exists(hdf_filename):
                                roi_misr_count +=1
                    print("--> the count of MISR avaliable files for ROI is:", roi_misr_count)