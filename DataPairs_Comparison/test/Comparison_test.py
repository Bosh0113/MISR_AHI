# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import math
import numpy
import matplotlib.pyplot as plt

workspace = r'D:\Work_PhD\MISR_AHI_WS\220602\70_80'
MISR_hdf = os.path.join(workspace, 'MISR_AM1_AS_LAND_P129_O089469_F07_0022.hdf')
AHI_AC_npy = os.path.join(workspace, '201610130340_ac_band1.npy')


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0
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
    MISR_orbit = 89469
    # band_index = 3
    band_index = 1
    MISR_camera = 0

    ac_info = numpy.load(AHI_AC_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    # roi_ahi_sr = ac_info['roi_ahi_data']
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(MISR_orbit)
    m_file = MtkFile(MISR_hdf)
    m_grid = m_file.grid('SubregParamsLnd')
    misr_resolution = m_grid.resolution
    m_field = m_grid.field('LandBRF[' + str(band_index) + ']'+'[' + str(MISR_camera) + ']')
    scale_landBRF = m_grid.attr_get('Scale LandBRF')
    offset_landBRF = m_grid.attr_get('Offset LandBRF')
    roi_misr_brf = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            misr_bls = latlon_to_bls(misr_path, misr_resolution, lat, lon)
            block_ll = misr_bls[0]
            b_lat_idx = int(misr_bls[1])
            b_lon_idx = int(misr_bls[2])
            block_brf_dn = m_field.read(block_ll, block_ll)[0]
            roi_brf_dn = block_brf_dn[b_lat_idx][b_lon_idx]
            roi_brf_t = BRF_TrueValue(roi_brf_dn, scale_landBRF, offset_landBRF)
            roi_misr_brf[lat_index][lon_index] = roi_brf_t
    
    # print(roi_misr_brf)
    mapping(roi_misr_brf)
    # https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
    ahi2misr_slope_b1 = 0.930   # temp
    ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, ahi2misr_slope_b1)
    # print(ahi_sr_misr)
    mapping(ahi_sr_misr)
    # diff
    diff_misr_ahi = roi_misr_brf - ahi_sr_misr
    mapping(diff_misr_ahi)
    # diff (<=0.01->np.NaN)
    diff_misr_ahi[abs(diff_misr_ahi) <= 0.01] = numpy.NaN
    mapping(diff_misr_ahi)

