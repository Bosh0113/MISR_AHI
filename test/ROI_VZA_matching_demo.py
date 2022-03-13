# 使用python 3.6
from MisrToolkit import *
import numpy
import math
import os
import json

start_t = '2016-05-01T00:00:00Z'
end_t = '2016-06-31T23:59:59Z'

ahi_vza_bin = '/data/beichen/data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
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


def get_region_ahi_vza(region_extent):
    ahi_vza_DN = numpy.fromfile(ahi_vza_bin, dtype='>f4')
    ahi_vza_DN = ahi_vza_DN.reshape(3000, 3000)
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)
    roi_vza = ahi_vza_DN[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    return roi_vza


if __name__ == "__main__":

    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    for vza in MISR_vza:
        folder = roi_folder + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                filename = folder + '/' + file
                with open(filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry'][
                        'coordinates'][0]
                    roi_extent = get_extent(polygon_pts)

                    print('***ROI:', vza, '-', file.split('.')[0])

                    ahi_vza = get_region_ahi_vza(roi_extent)
                    ahi_vza_mean = ahi_vza.mean()
                    print('-> mean vza of ROI in AHI data:', ahi_vza_mean)

                    roi_r = MtkRegion(roi_extent[0], roi_extent[1],
                                      roi_extent[2], roi_extent[3])
                    pathList = roi_r.path_list
                    for path in pathList:
                        orbits = path_time_range_to_orbit_list(
                            path, start_t, end_t)
                        for orbit in orbits:
                            P = 'P' + (3 - len(str(path))) * '0' + str(path)
                            O = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
                            F = 'F' + '07'
                            v = '0022'
                            hdf_filename = misr_folder + '/MISR_AM1_AS_LAND_' + P + '_' + O + '_' + F + '_' + v + '.hdf'
                            if os.path.exists(hdf_filename):
                                m_file = MtkFile(hdf_filename)
                                m_grid = m_file.grid('RegParamsLnd')

                                cameras = []
                                if vza == 0.0:
                                    cameras = [4]
                                elif vza == 26.1:
                                    cameras = [3, 5]
                                elif vza == 45.6:
                                    cameras = [2, 6]
                                elif vza == 60.0:
                                    cameras = [1, 7]
                                elif vza == 70.5:
                                    cameras = [0, 8]

                                for camera in cameras:
                                    m_field = m_grid.field('ViewZenAng[' +
                                                           str(camera) + ']')
                                    f_vza_data = m_field.read(roi_r).data()
                                    max_vza = f_vza_data.max()
                                    if max_vza > -9999:
                                        differ_cos = abs(
                                            math.cos(math.radians(
                                                ahi_vza_mean)) -
                                            math.cos(math.radians(max_vza)))
                                        if differ_cos < 0.01:
                                            # print(hdf_filename)
                                            print('-- path:', path, '--',
                                                  'orbit:', orbit)
                                            print('   ',
                                                  orbit_to_time_range(orbit))
                                            print(
                                                '   camera ' +
                                                str(camera + 1) +
                                                ' vza in MISR data:', max_vza)
                                            print('   differ of cos:',
                                                  differ_cos)
