import os
import numpy
import re
import math
import urllib.request
import netCDF4
from datetime import datetime, timedelta
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_path, orbit_to_time_range

WORK_SPACE = os.getcwd()

ROI_SIZE = 0.04
MISR_CAMERA_INDEX = {'0.0': [4], '26.1': [3, 5], '45.6': [2, 6], '60.0': [1, 7], '70.5': [0, 8]}

START_TIME = '2017-01-01T00:00:00Z'
END_TIME = '2019-12-31T23:59:59Z'
# daytime range
AHI_LOCALTIME_START = '08:00:00Z'
AHI_LOCALTIME_END = '15:59:59Z'

# VZA diff
DIFF_VZA_THRESHOLD = 1 # degree
# VAA diff
DIFF_VAA_THRESHOLD = 5 # degree
# time diff
DIFF_TIME_THRESHOLD = 10 * 60  # seconds

AHI_VZA_BIN = '/data01/people/beichen/data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
AHI_VAA_BIN = '/data01/people/beichen/data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'
MISR_DATA_FOLDER = '/data01/people/beichen/data/MISR4AHI2015070120210630_3'

GRO_OBS_COND_TXT = 'MISR_AHI_RAY_MATCH_RECORD.txt'


def re_download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    for orbit_time in time_range:
        matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(orbit_time))
        yy = matchObj.group(1)
        mm = matchObj.group(2)
        dd = matchObj.group(3)

        t = str(yy) + '.' + str(mm) + '.' + str(dd)
        P = 'P' + (3 - len(str(path))) * '0' + str(path)
        O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
        F = 'F' + '08'
        v = '0023'
        base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2ASLS.003'
        filename = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'

        download_url = base_url + '/' + t + '/' + filename
        storage_path = folder + '/' + filename

        try:
            urllib.request.urlretrieve(download_url, filename=storage_path)
        except Exception as e:
            print('Error: ' + download_url)
            print(e)


def get_misr_filename(orbit):
    path = orbit_to_path(orbit)
    P = 'P' + (3 - len(str(path))) * '0' + str(path)
    O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
    F = 'F' + '08'
    v = '0023'
    misr_v3_nc_file = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'
    misr_nc_filename = MISR_DATA_FOLDER + '/' + misr_v3_nc_file

    return misr_nc_filename


def get_misr_obs_angle(roi_extent, orbit, camera_idx):
    misr_filename = get_misr_filename(orbit)
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    if os.path.exists(misr_filename):
        m_file = None
        file_read_flag = 1
        while file_read_flag == 1:
            try:
                m_file = MtkFile(misr_filename)
                file_read_flag = 0
            except Exception as e:
                print(e)
                path = orbit_to_path(orbit)
                misr_v3_nc_file = misr_filename.split('/')[(len(misr_filename.split('/')))]
                print('re-download:', misr_v3_nc_file)
                re_download_MISR_MIL2ASLS03_NC(MISR_DATA_FOLDER, path, orbit)
        m_grid = m_file.grid('4.4_KM_PRODUCTS')
        # MISR VZA
        roi_misr_vza = 0.0
        vza_field = m_grid.field('GEOMETRY/View_Zenith_Angle[' + str(camera_idx) + ']')
        f_vza_data = vza_field.read(roi_r).data()
        f_vza_data = numpy.array(f_vza_data)
        # in single array
        roi_misr_vza_list = f_vza_data.flatten()
        roi_misr_vza_list = roi_misr_vza_list[roi_misr_vza_list > 0.]
        # has available values?
        if len(roi_misr_vza_list) > 0:
            roi_misr_vza = roi_misr_vza_list.mean()
        else:
            return None, None
        # MISR VAA
        roi_misr_vaa = 0.0
        vaa_field = m_grid.field('GEOMETRY/View_Azimuth_Angle[' + str(camera_idx) + ']')
        f_vaa_data = vaa_field.read(roi_r).data()
        f_vaa_data = numpy.array(f_vaa_data)
        roi_misr_vaa_list = f_vaa_data.flatten()
        roi_misr_vaa_list = roi_misr_vaa_list[roi_misr_vaa_list > 0.]
        # has available values?
        if len(roi_misr_vaa_list) > 0:
            if roi_misr_vaa_list.max() - roi_misr_vaa_list.min() > 180:
                roi_misr_vaa = 0.0
            else:
                roi_misr_vaa = roi_misr_vaa_list.mean()
        else:
            return None, None

        return roi_misr_vza, roi_misr_vaa

    else:
        return None, None


# get time offset to UTC, by lontitude not timezone
def ahi_lon_timeoffset(lon):
    lon_interval = 15
    UTC_e_lon = lon_interval / 2

    timeoffset = math.ceil((lon - UTC_e_lon) / lon_interval)

    return timeoffset


