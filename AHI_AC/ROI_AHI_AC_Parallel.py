import os
import sys
import bz2
import numpy
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
from datetime import datetime, timedelta
from ftplib import FTP
import xarray
import shutil
import time
from joblib import Parallel, delayed

# workspace
ws = os.getcwd()

# data paths
DN2Tbb_folder = '/disk1/Data/band_DN2Tbb'
BAND_RF_FOLDER = '/disk1/Data/AHI_SF'
CAMS_FOLDER = '/disk1/Data/CAMS1521_O_W'

# JMA AHI band reflect function
BAND_RF_CSV = {
    'band1': 'sixs_band1.csv',
    'band2': 'sixs_band2.csv',
    'band3': 'sixs_band3.csv',
    'band4': 'sixs_band4.csv',
}

# JMA AHI band: [CEReS gridded, resolution, file_suffix, DN2Tbb_name]
BAND_INFO = {
    'band1': ['VIS', '0.01', '.vis.01.fld.geoss.bz2', 'vis.01'],
    'band2': ['VIS', '0.01', '.vis.02.fld.geoss.bz2', 'vis.02'],
    'band3': ['EXT', '0.005', '.ext.01.fld.geoss.bz2', 'ext.01'],
    'band4': ['VIS', '0.01', '.vis.03.fld.geoss.bz2', 'vis.03'],
}

# parameters
CAMS_RESOLUTION = 0.75  # degree
JAXA_RESOLUTION = 0.375  # degree
AHI_ANGLE_RESOLUTION = 0.04  # degree
AHI_RESOLUTION = 0.01  # degree

BAND_SRF = None


# Calculate CAMS time for AHI Obs.
def calculate_cams_time(yyyy, mm, dd, obs_time):
    cams_times = ['0000', '0300', '0600', '0900', '1200', '1500', '1800', '2100']
    com_flag = ['0130', '0430', '0730', '1330', '1630', '1930', '2230']
    date_add = 0
    for index in range(len(cams_times)):
        if obs_time < com_flag[index]:
            date_add = 0
            cams_hour = cams_times[index]
            break
    if obs_time > com_flag[len(com_flag) - 1]:
        date_add = 1
        cams_hour = '0000'
    obs_date_str = yyyy + mm + dd + '0000'
    obs_date = datetime.strptime(obs_date_str, "%Y%m%d%H%M")
    add_time = timedelta(days=date_add, hours=int(cams_hour[:2]), minutes=int(cams_hour[2:]))
    cams_time = obs_date + add_time
    cams_yyyymmdd = cams_time.strftime("%Y%m%d")
    cams_hh = cams_time.strftime("%H")
    cams_hh_index = cams_times.index(str(cams_hh) + '00')
    # return yyyymmdd, hh
    return cams_yyyymmdd, cams_hh, cams_hh_index


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


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


# Get ROI Data from Rough Dataset with AHI Resolution (simple version)
def get_data_roi_ahi_reso(r_extent, data_v, lats, lons, o_resolution):
    r_ullat = r_extent[0]
    r_ullon = r_extent[1]
    r_lrlat = r_extent[2]
    r_lrlon = r_extent[3]

    ex_ds = xarray.Dataset(
        data_vars={
            "values": (("latitude", "longitude"), data_v),
        },
        coords={
            "latitude": lats,
            "longitude": lons
        },
    )

    ahi_lats = numpy.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
    ahi_lons = numpy.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)
    n_lats = ahi_lats[find_nearest_index(ahi_lats, r_ullat):find_nearest_index(ahi_lats, r_lrlat) + 1]
    n_lons = ahi_lons[find_nearest_index(ahi_lons, r_ullon):find_nearest_index(ahi_lons, r_lrlon) + 1]
    n_ex_ds = ex_ds.interp(longitude=n_lons, latitude=n_lats, method="nearest", kwargs={"fill_value": "extrapolate"})  # linear?
    n_ex_v = n_ex_ds["values"]
    return n_ex_v


