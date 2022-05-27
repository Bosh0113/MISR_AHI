# for python 3.6
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list
import math
from datetime import datetime, timedelta
import numpy
import os
import json
import bz2
import shutil
from ftplib import FTP

# time range for our study
start_t = '2015-07-01T00:00:00Z'
end_t = '2017-06-01T23:59:59Z'
# daytime range
ahi_localtime_start = '08:00:00Z'
ahi_localtime_end = '15:59:59Z'
# data path
ahi_vza_bin = '/disk1/Data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
ahi_vaa_bin = '/disk1/Data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'
misr_folder = '/disk1/Data/MISR4AHI2015070120170601'
roi_folder = '/disk1/Data/MISR_AHI_ROIs'
# storage path
WORK_SPACE = os.getcwd()

# cos diff
VZA_COS_THRESHOLD = 0.02

# time diff
SZA_TIME_THRESHOLD = 30*60  # seconds

# degree diff
RAA_DEGREE_THRESHOLD = 10.

# record files
condition = 'vza002raa10sza30min'
GRO_OBS_COND_TXT = 'geo-obs_cond_' + condition + '.txt'
MATCHED_INFO_NPY = 'MISR_AHI_matched_info_' + condition + '.npy'


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


# get time offset to UTC, by lontitude not timezone
def ahi_lon_timeoffset(lon):
    lon_interval = 15
    UTC_e_lon = lon_interval / 2

    timeoffset = math.ceil((lon - UTC_e_lon) / lon_interval)

    return timeoffset


def get_ahi_raa(vaa, saa):
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
            raa = get_ahi_raa(vaa, saa)
            roi_raa[y][x] = raa

    return roi_raa


def misr_ahi_raa_matching(roi_geoj_file, misr_ls_file, ahi_vaa_file,
                          ahi_saa_file, camera_index):
    with open(roi_geoj_file, 'r', encoding='utf-8') as f:
        geoobj = json.load(f)
        polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
        roi_extent = get_extent(polygon_pts)
        # MISR RAA
        roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2],
                          roi_extent[3])
        m_file = MtkFile(misr_ls_file)
        m_grid = m_file.grid('RegParamsLnd')
        m_field = m_grid.field('RelViewCamAziAng[' + str(camera_index) + ']')
        f_raa_data = m_field.read(roi_r).data()
        # in single array
        roi_misr_raa_list = f_raa_data.flatten()
        roi_misr_raa_list = numpy.setdiff1d(roi_misr_raa_list, [-9999])
        if len(roi_misr_raa_list) > 0:
            roi_misr_raa = roi_misr_raa_list.mean()
            # AHI RAA
            ahi_vaa_dn = numpy.fromfile(ahi_vaa_bin, dtype='>f4')
            ahi_saa_dn = numpy.fromfile(ahi_saa_bin, dtype='>f4')
            roi_ahi_all_raa = get_region_ahi_raa(roi_extent, ahi_vaa_dn,
                                                 ahi_saa_dn)
            roi_ahi_raa = roi_ahi_all_raa.mean()
            # show raa diff
            raa_diff = abs(roi_misr_raa - roi_ahi_raa)
            return roi_misr_raa, roi_ahi_raa, raa_diff
    return 0, 0, 0


def get_region_mean_misr_sza(misr_hdf_filename, roi_extent):
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
    return roi_misr_sza


def get_region_mean_ahi_sza(temp_folder, ahi_time, region_extent):
    ahi_data_folder1 = ahi_time[0:6]
    ahi_data_folder2 = ahi_time[0:8]
    ahi_sza_file = ahi_time + '.sun.zth.fld.4km.bin.bz2'
    ahi_sza_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_sza_file
    
    ahi_sza_bin_bz2 = os.path.join(temp_folder, ahi_sza_file)
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