def get_region_ahi_vza(region_extent):
    ahi_vza_DN = numpy.fromfile(AHI_VZA_BIN, dtype='>f4')
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


def get_region_ahi_vaa(region_extent):
    ahi_vaa_DN = numpy.fromfile(AHI_VAA_BIN, dtype='>f4')
    ahi_vaa_DN = ahi_vaa_DN.reshape(3000, 3000)
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)
    roi_vaa = ahi_vaa_DN[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    return roi_vaa


def get_ahi_obs_angle(roi_extent):
    ahi_vza = get_region_ahi_vza(roi_extent)
    ahi_vaa = get_region_ahi_vaa(roi_extent)
    return ahi_vza.mean(), ahi_vaa.mean()


def get_raa(aa1, aa2):
    raa = 0
    diff = abs(aa1 - aa2)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def is_vza_vaa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa):
    if abs(misr_vza - ahi_vza) <= DIFF_VZA_THRESHOLD:
        diff_vaa = get_raa(misr_vaa, ahi_vaa)
        if diff_vaa <= DIFF_VAA_THRESHOLD:
            return True
        else:
            return False
    else:
        return False


def roi_ray_match(roi_name, cood_point, misr_vza_str):
    print(roi_name)
    print(cood_point)
    # search full matching
    geocond_record_str = 'MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA\n'
    # print('MISR VZAs', misr_vza_str)
    # print(cood_point)
    # record
    matched_record = []
    misr_ray_matched_npy_filename = os.path.join(WORK_SPACE, roi_name + '_matched_record.npy')
    
    geocond_record_str += '\nROI_NAME:' + roi_name + '\n'

    # loc_info
    loc_record = {}
    loc_record['roi_name'] = roi_name
    matched_infos = []

    lon4search = cood_point[0]
    lat4search = cood_point[1]
    geocond_record_str += 'Location: (' + str(lon4search) + ', ' + str(lat4search) + ')\n'
    # ROI extent (ullat, ullon, lrlat, lrlon)
    roi_extent = [lat4search + ROI_SIZE / 2, lon4search - ROI_SIZE / 2, lat4search - ROI_SIZE / 2, lon4search + ROI_SIZE / 2]

    # AHI Obs Condition
    ahi_vza, ahi_vaa = get_ahi_obs_angle(roi_extent)

    # Full Match Screening
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    pathList = roi_r.path_list
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
        for orbit in orbits:
            camera_idx_array = MISR_CAMERA_INDEX[misr_vza_str]
            for camera_idx in camera_idx_array:
                try:
                    misr_vza, misr_vaa = get_misr_obs_angle(roi_extent, orbit, camera_idx)
                    if misr_vza != None:
                        vza_vaa_matched = is_vza_vaa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa)
                        if vza_vaa_matched:
                            # get AHI data with MISR Obs time
                            roi_blocks = roi_r.block_range(path)
                            block_no = roi_blocks[0]
                            misr_nc_filename = get_misr_filename(orbit)
                            misr_nc = netCDF4.Dataset(misr_nc_filename)
                            misr_nc_44 = misr_nc.groups['4.4_KM_PRODUCTS']
                            misr_block_var = misr_nc_44.variables['Block_Number']
                            misr_time_var = misr_nc_44.variables['Time']
                            misr_units = misr_time_var.units
                            start_time = misr_units[14:-8] + 'Z'
                            misr_start_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
                            block_time_num = int(len(misr_time_var[:]) / len(misr_block_var[:]))
                            blocks = numpy.array(misr_block_var[:])
                            block_time_s = numpy.argmax(blocks == block_no - 1)
                            block_time_e = numpy.argmax(blocks == block_no)
                            block_time_array = misr_time_var[block_time_s * block_time_num:block_time_e * block_time_num]
                            block_time_offset = round(block_time_array.mean())
                            block_time_offset_s = timedelta(seconds=block_time_offset)
                            camera_time_offset_s = timedelta(seconds=int((7 * 60) / 4 * (camera_idx - 4)))
                            misr_roi_date = misr_start_date + block_time_offset_s + camera_time_offset_s
                            misr_nc.close()

                            # daytime range on same day
                            center_pt = [(roi_extent[0] + roi_extent[2]) / 2, (roi_extent[1] + roi_extent[3]) / 2]
                            time_offset = ahi_lon_timeoffset(center_pt[1])
                            local_date = misr_roi_date + timedelta(hours=time_offset)
                            local_day_str = local_date.strftime("%Y-%m-%dT")
                            local_time_start_str = local_day_str + AHI_LOCALTIME_START
                            local_date_start = datetime.strptime(local_time_start_str, "%Y-%m-%dT%H:%M:%SZ")
                            utc_date_start = local_date_start - timedelta(hours=time_offset)
                            local_time_end_str = local_day_str + AHI_LOCALTIME_END
                            local_date_end = datetime.strptime(local_time_end_str, "%Y-%m-%dT%H:%M:%SZ")
                            utc_date_end = local_date_end - timedelta(hours=time_offset)

                            # for record required AHI SAA data
                            ahi_obstime_diffs = []
                            date_interval = timedelta(minutes=10)
                            date_ahi = utc_date_start
                            # print(utc_date_start.strftime("%Y-%m-%dT%H:%M:%SZ"), utc_date_end.strftime("%Y-%m-%dT%H:%M:%SZ"))
                            while date_ahi < utc_date_end:
                                datetime_diff = date_ahi - misr_roi_date
                                datetime_diff_s = abs(datetime_diff.total_seconds())
                                # ## SZA match ###
                                if datetime_diff_s < DIFF_TIME_THRESHOLD:
                                    ahi_data_time = date_ahi.strftime("%Y%m%d%H%M")
                                    # no download, just record
                                    ahi_obstime_diffs.append([ahi_data_time, datetime_diff_s])
                                date_ahi = date_ahi + date_interval
                            # sort by time diff
                            ahi_obstime_diffs = sorted(ahi_obstime_diffs, key=(lambda x: x[1]))
                            # matched observation time
                            ahi_obs_time = ahi_obstime_diffs[0][0]
                            misr_roi_block_time = misr_roi_date.strftime("%Y%m%d%H%M")
                            # matched info
                            misr_roi_vza = '%.3f' % misr_vza
                            ahi_roi_vza = '%.3f' % ahi_vza
                            misr_roi_vaa = '%.3f' % misr_vaa
                            ahi_roi_vaa = '%.3f' % ahi_vaa
                            scattering_angle = '%.3f' % scattering_angle
                            # matched info: MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
                            record_item = str(path) + '\t' + str(orbit) + '\t' + str(camera_idx) + '\t' + misr_roi_block_time + '\t' + ahi_obs_time + '\t' + str(misr_roi_vza) + '\t' + str(ahi_roi_vza) + '\t' + str(misr_roi_vaa) + '\t' + str(ahi_roi_vaa) + '\t' + str(scattering_angle)
                            print(record_item)
                            geocond_record_str += record_item + '\n'
                            matched_info = [str(path), str(orbit), str(camera_idx), misr_roi_block_time, ahi_obs_time, str(misr_roi_vza), str(ahi_roi_vza), str(misr_roi_vaa), str(ahi_roi_vaa), str(scattering_angle)]
                            match_info_record = {}
                            misr_path_orbit_camera = 'P' + (3 - len(str(path))) * '0' + str(path) + '_O' + (6 - len(str(orbit))) * '0' + str(orbit) + '_' + str(camera_idx)
                            match_info_record['misr_path_orbit_camera'] = misr_path_orbit_camera
                            match_info_record['matched_info'] = matched_info
                            matched_infos.append(match_info_record)
                except Exception as e:
                    print('orbit:', orbit)
                    print(e)
    loc_record['roi_misr_infos'] = matched_infos
    if len(matched_infos) > 0:
        matched_record.append(loc_record)
    ###############################################
    # demo: [{
    #     "roi_name": "45.6_1",
    #     "roi_misr_infos": [{
    #         "misr_path_orbit_camera": "P099_O088273_4",
    #         "matched_info": [...]
    #     },
    #     ...]
    # },
    # ...]
    ###############################################
    numpy.save(misr_ray_matched_npy_filename, numpy.array(matched_record))

    # save result as txt
    with open(os.path.join(WORK_SPACE, roi_name + '_' + GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


if __name__ == "__main__":
    # roi_name = '45_1'
    # cood_point = [140.45, 40.75]
    # misr_vza_str = '45.6'

    roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0', '60.0_1', '70.5_0', '70.5_1']
    cood_points = [[143.45, -4.05], [140.25, -3.25], [125.15, -16.05], [149.05, -21.45], [140.45, 40.75], [116.35, -34.55], [142.45, 52.65], [139.75, 53.75], [162.25, 59.85], [163.25, 59.75]]
    misr_vza_str_s = ['0.0', '0.0', '26.1', '26.1', '45.6', '45.6', '60.0', '60.0', '70.5', '70.5']

    for idx in range(len(roi_names)):
        roi_name = roi_names[idx]
        cood_point = cood_points[idx]
        misr_vza_str = misr_vza_str_s[idx]

        roi_ray_match(roi_name, cood_point, misr_vza_str)
