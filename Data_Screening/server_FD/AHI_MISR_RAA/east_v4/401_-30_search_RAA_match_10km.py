import os
import numpy
import re
import math
import urllib.request
import netCDF4
from datetime import datetime, timedelta
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_path, orbit_to_time_range
from tqdm import tqdm

WORK_SPACE = os.getcwd()

ROI_SIZE = 0.04
MISR_CAMERA_INDEX = {'0.0': [4], '26.1': [3, 5], '45.6': [2, 6], '60.0': [1, 7], '70.5': [0, 8]}

MISR_CAMERA_VZA_NAME = ['DfZenith', 'CfZenith', 'BfZenith', 'AfZenith', 'AnZenith', 'AaZenith', 'BaZenith', 'CaZenith', 'DaZenith']
MISR_CAMERA_VAA_NAME = ['DfAzimuth', 'CfAzimuth', 'BfAzimuth', 'AfAzimuth', 'AnAzimuth', 'AaAzimuth', 'BaAzimuth', 'CaAzimuth', 'DaAzimuth']

START_TIME = '2018-01-01T00:00:00Z'
END_TIME = '2018-12-31T23:59:59Z'
# daytime range
AHI_LOCALTIME_START = '08:00:00Z'
AHI_LOCALTIME_END = '15:59:59Z'

# VZA diff
DIFF_VZA_THRESHOLD = 1 # degree
# RAA diff
DIFF_RAA_THRESHOLD = 10 # degree
# time diff
DIFF_TIME_THRESHOLD = 5 * 60  # seconds

MISR_SR_DATA_FOLDER = '/data01/people/beichen/data/MISR4AHI2015070120210630_3'
MISR_GEO_DATA_FOLDER = '/data01/people/beichen/data/MISR4AHI_GEO_2018/East'
AHI_VZA_BIN ='/data01/people/beichen/data/AHI/AHI_VZA.npy'
AHI_VAA_BIN ='/data01/people/beichen/data/AHI/AHI_VAA.npy'

ulat_range = -30

GRO_OBS_COND_TXT = 'MISR_GEO_RAA_MATCH_RECORD_E_10km_' + str(ulat_range) + '.txt'


def re_download_MISR_MIB2GEOP_3_HDF(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    for orbit_time in time_range:
        matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(orbit_time))
        yy = matchObj.group(1)
        mm = matchObj.group(2)
        dd = matchObj.group(3)

        t = str(yy) + '.' + str(mm) + '.' + str(dd)
        P = 'P' + (3-len(str(path)))*'0' + str(path)
        O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
        F = 'F' + '03'
        v = '0013'
        base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIB2GEOP.002'
        filename = 'MISR_AM1_GP_GMP_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'

        download_url = base_url + '/' + t + '/' + filename
        storage_path = folder + '/' + filename

        if os.path.exists(storage_path):
            try:
                m_file = MtkFile(storage_path)
            except Exception as e:
                print('Error: ' + download_url)
                print(e)
                urllib.request.urlretrieve(download_url, filename=storage_path)
        else:
            try:
                urllib.request.urlretrieve(download_url, filename=storage_path)
            except Exception as e:
                print('Error: ' + download_url)
                print(e)


def get_misr_geo_filename(orbit):
    path = orbit_to_path(orbit)
    P = 'P' + (3-len(str(path)))*'0' + str(path)
    O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
    F = 'F' + '03'
    v = '0013'
    misr_geo_filename = 'MISR_AM1_GP_GMP_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'
    misr_hdf_filename = MISR_GEO_DATA_FOLDER + '/' + misr_geo_filename

    return misr_hdf_filename


def get_misr_time_filename(orbit):
    path = orbit_to_path(orbit)
    P = 'P' + (3 - len(str(path))) * '0' + str(path)
    O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
    F = 'F' + '08'
    v = '0023'
    misr_v3_nc_file = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'
    misr_nc_filename = MISR_SR_DATA_FOLDER + '/' + misr_v3_nc_file

    return misr_nc_filename


