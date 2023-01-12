# for python 3.6
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_time_range
import math
from datetime import datetime, timedelta
import numpy
import os
import bz2
# import shutil
import netCDF4
import re
import urllib.request

# storage path
WORK_SPACE = os.getcwd()

ROI_SIZE = 0.1
MISR_CAMERA_INDEX = {'0.0': [4], '26.1': [3, 5], '45.6': [2, 6], '60.0': [1, 7], '70.5': [0, 8]}

# time range for our study
START_TIME = '2017-01-01T00:00:00Z'
END_TIME = '2019-12-31T23:59:59Z'
# daytime range
AHI_LOCALTIME_START = '08:00:00Z'
AHI_LOCALTIME_END = '15:59:59Z'

# time diff
SZA_TIME_THRESHOLD = 10 * 60  # seconds
# angle threshold
SCATTERING_ANGLE_THRESHOLD = 175

# data path
MISR_DATA_FOLDER = '/data01/people/beichen/data/MISR4AHI2015070120210630_3'
AHI_VZA_BIN = '/data01/people/beichen/data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
AHI_VAA_BIN = '/data01/people/beichen/data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'

# record files
GRO_OBS_COND_TXT = 'MISR_AHI_RAA_MATCH_RECORD.txt'


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


# get time offset to UTC, by lontitude not timezone
def ahi_lon_timeoffset(lon):
    lon_interval = 15
    UTC_e_lon = lon_interval / 2

    timeoffset = math.ceil((lon - UTC_e_lon) / lon_interval)

    return timeoffset


def get_raa(vaa, saa):
    raa = 0
    diff = abs(vaa - saa)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def get_region_ahi_raa(region_extent, ahi_vaa, ahi_saa):
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)

    ahi_vaa = ahi_vaa.reshape(3000, 3000)
    ahi_saa = ahi_saa.reshape(3000, 3000)
    roi_vaa = ahi_vaa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    roi_saa = ahi_saa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]

    roi_raa = numpy.zeros_like(roi_vaa)
    for y in range(len(roi_vaa)):
        for x in range(len(roi_vaa[0])):
            vaa = roi_vaa[y][x]
            saa = roi_saa[y][x]
            raa = get_raa(vaa, saa)
            roi_raa[y][x] = raa

    return roi_vaa, roi_saa, roi_raa


def get_misr_raa(misr_vaa, misr_saa):
    misr_raa = numpy.zeros_like(misr_vaa)
    for i in range(len(misr_vaa)):
        vaa = misr_vaa[i]
        saa = misr_saa[i]
        raa = get_raa(vaa, saa)
        misr_raa[i] = raa

    return misr_raa


def misr_saa_true(saa_dn):
    return (saa_dn + 180) % 360


def misr_saa_true_list(saa_dn_list):
    saa_list = []
    for saa_dn in saa_dn_list:
        misr_saa = misr_saa_true(saa_dn)
        saa_list.append(misr_saa)
    return numpy.array(saa_list)


def get_scattering_angle(misr_vza, misr_raa, ahi_vza, ahi_raa):
    # cos(ScatteringAngle) = -cos(GEO_VZA)*cos(LEO_VZA)-cos(GEO_VAA-LEO_VAA)*sin(GEO_VZA)*sin(LEO_VZA)
    scattering_angle = math.degrees(math.acos(-math.cos(math.radians(ahi_vza)) * math.cos(math.radians(misr_vza)) - math.cos(math.radians(ahi_raa - misr_raa)) * math.sin(math.radians(ahi_vza)) * math.sin(math.radians(misr_vza))))
    return scattering_angle


