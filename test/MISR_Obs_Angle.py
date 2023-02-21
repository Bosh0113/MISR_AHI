import os
import numpy
import re
import urllib.request
import netCDF4
from datetime import datetime, timedelta
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_path, orbit_to_time_range, latlon_to_bls

WORK_SPACE = os.getcwd()

ROI_SIZE = 0.04

START_TIME = '2018-07-21T00:00:00Z'
END_TIME = '2018-07-31T23:59:59Z'

MISR_DATA_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'

GRO_OBS_COND_TXT = 'MISR_ANGLE_RECORD.txt'


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0.
    else:
        y = o_value*scale + offset
        return y


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


def get_misr_obs_angle(roi_extent, path, orbit, camera_idx):
    misr_filename = get_misr_filename(orbit)
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    roi_ct = roi_r.center
    roi_ct_lat = roi_ct[0]
    roi_ct_lon = roi_ct[1]
    roi_ct_info = latlon_to_bls(path, 4400, roi_ct_lat, roi_ct_lon)
    block_no = roi_ct_info[0]
    block_roi_line = round(roi_ct_info[1])
    block_roi_sample = round(roi_ct_info[2])
    block_r = MtkRegion(path, block_no, block_no)

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
        f_vza_data = vza_field.read(block_r).data()
        f_vza_data = numpy.array(f_vza_data)
        roi_misr_vza = f_vza_data[block_roi_line, block_roi_sample]
        # has available values?
        if roi_misr_vza <= 0:
            return 0.0, 0.0
        # MISR VAA
        roi_misr_vaa = 0.0
        vaa_field = m_grid.field('GEOMETRY/View_Azimuth_Angle[' + str(camera_idx) + ']')
        f_vaa_data = vaa_field.read(block_r).data()
        f_vaa_data = numpy.array(f_vaa_data)
        roi_misr_vaa = f_vaa_data[block_roi_line, block_roi_sample]
        # has available values?
        if roi_misr_vaa <= 0:
            return 0.0, 0.0

        return roi_misr_vza, roi_misr_vaa

    else:
        return 0.0, 0.0