if __name__ == "__main__":
    # AHI data ftp server
    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()

    # angles of MISR cameras
    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    geocond_record_str = ''
    matched_info_record = []

    for vza in MISR_vza:
        # read roi geoinfo
        folder = roi_folder + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                # build roi folder
                roi_matched_folder = WORK_SPACE + '/MISR_AHI_inter-com/' + str(vza) + '_' + file.split('.')[0]
                if not os.path.exists(roi_matched_folder):
                    os.makedirs(roi_matched_folder)
                roi_geoj_filename = os.path.join(folder, file)
                with open(roi_geoj_filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
                    roi_extent = get_extent(polygon_pts)
                    roi_name = str(vza) + '_' + file.split('.')[0]
                    print('***ROI:', roi_name)
                    geocond_record_str += '\n' + roi_name
                    geocond_record_str += '\n'
                    tab_str = 'misr_orbit misr_camera_index misr_block_time ahi_time misr_vza ahi_vza misr_raa ahi_raa misr_sza ahi_sza'
                    geocond_record_str += tab_str + '\n'

                    matched_roi_info = {}
                    matched_roi_info['roi_name'] = roi_name

                    ahi_vza = get_region_ahi_vza(roi_extent)
                    ahi_vza_mean = ahi_vza.mean()

                    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
                    pathList = roi_r.path_list
                    matched_roi_misr_infos = []
                    for path in pathList:
                        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
                        for orbit in orbits:
                            P = 'P' + (3 - len(str(path))) * '0' + str(path)
                            O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
                            F = 'F' + '07'
                            v = '0022'
                            hdf_file = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'
                            hdf_filename = misr_folder + '/' + hdf_file
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
                                    m_field = m_grid.field('ViewZenAng[' + str(camera) + ']')
                                    f_vza_data = m_field.read(roi_r).data()
                                    # in single array
                                    roi_misr_vza_list = f_vza_data.flatten()
                                    roi_misr_vza_list = numpy.setdiff1d(roi_misr_vza_list, [-9999])
                                    # has available values?
                                    if len(roi_misr_vza_list) > 0:
                                        roi_misr_vza = roi_misr_vza_list.mean()
                                        # ## VZA match ###
                                        a1 = 0
                                        a2 = 0
                                        if ahi_vza_mean > roi_misr_vza:
                                            a1 = ahi_vza_mean
                                            a2 = roi_misr_vza
                                        else:
                                            a1 = roi_misr_vza
                                            a2 = ahi_vza_mean
                                        differ_cos = 1 - (math.cos(math.radians(a1)) / math.cos(math.radians(a2)))
                                        if differ_cos <= VZA_COS_THRESHOLD:
                                            print('-- path:', path, '--', 'orbit:', orbit, '--', 'camera:', camera)

                                            # for SZA match
                                            roi_blocks = roi_r.block_range(path)
                                            blocks_time_list = m_file.block_metadata_field_read('PerBlockMetadataTime', 'BlockCenterTime')
                                            roi_misr_time = blocks_time_list[roi_blocks[0]-1]
                                            # print('   ', roi_misr_time)

                                            misr_time_str = roi_misr_time.split('.')[0] + 'Z'
                                            misr_roi_date = datetime.strptime(misr_time_str, "%Y-%m-%dT%H:%M:%SZ")
                                            # daytime range on same day
                                            center_pt = [(roi_extent[0] + roi_extent[2]) / 2, (roi_extent[1] + roi_extent[3]) / 2]
                                            time_offset = ahi_lon_timeoffset(center_pt[1])
                                            local_date = misr_roi_date + timedelta(hours=time_offset)
                                            local_day_str = local_date.strftime("%Y-%m-%dT")
                                            local_time_start_str = local_day_str + ahi_localtime_start
                                            local_date_start = datetime.strptime(local_time_start_str, "%Y-%m-%dT%H:%M:%SZ")
                                            utc_date_start = local_date_start - timedelta(hours=time_offset)
                                            local_time_end_str = local_day_str + ahi_localtime_end
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
                                                    ahi_saa_data_ftp = AHI_saa_filename_diff[0]
                                                    temp_ws = os.path.join(WORK_SPACE, 'temp')
                                                    if not os.path.exists(temp_ws):
                                                        os.makedirs(temp_ws)
                                                    filename_parts = ahi_saa_data_ftp.split('/')
                                                    ahi_saa_file = filename_parts[len(filename_parts) - 1]
                                                    ahi_saa_bin_bz2 = os.path.join(temp_ws, ahi_saa_file)
                                                    ahi_saa_bin = ''
                                                    try:
                                                        with open(ahi_saa_bin_bz2, 'wb') as f:
                                                            ftp.retrbinary('RETR ' + ahi_saa_data_ftp, f.write, 1024 * 1024)
                                                        zipfile = bz2.BZ2File(ahi_saa_bin_bz2)
                                                        data = zipfile.read()
                                                        ahi_saa_bin = ahi_saa_bin_bz2[:-4]
                                                        with open(ahi_saa_bin, 'wb') as f:
                                                            f.write(data)
                                                    except Exception as e:
                                                        os.remove(ahi_saa_bin_bz2)
                                                        # print('Error: ' + ahi_saa_data_ftp)
                                                        # print(e)
                                                    # print('ahi_saa', os.path.exists(ahi_saa_bin_bz2))
                                                    if os.path.exists(ahi_saa_bin_bz2):
                                                        m_raa, ahi_raa, diff_raa = misr_ahi_raa_matching(roi_geoj_filename, hdf_filename, ahi_vaa_bin, ahi_saa_bin, camera)
                                                        # ## RAA match ###
                                                        # print(diff_raa < RAA_DEGREE_THRESHOLD)
                                                        if diff_raa > 0 and diff_raa < RAA_DEGREE_THRESHOLD:
                                                            matched_flag = True
                                                            # geo-obs condition
                                                            misr_orbit = orbit
                                                            misr_camera = camera
                                                            misr_roi_block_time = misr_roi_date.strftime("%Y%m%d%H%M")
                                                            ahi_obs_time = ahi_saa_file.split('.')[0]
                                                            misr_roi_vza = '%.3f' % roi_misr_vza
                                                            ahi_roi_vza = '%.3f' % ahi_vza_mean
                                                            misr_roi_raa = '%.3f' % m_raa
                                                            ahi_roi_raa = '%.3f' % ahi_raa
                                                            misr_roi_sza = get_region_mean_misr_sza(hdf_filename, roi_extent)
                                                            misr_roi_sza = '%.3f' % misr_roi_sza
                                                            ahi_roi_sza = get_region_mean_ahi_sza(temp_ws, ahi_obs_time, roi_extent)
                                                            ahi_roi_sza = '%.3f' % ahi_roi_sza
                                                            # misr_orbit misr_camera_index misr_block_time ahi_time misr_vza ahi_vza misr_raa ahi_raa misr_sza ahi_sza
                                                            record_item = str(misr_orbit) + '\t' + str(misr_camera) + '\t' + misr_roi_block_time + '\t' + ahi_obs_time + '\t' + str(misr_roi_vza) + '\t' + str(ahi_roi_vza) + '\t' + str(misr_roi_raa) + '\t' + str(ahi_roi_raa) + '\t' + str(misr_roi_sza) + '\t' + str(ahi_roi_sza)
                                                            print(record_item)
                                                            geocond_record_str += record_item + '\n'
                                                            print('-- path:', path, '--', 'orbit:', orbit, '--', 'camera:', camera)
                                                            # build folder for MISR-AHI data
                                                            misr_path_orbit_camera = str(P) + '_' + str(O_) + '_' + str(camera)
                                                            misr_ws_c_folder = roi_matched_folder + '/' + misr_path_orbit_camera
                                                            if not os.path.exists(misr_ws_c_folder):
                                                                os.makedirs(misr_ws_c_folder)
                                                            misr_ws_data_filename = misr_ws_c_folder + '/' + hdf_file
                                                            shutil.copy(hdf_filename, misr_ws_data_filename)
                                                            # record matched info
                                                            matched_roi_misr = {}
                                                            matched_roi_misr['misr_path_orbit_camera'] = misr_ws_c_folder
                                                            matched_roi_misr['matched_info'] = [misr_orbit, misr_camera, int(misr_roi_block_time), int(ahi_obs_time), misr_roi_vza, ahi_roi_vza, misr_roi_raa, ahi_roi_raa, misr_roi_sza, ahi_roi_sza]
                                                            matched_roi_misr_infos.append(matched_roi_misr)

                                                    shutil.rmtree(temp_ws)
                    matched_roi_info['roi_misr_infos'] = matched_roi_misr_infos
                    matched_info_record.append(matched_roi_info)
    ###############################################
    # demo: [{
    #     "roi_name": "0.0_120",
    #     "roi_misr_infos": [{
    #         "misr_path_orbit_camera": "P099_O088273_4",
    #         "matched_info": [...]
    #     },
    #     ...]
    # },
    # ...]
    ###############################################

    # save result
    with open(os.path.join(WORK_SPACE, GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)
    matched_info_npy = os.path.join(WORK_SPACE, MATCHED_INFO_NPY)
    numpy.save(matched_info_npy, matched_info_record)

    # disconnect ftp server
    ftp.close()