# Get ROI Ozone & Watervaper from CAMS with AHI Resolution
def roi_oz_wv_ahi_from_cams(r_extent, ahi_obs_t):
    # ahi obs time
    ahi_yyyy = ahi_obs_t[:4]
    ahi_mm = ahi_obs_t[4:6]
    ahi_dd = ahi_obs_t[6:8]
    ahi_time = ahi_obs_t[-4:]
    # CAMS for Obs
    cams_yyyymmdd, cams_hh, cams_hh_index = calculate_cams_time(ahi_yyyy, ahi_mm, ahi_dd, ahi_time)
    cams_filename = os.path.join(CAMS_FOLDER, cams_yyyymmdd + '.nc')
    # Watervapour & Ozone
    ds_oz_wv = xarray.open_dataset(cams_filename)
    oz_wv_name = ['gtco3', 'tcwv']
    oz_wv_ahi_roi = []
    for type_name in oz_wv_name:
        data_v = ds_oz_wv[type_name].data[cams_hh_index]
        data_v = numpy.array(data_v)
        lats = ds_oz_wv['latitude']
        lons = ds_oz_wv['longitude']
        lats = numpy.array(lats)
        lons = numpy.array(lons)
        v_ahi_roi = get_data_roi_ahi_reso(r_extent, data_v, lats, lons, CAMS_RESOLUTION)
        oz_wv_ahi_roi.append(v_ahi_roi)
    oz_ahi_roi_dn = oz_wv_ahi_roi[0]
    wv_ahi_roi_dn = oz_wv_ahi_roi[1]
    # Unit conversion
    oz_ahi_roi_v = oz_ahi_roi_dn / 0.021415
    wv_ahi_roi_v = wv_ahi_roi_dn / 10
    ds_oz_wv.close()
    return oz_ahi_roi_v, wv_ahi_roi_v


# Calculate CAMS time for AHI Obs.
def calculate_jaxa_time(yyyy, mm, dd, obs_time):
    jaxa_times = ['0000', '0100', '0200', '0300', '0400', '0500', '0600', '0700', '0800', '0900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300']
    com_flag = ['0030', '0130', '0230', '0330', '0430', '0530', '0630', '0730', '0830', '0930', '1030', '1130', '1230', '1330', '1430', '1530', '1630', '1730', '1830', '1930', '2030', '2130', '2230', '2330']
    date_add = 0
    for index in range(len(jaxa_times)):
        if obs_time < com_flag[index]:
            date_add = 0
            jaxa_hour = jaxa_times[index]
            break
    if obs_time > com_flag[len(com_flag) - 1]:
        date_add = 1
        jaxa_hour = '0000'
    obs_date_str = yyyy + mm + dd + '0000'
    obs_date = datetime.strptime(obs_date_str, "%Y%m%d%H%M")
    add_time = timedelta(days=date_add, hours=int(jaxa_hour[:2]), minutes=int(jaxa_hour[2:]))
    jaxa_time = obs_date + add_time
    jaxa_yyyy = jaxa_time.strftime("%Y")
    jaxa_mm = jaxa_time.strftime("%m")
    jaxa_dd = jaxa_time.strftime("%d")
    jaxa_hh = jaxa_time.strftime("%H")
    # return yyyymmdd, hh
    return jaxa_yyyy, jaxa_mm, jaxa_dd, jaxa_hh


def download_AOT(YYYY, MM, DD, HH, folder):
    ftp_addr = 'ftp.ptree.jaxa.jp'
    f = FTP(ftp_addr)
    f.login('zbc0113_outlook.com', 'SP+wari8')
    # print(f.getwelcome())
    remote_filepath = '/pub/model/ARP/MS/bet/' + YYYY + MM + '/' + DD + '/'
    f.cwd(remote_filepath)
    list = f.nlst()
    bufsize = 1024
    for name in list:
        if name[13:17] == HH + '00':
            data = open(folder + '/' + name, 'wb')
            filename = 'RETR ' + name
            f.retrbinary(filename, data.write, bufsize)
    f.quit()
    return os.path.join(folder, 'H08_' + YYYY + MM + DD + '_' + HH + '00_MSARPbet_ANL.00960_00480.nc')


