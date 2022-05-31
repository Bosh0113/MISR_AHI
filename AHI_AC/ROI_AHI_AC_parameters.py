import os
import sys
import bz2
import numpy
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
from datetime import datetime, timedelta
from ftplib import FTP
import xarray
import shutil

# workspace
ws = r'D:\Work_PhD\MISR_AHI_WS\220527'

# data paths
WORK_SPACE = os.getcwd()
BAND_RF_CSV = WORK_SPACE + "/AHI_AC/AHI_SF/sixs_band1.csv"
CAMS_FOLDER = os.path.join(ws, 'CAMS')

# parameters
CAMS_RESOLUTION = 0.75  # degree
JAXA_RESOLUTION = 0.375  # degree
AHI_ANGLE_RESOLUTION = 0.04  # degree
AHI_RESOLUTION = 0.01  # degree


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
    # return yyyymmdd, hh
    return cams_yyyymmdd, cams_hh


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


def get_roi_para_extent(r_extent, f_lats, f_lons, resolution):
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

    return m_ex_ullat + resolution, m_ex_ullon - resolution, m_ex_lrlat - resolution, m_ex_lrlon + resolution


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


# Get ROI Ozone & Watervaper from Rough Dataset with AHI Resolution
def get_data_roi_ahi_reso(r_extent, data_v, lats, lons, o_resolution):
    # min extent of ROI in CAMS dataset
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = get_roi_para_extent(r_extent, lats, lons, o_resolution)
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


# Get ROI Ozone & Watervaper from CAMS with AHI Resolution
def roi_oz_wv_ahi_from_cams(r_extent, ahi_obs_t):
    # ahi obs time
    ahi_yyyy = ahi_obs_t[:4]
    ahi_mm = ahi_obs_t[4:6]
    ahi_dd = ahi_obs_t[6:8]
    ahi_time = ahi_obs_t[-4:]
    # CAMS for Obs
    cams_yyyymmdd, cams_hh = calculate_cams_time(ahi_yyyy, ahi_mm, ahi_dd, ahi_time)
    cams_filename = os.path.join(CAMS_FOLDER, cams_yyyymmdd + '.nc')
    # Watervapour & Ozone
    ds_oz_wv = xarray.open_dataset(cams_filename)
    oz_wv_name = ['gtco3', 'tcwv']
    oz_wv_ahi_roi = []
    for type_name in oz_wv_name:
        data_v = ds_oz_wv[type_name].data[int(cams_hh) - 1]
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
    oz_ahi_roi_v = oz_ahi_roi_dn * 46.6975764
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
        ftp.close()
        sys.exit()
    # disconnect ftp server
    ftp.close()
    # get roi angle array with AHI resolution (1km)
    lons = numpy.arange(85.+AHI_ANGLE_RESOLUTION/2, 205, AHI_ANGLE_RESOLUTION)
    lats = numpy.arange(60.-AHI_ANGLE_RESOLUTION/2, -60, -AHI_ANGLE_RESOLUTION)
    ahi_dn = numpy.fromfile(ahi_bin, dtype='>f4')
    ahi_dn = ahi_dn.reshape(len(lats), len(lons))
    angle_ahi_roi = get_data_roi_ahi_reso(r_extent, ahi_dn, lats, lons, JAXA_RESOLUTION)

    shutil.rmtree(temp_ws)
    return angle_ahi_roi


def get_ahi_raa(vaa, saa):
    raa = 0
    diff = abs(vaa - saa)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def calculate_raa_array(vaa_array, saa_array):
    raa_array = numpy.zeros_like(vaa_array)
    for lat in range(len(vaa_array)):
        for lon in range(len(vaa_array[0])):
            raa_array[lat][lon] = get_ahi_raa(vaa_array[lat][lon], saa_array[lat][lon])
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


