import os
import numpy
import bz2
import shutil
import json
from ftplib import FTP

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


def get_region_ahi_saa(region_extent, ahi_saa):
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)
    ahi_saa = ahi_saa.reshape(3000, 3000)
    roi_saa = ahi_saa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]

    return roi_saa


def get_roi_ahi_saa(roi_geoj_file, ahi_saa_file):
    with open(roi_geoj_file, 'r', encoding='utf-8') as f:
        geoobj = json.load(f)
        polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
        roi_extent = get_extent(polygon_pts)
        # AHI SAA
        ahi_saa_dn = numpy.fromfile(ahi_saa_bin, dtype='>f4')
        roi_ahi_all_saa = get_region_ahi_saa(roi_extent, ahi_saa_dn)
        roi_ahi_saa = roi_ahi_all_saa.mean()
        
        return roi_ahi_saa


if __name__ == "__main__":
    # AHI data ftp server
    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()

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
            # for record SAA
            SAA_ahi_npy = camera_folder_path + '/SAA_AHITime_AHI.npy'
            saa_records = []
            ahi_saa_record_filename = os.path.join(camera_folder_path, 'AHI_saa_ftp_paths.npy')
            ahi_saa_data_ftps = numpy.load(ahi_saa_record_filename)
            for ahi_saa_data_ftp in ahi_saa_data_ftps:
                temp_ws = os.path.join(camera_folder_path, 'temp')
                if not os.path.exists(temp_ws):
                    os.makedirs(temp_ws)
                filename_parts = ahi_saa_data_ftp.split('/')
                ahi_saa_file = filename_parts[len(filename_parts) - 1]
                ahi_saa_bin_bz2 = os.path.join(temp_ws, ahi_saa_file)
                ahi_saa_bin = ''
                try:
                    with open(ahi_saa_bin_bz2, 'wb') as f:
                        ftp.retrbinary('RETR ' + ahi_saa_data_ftp, f.write,
                                       1024 * 1024)
                    zipfile = bz2.BZ2File(ahi_saa_bin_bz2)
                    data = zipfile.read()
                    ahi_saa_bin = ahi_saa_bin_bz2[:-4]
                    with open(ahi_saa_bin, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    os.remove(ahi_saa_bin_bz2)
                    # print('Error: ' + ahi_saa_data_ftp)
                    # print(e)
                if os.path.exists(ahi_saa_bin_bz2):
                    roi_geoj_filename = roi_geoj_folder + '/' + roi_folder.split('_')[0] + '/' + roi_folder.split('_')[1] + '.json'
                    ahi_saa = get_roi_ahi_saa(roi_geoj_filename, ahi_saa_bin)
                    ahi_obs_time = ahi_saa_file.split('.')[0]
                    saa_records.append([ahi_obs_time, ahi_saa])
                shutil.rmtree(temp_ws)

            numpy.save(SAA_ahi_npy, numpy.array(saa_records))

    # disconnect ftp server
    ftp.close()