def misr_ahi_raa_matching(roi_extent, roi_vza_misr, roi_vza_ahi, misr_ls_file, ahi_vaa_file, ahi_saa_file, camera_index):
    # MISR RAA
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    m_file = MtkFile(misr_ls_file)
    m_grid = m_file.grid('4.4_KM_PRODUCTS')
    m_field_vaa = m_grid.field('GEOMETRY/View_Azimuth_Angle[' + str(camera_index) + ']')
    m_field_saa = m_grid.field('GEOMETRY/Solar_Azimuth_Angle')
    # in single array
    f_vaa_data = m_field_vaa.read(roi_r).data()
    f_vaa_data = numpy.array(f_vaa_data)
    roi_misr_vaa_list = f_vaa_data.flatten()
    f_saa_data = m_field_saa.read(roi_r).data()
    f_saa_data = numpy.array(f_saa_data)
    roi_misr_saa_list = f_saa_data.flatten()
    roi_misr_vaa_list = roi_misr_vaa_list[roi_misr_vaa_list > 0.]
    roi_misr_saa_list = roi_misr_saa_list[roi_misr_saa_list > 0.]
    try:
        roi_misr_saa_list = misr_saa_true_list(roi_misr_saa_list)
        f_raa_data = get_misr_raa(roi_misr_vaa_list, roi_misr_saa_list)
        roi_misr_vaa = roi_misr_vaa_list.mean()
        roi_misr_saa = roi_misr_saa_list.mean()
        roi_misr_raa = f_raa_data.mean()
        # AHI RAA
        ahi_vaa_dn = numpy.fromfile(ahi_vaa_file, dtype='>f4')
        ahi_saa_dn = numpy.fromfile(ahi_saa_file, dtype='>f4')
        roi_ahi_all_vaa, roi_ahi_all_saa, roi_ahi_all_raa = get_region_ahi_raa(roi_extent, ahi_vaa_dn, ahi_saa_dn)
        roi_ahi_vaa = roi_ahi_all_vaa.mean()
        roi_ahi_saa = roi_ahi_all_saa.mean()
        roi_ahi_raa = roi_ahi_all_raa.mean()
        
        # scattering angle with RAA
        scattering_angle_raa = get_scattering_angle(roi_vza_misr, roi_misr_raa, roi_vza_ahi, roi_ahi_raa)

        # misr_vaa, ahi_vaa, misr_saa, ahi_saa, misr_raa, ahi_raa, scattering_angle_raa
        return roi_misr_vaa, roi_ahi_vaa, roi_misr_saa, roi_ahi_saa, roi_misr_raa, roi_ahi_raa, scattering_angle_raa
    except Exception as e:
        print(e)
        return 0, 0, 0, 0, 0, 0, 0


def get_region_mean_misr_sza(misr_hdf_filename, roi_extent):
    m_file = MtkFile(misr_hdf_filename)
    m_grid = m_file.grid('4.4_KM_PRODUCTS')
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    m_field = m_grid.field('GEOMETRY/Solar_Zenith_Angle')       # angle at 0° scan time...
    f_sza_data = m_field.read(roi_r).data()
    f_sza_data = numpy.array(f_sza_data)
    # in single array
    roi_misr_sza_list = f_sza_data.flatten()
    roi_misr_sza_list = roi_misr_sza_list[roi_misr_sza_list > 0.]
    roi_misr_sza = roi_misr_sza_list.mean()
    return roi_misr_sza


