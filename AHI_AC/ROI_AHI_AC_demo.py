import numpy
import os
from ftplib import FTP
import sys
import bz2
import shutil
import xarray
import time

# workspace
ws = r'D:\Work_PhD\MISR_AHI_WS\220527'
DN2Tbb_folder = r'D:\Work_PhD\MISR_AHI_WS\220527\band_DN2Tbb'
AHI_AC_PARAMETER_FOLDER = r'D:\Work_PhD\MISR_AHI_WS\220527\AHI_AC_PARAMETER'

AHI_RESOLUTION = 0.01  # degree
# DATA_RESOLUTION = 0.01  # degree    VIS
# DATA_RESOLUTION = 0.005  # degree EXT

# JMA AHI band: [CEReS gridded, resolution, file_suffix, DN2Tbb_name]
BAND_INFO = {
    'band1': ['VIS', '0.01', '.vis.01.fld.geoss.bz2', 'vis.01'],
    'band2': ['VIS', '0.01', '.vis.02.fld.geoss.bz2', 'vis.02'],
    'band3': ['EXT', '0.005', '.ext.01.fld.geoss.bz2', 'ext.01'],
    'band4': ['VIS', '0.01', '.vis.03.fld.geoss.bz2', 'vis.03'],
}


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def get_roi_data_extent(r_extent, f_lats, f_lons, resolution):
    r_ullat = r_extent[0]
    r_ullon = r_extent[1]
    r_lrlat = r_extent[2]
    r_lrlon = r_extent[3]

    m_ex_ullat = f_lats[(numpy.abs(f_lats - r_ullat)).argmin()]
    m_ex_ullon = f_lons[(numpy.abs(f_lons - r_ullon)).argmin()]
    m_ex_lrlat = f_lats[(numpy.abs(f_lats - r_lrlat)).argmin()]
    m_ex_lrlon = f_lons[(numpy.abs(f_lons - r_lrlon)).argmin()]

    return m_ex_ullat + resolution*2, m_ex_ullon - resolution*2, m_ex_lrlat - resolution*2, m_ex_lrlon + resolution*2


def get_roi_min_extent(r_extent, f_lats, f_lons, resolution):
    r_ullat = r_extent[0]
    r_ullon = r_extent[1]
    r_lrlat = r_extent[2]
    r_lrlon = r_extent[3]
    max_lat_c = f_lats[0]
    min_lat_c = f_lats[len(f_lats) - 1]
    max_lon_c = f_lons[len(f_lons) - 1]
    min_lon_c = f_lons[0]
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = None, None, None, None
    while max_lat_c > r_ullat:
        m_ex_ullat = max_lat_c
        max_lat_c = max_lat_c - resolution
    while min_lon_c < r_ullon:
        m_ex_ullon = min_lon_c
        min_lon_c = min_lon_c + resolution
    while min_lat_c < r_lrlat:
        m_ex_lrlat = min_lat_c
        min_lat_c = min_lat_c + resolution
    while max_lon_c > r_lrlon:
        m_ex_lrlon = max_lon_c
        max_lon_c = max_lon_c - resolution

    return m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon


# Get ROI Data from Rough Dataset with AHI Resolution
def get_data_roi_ahi_reso2(r_extent, data_v, lats, lons, o_resolution):
    # min extent of ROI in CAMS dataset
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = get_roi_data_extent(r_extent, lats, lons, o_resolution)
    ex_ds = xarray.Dataset(
        data_vars={
            "values": (("latitude", "longitude"), data_v[find_nearest_index(lats, m_ex_ullat):find_nearest_index(lats, m_ex_lrlat) + 1,
                                                         find_nearest_index(lons, m_ex_ullon):find_nearest_index(lons, m_ex_lrlon) + 1]),
        },
        coords={
            "latitude": lats[find_nearest_index(lats, m_ex_ullat):find_nearest_index(lats, m_ex_lrlat) + 1],
            "longitude": lons[find_nearest_index(lons, m_ex_ullon):find_nearest_index(lons, m_ex_lrlon) + 1]
        },
    )
    # get min extent with AHI pixel size
    ahi_lats = numpy.arange(60.-AHI_RESOLUTION/2, -60, -AHI_RESOLUTION)
    ahi_lons = numpy.arange(85.+AHI_RESOLUTION/2, 205, AHI_RESOLUTION)
    n_lats = ahi_lats[find_nearest_index(ahi_lats, m_ex_ullat):find_nearest_index(ahi_lats, m_ex_lrlat) + 1]
    n_lons = ahi_lons[find_nearest_index(ahi_lons, m_ex_ullon):find_nearest_index(ahi_lons, m_ex_lrlon) + 1]
    n_ex_ds = ex_ds.interp(longitude=n_lons, latitude=n_lats, method="nearest", kwargs={"fill_value": "extrapolate"})  # linear?
    n_ex_ullat, n_ex_ullon, n_ex_lrlat, n_ex_lrlon = get_roi_min_extent(r_extent, n_lats, n_lons, AHI_RESOLUTION)
    n_ex_v = n_ex_ds["values"]
    v_ahi_roi = n_ex_v[find_nearest_index(n_lats, n_ex_ullat):find_nearest_index(n_lats, n_ex_lrlat) + 1, find_nearest_index(n_lons, n_ex_ullon):find_nearest_index(n_lons, n_ex_lrlon) + 1]
    return v_ahi_roi


