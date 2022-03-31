import numpy
import re
import os
from MisrToolkit import orbit_to_time_range
from datetime import datetime

misr_ahi_matching_folder = '/data/beichen/data/MISR_AHI_ROIs_inter-com'
# # cos diff
# VZA_cos_threshold = 0.01
# degree
RAA_threshold = 3.
# second
SZA_time_threshold = 1*60*60

max_sza_count = 5
vza_raa_sza_record_file = 'VZA001_RAA3_SZA1h_c5.npy'


def get_time_diff_MISR_AHI(misr_time_range, ahi_time):
    # MISR mean time of scan
    misr_start_time_str = misr_time_range[0]
    misr_end_time_str = misr_time_range[1]
    misr_start_date = datetime.strptime(misr_start_time_str,
                                        "%Y-%m-%dT%H:%M:%SZ")
    misr_end_date = datetime.strptime(misr_end_time_str, "%Y-%m-%dT%H:%M:%SZ")
    diff_date = misr_end_date - misr_start_date
    misr_mean_date = misr_start_date + diff_date / 2
    # AHI time of scan
    ahi_date = datetime.strptime(ahi_time, "%Y%m%d%H%M")
    # time diff (hours and minutes)
    datetime_diff = misr_mean_date - ahi_date
    datetime_diff_s = abs(datetime_diff.total_seconds())
    if datetime_diff_s > 12 * 60 * 60:
        return abs(datetime_diff_s - 24 * 60 * 60)
    return datetime_diff_s


def vza_raa_sza_time(misr_hdf_filename, raa_record_filename):
    raa_record = numpy.load(raa_record_filename)
    raa_diff_records = []
    for raa_item in raa_record:
        # print('-MISR_RAA:', float(raa_item[0]), '-AHI_time:', raa_item[1], '-AHI_RAA:', float(raa_item[2]), '-Diff_RAA:', float(raa_item[3]))
        raa_diff = float(raa_item[3])
        datetime = raa_item[1]
        raa_diff_record = {}
        raa_diff_record['ahi_time'] = datetime
        raa_diff_record['raa_diff'] = raa_diff
        raa_diff_records.append(raa_diff_record)
    # sort by raa_diff
    raa_diff_record_sorted = sorted(raa_diff_records,
                                    key=lambda i: (i['raa_diff']))
    # get min_raa_diff ≤ RAA_threshold
    raa_diff_r3 = []
    for record in raa_diff_record_sorted:
        if record['raa_diff'] <= RAA_threshold:
            raa_diff_r3.append(record)
    # sort by time_diff
    matchObj = re.search(r'O(\d+)_F', misr_hdf_filename)
    orbit_str = matchObj.group(1)
    misr_time_range_str = orbit_to_time_range(int(orbit_str))
    time_diff_record = []
    for raa_diff3 in raa_diff_r3:
        ahi_time_str = raa_diff3['ahi_time']
        time_diff_s = get_time_diff_MISR_AHI(misr_time_range_str, ahi_time_str)
        if time_diff_s < SZA_time_threshold:
            raa_diff_record = {}
            raa_diff_record['ahi_time'] = ahi_time_str
            raa_diff_record['raa_diff'] = raa_diff3['raa_diff']
            raa_diff_record['time_diff'] = time_diff_s
            time_diff_record.append(raa_diff_record)
    time_diff_record_sorted = sorted(time_diff_record,
                                     key=lambda i: (i['time_diff']))
    return time_diff_record_sorted  # demo: [{'ahi_time': '201607212300', 'raa_diff': 1.902, 'time_diff': 6869.5}, ...]


def record_VZA_RAA_SZA_matched():
    # matched data pairs record
    vza_raa_sza_matched_record = []
    roi_folders = os.listdir(misr_ahi_matching_folder)
    for roi_folder in roi_folders:
        # print('***', roi_folder)
        # roi
        roi_record = {}
        roi_name = roi_folder
        roi_record['roi_name'] = roi_name
        roi_folder_path = os.path.join(misr_ahi_matching_folder, roi_folder)
        misr_ws_folders = os.listdir(roi_folder_path)
        misr_records = []
        for misr_ws_folder in misr_ws_folders:
            # print('-->', misr_ws_folder)
            # misr
            misr_record = {}
            path_orbit_camera = misr_ws_folder
            misr_record['path_orbit_camera'] = path_orbit_camera

            misr_folder_path = os.path.join(roi_folder_path, misr_ws_folder)
            folder_files = os.listdir(misr_folder_path)
            misr_file = ''
            for record_file in folder_files:
                if record_file.split('.')[1] == 'hdf':
                    misr_file = record_file
            misr_hdf_file = os.path.join(misr_folder_path, misr_file)
            raa_record_file = os.path.join(misr_folder_path, 'RAA_MISR_AHITime_AHI_diff.npy')

            ahi_time_diff_array = vza_raa_sza_time(misr_hdf_file, raa_record_file)
            misr_ahi_count = max_sza_count
            if len(ahi_time_diff_array) < misr_ahi_count:
                misr_ahi_count = len(ahi_time_diff_array)
            vza_raa_sza_record = ahi_time_diff_array[:misr_ahi_count]
            misr_record['ahi_matched'] = vza_raa_sza_record

            # no pair is not recorded
            if len(vza_raa_sza_record) > 0:
                misr_records.append(misr_record)

        roi_record['misr_ahi'] = misr_records
        vza_raa_sza_matched_record.append(roi_record)

    ###############################################
    # demo: [{
    #     "roi_name": "0.0_120",
    #     "misr_ahi": [{
    #         "path_orbit_camera": "P099_O088273_4",
    #         "ahi_matched": [{
    #             "ahi_time": "201607232300",
    #             "raa_diff": 1.6948099999999897,
    #             "time_diff": 6869.5
    #         }]
    #     }]
    # }]
    ###############################################

    # save matched data pairs
    current_dir = os.getcwd()
    vza_raa_sza_record_filename = os.path.join(current_dir,
                                               vza_raa_sza_record_file)
    numpy.save(vza_raa_sza_record_filename, vza_raa_sza_matched_record)

    return vza_raa_sza_matched_record


if __name__ == "__main__":
    vza_raa_sza_matched_data_pairs = record_VZA_RAA_SZA_matched()
    print(vza_raa_sza_matched_data_pairs)