#!/usr/bin/env python
# coding: utf-8
import os
import numpy
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
from datetime import datetime, timedelta
from ftplib import FTP
import xarray

ws = r'D:\Work_PhD\MISR_AHI_WS\220527'

WORK_SPACE = os.getcwd()
CAMS_FOLDER = os.path.join(ws, 'CAMS')
CAMS_RESOLUTION = 0.75  # degree
AHI_RESOLUTION = 0.01  # degree

WATER = 3
OZONE = 0.25
ALTITUDE = 0
AOT = 0.1
SZA = 45
VZA = 45
RAA = 90
# Aeropro = 3


# Calculate CAMS time for AHI Obs.
def calculate_cams_time(yyyy, mm, dd, obs_time):
    cams_times = [
        '0000', '0300', '0600', '0900', '1200', '1500', '1800', '2100'
    ]
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
    add_time = timedelta(days=date_add,
                         hours=int(cams_hour[:2]),
                         minutes=int(cams_hour[2:]))
    cams_time = obs_date + add_time
    cams_yyyymmdd = cams_time.strftime("%Y%m%d")
    cams_hh = cams_time.strftime("%H")
    # return yyyymmdd, hh
    return cams_yyyymmdd, cams_hh


def get_roi_min_extent(r_extent, f_lats, f_lons, resulution):
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
        max_lat_c = max_lat_c - resulution
    while min_lon_c < r_ullon:
        m_ex_ullon = min_lon_c
        min_lon_c = min_lon_c + resulution
    while min_lat_c < r_lrlat:
        m_ex_lrlat = min_lat_c
        min_lat_c = min_lat_c + resulution
    while max_lon_c > r_lrlon:
        m_ex_lrlon = max_lon_c
        max_lon_c = max_lon_c - resulution

    return m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon


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


def ac_band1(In_Ozone, In_AOT, In_SZA, In_VZA, In_RAA):
    wl_band = WORK_SPACE + "/AHI_AC/AHI_SF/sixs_band1.csv"
    band = numpy.loadtxt(wl_band, delimiter=",")

    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(WATER, In_Ozone)
    s.aero_profile = AeroProfile.PredefinedType(2)  # AeroProfile.Maritime
    s.aot550 = In_AOT
    s.wavelength = Wavelength(band[0, 0], band[len(band) - 1, 0], band[:, 1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(ALTITUDE)
    s.geometry = Geometry.User()
    s.geometry.solar_z = In_SZA
    s.geometry.solar_a = In_RAA
    s.geometry.view_z = In_VZA
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)
    s.run()

    f1 = 1 / (s.outputs.transmittance_total_scattering.total *
              s.outputs.transmittance_global_gas.total)
    return (f1, s.outputs.coef_xb, s.outputs.coef_xc)
    del s


# Get ROI Ozone & Watervaper from Rough Dataset with AHI Resolution
def get_data_roi_ahi_reso(r_extent, data_v, lats, lons, o_resolution):
    # min extent of ROI in CAMS dataset
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = get_roi_min_extent(r_extent, lats, lons, o_resolution)
    n_lats = numpy.arange(m_ex_ullat, m_ex_lrlat - o_resolution, -AHI_RESOLUTION)
    n_lons = numpy.arange(m_ex_ullon, m_ex_lrlon + o_resolution, AHI_RESOLUTION)
    ex_ds = xarray.Dataset(
        data_vars={
            "values": (
                ("latitude", "longitude"),
                data_v[numpy.argmax(lats == m_ex_ullat):numpy.argmax(lats == m_ex_lrlat) + 1, numpy.argmax(lons == m_ex_ullon):numpy.argmax(lons == m_ex_lrlon) + 1],
            ),
        },
        coords={"latitude": lats[numpy.argmax(lats == m_ex_ullat):numpy.argmax(lats == m_ex_lrlat) + 1], "longitude": lons[numpy.argmax(lons == m_ex_ullon):numpy.argmax(lons == m_ex_lrlon) + 1]},
    )
    # get min extent with AHI pixel size
    n_ex_ds = ex_ds.interp(longitude=n_lons, latitude=n_lats, method="nearest")
    n_ex_ullat, n_ex_ullon, n_ex_lrlat, n_ex_lrlon = get_roi_min_extent(r_extent, n_lats, n_lons, AHI_RESOLUTION)
    n_ex_v = n_ex_ds["values"]
    v_ahi_roi = n_ex_v[numpy.argmax(n_lats == n_ex_ullat):numpy.argmax(n_lats == n_ex_lrlat) + 1, numpy.argmax(n_lons == n_ex_ullon):numpy.argmax(n_lons == n_ex_lrlon) + 1]
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
    oz_ahi_roi_v = oz_ahi_roi_dn*46.6975764
    wv_ahi_roi_v = wv_ahi_roi_dn/10

    return oz_ahi_roi_v, wv_ahi_roi_v


if __name__ == "__main__":
    # start = time.time()

    # AC_output = ac_band1(Ozone, AOT, SZA, VZA, RAA)
    # print(AC_output)

    # end = time.time()
    # T = end - start
    # print('time: {:.1f} secs, {:.1f} mins, {:.1f} hours'.format(
    #     T, T / 60, T / 3600))

    # AHI Observation Time
    ahi_obs_time = '201608230450'
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [47.325, 94.329, 47.203, 94.508]
    # Get ROI Ozone & Watervaper (xarray.core.dataarray.DataArray) from CAMS with AHI Resolution
    oz_ahi_roi_da, wv_ahi_roi_da = roi_oz_wv_ahi_from_cams(roi_extent, ahi_obs_time)
    # print(oz_ahi_roi_da)
    # print(numpy.array(oz_ahi_roi_da))
    # print(numpy.array(oz_ahi_roi_da['latitude']))