# Get ROI AOT from JAXA with AHI Resolution
def roi_od550_ahi_from_jaxa(r_extent, ahi_obs_t):
    # ahi obs time
    ahi_yyyy = ahi_obs_t[:4]
    ahi_mm = ahi_obs_t[4:6]
    ahi_dd = ahi_obs_t[6:8]
    ahi_time = ahi_obs_t[-4:]
    jaxa_yyyy, jaxa_mm, jaxa_dd, jaxa_hh = calculate_jaxa_time(ahi_yyyy, ahi_mm, ahi_dd, ahi_time)
    temp_folder = os.path.join(ws, 'temp')
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    aot_filename = download_AOT(jaxa_yyyy, jaxa_mm, jaxa_dd, jaxa_hh, temp_folder)
    # AOT550
    ds_aot550 = xarray.open_dataset(aot_filename)
    # AOT SeaSalt Dust OA SO4 BC
    jaxa_names = ['od550aer', 'od550ss', 'od550dust', 'od550oa', 'od550so4', 'od550bc']
    jaxa_ahi_roi = []
    for jaxa_name in jaxa_names:
        data_v = ds_aot550[jaxa_name]
        data_v = numpy.array(data_v)
        lats = ds_aot550['lat']
        lons = ds_aot550['lon']
        lats = numpy.array(lats)
        lons = numpy.array(lons)
        ad550_ahi_roi = get_data_roi_ahi_reso(r_extent, data_v, lats, lons, JAXA_RESOLUTION)
        jaxa_ahi_roi.append(ad550_ahi_roi)
    ds_aot550.close()
    aot550_ahi_roi = jaxa_ahi_roi[0]
    ss550_ahi_roi = jaxa_ahi_roi[1]
    dust550_ahi_roi = jaxa_ahi_roi[2]
    oa550_ahi_roi = jaxa_ahi_roi[3]
    so4550_ahi_roi = jaxa_ahi_roi[4]
    bc550_ahi_roi = jaxa_ahi_roi[5]
    shutil.rmtree(temp_folder)

    return aot550_ahi_roi, ss550_ahi_roi, dust550_ahi_roi, oa550_ahi_roi, so4550_ahi_roi, bc550_ahi_roi


def get_aero_type(oceanic, dust_like, water_soluble, soot_like):
    total = oceanic + dust_like + water_soluble + soot_like
    # 1:oceanic, 2:dust_like, 3:water_soluble, 4:soot_like
    percent_array = [[1, oceanic / total], [2, dust_like / total], [3, water_soluble / total], [4, soot_like / total]]
    # sort by percentation
    sorted_array = sorted(percent_array, key=(lambda x: x[1]), reverse=True)
    max_type_index = sorted_array[0][0]
    if max_type_index == 1:
        return AeroProfile.Maritime
    else:
        return AeroProfile.Continental


# Get ROI Aerosol Type with AHI Resolution
def set_roi_aero_type(oceanic, dust_like, water_soluble, soot_like):
    aero_type_roi = numpy.zeros_like(oceanic)
    for lat in range(len(oceanic)):
        for lon in range(len(oceanic[0])):
            aero_type = get_aero_type(oceanic[lat][lon], dust_like[lat][lon], water_soluble[lat][lon], soot_like[lat][lon])
            aero_type_roi[lat][lon] = aero_type
    return aero_type_roi


def roi_ahi_angle(r_extent, ftp_link):
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
        print(e)
        ftp.close()
        # sys.exit()
    # disconnect ftp server
    ftp.close()
    # get roi angle array with AHI resolution (1km)
    lons = numpy.arange(85. + AHI_ANGLE_RESOLUTION / 2, 205, AHI_ANGLE_RESOLUTION)
    lats = numpy.arange(60. - AHI_ANGLE_RESOLUTION / 2, -60, -AHI_ANGLE_RESOLUTION)
    ahi_dn = numpy.fromfile(ahi_bin, dtype='>f4')
    ahi_dn = ahi_dn.reshape(len(lats), len(lons))
    angle_ahi_roi = get_data_roi_ahi_reso(r_extent, ahi_dn, lats, lons, AHI_ANGLE_RESOLUTION)

    shutil.rmtree(temp_ws)
    return angle_ahi_roi