def get_misr_obs_angle(roi_extent, orbit, camera_idx):
    misr_filename = get_misr_geo_filename(orbit)
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
                re_download_MISR_MIB2GEOP_3_HDF(MISR_GEO_DATA_FOLDER, path, orbit)
        m_grid = m_file.grid('GeometricParameters')
        # MISR VZA
        roi_misr_vza = 0.0
        vza_field = m_grid.field(MISR_CAMERA_VZA_NAME[camera_idx])
        f_vza_data = vza_field.read(roi_r).data()
        f_vza_data = numpy.array(f_vza_data)
        # in single array
        roi_misr_vza_list = f_vza_data.flatten()
        roi_misr_vza_list = roi_misr_vza_list[roi_misr_vza_list > 0.]
        # has available values?
        if len(roi_misr_vza_list) > 0:
            roi_misr_vza = roi_misr_vza_list.mean()
        else:
            return None, None, None, None
        # MISR VAA
        roi_misr_vaa = 0.0
        vaa_field = m_grid.field(MISR_CAMERA_VAA_NAME[camera_idx])
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
            return None, None, None, None
        # MISR SZA
        roi_misr_sza = 0.0
        sza_field = m_grid.field('SolarZenith')
        f_sza_data = sza_field.read(roi_r).data()
        f_sza_data = numpy.array(f_sza_data)
        # in single array
        roi_misr_sza_list = f_sza_data.flatten()
        roi_misr_sza_list = roi_misr_sza_list[roi_misr_sza_list > 0.]
        # has available values?
        if len(roi_misr_sza_list) > 0:
            roi_misr_sza = roi_misr_sza_list.mean()
        else:
            return None, None, None, None
        # MISR SSA
        roi_misr_saa = 0.0
        saa_field = m_grid.field('SolarAzimuth')
        f_saa_data = saa_field.read(roi_r).data()
        f_saa_data = numpy.array(f_saa_data)
        # in single array
        roi_misr_saa_list = f_saa_data.flatten()
        roi_misr_saa_list = roi_misr_saa_list[roi_misr_saa_list > 0.]
        # has available values?
        if len(roi_misr_saa_list) > 0:
            roi_misr_saa = roi_misr_saa_list.mean()
            roi_misr_saa = (roi_misr_saa + 180) % 360
        else:
            return None, None, None, None

        return roi_misr_vza, roi_misr_vaa, roi_misr_sza, roi_misr_saa

    else:
        return None, None, None, None


# get time offset to UTC, by lontitude not timezone
def ahi_lon_timeoffset(lon):
    lon_interval = 15
    UTC_e_lon = lon_interval / 2

    timeoffset = math.ceil((lon - UTC_e_lon) / lon_interval)

    return timeoffset


def get_region_ahi_vza(region_extent):
    ahi_vza_DN = numpy.load(AHI_VZA_BIN, allow_pickle=True)
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
    ahi_vaa_DN = numpy.load(AHI_VAA_BIN, allow_pickle=True)
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


def is_raa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa, misr_saa, ahi_saa):
    if abs(misr_vza - ahi_vza) <= DIFF_VZA_THRESHOLD:
        misr_raa = get_raa(misr_vaa, misr_saa)
        ahi_raa = get_raa(ahi_vaa, ahi_saa)
        if abs(misr_raa-ahi_raa) <= DIFF_RAA_THRESHOLD:
            return True
        else:
            return False
    else:
        return False


