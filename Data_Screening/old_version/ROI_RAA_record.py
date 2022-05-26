# for python 3.6
from MisrToolkit import MtkRegion, MtkFile
import os
import numpy
import shutil
import json

ahi_vaa_bin = '/data/beichen/data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'
roi_geoj_folder = '/data/beichen/data/MISR_AHI_ROIs'
misr_ahi_matching_folder = '/data/beichen/data/MISR_AHI_ROIs_inter-com'


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


def get_ahi_raa(vaa, saa):
    raa = 0
    diff = abs(vaa - saa)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def get_roi_ahi_vaa(region_extent):
    ahi_vaa = numpy.fromfile(ahi_vaa_bin, dtype='>f4')
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)

    ahi_vaa = ahi_vaa.reshape(3000, 3000)
    roi_vaa = ahi_vaa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    roi_mean_vaa = roi_vaa.mean()

    return roi_mean_vaa


def misr_ahi_raa(roi_geoj_file, misr_ls_file, camera_index, roi_ahi_saa):
    with open(roi_geoj_file, 'r', encoding='utf-8') as f:
        geoobj = json.load(f)
        polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
        roi_extent = get_extent(polygon_pts)
        # MISR RAA
        roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2],
                          roi_extent[3])
        m_file = MtkFile(misr_ls_file)
        m_grid = m_file.grid('RegParamsLnd')
        m_field = m_grid.field('RelViewCamAziAng[' + camera_index + ']')
        f_raa_data = m_field.read(roi_r).data()
        # in single array
        roi_misr_raa_list = f_raa_data.flatten()
        roi_misr_raa_list = numpy.setdiff1d(roi_misr_raa_list, [-9999])
        if len(roi_misr_raa_list) > 0:
            roi_misr_raa = roi_misr_raa_list.mean()
            # AHI RAA
            roi_ahi_vaa = get_roi_ahi_vaa(roi_extent)
            roi_ahi_raa = get_ahi_raa(roi_ahi_vaa, roi_ahi_saa)
            # show raa diff
            raa_diff = abs(roi_misr_raa - roi_ahi_raa)
            return roi_misr_raa, roi_ahi_raa, raa_diff
    return 0, 0, 0


if __name__ == "__main__":

    roi_folders = os.listdir(misr_ahi_matching_folder)
    for roi_folder in roi_folders:
        print('***', roi_folder)
        roi_folder_path = os.path.join(misr_ahi_matching_folder, roi_folder)
        misr_ws_folders = os.listdir(roi_folder_path)
        for misr_ws_folder in misr_ws_folders:
            print('-->', misr_ws_folder)
            raa_diffs = []
            camera_folder_path = os.path.join(roi_folder_path, misr_ws_folder)
            folder_files = os.listdir(camera_folder_path)
            SAA_ahi_npy = camera_folder_path + '/SAA_AHITime_AHI.npy'
            # for record RAA
            RAA_misr_ahi_npy = camera_folder_path + '/RAA_MISR_AHITime_AHI_diff.npy'
            raa_records = []
            misr_filename = ''
            for record_file in folder_files:
                print(record_file)
                if record_file.split('.')[1] == 'hdf':
                    misr_filename = os.path.join(camera_folder_path, record_file)
                    break
            ahi_saa_list = numpy.load(SAA_ahi_npy)
            for ahi_saa_item in ahi_saa_list:
                temp_ws = os.path.join(camera_folder_path, 'temp')
                if not os.path.exists(temp_ws):
                    os.makedirs(temp_ws)
                ahi_time_str = ahi_saa_item[0]
                ahi_time = ahi_time_str
                ahi_saa = float(ahi_saa_item[1])
                roi_geoj_filename = roi_geoj_folder + '/' + roi_folder.split('_')[0] + '/' + roi_folder.split('_')[1] + '.json'
                camera = misr_ws_folder.split('_')[2]
                m_raa, ahi_raa, diff_raa = misr_ahi_raa(roi_geoj_filename, misr_filename, camera, ahi_saa)
                raa_records.append([m_raa, ahi_time, ahi_raa, diff_raa])
                raa_diffs.append(diff_raa)
                shutil.rmtree(temp_ws)

            numpy.save(RAA_misr_ahi_npy, numpy.array(raa_records))
