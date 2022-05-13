import numpy
import os
from MisrToolkit import MtkFile, MtkRegion, orbit_to_time_range
import json
from datetime import datetime
from ftplib import FTP
import bz2
import shutil

roi_data_path = '/home/beichen/disk1/data/MISR_AHI_ROIs'
sat_data_path = '/home/beichen/disk1/workspace/20220512/MISR_AHI_inter-com'
matched_record_path = '/home/beichen/disk1/workspace/20220512/MISR_AHI_matched_info_vza001raa5sza30min.npy'

workspace = current_dir = os.getcwd()

ahi_vza_bin = '/home/beichen/disk1/data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'


def get_roi_extent(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        geoobj = json.load(f)
        polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
        ullat = polygon_pts[0][1]
        ullon = polygon_pts[0][0]
        lrlat = polygon_pts[0][1]
        lrlon = polygon_pts[0][0]

        for pt in polygon_pts:
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
    return roi_vza, roi_vza.mean()


def get_region_misr_vza(roi_extent, camera):
    m_file = MtkFile(misr_hdf_filename)
    m_grid = m_file.grid('RegParamsLnd')
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2],
                      roi_extent[3])
    m_field = m_grid.field('ViewZenAng[' + str(camera) + ']')
    f_vza_data = m_field.read(roi_r).data()
    # in single array
    roi_misr_vza_list = f_vza_data.flatten()
    roi_misr_vza_list = numpy.setdiff1d(roi_misr_vza_list, [-9999])
    roi_misr_vza = roi_misr_vza_list.mean()
    return roi_misr_vza_list, roi_misr_vza


def get_region_misr_sza(roi_extent):
    m_file = MtkFile(misr_hdf_filename)
    m_grid = m_file.grid('RegParamsLnd')
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2],
                      roi_extent[3])
    m_field = m_grid.field('SolZenAng')
    f_sza_data = m_field.read(roi_r).data()
    # in single array
    roi_misr_sza_list = f_sza_data.flatten()
    roi_misr_sza_list = numpy.setdiff1d(roi_misr_sza_list, [-9999])
    roi_misr_sza = roi_misr_sza_list.mean()
    return roi_misr_sza_list, roi_misr_sza


def raa_ahitime_object(npy_path):
    raa_record_obj = {}
    raa_record_list = numpy.load(npy_path, allow_pickle=True)
    for raa_record in raa_record_list:
        raa_record_obj[raa_record[1]] = [raa_record[0], raa_record[2]]
    return raa_record_obj


def get_region_ahi_sza(ahi_time, region_extent):
    ahi_time = str(ahi_time)
    ahi_data_folder1 = ahi_time[0:6]
    ahi_data_folder2 = ahi_time[0:8]
    ahi_sza_file = ahi_time + '.sun.zth.fld.4km.bin.bz2'
    ahi_sza_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_sza_file

    temp_ws = os.path.join(current_dir, 'temp')
    if not os.path.exists(temp_ws):
        os.makedirs(temp_ws)
    ahi_sza_bin_bz2 = os.path.join(temp_ws, ahi_sza_file)
    ahi_sza_bin = ''
    try:
        with open(ahi_sza_bin_bz2, 'wb') as f:
            ftp.retrbinary('RETR ' + ahi_sza_path, f.write, 1024 * 1024)
        zipfile = bz2.BZ2File(ahi_sza_bin_bz2)
        data = zipfile.read()
        ahi_sza_bin = ahi_sza_bin_bz2[:-4]
        with open(ahi_sza_bin, 'wb') as f:
            f.write(data)
    except Exception as e:
        os.remove(ahi_sza_bin_bz2)
        # print('Error: ' + ahi_saa_data_ftp)
        # print(e)
    if os.path.exists(ahi_sza_bin_bz2):
        ahi_sza_DN = numpy.fromfile(ahi_sza_bin, dtype='>f4')
        ahi_sza_DN = ahi_sza_DN.reshape(3000, 3000)
        p_size = 120 / 3000
        ullon_ahi = 85
        ullat_ahi = 60
        ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
        xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
        ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
        xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
        # print(ymin_index, xmin_index, ymax_index, xmax_index)
        roi_sza = ahi_sza_DN[ymin_index:ymax_index + 1,
                             xmin_index:xmax_index + 1]
        roi_vsa_mean = roi_sza.mean()
        shutil.rmtree(temp_ws)
        return roi_sza, roi_vsa_mean, 0

    shutil.rmtree(temp_ws)

    return [], 0, 1