def main():
    # loc_folder = os.path.join(WORK_SPACE, 'lonlat4searchFM')
    # search full matching
    geocond_record_str = 'MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA MISR_SZA AHI_SZA MISR_SAA AHI_SAA\n'
    MISRVZAs = [0.0, 26.1, 45.6, 60.0, 70.5]
    # record
    matched_record = []
    misr_ray_matched_npy_filename = os.path.join(WORK_SPACE, 'MISR_matched_record_east_10km_' + str(ulat_range) + '.npy')

    point_locations_npy_filename = os.path.join(WORK_SPACE, 'FD_180e_10km_lonlat.npy')
    search_cood = numpy.load(point_locations_npy_filename, allow_pickle=True)
    for cood_point_idx in tqdm(range(len(search_cood)), desc='Location', leave=False):
        cood_point = search_cood[cood_point_idx]
        # loc_info
        loc_record = {}
        loc_record['location'] = cood_point
        matched_infos = []

        lon4search = cood_point[0]
        lat4search = cood_point[1]
        
        if lat4search <= ulat_range and lat4search > (ulat_range-10):
            # geocond_record_str += 'Location: (' + str(lon4search) + ', ' + str(lat4search) + ')\n'
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
                    for vza_idx in range(len(MISRVZAs)):
                        misr_vza_str = str(MISRVZAs[vza_idx])
                        # print('MISR VZAs', misr_vza_str)
                        # geocond_record_str += '\nMISR_CAMERA_ANGLE:' + misr_vza_str + '\n'
                        camera_idx_array = MISR_CAMERA_INDEX[misr_vza_str]
                        for camera_idx in camera_idx_array:
                            try:
                                misr_vza, misr_vaa, misr_sza, misr_saa = get_misr_obs_angle(roi_extent, orbit, camera_idx)
                                if misr_vza != None:
                                    ahi_sza = misr_sza # temp
                                    ahi_saa = misr_saa # temp
                                    raa_matched = is_raa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa, misr_saa, ahi_saa)
                                    if raa_matched:
                                        # get AHI data with MISR Obs time
                                        roi_blocks = roi_r.block_range(path)
                                        block_no = roi_blocks[0]
                                        misr_nc_filename = get_misr_time_filename(orbit)
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
                                        print('**********Full Matching**********')
                                        misr_roi_vza = '%.3f' % misr_vza
                                        ahi_roi_vza = '%.3f' % ahi_vza
                                        misr_roi_vaa = '%.3f' % misr_vaa
                                        ahi_roi_vaa = '%.3f' % ahi_vaa
                                        misr_roi_sza = '%.3f' % misr_sza
                                        ahi_roi_sza = '%.3f' % ahi_sza
                                        misr_roi_saa = '%.3f' % misr_saa
                                        ahi_roi_saa = '%.3f' % ahi_saa
                                        
                                        # matched info: MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA MISR_SZA AHI_SZA MISR_SAA AHI_SAA
                                        matched_info = [str(path), str(orbit), str(camera_idx), misr_roi_block_time, ahi_obs_time, str(misr_roi_vza), str(ahi_roi_vza), str(misr_roi_vaa), str(ahi_roi_vaa), str(misr_roi_sza), str(ahi_roi_sza), str(misr_roi_saa), str(ahi_roi_saa)]
                                        print(cood_point)
                                        print(matched_info)
                                        geocond_record_str += str(round(lon4search, 3)) + ', ' + str(round(lat4search, 3)) +'\t' + misr_vza_str + '\t' + str(path) + '\t' + str(orbit) + '\t' + str(camera_idx) + '\t' + misr_roi_block_time + '\t' + ahi_obs_time + '\t' + str(misr_roi_vza) + '\t' + str(ahi_roi_vza) + '\t' + str(misr_roi_vaa) + '\t' + str(ahi_roi_vaa) + '\t' + str(misr_roi_sza) + '\t' + str(ahi_roi_sza) + '\t' + str(misr_roi_saa) + '\t' + str(ahi_roi_saa) + '\n'

                                        matched_infos.append(matched_info)
                            except Exception as e:
                                print('orbit:', orbit)
                                print(e)
        loc_record['matched_infos'] = matched_infos
        if len(matched_infos) > 0:
            matched_record.append(loc_record)
    numpy.save(misr_ray_matched_npy_filename, numpy.array(matched_record))
    ###############################################
    # demo: [{
    #     'location': [lon, lat],
    #     "matched_infos": [[...], ...]
    # },
    # ...]
    ###############################################

    # save result as txt
    with open(os.path.join(WORK_SPACE, GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


if __name__ == "__main__":
    main()
