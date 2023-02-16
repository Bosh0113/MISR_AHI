# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import numpy
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

WORK_SPACE = os.getcwd()
MISR_NC_FOLDER = '/data01/people/beichen/data/MISR4AHI2015070120210630_3'

AHI_RESOLUTION = 0.01


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0.
    else:
        y = o_value * scale + offset
        return y


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def get_roi_latlon_list(center_lat, center_lon):
    roi_ullat = center_lat + 0.05
    roi_ullon = center_lon - 0.05
    roi_lrlat = center_lat - 0.05
    roi_lrlon = center_lon + 0.05
    ahi_lats = numpy.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
    ahi_lons = numpy.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)
    n_lats = ahi_lats[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1]
    n_lons = ahi_lons[find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
    return n_lats, n_lons



def is_valuable_MISR_BRF(cood_point, band_index, misr_orbit, misr_camera_index, misr_nc_filename):
    roi_c_lat = cood_point[1]
    roi_c_lon = cood_point[0]
    roi_lats, roi_lons = get_roi_latlon_list(roi_c_lat, roi_c_lon)
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(misr_orbit)
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
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']' + '[' + str(misr_camera_index) + ']')

    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros((len(roi_lats), len(roi_lons)))
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            try:
                misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
                block_llv3 = misr_blsv3[0]
                b_lat_idxv3 = round(misr_blsv3[1])
                b_lon_idxv3 = round(misr_blsv3[2])

                block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
                roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
                roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)

                roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3
            except Exception as e:
                roi_misr_brfv3[lat_index][lon_index] = 0.

    # if any cloud-free obs. is existed
    roi_misr_brfv3 = roi_misr_brfv3.flatten()
    if len(roi_misr_brfv3[roi_misr_brfv3 > 0.0]) > 20:
        return 1
    return 0


def is_valuable_record(cood_point, misr_path_orbit_camera):
    misr_path_orbit = misr_path_orbit_camera[:12]
    misr_orbit = int(misr_path_orbit[-6:])
    misr_camera_index = int(misr_path_orbit_camera[-1:])
    misr_nc_filename = os.path.join(MISR_NC_FOLDER, 'MISR_AM1_AS_LAND_' + misr_path_orbit + '_F08_0023.nc')
    to_record = 0
    band_indes = [2, 3]
    for band_index in band_indes:
        has_value = is_valuable_MISR_BRF(cood_point, band_index, misr_orbit, misr_camera_index, misr_nc_filename)
        if has_value > 0:
            to_record = has_value
    return to_record


if __name__ == "__main__":

    folder_l1_list = ['0', '26', '45', '60', '70']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                roi_infos = roi_folder.split('_')
                roi_name = roi_folder
                misr_vza_str = roi_infos[0]
                cood_point = [float(roi_infos[3]), float(roi_infos[2])] # lon lat
                misr_ray_matched_npy_filename = os.path.join(roi_folder_path, roi_name + '_matched_record.npy')
                
                matched_record = numpy.load(misr_ray_matched_npy_filename, allow_pickle=True)
                roi_valuable_record = []
                record_str = ''
                if len(matched_record) > 0:
                    matched_roi_info = matched_record[0]
                    roi_misr_infos = matched_roi_info['roi_misr_infos']
                    for roi_misr_info in roi_misr_infos:
                        misr_path_orbit_camera = roi_misr_info['misr_path_orbit_camera']
                        matched_info = roi_misr_info['matched_info']
                        is_valuable = is_valuable_record(cood_point, misr_path_orbit_camera)
                        if is_valuable:
                            roi_valuable_record.append(matched_info)
                            record_str += str(matched_info) + '\n'
                    record4AHI_AC_npy = os.path.join(roi_folder_path, roi_name + '_4AC_record.npy')
                    numpy.save(record4AHI_AC_npy, numpy.array(roi_valuable_record))    # save result as txt
                    with open(os.path.join(roi_folder_path, roi_name + '_4AC_record.txt'), 'w') as f:
                        f.write(record_str)