def roi_misr_angle(roi_name, cood_point, misr_vza_str):
    # search full matching
    geocond_record_str = 'MISR_roi_time MISR_VZA MISR_VAA BRF_band3 BRF_band4\n'
    print('MISR VZAs', misr_vza_str)
    print(cood_point)
    # record
    misr_angle_record = []
    misr_vza_matched_npy_filename = os.path.join(WORK_SPACE, misr_vza_str + '_angle_record.npy')

    # loc_info
    loc_record = {}
    loc_record['roi_name'] = roi_name
    matched_infos = []

    lon4search = cood_point[0]
    lat4search = cood_point[1]
    geocond_record_str += 'Location: (' + str(lon4search) + ', ' + str(lat4search) + ')\n'
    # ROI extent (ullat, ullon, lrlat, lrlon)
    roi_extent = [lat4search + ROI_SIZE / 2, lon4search - ROI_SIZE / 2, lat4search - ROI_SIZE / 2, lon4search + ROI_SIZE / 2]

    # Full Match Screening
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    pathList = roi_r.path_list
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
        for orbit in orbits:
            camera_idx_array = range(0, 9)
            for camera_idx in camera_idx_array:
                try:
                    misr_vza, misr_vaa = get_misr_obs_angle(roi_extent, path, orbit, camera_idx)
                    if misr_vza != None:
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
                        # get SRF values
                        band3_index = 2
                        band4_index = 3
                        # MISR v3 netCDF4
                        misr_nc = netCDF4.Dataset(misr_nc_filename)
                        misr_nc_11 = misr_nc.groups['1.1_KM_PRODUCTS']
                        misr_brf_var = misr_nc_11.variables['Bidirectional_Reflectance_Factor']
                        misr_brf_scalev3 = misr_brf_var.scale_factor
                        misr_brf_offsetv3 = misr_brf_var.add_offset
                        misr_nc.close()
                        m_file2 = MtkFile(misr_nc_filename)
                        m_grid11 = m_file2.grid('1.1_KM_PRODUCTS')
                        misr_resolutionv3 = m_grid11.resolution
                        m_field11_3 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band3_index) + ']'+'[' + str(camera_idx) + ']')
                        m_field11_4 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band4_index) + ']'+'[' + str(camera_idx) + ']')
                        roi_ct = roi_r.center
                        roi_ct_lat = roi_ct[0]
                        roi_ct_lon = roi_ct[1]
                        roi_ct_info = latlon_to_bls(path, misr_resolutionv3, roi_ct_lat, roi_ct_lon)
                        block_no = roi_ct_info[0]
                        block_roi_line = round(roi_ct_info[1])
                        block_roi_sample = round(roi_ct_info[2])
                        block_r = MtkRegion(path, block_no, block_no)
                        sr_band3_dn = m_field11_3.read(block_r).data()
                        sr_band3_dn = numpy.array(sr_band3_dn)
                        roi_sr_band3_dn = sr_band3_dn[block_roi_line, block_roi_sample]
                        roi_sr_band3 = BRF_TrueValue(roi_sr_band3_dn, misr_brf_scalev3, misr_brf_offsetv3)
                        sr_band4_dn = m_field11_4.read(block_r).data()
                        sr_band4_dn = numpy.array(sr_band4_dn)
                        roi_sr_band4_dn = sr_band4_dn[block_roi_line, block_roi_sample]
                        roi_sr_band4 = BRF_TrueValue(roi_sr_band4_dn, misr_brf_scalev3, misr_brf_offsetv3)
                        if roi_sr_band3 > 0.0 and roi_sr_band4 > 0.0:
                            misr_roi_block_time = misr_roi_date.strftime("%Y%m%d%H%M")
                            # matched info
                            misr_roi_vza = '%.3f' % misr_vza
                            misr_roi_vaa = '%.3f' % misr_vaa
                            # matched info: MISR_roi_time MISR_VZA MISR_VAA
                            misr_angle_info = [misr_roi_block_time, str(misr_roi_vza), str(misr_roi_vaa), str(roi_sr_band3), str(roi_sr_band4)]
                            print(misr_angle_info)
                            geocond_record_str += misr_roi_block_time + '\t' + str(misr_roi_vza) + '\t' + str(misr_roi_vaa) + '\t' + str(roi_sr_band3) + '\t' + str(roi_sr_band4) + '\n'
                            match_info_record = {}
                            misr_path_orbit_camera = 'P' + (3 - len(str(path))) * '0' + str(path) + '_O' + (6 - len(str(orbit))) * '0' + str(orbit) + '_' + str(camera_idx)
                            match_info_record['misr_path_orbit_camera'] = misr_path_orbit_camera
                            match_info_record['misr_angle_info'] = misr_angle_info
                            matched_infos.append(match_info_record)
                except Exception as e:
                    print('orbit:', orbit)
                    print(e)
    loc_record['roi_misr_infos'] = matched_infos
    if len(matched_infos) > 0:
        misr_angle_record.append(loc_record)
    ###############################################
    # demo: [{
    #     "roi_name": "45.6_1",
    #     "roi_misr_infos": [{
    #         "misr_path_orbit_camera": "P099_O088273_4",
    #         "misr_angle_info": [...]
    #     },
    #     ...]
    # },
    # ...]
    ###############################################
    numpy.save(misr_vza_matched_npy_filename, numpy.array(misr_angle_record))

    # save result as txt
    with open(os.path.join(WORK_SPACE, GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


if __name__ == "__main__":
    roi_name = '45_1'
    cood_point = [140.45, 40.75]
    misr_vza_str = '45.6'

    roi_misr_angle(roi_name, cood_point, misr_vza_str)
