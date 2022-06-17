# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import math
import numpy
import matplotlib.pyplot as plt

# https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
# # AHI2MISR_SLOPE = 1.039  # 26-10 band1
# # AHI2MISR_SLOPE = 0.966  # 26-10 band2
# # AHI2MISR_SLOPE = 0.973  # 26-10 band3
# AHI2MISR_SLOPE = 0.992  # 26-10 band4
# MISR_orbit = 84051
# band_index = 3
# MISR_camera = 3
# time = 201510070250
# workspace = r'D:\Work_PhD\MISR_AHI_WS\220614\26_10'
# MISR_hdf = os.path.join(workspace, 'MISR_AM1_AS_LAND_P117_O084051_F07_0022.hdf')
# misr_nc_filename = os.path.join(workspace, 'MISR_AM1_AS_LAND_P117_O084051_F08_0023.nc')
# AHI_AC_npy = os.path.join(workspace, str(time) + '_ac_band' + str(band_index+1) + '.npy')

# AHI2MISR_SLOPE = 0.930  # 70-80 band1
# AHI2MISR_SLOPE = 1.212  # 70-80 band2
# AHI2MISR_SLOPE = 1.034  # 70-80 band3
AHI2MISR_SLOPE = 0.983  # 70-80 band4
MISR_orbit = 89469
band_index = 3
MISR_camera = 0
time = 201610130340
workspace = r'D:\Work_PhD\MISR_AHI_WS\220614\70_80'
MISR_hdf = os.path.join(workspace, 'MISR_AM1_AS_LAND_P129_O089469_F07_0022.hdf')
misr_nc_filename = os.path.join(workspace, 'MISR_AM1_AS_LAND_P129_O089469_F08_0023.nc')
AHI_AC_npy = os.path.join(workspace, str(time) + '_ac_band' + str(band_index+1) + '.npy')


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


if __name__ == "__main__":

    ac_info = numpy.load(AHI_AC_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    roi_ahi_toa = ac_info['roi_ahi_data']
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(MISR_orbit)
    # MISR v2 HDF
    m_file = MtkFile(MISR_hdf)
    m_grid = m_file.grid('SubregParamsLnd')
    misr_resolutionv2 = m_grid.resolution
    m_field = m_grid.field('LandBRF[' + str(band_index) + ']'+'[' + str(MISR_camera) + ']')
    scale_landBRFv2 = m_grid.attr_get('Scale LandBRF')
    offset_landBRFv2 = m_grid.attr_get('Offset LandBRF')
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
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']'+'[' + str(MISR_camera) + ']')
    # MISR data at ROI
    roi_misr_brfv2 = numpy.zeros_like(roi_ahi_sr)
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            misr_blsv2 = latlon_to_bls(misr_path, misr_resolutionv2, lat, lon)
            misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
            block_llv2 = misr_blsv2[0]
            block_llv3 = misr_blsv3[0]
            b_lat_idxv2 = round(misr_blsv2[1])
            b_lon_idxv2 = round(misr_blsv2[2])
            b_lat_idxv3 = round(misr_blsv3[1])
            b_lon_idxv3 = round(misr_blsv3[2])
            block_brf_dnv2 = m_field.read(block_llv2, block_llv2)[0]
            block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
            roi_brf_dnv2 = block_brf_dnv2[b_lat_idxv2][b_lon_idxv2]
            roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
            roi_brf_tv2 = BRF_TrueValue(roi_brf_dnv2, scale_landBRFv2, offset_landBRFv2)
            roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)
            roi_misr_brfv2[lat_index][lon_index] = roi_brf_tv2
            roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3

    # MISR BRF v2
    roi_misr_brfv2[roi_misr_brfv2 <= 0.0] = numpy.NaN
    mapping(roi_misr_brfv2)
    # MISR BRF v3
    roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
    mapping(roi_misr_brfv3)

    # value = MISRv2-MISRv3*2
    mapping(roi_misr_brfv2-roi_misr_brfv3*2)

    mask_array = numpy.copy(roi_misr_brfv3)
    mask_array[mask_array > 0.0] = 1.

    # TOA(AHI)
    ahi_toa_misr = roi_ahi_toa*mask_array
    mapping(ahi_toa_misr)

    # SR(AHI2MISR)
    ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_SLOPE)
    # print(ahi_sr_misr)
    ahi_sr_misr = ahi_sr_misr*mask_array
    mapping(ahi_sr_misr)

    # record as npy file
    record_info = [
        {
            'misr_v2': roi_misr_brfv2,
            'misr_v3': roi_misr_brfv3,
            'ahi_toa': roi_ahi_toa,
            'ahi_sr': roi_ahi_sr,
            'ahi_sr2misr': ahi_sr_misr
        }
    ]
    file_path = os.path.join(workspace, str(time) + '_sr_band' + str(band_index+1) + '.npy')
    numpy.save(file_path, record_info)
