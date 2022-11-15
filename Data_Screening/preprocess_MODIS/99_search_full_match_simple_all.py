import os
import numpy
import re
import math
import urllib.request
import netCDF4
from datetime import datetime, timedelta
from MisrToolkit import MtkRegion, orbit_to_path, orbit_to_time_range, time_range_to_orbit_list, latlon_to_path_list
from tqdm import tqdm
import xarray

WORK_SPACE = os.getcwd()

ROI_SIZE = 0.12

START_TIME = '2017-01-01T00:00:00Z'
END_TIME = '2017-12-31T23:59:59Z'
# daytime range
AHI_LOCALTIME_START = '08:00:00Z'
AHI_LOCALTIME_END = '15:59:59Z'

# time diff
DIFF_TIME_THRESHOLD = 10 * 60  # seconds

# angle threshold
SCATTERING_ANGLE_THRESHOLD = 175

MISR_DATA_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'
MODIS_DATA_FOLDER = '/disk1/workspace/20221103/MOD09_AHI_2017'
AHI_VZA_BIN = '/disk1/Data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
AHI_VAA_BIN = '/disk1/Data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'

# point_locations_npy_filename = '/disk1/workspace/20221103/MODIS_FM/AHI_180_10km_onland_lonlat.npy'
GRO_OBS_COND_TXT = 'MODIS_AHI_FULL_MATCH_RECORD_50km_365_all.txt'


def re_download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    s_time = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(s_time))
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


def get_scattering_angle(misr_vza, misr_vaa, ahi_vza, ahi_vaa):
    # cos(ScatteringAngle) = -cos(GEO_VZA)*cos(LEO_VZA)-cos(GEO_VAA-LEO_VAA)*sin(GEO_VZA)*sin(LEO_VZA)
    scattering_angle = math.degrees(math.acos(-math.cos(math.radians(ahi_vza)) * math.cos(math.radians(misr_vza)) - math.cos(math.radians(ahi_vaa - misr_vaa)) * math.sin(math.radians(ahi_vza)) * math.sin(math.radians(misr_vza))))
    return scattering_angle


def get_misr_path_orbit(lon, lat, day):
    year_start_date = datetime.strptime(START_TIME, "%Y-%m-%dT%H:%M:%SZ")
    day_start_offset_d = timedelta(hours=(day-1)*24)
    day_end_offset_d = timedelta(hours=(day-1)*24)
    day_start_date = year_start_date + day_start_offset_d
    day_end_date = year_start_date + day_end_offset_d
    day_start_str = day_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    day_end_str = day_end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    day_orbits = time_range_to_orbit_list(day_start_str, day_end_str)
    for day_orbit in day_orbits:
        orbit_path = orbit_to_path(day_orbit)
        roi_paths = latlon_to_path_list(lat, lon)
        if orbit_path in roi_paths:
            return orbit_path, day_orbit
    return 0, 0


def read_modis_obs_angle(lon, lat, modis_value):
    modis_ullat = 60
    modis_ullon = 85
    modis_lrlat = -60
    modis_lrlon = 180
    # modis_nodata = -32767

    lat_p_c = modis_value.shape[0]
    lon_p_c = modis_value.shape[1]
    modis_lat_re = (modis_ullat - modis_lrlat)/lat_p_c
    modis_lon_re = (modis_lrlon- modis_ullon)/lon_p_c

    lat_idx_offset = round((ROI_SIZE/2)/modis_lat_re)
    lon_idx_offset = round((ROI_SIZE/2)/modis_lon_re)

    lon_c_idx = round((lon-modis_ullon)/modis_lon_re)
    lat_c_idx = round((modis_ullat-lat)/modis_lat_re)
    # print(modis_value)
    roi_arr = modis_value[lat_c_idx-lat_idx_offset:lat_c_idx+lat_idx_offset, lon_c_idx-lon_idx_offset:lon_c_idx+lon_idx_offset]
    # print(lat_c_idx-lat_idx_offset, lat_c_idx+lat_idx_offset, lon_c_idx-lon_idx_offset, lon_c_idx+lon_idx_offset)
    roi_arr = roi_arr * 0.01
    # print(roi_arr)
    roi_arr_vs = roi_arr[roi_arr >= -180.]
    if len(roi_arr_vs) > 0:
        roi_a2ahi = []
        for roi_arr_v in roi_arr_vs:
            if roi_arr_v >= 0.0:
                roi_a2ahi.append(roi_arr_v)
            else:
                roi_a2ahi.append(360. + roi_arr_v)
        return numpy.mean(roi_a2ahi)
    else:
        return 0.0


def get_modis_obs_angle(lon, lat, modis_vza_value, modis_vaa_value):
    modis_vza = read_modis_obs_angle(lon, lat, modis_vza_value)
    modis_vaa = read_modis_obs_angle(lon, lat, modis_vaa_value)
    return modis_vza, modis_vaa