def calculate_raa_array(vaa_array, saa_array):
    raa_array = numpy.zeros_like(vaa_array)
    for lat in range(len(vaa_array)):
        for lon in range(len(vaa_array[0])):
            raa = 0
            diff = abs(vaa_array[lat][lon] - saa_array[lat][lon])
            if diff < 180:
                raa = diff
            else:
                raa = 360 - diff
            raa_array[lat][lon] = raa
    return raa_array


# Get ROI AHI Obs. condition with AHI Resolution
def roi_ahi_geo(r_extent, ahi_obs_t):
    obs_time = ahi_obs_t
    ahi_ftp_folder1 = ahi_obs_t[:6]
    ahi_ftp_folder2 = ahi_obs_t[:8]
    common_filename = '/gridded/FD/V20190123/' + ahi_ftp_folder1 + '/4KM/' + ahi_ftp_folder2 + '/' + obs_time
    # vza vaa saa sza
    angles_suffix = ['.sat.zth.fld.4km.bin.bz2', '.sat.azm.fld.4km.bin.bz2', '.sun.azm.fld.4km.bin.bz2', '.sun.zth.fld.4km.bin.bz2']
    angles_roi = []
    for index in range(len(angles_suffix)):
        angle_suffix = angles_suffix[index]
        ftp_link = common_filename + angle_suffix
        angle_roi = roi_ahi_angle(r_extent, ftp_link)
        angles_roi.append(angle_roi)
    roi_ahi_vza = numpy.array(angles_roi[0])
    roi_ahi_raa = calculate_raa_array(angles_roi[1], angles_roi[2])
    roi_ahi_sza = numpy.array(angles_roi[3])
    return roi_ahi_vza, roi_ahi_raa, roi_ahi_sza


