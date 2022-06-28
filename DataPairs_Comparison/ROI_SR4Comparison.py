# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import math
import numpy
import matplotlib.pyplot as plt

workspace = os.getcwd()

# https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
AHI2MISR_roi_slope = {
    '0.0_60_band1': 0.938,
    '0.0_60_band2': 1.056,
    '0.0_60_band3': 1.073,
    '0.0_60_band4': 1.009,
    '0.0_50_band1': 0.922,
    '0.0_50_band2': 1.111,
    '0.0_50_band3': 1.173,
    '0.0_50_band4': 1.002,
    '0.0_120_band1': 1.013,
    '0.0_120_band2': 0.915,
    '0.0_120_band3': 0.963,
    '0.0_120_band4': 1.015,
    '26.1_150_band1': 0.992,
    '26.1_150_band2': 1.002,
    '26.1_150_band3': 0.981,
    '26.1_150_band4': 1.008,
    '26.1_10_band1': 0.962,
    '26.1_10_band2': 1.032,
    '26.1_10_band3': 1.026,
    '26.1_10_band4': 1.008,
    '26.1_50_band1': 0.922,
    '26.1_50_band2': 1.111,
    '26.1_50_band3': 1.173,
    '26.1_50_band4': 1.002,
    '45.6_60_band1': 0.938,
    '45.6_60_band2': 1.056,
    '45.6_60_band3': 1.073,
    '45.6_60_band4': 1.009,
    '45.6_20_band1': 0.981,
    '45.6_20_band2': 1.031,
    '45.6_20_band3': 1.020,
    '45.6_20_band4': 1.010,
    '45.6_10_band1': 0.962,
    '45.6_10_band2': 1.032,
    '45.6_10_band3': 1.026,
    '45.6_10_band4': 1.008,
    '60.0_200_band1': 1.074,
    '60.0_200_band2': 0.823,
    '60.0_200_band3': 0.967,
    '60.0_200_band4': 1.017,
    '60.0_80_band1': 0.921,
    '60.0_80_band2': 1.056,
    '60.0_80_band3': 1.126,
    '60.0_80_band4': 1.011,
    '60.0_130_band1': 1.022,
    '60.0_130_band2': 0.987,
    '60.0_130_band3': 0.986,
    '60.0_130_band4': 1.013,
    '70.5_200_band1': 1.074,
    '70.5_200_band2': 0.823,
    '70.5_200_band3': 0.967,
    '70.5_200_band4': 1.017,
    '70.5_80_band1': 0.921,
    '70.5_80_band2': 1.056,
    '70.5_80_band3': 1.126,
    '70.5_80_band4': 1.011,
    '70.5_130_band1': 1.022,
    '70.5_130_band2': 0.987,
    '70.5_130_band3': 0.986,
    '70.5_130_band4': 1.013
}


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0.
    else:
        x = math.floor(o_value/2)
        y = x*scale + offset
        return y


def ahi_sr2misr_sr(ahi_sr_array, slope):
    return ahi_sr_array/slope


def mapping(array):
    plt.imshow(array)
    plt.colorbar()
    plt.show()


def record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_slope):
    ac_info = numpy.load(ahi_ac_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    roi_ahi_toa = ac_info['roi_ahi_data']
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
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']'+'[' + str(misr_camera_index) + ']')
    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
            block_llv3 = misr_blsv3[0]
            b_lat_idxv3 = round(misr_blsv3[1])
            b_lon_idxv3 = round(misr_blsv3[2])
            block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
            roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
            roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)
            roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3

    # MISR BRF v3
    roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
    mapping(roi_misr_brfv3)

    mask_array = numpy.copy(roi_misr_brfv3)
    mask_array[mask_array > 0.0] = 1.

    # TOA(AHI)
    ahi_toa_misr = roi_ahi_toa*mask_array
    mapping(ahi_toa_misr)

    # SR(AHI2MISR)
    ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_slope)
    # print(ahi_sr_misr)
    ahi_sr_misr = ahi_sr_misr*mask_array
    mapping(ahi_sr_misr)

    # record as npy file
    record_info = [
        {
            'roi_name': roi_name,
            'band_index': band_index,
            'misr_orbit': misr_orbit,
            'misr_camera_index': misr_camera_index,
            'misr_v3': roi_misr_brfv3,
            'ahi_toa': roi_ahi_toa,
            'ahi_sr': roi_ahi_sr,
            'ahi_sr2misr': ahi_sr_misr
        }
    ]
    file_path = os.path.join(workspace, str(ahi_obs_time) + '_sr_band' + str(band_index+1) + '.npy')
    numpy.save(file_path, record_info)


def get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy):
    misr_path_orbit = misr_path_orbit_camera[:12]
    misr_orbit = int(misr_path_orbit[-6:])
    band_index = int(ahi_ac_npy[-5:-4]) - 1
    band_name = 'band' + str(band_index + 1)
    AHI2MISR_slope = AHI2MISR_roi_slope[roi_name + '_' + band_name]
    misr_camera_index = int(misr_path_orbit_camera[-1:])
    ahi_obs_time = ahi_ac_npy[-25:-13]
    misr_nc_filename = os.path.join(workspace, 'MISR_AM1_AS_LAND_' + misr_path_orbit + '_F08_0023.nc')
    record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_slope)


if __name__ == "__main__":
    roi_name = '0.0_50'
    misr_path_orbit_camera = 'P100_O090705_4'
    ahi_ac_npy = os.path.join(workspace, '201701060100_ac_band4.npy')
    get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy)