def main():
    # search full matching
    geocond_record_str = 'Lon Lat MODIS_roi_time AHI_roi_time MODIS_VZA AHI_VZA MODIS_VAA AHI_VAA Scattering_Angle(GEO-LEO)\n'
    # record
    matched_record = {}
    modis_matched_npy_filename = os.path.join(WORK_SPACE, 'MODIS_matched_record_50km_365_all.npy')

    # search_cood = numpy.load(point_locations_npy_filename)
    search_cood = []
    # INTERNAL_DEGREE = 0.5
    INTERNAL_DEGREE = 0.1
    lats_s = numpy.arange(20. - INTERNAL_DEGREE / 2, -20, -INTERNAL_DEGREE)
    lons_s = numpy.arange(85. + INTERNAL_DEGREE / 2, 180, INTERNAL_DEGREE)
    for lon_s in lons_s:
        for lat_s in lats_s:
            search_cood.append([lon_s, lat_s])

    # for year_day in tqdm(range(1, 366, 1), desc='Doy', leave=False):
    for year_day in tqdm(range(1, 366, 1), desc='Doy', leave=False):
        year_day_str = (3 - len(str(year_day))) * '0' + str(year_day)

        modis_vza_file = 'MOD09GA.061_SensorZenith_1_doy2017' + year_day_str + '_aid0001.tif'
        modis_vaa_file = 'MOD09GA.061_SensorAzimuth_1_doy2017' + year_day_str + '_aid0001.tif'

        modis_vza_filename = os.path.join(MODIS_DATA_FOLDER, modis_vza_file)
        modis_vaa_filename = os.path.join(MODIS_DATA_FOLDER, modis_vaa_file)

        if os.path.exists(modis_vza_filename) and os.path.exists(modis_vaa_filename):
            modis_vza_ds = xarray.open_rasterio(modis_vza_filename)
            modis_vza_value = numpy.array(modis_vza_ds[0])
            modis_vaa_ds = xarray.open_rasterio(modis_vaa_filename)
            modis_vaa_value = numpy.array(modis_vaa_ds[0])

            for cood_point_idx in range(len(search_cood)):
                cood_point = search_cood[cood_point_idx]
                # loc_info
                loc_matched = []
                if str(cood_point) in matched_record:
                    loc_matched = matched_record[str(cood_point)]

                lon4search = round(cood_point[0], 3)
                lat4search = round(cood_point[1], 3)
                if lat4search > -30 and lat4search < 30:
                    # geocond_record_str += 'Location: (' + str(lon4search) + ', ' + str(lat4search) + ')\n'
                    # ROI extent (ullat, ullon, lrlat, lrlon)
                    roi_extent = [lat4search + ROI_SIZE / 2, lon4search - ROI_SIZE / 2, lat4search - ROI_SIZE / 2, lon4search + ROI_SIZE / 2]

                    # AHI Obs Condition
                    ahi_vza, ahi_vaa = get_ahi_obs_angle(roi_extent)
                    misr_path, misr_orbit = get_misr_path_orbit(lon4search, lat4search, year_day)
                    if misr_orbit > 0:
                        try:
                            # Full Match Screening
                            roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
                            modis_vza, modis_vaa = get_modis_obs_angle(lon4search, lat4search, modis_vza_value, modis_vaa_value)
                            if modis_vza != 0.0:
                                # print(modis_vza, modis_vaa)
                                scattering_angle = get_scattering_angle(modis_vza, modis_vaa, ahi_vza, ahi_vaa)
                                if scattering_angle > SCATTERING_ANGLE_THRESHOLD:
                                    # get AHI data with MISR Obs time
                                    roi_blocks = roi_r.block_range(misr_path)
                                    block_no = roi_blocks[0]
                                    misr_nc_filename = get_misr_filename(misr_orbit)
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
                                    misr_roi_date = misr_start_date + block_time_offset_s
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
                                    # print('**********Full Matching**********')
                                    modis_roi_vza = '%.3f' % modis_vza
                                    ahi_roi_vza = '%.3f' % ahi_vza
                                    modis_roi_vaa = '%.3f' % modis_vaa
                                    ahi_roi_vaa = '%.3f' % ahi_vaa
                                    scattering_angle = '%.3f' % scattering_angle
                                    # matched info: MISR_roi_time AHI_roi_time MODIS_VZA AHI_VZA MODIS_VAA AHI_VAA Scattering_Angle(GEO-LEO)
                                    matched_info = [misr_roi_block_time, ahi_obs_time, str(modis_roi_vza), str(ahi_roi_vza), str(modis_roi_vaa), str(ahi_roi_vaa), str(scattering_angle)]
                                    # print(cood_point)
                                    print([lon4search, lat4search, misr_roi_block_time, ahi_obs_time, str(modis_roi_vza), str(ahi_roi_vza), str(modis_roi_vaa), str(ahi_roi_vaa), str(scattering_angle)])
                                    geocond_record_str += str(lon4search) + '\t' + str(lat4search) + '\t' + misr_roi_block_time + '\t' + ahi_obs_time + '\t' + str(modis_roi_vza) + '\t' + str(ahi_roi_vza) + '\t' + str(modis_roi_vaa) + '\t' + str(ahi_roi_vaa) + '\t' + str(scattering_angle) + '\n'
                                    loc_matched.append(matched_info)
                        except Exception as e:
                            print('doy:', year_day)
                            print(e)
                matched_record[str(cood_point)] = loc_matched
    
    save_matched_record = []
    for cood_point_idx in range(len(search_cood)):
        cood_point = search_cood[cood_point_idx]
        matched_info = matched_record[str(cood_point)]
        if len(matched_info) > 0:
            loc_record = {}
            loc_record['location'] = cood_point
            loc_record['matched_infos'] = matched_info
            save_matched_record.append(loc_record)

    numpy.save(modis_matched_npy_filename, numpy.array(save_matched_record))

    # save result as txt
    with open(os.path.join(WORK_SPACE, GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


if __name__ == "__main__":
    main()
