import os
import numpy

base_path = '/data01/people/beichen/workspace/20230226/ray_VZA_VAA_case'

MCD12Q1_006_10KM_npy = os.path.join(base_path, 'MCD12Q1_006_10km.npy')
misr_matched_info_npy = os.path.join(base_path, 'AHI_MISR_Ray-matched_1mon.npy')

LC_SIZE = 0.1
MISR_CAMERA_ANGLE = {
    '0': '70',
    '1': '60',
    '2': '45',
    '3': '26',
    '4': '0',
    '5': '26',
    '6': '45',
    '7': '60',
    '8': '70',
}
MODIS_LC_IS_FOREST = {
    '0': '0',
    '1': '1',
    '2': '1',
    '3': '1',
    '4': '1',
    '5': '1',
    '6': '0',
    '7': '0',
    '8': '0',
    '9': '0',
    '10': '0',
    '11': '0',
    '12': '0',
    '13': '0',
    '14': '0',
    '15': '0',
    '16': '0'
}


def build_ROI_ws(lc_map, matched_record):
    for matched_info in matched_record:
        loc = matched_info['location']
        camera_idx = matched_info['matched_infos'][0][2]
        camera_angle_str = MISR_CAMERA_ANGLE[camera_idx]
        lon = round(loc[0], 3)
        lat = round(loc[1], 3)
        lat_lon_str = str(lat) + '_' + str(lon)
        lc_lon_idx = int((lon - 85)/LC_SIZE)
        lc_lat_idx = int((60 - lat)/LC_SIZE)
        lc_code_str = str(int(lc_map[lc_lat_idx][lc_lon_idx]))
        lc_is_forest = MODIS_LC_IS_FOREST[lc_code_str]

        angle_folder = os.path.join(base_path, camera_angle_str)
        if not os.path.exists(angle_folder):
            os.makedirs(angle_folder)
        lc_folder = os.path.join(angle_folder, lc_is_forest)
        if not os.path.exists(lc_folder):
            os.makedirs(lc_folder)
        roi_folder = os.path.join(lc_folder, camera_angle_str + '_' + lc_code_str + '_' + lat_lon_str)
        if not os.path.exists(roi_folder):
            os.makedirs(roi_folder)


if __name__ == "__main__":
    modis_lc = numpy.load(MCD12Q1_006_10KM_npy, allow_pickle=True)
    ray_matches = numpy.load(misr_matched_info_npy, allow_pickle=True)

    build_ROI_ws(modis_lc, ray_matches)