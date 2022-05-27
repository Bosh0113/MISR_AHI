#!/usr/bin/env python
# coding: utf-8
import os
import numpy
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
from datetime import datetime, timedelta
from ftplib import FTP
import xarray

WORK_SPACE = os.getcwd()
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

YYYY = '2016'
MM = '08'
DD = '23'
HH = '04'


def calcuate_cams_time(yyyy, mm, dd, obs_time):
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


def get_roi_min_extent_cams(roi_extent, lats, lons):
    r_ullat = roi_extent[0]
    r_ullon = roi_extent[1]
    r_lrlat = roi_extent[2]
    r_lrlon = roi_extent[3]
    max_lat_c = lats[0]
    min_lat_c = lats[len(lats) - 1]
    max_lon_c = lons[len(lons) - 1]
    min_lon_c = lons[0]
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = None, None, None, None
    while max_lat_c > r_ullat:
        m_ex_ullat = max_lat_c
        max_lat_c = max_lat_c - CAMS_RESOLUTION
    while min_lon_c < r_ullon:
        m_ex_ullon = min_lon_c
        min_lon_c = min_lon_c + CAMS_RESOLUTION
    while min_lat_c < r_lrlat:
        m_ex_lrlat = min_lat_c
        min_lat_c = min_lat_c + CAMS_RESOLUTION
    while max_lon_c > r_lrlon:
        m_ex_lrlon = max_lon_c
        max_lon_c = max_lon_c - CAMS_RESOLUTION

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


if __name__ == "__main__":
    # start = time.time()

    # AC_output = ac_band1(Ozone, AOT, SZA, VZA, RAA)
    # print(AC_output)

    # end = time.time()
    # T = end - start
    # print('time: {:.1f} secs, {:.1f} mins, {:.1f} hours'.format(
    #     T, T / 60, T / 3600))

    ws = r'D:\Work_PhD\MISR_AHI_WS\220527'
    cams_folder = os.path.join(ws, 'CAMS')
    ahi_time = '0450'
    # CAMS for Obs
    cams_yyyymmdd, cams_hh = calcuate_cams_time(YYYY, MM, DD, ahi_time)
    cams_filename = os.path.join(cams_folder, cams_yyyymmdd + '.nc')
    # Watervapour & Ozone
    ds_oz_wv = xarray.open_dataset(cams_filename)
    oz = ds_oz_wv['gtco3'].data[int(cams_hh) - 1]
    oz = numpy.array(oz)
    lats = ds_oz_wv['latitude']
    lons = ds_oz_wv['longitude']
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [47.325, 94.329, 47.203, 94.508]
    # min extent of ROI in CAMS dataset
    m_ex_ullat, m_ex_ullon, m_ex_lrlat, m_ex_lrlon = get_roi_min_extent_cams(roi_extent, lats, lons)
    n_lats = numpy.arange(m_ex_ullat, m_ex_lrlat - CAMS_RESOLUTION, -AHI_RESOLUTION)
    n_lons = numpy.arange(m_ex_ullon, m_ex_lrlon + CAMS_RESOLUTION, AHI_RESOLUTION)
    ex_oz_ds = xarray.Dataset(
        data_vars={
            "gtco3": (
                ("latitude", "longitude"),
                oz[numpy.argmax(lats == m_ex_ullat):numpy.argmax(lats == m_ex_lrlat) + 1, numpy.argmax(lons == m_ex_ullon):numpy.argmax(lons == m_ex_lrlon) + 1],
            ),
        },
        coords={"latitude": lats[numpy.argmax(lats == m_ex_ullat):numpy.argmax(lats == m_ex_lrlat) + 1], "longitude": lons[numpy.argmax(lons == m_ex_ullon):numpy.argmax(lons == m_ex_lrlon) + 1]},
    )
    # get min extent with AHI pixel size
    n_ex_oz_ds = ex_oz_ds.interp(longitude=n_lons, latitude=n_lats, method="nearest")
    # print(n_ex_oz_ds)