def roi_ahi_data_dn(r_extent, ftp_link, o_resolution):
    temp_ws = os.path.join(ws, 'temp')
    if not os.path.exists(temp_ws):
        os.makedirs(temp_ws)
    filename_parts = ftp_link.split('/')
    ahi_file = filename_parts[len(filename_parts) - 1]
    ahi_bin_bz2 = os.path.join(temp_ws, ahi_file)
    # AHI data ftp server
    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()
    ahi_bin = ''
    try:
        with open(ahi_bin_bz2, 'wb') as f:
            ftp.retrbinary('RETR ' + ftp_link, f.write, 1024 * 1024)
        zipfile = bz2.BZ2File(ahi_bin_bz2)
        data = zipfile.read()
        ahi_bin = ahi_bin_bz2[:-4]
        with open(ahi_bin, 'wb') as f:
            f.write(data)
        zipfile.close()
    except Exception as e:
        os.remove(ahi_bin_bz2)
        print('Error: ' + ftp_link)
        ftp.close()
        sys.exit()
    # disconnect ftp server
    ftp.close()
    # get roi angle array with AHI resolution (1km)
    lons = numpy.arange(85.+o_resolution/2, 205, o_resolution)
    lats = numpy.arange(60.-o_resolution/2, -60, -o_resolution)
    ahi_dn = numpy.fromfile(ahi_bin, dtype='>u2')
    ahi_dn = ahi_dn.reshape(len(lats), len(lons))
    data_ahi_roi = get_data_roi_ahi_reso2(r_extent, ahi_dn, lats, lons, o_resolution)

    shutil.rmtree(temp_ws)
    return data_ahi_roi


def roi_ahi_data(r_extent, ahi_obs_t, band_jma):
    # JMA AHI band: [CEReS gridded, resolution, file_suffix, DN2Tbb_name]
    band_info_ = BAND_INFO[band_jma]
    # AHI data
    obs_time = ahi_obs_t
    ahi_ftp_folder1 = ahi_obs_t[:6]
    ahi_ftp_folder2 = band_info_[0]
    ahi_ftp_suffix = band_info_[2]
    ftp_filename = '/gridded/FD/V20190123/' + ahi_ftp_folder1 + '/' + ahi_ftp_folder2 + '/' + obs_time + ahi_ftp_suffix
    resolution = float(band_info_[1])
    roi_ahi_dn = roi_ahi_data_dn(r_extent, ftp_filename, resolution)
    # DN to Tbb
    LUT_file = band_info_[3]
    LUT_filename = os.path.join(DN2Tbb_folder, LUT_file)
    DN2Tbb_LUT = numpy.loadtxt(LUT_filename)
    roi_ahi_ref = numpy.zeros_like(roi_ahi_dn)
    for lat in range(len(roi_ahi_dn)):
        for lon in range(len(roi_ahi_dn[0])):
            roi_ahi_ref[lat][lon] = DN2Tbb_LUT[int(roi_ahi_dn[lat][lon]), 1]
    roi_ahi_ref = roi_ahi_ref/100
    return roi_ahi_ref


def band_SR(xa, xb, xc, obs_r):
    y = xa * obs_r - xb
    sr = y / (1 + xc * y)
    return sr


def calculate_SR(roi_xa, roi_xb, roi_xc, roi_obs_r):
    roi_sr = numpy.zeros_like(roi_xa)
    for lat in range(len(roi_xa)):
        for lon in range(len(roi_xa[0])):
            xa = roi_xa[lat][lon]
            xb = roi_xb[lat][lon]
            xc = roi_xc[lat][lon]
            obs_r = roi_obs_r[lat][lon]
            roi_sr[lat][lon] = band_SR(xa, xb, xc, obs_r)
    return roi_sr


if __name__ == "__main__":
    start = time.perf_counter()

    # AHI Observation Time
    ahi_obs_time = '201608230450'
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [47.325, 94.329, 47.203, 94.508]

    # GET ROI AHI data
    ahi_data_roi = roi_ahi_data(roi_extent, ahi_obs_time, 'band4')
    print(ahi_data_roi)
    # print(ahi_data_roi.shape)

    # Calculate SR (surface reflectance)
    ac_parameter_filename = os.path.join(AHI_AC_PARAMETER_FOLDER, ahi_obs_time + '_ac.npy')
    ac_parameter = numpy.load(ac_parameter_filename, allow_pickle=True)[0]
    fa_roi = ac_parameter['roi_ac_fa']
    xb_roi = ac_parameter['roi_ac_xb']
    xc_roi = ac_parameter['roi_ac_xc']
    roi_ahi_sr = calculate_SR(fa_roi, xb_roi, xc_roi, ahi_data_roi)
    print(roi_ahi_sr)

    print(roi_ahi_sr - ahi_data_roi)

    end = time.perf_counter()
    print("Run time: ", end - start, 's')