def get_roi_angle_detail(geocond_record_str, a_array, array_name):
    geocond_record_str += '### ' + array_name
    # print(len(a_array.shape))
    if len(a_array.shape) > 1:
        for j in range(len(a_array)):
            geocond_record_str += '\n'
            for i in range(len(a_array[0])):
                geocond_record_str += str(a_array[j][i]) + '\t'
    else:
        geocond_record_str += '\n'
        for i in range(len(a_array)):
                geocond_record_str += str(a_array[i]) + '\t'
    geocond_record_str += '\n'
    max_v = a_array.max()
    min_v = a_array.min()
    diff = max_v - min_v
    geocond_record_str += 'max value: ' + str(max_v) + '\t main value:' + str(min_v) + '\t diff:' + str(diff) + '\n'
    return geocond_record_str


if __name__ == "__main__":
    # AHI data ftp server
    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()

    geocond_record_str = ''

    matched_record = numpy.load(matched_record_path, allow_pickle=True)
    for roi_matched in matched_record:
        roi_name = roi_matched['roi_name']
        print(roi_name)
        geocond_record_str += '\n' + roi_name

        roi_info = roi_name.split('_')
        roi_misr_angle = roi_info[0]
        roi_lc_type = roi_info[1]
        roi_geojson_path = roi_data_path + '/' + roi_misr_angle + '/' + roi_lc_type + '.json'
        roi_extent = get_roi_extent(roi_geojson_path)
        roi_folder_path = os.path.join(sat_data_path, roi_name)
        geocond_record_str += '\n'
        tab_str = 'misr_time ahi_time misr_vza ahi_vza misr_raa ahi_raa misr_sza ahi_sza'
        print(tab_str)
        geocond_record_str += tab_str + '\n'

        roi_ahi_vza_array, roi_ahi_vza = get_region_ahi_vza(roi_extent)
        roi_ahi_vza = '%.3f' % roi_ahi_vza

        misr_ahi = roi_matched['roi_misr_infos']
        roi_matched_count = len(misr_ahi)
        for misr_ahi_item in misr_ahi:
            path_orbit_camera = misr_ahi_item['misr_path_orbit_camera']
            misr_folder_path = os.path.join(roi_folder_path, path_orbit_camera)
            misr_hdf_file = ''
            misr_folder_files = os.listdir(misr_folder_path)
            for misr_folder in misr_folder_files:
                if misr_folder.split('.')[1] == 'hdf':
                    misr_hdf_file = misr_folder
            misr_hdf_filename = os.path.join(misr_folder_path, misr_hdf_file)
            ahi_matched = misr_ahi_item['matched_info']
            misr_midtime = ahi_matched[2]

            roi_misr_vza_array, roi_misr_vza = get_region_misr_vza(
                roi_extent,
                path_orbit_camera.split('_')[2])
            roi_misr_vza = '%.3f' % roi_misr_vza
            roi_misr_sza_array, roi_misr_sza = get_region_misr_sza(
                roi_extent)
            roi_misr_sza = '%.3f' % roi_misr_sza

            best_match_ahi_time = ahi_matched[3]
            roi_ahi_sza_array, roi_ahi_sza, flag = get_region_ahi_sza(best_match_ahi_time, roi_extent)
            roi_ahi_sza = '%.3f' % roi_ahi_sza
            roi_misr_raa = ahi_matched[6]
            roi_misr_raa = '%.3f' % float(roi_misr_raa)
            roi_ahi_raa = ahi_matched[7]
            roi_ahi_raa = '%.3f' % float(roi_ahi_raa)

            record_item = str(misr_midtime) + '\t' + str(best_match_ahi_time) + '\t' + str(roi_misr_vza) + '\t' + str(roi_ahi_vza) + '\t' + str(roi_misr_raa) + '\t' + str(roi_ahi_raa) + '\t' + str(roi_misr_sza) + '\t' + str(roi_ahi_sza)
            print(record_item)
            geocond_record_str += record_item + '\n'
            # detail info -roi_ahi_vza_array -roi_misr_vza_array -roi_misr_sza_array -roi_ahi_sza_array
            roi_angle_arrays = [roi_ahi_vza_array, roi_misr_vza_array, roi_ahi_sza_array, roi_misr_sza_array]
            roi_angle_arrays_name = ['roi_ahi_vza_array', 'roi_misr_vza_array', 'roi_ahi_sza_array', 'roi_misr_sza_array']
            for i in range(len(roi_angle_arrays)):
                geocond_record_str = get_roi_angle_detail(geocond_record_str, roi_angle_arrays[i], roi_angle_arrays_name[i])

    
    with open(os.path.join(current_dir, 'geo-obs_condition_matched_detail.txt'), 'w') as f:
        f.write(geocond_record_str)

    # disconnect ftp server
    ftp.close()