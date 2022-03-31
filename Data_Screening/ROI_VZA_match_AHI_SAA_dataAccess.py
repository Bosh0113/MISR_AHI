# for python 3.6
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_time_range
import math
from datetime import datetime, timedelta
import numpy
import os
import json
import shutil

# time range for our study
start_t = '2016-01-01T00:00:00Z'
end_t = '2016-12-31T23:59:59Z'
# daytime range
ahi_localtime_start = '08:00:00Z'
ahi_localtime_end = '15:59:59Z'
# data path
ahi_vza_bin = '/data/beichen/data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
misr_folder = '/data/beichen/data/MISR4AHI'
roi_folder = '/data/beichen/data/MISR_AHI_ROIs'
# storage path
roi_raa_ws = '/data/beichen/data/MISR_AHI_ROIs_inter-com'

# cos diff
VZA_cos_threshold = 0.01


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


if __name__ == "__main__":
    # angles of MISR cameras
    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    for vza in MISR_vza:
        # read roi geoinfo
        folder = roi_folder + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                # build roi folder
                roi_raa_folder = roi_raa_ws + '/' + str(
                    vza) + '_' + file.split('.')[0]
                if not os.path.exists(roi_raa_folder):
                    os.makedirs(roi_raa_folder)
                filename = folder + '/' + file
                with open(filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry'][
                        'coordinates'][0]
                    roi_extent = get_extent(polygon_pts)

                    print('***ROI:', vza, '-', file.split('.')[0])

                    ahi_vza = get_region_ahi_vza(roi_extent)
                    ahi_vza_mean = ahi_vza.mean()
                    # print('-> mean vza of ROI in AHI data:', ahi_vza_mean)

                    roi_r = MtkRegion(roi_extent[0], roi_extent[1],
                                      roi_extent[2], roi_extent[3])
                    pathList = roi_r.path_list
                    for path in pathList:
                        orbits = path_time_range_to_orbit_list(
                            path, start_t, end_t)
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
                                    m_field = m_grid.field('ViewZenAng[' +
                                                           str(camera) + ']')
                                    f_vza_data = m_field.read(roi_r).data()
                                    max_vza = f_vza_data.max()
                                    # has available values?
                                    if max_vza > -9999:
                                        # vza matching
                                        differ_cos = abs(
                                            math.cos(math.radians(
                                                ahi_vza_mean)) -
                                            math.cos(math.radians(max_vza)))
                                        if differ_cos < VZA_cos_threshold:
                                            # print(hdf_filename)
                                            print('-- path:', path, '--',
                                                  'orbit:', orbit, '--',
                                                  'camera:', camera)
                                            # build folder for MISR-AHI data
                                            misr_ws_c_folder = roi_raa_folder + '/' + str(
                                                P) + '_' + str(O_) + '_' + str(
                                                    camera)
                                            if not os.path.exists(
                                                    misr_ws_c_folder):
                                                os.makedirs(misr_ws_c_folder)
                                            misr_ws_data_filename = misr_ws_c_folder + '/' + hdf_file
                                            shutil.copy(
                                                hdf_filename,
                                                misr_ws_data_filename)

                                            # for record required AHI SAA data
                                            AHI_saa_filenames_npy = misr_ws_c_folder + '/AHI_saa_ftp_paths.npy'
                                            AHI_saa_filenames = []

                                            misr_time = orbit_to_time_range(
                                                orbit)
                                            print('   ', misr_time)
                                            # print('   camera ' + str(camera + 1) + ' vza in MISR data:', max_vza)
                                            # print('   differ of cos:', differ_cos)

                                            # ## to screening AHI data ###
                                            center_pt = [
                                                (roi_extent[0] + roi_extent[2])
                                                / 2,
                                                (roi_extent[1] + roi_extent[3])
                                                / 2
                                            ]

                                            time_offset = ahi_lon_timeoffset(
                                                center_pt[1])
                                            # MISR mean time of scan
                                            misr_start_time_str = misr_time[0]
                                            misr_end_time_str = misr_time[1]
                                            misr_start_date = datetime.strptime(
                                                misr_start_time_str,
                                                "%Y-%m-%dT%H:%M:%SZ")
                                            misr_end_date = datetime.strptime(
                                                misr_end_time_str,
                                                "%Y-%m-%dT%H:%M:%SZ")
                                            diff_date = misr_end_date - misr_start_date
                                            misr_mean_date = misr_start_date + diff_date / 2
                                            misr_mean_date_str = misr_mean_date.strftime(
                                                "%Y-%m-%dT%H:%M:%SZ")
                                            # print(misr_mean_date_str)

                                            # days of required AHI data (3 day)
                                            # misr_mean_date = datetime.strptime(misr_mean_date_str, "%Y-%m-%dT%H:%M:%SZ")
                                            local_date2 = misr_mean_date + timedelta(
                                                hours=time_offset)
                                            local_date1 = local_date2 + timedelta(
                                                days=-1)
                                            local_date3 = local_date2 + timedelta(
                                                days=1)
                                            # UTC time range of required AHI data
                                            # local_dates = [
                                            #     local_date1, local_date2,
                                            #     local_date3
                                            # ]
                                            local_dates = [local_date2]     # same day not near 3 days
                                            for local_date in local_dates:
                                                local_day_str = local_date.strftime(
                                                    "%Y-%m-%dT")

                                                local_time_start_str = local_day_str + ahi_localtime_start
                                                local_date_start = datetime.strptime(
                                                    local_time_start_str,
                                                    "%Y-%m-%dT%H:%M:%SZ")
                                                utc_date_start = local_date_start - timedelta(
                                                    hours=time_offset)
                                                utc_date_start_str = utc_date_start.strftime(
                                                    "%Y-%m-%dT%H:%M:%SZ")

                                                local_time_end_str = local_day_str + ahi_localtime_end
                                                local_date_end = datetime.strptime(
                                                    local_time_end_str,
                                                    "%Y-%m-%dT%H:%M:%SZ")
                                                utc_date_end = local_date_end - timedelta(
                                                    hours=time_offset)
                                                utc_date_end_str = utc_date_end.strftime(
                                                    "%Y-%m-%dT%H:%M:%SZ")

                                                ahi_saa_date_range = (
                                                    utc_date_start_str,
                                                    utc_date_end_str)
                                                # print(ahi_saa_date_range)
                                                # utc_date_start = datetime.strptime(ahi_saa_date_range[0], "%Y-%m-%dT%H:%M:%SZ")
                                                # utc_date_end = datetime.strptime(ahi_saa_date_range[1], "%Y-%m-%dT%H:%M:%SZ")
                                                date_interval = timedelta(
                                                    minutes=10)
                                                date_ahi = utc_date_start
                                                while date_ahi < utc_date_end:
                                                    ahi_data_time = date_ahi.strftime(
                                                        "%Y%m%d%H%M")
                                                    ahi_data_folder1 = date_ahi.strftime(
                                                        "%Y%m")
                                                    ahi_data_folder2 = date_ahi.strftime(
                                                        "%Y%m%d")
                                                    ahi_saa_file = ahi_data_time + '.sun.azm.fld.4km.bin.bz2'
                                                    ahi_saa_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_saa_file
                                                    # no download, just record
                                                    AHI_saa_filenames.append(ahi_saa_path)

                                                    date_ahi = date_ahi + date_interval
                                            numpy.save(AHI_saa_filenames_npy,  numpy.array(AHI_saa_filenames))