def get_region_mean_ahi_sza(temp_folder, ahi_time, region_extent):
    ahi_data_folder1 = ahi_time[0:6]
    ahi_data_folder2 = ahi_time[0:8]
    ahi_sza_file = ahi_time + '.sun.zth.fld.4km.bin.bz2'
    ahi_sza_server_path = '/data01/people/beichen/data/AHI_ANGLE2017010120201231/hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_sza_file

    ahi_sza_bin_bz2 = os.path.join(temp_folder, ahi_sza_file)
    ahi_sza_bin = ahi_sza_bin_bz2[:-4]
    if not os.path.exists(ahi_sza_bin):
        try:
            # shutil.copy(ahi_sza_server_path, ahi_sza_bin_bz2)
            # zipfile = bz2.BZ2File(ahi_sza_bin_bz2)
            zipfile = bz2.BZ2File(ahi_sza_server_path)
            data = zipfile.read()
            with open(ahi_sza_bin, 'wb') as f:
                f.write(data)
            zipfile.close()
        except Exception as e:
            print(e)
            os.remove(ahi_sza_bin_bz2)
            # print(e)
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
    roi_sza = ahi_sza_DN[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    roi_vsa_mean = roi_sza.mean()

    return roi_vsa_mean


def re_download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    s_time = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(s_time))
    yy = matchObj.group(1)
    mm = matchObj.group(2)
    dd = matchObj.group(3)
    
    t = str(yy) + '.' + str(mm) + '.' + str(dd)
    P = 'P' + (3-len(str(path)))*'0' + str(path)
    O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
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