def atmospheric_correction_6s(VZA, SZA, RAA, AOT, aerosol_type, ozone, water_vapour, altitude=0.):
    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(water_vapour, ozone)
    s.aero_profile = AeroProfile.PredefinedType(aerosol_type)
    s.aot550 = AOT
    s.wavelength = Wavelength(BAND_SRF[0, 0], BAND_SRF[len(BAND_SRF) - 1, 0], BAND_SRF[:, 1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(altitude)
    s.geometry = Geometry.User()
    s.geometry.solar_z = SZA
    s.geometry.solar_a = RAA
    s.geometry.view_z = VZA
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)  # value is no matter, results are same
    s.run()

    # TOA Reflectance to TOA Radiance?
    f1 = 1 / (s.outputs.transmittance_total_scattering.total * s.outputs.transmittance_global_gas.total)

    x1 = s.outputs.coef_xa
    x2 = s.outputs.coef_xb
    x3 = s.outputs.coef_xc
    del s
    return (f1, x1, x2, x3)


def ac_roi_parameter(VZA_ar, SZA_ar, RAA_ar, AOT_ar, aerosol_type_ar, ozone_ar, water_vapour_ar):
    global BAND_SRF
    VZA_ar = numpy.array(VZA_ar).flatten()
    SZA_ar = numpy.array(SZA_ar).flatten()
    RAA_ar = numpy.array(RAA_ar).flatten()
    AOT_ar = numpy.array(AOT_ar).flatten()
    aerosol_type_ar = numpy.array(aerosol_type_ar).flatten()
    ozone_ar = numpy.array(ozone_ar).flatten()
    water_vapour_ar = numpy.array(water_vapour_ar).flatten()
    AC_output = Parallel(n_jobs=16)(delayed(atmospheric_correction_6s)(VZA, SZA, RAA, AOT, aerosol_type, ozone, water_vapour) for VZA in VZA_ar for SZA in SZA_ar for RAA in RAA_ar for AOT in AOT_ar for aerosol_type in aerosol_type_ar for ozone in ozone_ar for water_vapour in water_vapour_ar)

    AC_output = numpy.array(AC_output)
    ac_fa = AC_output[:, 0]
    ac_xa = AC_output[:, 1]
    ac_xb = AC_output[:, 2]
    ac_xc = AC_output[:, 3]
    ac_fa = ac_fa.reshape(VZA_ar.shape)
    ac_xa = ac_fa.reshape(VZA_ar.shape)
    ac_xb = ac_fa.reshape(VZA_ar.shape)
    ac_xc = ac_fa.reshape(VZA_ar.shape)

    return ac_fa, ac_xa, ac_xb, ac_xc


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
        print(e)
        ftp.close()
        # sys.exit()
    # disconnect ftp server
    ftp.close()
    # get roi angle array with AHI resolution (1km)
    lons = numpy.arange(85. + o_resolution / 2, 205, o_resolution)
    lats = numpy.arange(60. - o_resolution / 2, -60, -o_resolution)
    ahi_dn = numpy.fromfile(ahi_bin, dtype='>u2')
    ahi_dn = ahi_dn.reshape(len(lats), len(lons))
    data_ahi_roi = get_data_roi_ahi_reso(r_extent, ahi_dn, lats, lons, o_resolution)

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
    roi_ahi_ref = roi_ahi_ref / 100
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


# Record the data in ROI, and calculate the AC parameters
def record_roi_data_AC_parameters_sr(r_extent, ahi_obs_t, band_jma):
    global BAND_SRF
    folder_path = os.path.join(ws, 'AHI_AC_PARAMETER')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    record_npy = os.path.join(folder_path, ahi_obs_t + '_ac_' + band_jma + '.npy')
    if not os.path.exists(record_npy):
        try:

            # Get ROI Ozone & Watervaper (xarray.core.dataarray.DataArray) from CAMS with AHI Resolution
            oz_ahi_roi_da, wv_ahi_roi_da = roi_oz_wv_ahi_from_cams(r_extent, ahi_obs_time)
            oz_ahi_roi = numpy.array(oz_ahi_roi_da)
            wv_ahi_roi = numpy.array(wv_ahi_roi_da)

            # Get ROI 550nm data from JAXA dataset with AHI Resolution
            aot_ahi_roi_da, ss_ahi_roi_da, dust_ahi_roi_da, oa_ahi_roi_da, so4_ahi_roi_da, bc_ahi_roi_da = roi_od550_ahi_from_jaxa(r_extent, ahi_obs_time)
            aot_ahi_roi = numpy.array(aot_ahi_roi_da)

            # Calculate aerosol type
            aero_type_ahi_roi = set_roi_aero_type(ss_ahi_roi_da, dust_ahi_roi_da, oa_ahi_roi_da, so4_ahi_roi_da + bc_ahi_roi_da)

            # AHI data: vza, raa, sza
            roi_ahi_vza, roi_ahi_raa, roi_ahi_sza = roi_ahi_geo(r_extent, ahi_obs_time)

            # Get Atmospheric Correction Parameters using
            filename = BAND_RF_CSV[band_jma]
            band_rf_csv_path = os.path.join(BAND_RF_FOLDER, filename)
            BAND_SRF = numpy.loadtxt(band_rf_csv_path, delimiter=",")
            ac_roi_fa, ac_roi_xa, ac_roi_xb, ac_roi_xc = ac_roi_parameter(roi_ahi_vza, roi_ahi_sza, roi_ahi_raa, aot_ahi_roi, aero_type_ahi_roi, oz_ahi_roi, wv_ahi_roi)

            # GET ROI AHI data
            ahi_data_roi = roi_ahi_data(r_extent, ahi_obs_time, band_jma)

            # AHI AC
            roi_ahi_sr = calculate_SR(ac_roi_fa, ac_roi_xb, ac_roi_xc, ahi_data_roi)

            # Template of record
            #############################
            # demo = [
            #     {
            #         'obs_time': '201608230450',
            #         'roi_lats': [60.0, 59.99, ..., -60.0],
            #         'roi_lons': [85.0, 85.01, ..., 205.0],
            #         'roi_vza': [[..., ..., ...], ...],
            #         'roi_sza': [[..., ..., ...], ...],
            #         'roi_raa': [[..., ..., ...], ...],
            #         'roi_aot': [[..., ..., ...], ...],
            #         'roi_aero_type': [[..., ..., ...], ...],
            #         'roi_oz': [[..., ..., ...], ...],
            #         'roi_wv': [[..., ..., ...], ...],
            #         'roi_ac_fa': [[..., ..., ...], ...],
            #         'roi_ac_xa': [[..., ..., ...], ...],
            #         'roi_ac_xb': [[..., ..., ...], ...],
            #         'roi_ac_xc': [[..., ..., ...], ...],
            #         'roi_ahi_data': [[..., ..., ...], ...],
            #         'roi_ahi_sr': [[..., ..., ...], ...],
            #     }
            # ]
            #############################

            r_lats = numpy.array(wv_ahi_roi_da['latitude'])
            r_lons = numpy.array(wv_ahi_roi_da['longitude'])
            record_info = [{
                'obs_time': ahi_obs_t,
                'roi_lats': r_lats,
                'roi_lons': r_lons,
                'roi_vza': roi_ahi_vza,
                'roi_sza': roi_ahi_sza,
                'roi_raa': roi_ahi_raa,
                'roi_aot': aot_ahi_roi,
                'roi_aero_type': aero_type_ahi_roi,
                'roi_oz': oz_ahi_roi,
                'roi_wv': wv_ahi_roi,
                'roi_ac_fa': ac_roi_fa,
                'roi_ac_xa': ac_roi_xa,
                'roi_ac_xb': ac_roi_xb,
                'roi_ac_xc': ac_roi_xc,
                'roi_ahi_data': ahi_data_roi,
                'roi_ahi_sr': roi_ahi_sr,
            }]

            # Storage to file
            folder_path = os.path.join(ws, 'AHI_AC_PARAMETER')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, ahi_obs_t + '_ac_' + band_jma + '.npy')
            txt_path = os.path.join(folder_path, ahi_obs_t + '_ac_' + band_jma + '.txt')
            numpy.save(file_path, record_info)
            with open(txt_path, 'w') as f:
                f.write(str(record_info[0]))
        except Exception as e:
            print(record_npy)
            print(e)