def atmospheric_correction_6s(band_RF, VZA, SZA, RAA, AOT, aerosol_type, ozone, water_vapour, altitude=0.):
    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(water_vapour, ozone)
    s.aero_profile = AeroProfile.PredefinedType(aerosol_type)
    s.aot550 = AOT
    s.wavelength = Wavelength(band_RF[0, 0], band_RF[len(band_RF) - 1, 0], band_RF[:, 1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(altitude)
    s.geometry = Geometry.User()
    s.geometry.solar_z = SZA
    s.geometry.solar_a = RAA
    s.geometry.view_z = VZA
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)    # value is no matter, results are same
    s.run()

    # f1 = 1 / (s.outputs.transmittance_total_scattering.total * s.outputs.transmittance_global_gas.total)
    # print(f1, s.outputs.coef_xa, f1-s.outputs.coef_xa)
    # x1 = f1

    x1 = s.outputs.coef_xa
    x2 = s.outputs.coef_xb
    x3 = s.outputs.coef_xc
    del s
    return (x1, x2, x3)


def ac_roi_parameter(band_RF, VZA_ar, SZA_ar, RAA_ar, AOT_ar, aerosol_type_ar, ozone_ar, water_vapour_ar):
    ac_para = numpy.zeros_like(VZA_ar)
    for lat in range(len(VZA_ar)):
        for lon in range(len(VZA_ar[0])):
            ac_para[lat][lon] = atmospheric_correction_6s(band_RF, VZA_ar[lat][lon], SZA_ar[lat][lon], RAA_ar[lat][lon], AOT_ar[lat][lon], aerosol_type_ar[lat][lon], ozone_ar[lat][lon], water_vapour_ar[lat][lon])
    return ac_para


if __name__ == "__main__":

    # AHI Observation Time
    ahi_obs_time = '201608230450'
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [47.325, 94.329, 47.203, 94.508]

    # Get ROI Ozone & Watervaper (xarray.core.dataarray.DataArray) from CAMS with AHI Resolution
    oz_ahi_roi_da, wv_ahi_roi_da = roi_oz_wv_ahi_from_cams(roi_extent, ahi_obs_time)
    oz_ahi_roi = numpy.array(oz_ahi_roi_da)
    wv_ahi_roi = numpy.array(wv_ahi_roi_da)
    # print(oz_ahi_roi_da)
    # print(numpy.array(oz_ahi_roi_da).shape)
    # print(numpy.array(oz_ahi_roi_da))
    # print(numpy.array(oz_ahi_roi_da['latitude']))

    # Get ROI 550nm data from JAXA dataset with AHI Resolution
    aot_ahi_roi_da, ss_ahi_roi_da, dust_ahi_roi_da, oa_ahi_roi_da, so4_ahi_roi_da, bc_ahi_roi_da = roi_od550_ahi_from_jaxa(roi_extent, ahi_obs_time)
    aot_ahi_roi = numpy.array(aot_ahi_roi_da)
    # print(aot_ahi_roi_da)
    # print(numpy.array(aot_ahi_roi_da).shape)

    # Calculate aerosol type
    aero_type_ahi_roi = set_roi_aero_type(ss_ahi_roi_da, dust_ahi_roi_da, oa_ahi_roi_da, so4_ahi_roi_da + bc_ahi_roi_da)
    # print(aero_type_ahi_roi)

    # AHI data: vza, raa, sza
    roi_ahi_vza, roi_ahi_raa, roi_ahi_sza = roi_ahi_geo(roi_extent, ahi_obs_time)
    # print(roi_ahi_vza)
    # print(numpy.array(roi_ahi_vza).shape)
    # print(roi_ahi_raa)
    # print(numpy.array(roi_ahi_raa).shape)
    # print(roi_ahi_sza)
    # print(numpy.array(roi_ahi_sza).shape)

    # Get Atmospheric Correction Parameters using 6SV
    band_rf = numpy.loadtxt(BAND_RF_CSV, delimiter=",")
    ac_roi_parameters = ac_roi_parameter(band_rf, roi_ahi_vza, roi_ahi_sza, roi_ahi_raa, aot_ahi_roi, aero_type_ahi_roi, oz_ahi_roi, wv_ahi_roi)
    # 
    # ac_parameters = atmospheric_correction_6s(band_rf, roi_ahi_vza[0][0], roi_ahi_sza[0][0], roi_ahi_raa[0][0], aot_ahi_roi[0][0], aero_type_ahi_roi[0][0], oz_ahi_roi[0][0], wv_ahi_roi[0][0])
    # print(ac_parameters)

    # Atmospheric Correction using 6SV