def roi_raa_match(roi_name, cood_point, misr_vza_str):
    print(roi_name)
    print(cood_point)
    # search RAA match
    tab_str = 'misr_path misr_orbit misr_camera_index misr_block_time ahi_time misr_vza ahi_vza misr_vaa ahi_vaa misr_saa ahi_saa misr_raa ahi_raa misr_sza ahi_sza scattering_angle_raa'
    geocond_record_str = tab_str + '\n'

    # record
    matched_record = []
    misr_raa_matched_npy_filename = os.path.join(WORK_SPACE, roi_name + '_matched_record.npy')
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

    ahi_vza = get_region_ahi_vza(roi_extent)
    roi_ahi_vza = ahi_vza.mean()

    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    pathList = roi_r.path_list
    
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
        for orbit in orbits:
            P = 'P' + (3 - len(str(path))) * '0' + str(path)
            O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
            F = 'F' + '08'
            v = '0023'
            misr_v3_nc_file = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'
            misr_nc_filename = MISR_DATA_FOLDER + '/' + misr_v3_nc_file
            if os.path.exists(misr_nc_filename):
                m_file = None
                file_read_flag = 1
                while file_read_flag == 1:
                    try:
                        m_file = MtkFile(misr_nc_filename)
                        file_read_flag = 0
                    except Exception as e:
                        print(e)
                        print('re-download:', misr_v3_nc_file)
                        re_download_MISR_MIL2ASLS03_NC(MISR_DATA_FOLDER, path, orbit)

                m_grid = m_file.grid('4.4_KM_PRODUCTS')
                
                camera_idx_array = MISR_CAMERA_INDEX[misr_vza_str]
                for camera_idx in camera_idx_array:
                    m_field = m_grid.field('GEOMETRY/View_Zenith_Angle[' + str(camera_idx) + ']')
                    f_vza_data = m_field.read(roi_r).data()
                    f_vza_data = numpy.array(f_vza_data)
                    # in single array
                    roi_misr_vza_list = f_vza_data.flatten()
                    roi_misr_vza_list = roi_misr_vza_list[roi_misr_vza_list > 0.]
                    # has available values?
                    if len(roi_misr_vza_list) > 0:
                        roi_misr_vza = roi_misr_vza_list.mean()
                        try:
                            roi_blocks = roi_r.block_range(path)
                            block_no = roi_blocks[0]
                            misr_nc = netCDF4.Dataset(misr_nc_filename)
                            misr_nc_44 = misr_nc.groups['4.4_KM_PRODUCTS']
                            misr_block_var = misr_nc_44.variables['Block_Number']
                            misr_time_var = misr_nc_44.variables['Time']
                            misr_units = misr_time_var.units
                            start_time = misr_units[14:-8]+'Z'
                            misr_start_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
                            block_time_num = int(len(misr_time_var[:])/len(misr_block_var[:]))
                            blocks = numpy.array(misr_block_var[:])
                            block_time_s = numpy.argmax(blocks == block_no-1)
                            block_time_e = numpy.argmax(blocks == block_no)
                            block_time_array = misr_time_var[block_time_s*block_time_num:block_time_e*block_time_num]
                            block_time_offset = round(block_time_array.mean())
                            block_time_offset_s = timedelta(seconds=block_time_offset)
                            camera_time_offset_s = timedelta(seconds=int((7*60)/4*(camera_idx-4)))
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
                            AHI_saa_filename_diffs = []
                            date_interval = timedelta(minutes=10)
                            date_ahi = utc_date_start
                            # print(utc_date_start.strftime("%Y-%m-%dT%H:%M:%SZ"), utc_date_end.strftime("%Y-%m-%dT%H:%M:%SZ"))
                            while date_ahi < utc_date_end:
                                datetime_diff = date_ahi - misr_roi_date
                                datetime_diff_s = abs(datetime_diff.total_seconds())
                                # ## SZA match ###
                                if datetime_diff_s < SZA_TIME_THRESHOLD:
                                    ahi_data_time = date_ahi.strftime("%Y%m%d%H%M")
                                    ahi_data_folder1 = date_ahi.strftime("%Y%m")
                                    ahi_data_folder2 = date_ahi.strftime("%Y%m%d")
                                    ahi_saa_file = ahi_data_time + '.sun.azm.fld.4km.bin.bz2'
                                    ahi_saa_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_saa_file
                                    # no download, just record
                                    AHI_saa_filename_diffs.append([ahi_saa_path, datetime_diff_s])
                                date_ahi = date_ahi + date_interval
                            # sort by time diff
                            AHI_saa_filename_diffs = sorted(AHI_saa_filename_diffs, key=(lambda x: x[1]))
                            # for raa match
                            matched_flag = False
                            for AHI_saa_filename_diff in AHI_saa_filename_diffs:
                                if not matched_flag:
                                    ahi_saa_server_path = '/data01/people/beichen/data/AHI_ANGLE2017010120201231/hmwr829gr.cr.chiba-u.ac.jp' + AHI_saa_filename_diff[0]
                                    temp_ws = os.path.join(WORK_SPACE, 'temp')
                                    if not os.path.exists(temp_ws):
                                        os.makedirs(temp_ws)
                                    filename_parts = ahi_saa_server_path.split('/')
                                    ahi_saa_file = filename_parts[len(filename_parts) - 1]
                                    ahi_saa_bin_bz2 = os.path.join(temp_ws, ahi_saa_file)
                                    ahi_saa_bin = ahi_saa_bin_bz2[:-4]
                                    if not os.path.exists(ahi_saa_bin):
                                        try:                                                            
                                            # shutil.copy(ahi_saa_server_path, ahi_saa_bin_bz2)
                                            # zipfile = bz2.BZ2File(ahi_saa_bin_bz2)
                                            zipfile = bz2.BZ2File(ahi_saa_server_path)
                                            data = zipfile.read()
                                            with open(ahi_saa_bin, 'wb') as f:
                                                f.write(data)
                                            zipfile.close()
                                        except Exception as e:
                                            print(e)
                                    if os.path.exists(ahi_saa_bin):
                                        m_vaa, ahi_vaa, m_saa, ahi_saa, m_raa, ahi_raa, scattering_angle_raa = misr_ahi_raa_matching(roi_extent, roi_misr_vza, roi_ahi_vza, misr_nc_filename, AHI_VAA_BIN, ahi_saa_bin, camera_idx)
                                        # ## RAA match ###
                                        scattering_angle_raa = round(scattering_angle_raa, 3)
                                        if scattering_angle_raa > SCATTERING_ANGLE_THRESHOLD:
                                            matched_flag = True
                                            # geo-obs condition
                                            misr_orbit = orbit
                                            misr_camera = camera_idx
                                            misr_roi_block_time = misr_roi_date.strftime("%Y%m%d%H%M")
                                            ahi_obs_time = ahi_saa_file.split('.')[0]
                                            misr_roi_vza = '%.3f' % roi_misr_vza
                                            ahi_roi_vza = '%.3f' % roi_ahi_vza
                                            misr_roi_vaa = '%.3f' % m_vaa
                                            ahi_roi_vaa = '%.3f' % ahi_vaa
                                            misr_roi_saa = '%.3f' % m_saa
                                            ahi_roi_saa = '%.3f' % ahi_saa
                                            misr_roi_raa = '%.3f' % m_raa
                                            ahi_roi_raa = '%.3f' % ahi_raa
                                            misr_roi_sza = get_region_mean_misr_sza(misr_nc_filename, roi_extent)
                                            misr_roi_sza = '%.3f' % misr_roi_sza
                                            ahi_roi_sza = get_region_mean_ahi_sza(temp_ws, ahi_obs_time, roi_extent)
                                            ahi_roi_sza = '%.3f' % ahi_roi_sza
                                            # misr_path misr_orbit misr_camera_index misr_block_time ahi_time misr_vza ahi_vza misr_vaa ahi_vaa misr_saa ahi_saa misr_raa ahi_raa misr_sza ahi_sza scattering_angle_raa
                                            record_item = str(path) + '\t' + str(misr_orbit) + '\t' + str(misr_camera) + '\t' + misr_roi_block_time + '\t' + ahi_obs_time + '\t' + str(misr_roi_vza) + '\t' + str(ahi_roi_vza) + '\t' + str(misr_roi_vaa) + '\t' + str(ahi_roi_vaa) + '\t' + str(misr_roi_saa) + '\t' + str(ahi_roi_saa) + '\t' + str(misr_roi_raa) + '\t' + str(ahi_roi_raa) + '\t' + str(misr_roi_sza) + '\t' + str(ahi_roi_sza) + '\t' + str(scattering_angle_raa)
                                            print(record_item)
                                            geocond_record_str += record_item + '\n'
                                            # record matched info
                                            matched_obs_info = [
                                                str(path), str(misr_orbit), str(misr_camera), misr_roi_block_time, ahi_obs_time, str(misr_roi_vza), str(ahi_roi_vza), str(misr_roi_vaa), str(ahi_roi_vaa), str(misr_roi_saa), str(ahi_roi_saa), str(misr_roi_raa), str(ahi_roi_raa), str(misr_roi_sza), str(ahi_roi_sza), str(scattering_angle_raa)
                                            ]
                                            match_info_record = {}
                                            misr_path_orbit_camera = 'P' + (3 - len(str(path))) * '0' + str(path) + '_O' + (6 - len(str(orbit))) * '0' + str(orbit) + '_' + str(camera_idx)
                                            match_info_record['misr_path_orbit_camera'] = misr_path_orbit_camera
                                            match_info_record['matched_info'] = matched_obs_info
                                            matched_infos.append(match_info_record)
                                    # shutil.rmtree(temp_ws)
                        except Exception as e:
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
    numpy.save(misr_raa_matched_npy_filename, numpy.array(matched_record))

    # save result as txt
    with open(os.path.join(WORK_SPACE, roi_name + '_' + GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


if __name__ == "__main__":

    roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0', '60.0_1', '70.5_0', '70.5_1']
    cood_points = [[143.45, -4.05], [140.25, -3.25], [125.15, -16.05], [149.05, -21.45], [140.45, 40.75], [116.35, -34.55], [142.45, 52.65], [139.75, 53.75], [162.25, 59.85], [163.25, 59.75]]
    misr_vza_str_s = ['0.0', '0.0', '26.1', '26.1', '45.6', '45.6', '60.0', '60.0', '70.5', '70.5']

    for idx in range(len(roi_names)):
        roi_name = roi_names[idx]
        cood_point = cood_points[idx]
        misr_vza_str = misr_vza_str_s[idx]

        roi_raa_match(roi_name, cood_point, misr_vza_str)