if __name__ == "__main__":
    start = time.perf_counter()
    # 0.0_50
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [-3.101, 141.153, -3.281, 141.333]

    # Matched AHI Obs. Time
    ahi_obs_times = [
        '201701060100', '201711060120', '201711220100', '201712080100', '201712240100', '201801090100', '201811090120', '201811250100', '201812110100', '201812270100', '201901120110', '201911120110', '201911280100', '201912140100',
        '201912300100', '201704190130', '201705050110', '201705210100', '201706060040', '201706220040', '201707080050', '201707240110', '201708090110', '201804220130', '201805080110', '201805240050', '201806090040', '201806250040',
        '201807110100', '201807270110', '201808120110', '201904250120', '201905110110', '201905270050', '201906120040', '201906280040', '201907140100', '201907300110', '201908150120'
    ]
    # Bands
    band_names = ['band3', 'band4']
    total_c = len(ahi_obs_times)
    for idx in range(total_c):
        ahi_obs_time = ahi_obs_times[idx]
        for band_name in band_names:
            print(str(idx+1) + '/' + str(total_c), ahi_obs_time + '_' + band_name)
            # Record data and AC parameter at ROI
            record_roi_data_AC_parameters_sr(roi_extent, ahi_obs_time, band_name)

    end = time.perf_counter()
    print("Run time: ", end - start, 's')
