#!/usr/bin/env python
# coding: utf-8

import numpy as np
import time as T
from joblib import Parallel, delayed
from scipy.interpolate import griddata, RegularGridInterpolator
import os
import cv2
# from H8utils import *
from ftplib import FTP
import xarray as xr
import paramiko
from scp import SCPClient

YYYY = '2018'
MM = ['05']
DD = ['06']

HH = ['23']
MIN = ['40']
MIN = ['00', '10', '20', '30', '40', '50']

sza = np.linspace(0, 80, 17)
vza = np.linspace(0, 80, 17)
water = np.linspace(0, 7, 8)
ozone = np.linspace(0.2, 0.4, 5)
# AL = np.linspace(0,4,5)
AOT = np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0])
raa = np.linspace(0, 180, 19)
# Aeropro = np.array([1,2,3,5,6])


class read_H8data:
    def __init__(self, band, band_number):
        self.band = band
        self.band_number = band_number

    def get_path(self, date):
        return '/mnt/nas01G/geo01/H8AHI/download/org/192.168.1.5/gridded/FD/V20190123/' + date[
            0:6] + '/' + self.band.upper() + '/'

    def get_filename(self):
        return self.band + "." + self.band_number + ".fld.geoss.bz2"


def file_path(band_num, date):
    return read_H8data.get_path(BAND[band_num - 1],
                                date) + date + "." + read_H8data.get_filename(
                                    BAND[band_num - 1])


def Hi8_band():
    b01 = read_H8data('vis', '01')
    b02 = read_H8data('vis', '02')
    b03 = read_H8data('ext', '01')
    b04 = read_H8data('vis', '03')
    b05 = read_H8data('sir', '01')
    b06 = read_H8data('sir', '02')
    b07 = read_H8data('tir', '05')
    b08 = read_H8data('tir', '06')
    b09 = read_H8data('tir', '07')
    b10 = read_H8data('tir', '08')
    b11 = read_H8data('tir', '09')
    b12 = read_H8data('tir', '10')
    b13 = read_H8data('tir', '01')
    b14 = read_H8data('tir', '02')
    b15 = read_H8data('tir', '03')
    b16 = read_H8data('tir', '04')
    BAND = [
        b01, b02, b03, b04, b05, b06, b07, b08, b09, b10, b11, b12, b13, b14,
        b15, b16
    ]
    return BAND


def download_H8data(date):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname='10.4.200.105',
                   port=22,
                   username='liwei',
                   password='liwei000')
    scp = SCPClient(client.get_transport())
    sftp = client.open_sftp()

    try:
        sftp.stat(file_path(3, date))

    except FileNotFoundError:
        print("File Not Found")
        pass

    else:
        scp.get(file_path(3, date), folder_original + '/')
        os.system('lbzip2 -d {}{}'.format(folder_original + '/',
                                          file_path(3, date)[-33:]))


def remove_original_file(path):
    os.system('rm -rf {}'.format(path))


def download_AOT(YYYY, MM, DD, HH, folder):
    ftp_addr = 'ftp.ptree.jaxa.jp'
    f = FTP(ftp_addr)
    f.login('liwei1997_chiba-u.jp', 'SP+wari8')
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


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def DN2tbb(dn):
    LUT = np.loadtxt('ext.01')
    return LUT[dn, 1]


# def calc_sunpos(dtime, col, row):
#     sun = ephem.Sun()
#     obs = ephem.Observer()
#     obs.date = dtime
#     obs.lat = latgridrad[row]
#     obs.long = longridrad[col]
#     sun.compute(obs)
#     return np.degrees(sun.az), 90.0 - np.degrees(sun.alt), sun.earth_distance


def get_point():
    A = []
    for i in range(len(vza)):
        for j in range(len(sza)):
            A.append(vza[i])
            A.append(sza[j])
    point = np.array(A).reshape(17 * 17, 2)
    return point


def griddata_inter(X1, X2, X3, a, b, c, d):
    X1_new_inter = []
    X2_new_inter = []
    X3_new_inter = []

    X1_inter = X1[a, b, c, :, :, d].reshape(17 * 17, 1)
    X2_inter = X2[a, b, c, :, :, d].reshape(17 * 17, 1)
    X3_inter = X3[a, b, c, :, :, d].reshape(17 * 17, 1)

    X1_new = griddata(point, X1_inter, (xi, yi), method='cubic')
    X2_new = griddata(point, X2_inter, (xi, yi), method='cubic')
    X3_new = griddata(point, X3_inter, (xi, yi), method='nearest')

    X1_new_inter.append(X1_new)
    X2_new_inter.append(X2_new)
    X3_new_inter.append(X3_new)

    del X1_inter, X2_inter, X3_inter, X1_new, X2_new, X3_new
    return X1_new_inter, X2_new_inter, X3_new_inter


###############################################
def ATMO_time(HH):
    if int(HH) % 3 == 0:
        return HH
    elif (int(HH) - 1) % 3 == 0:
        return str(int(HH) - 1).zfill(2)
    elif int(HH) == 23:
        return str(21).zfill(2)
    else:
        return str(int(HH) + 1).zfill(2)


######################################################


def calculate_6s_band3(i):
    WV_input = WV[i, :]
    OZ_input = OZ[i, :]
    AOT550_input = AOT550[i, :]
    RAA_input = RAA[i, :]
    SZA_input = Solar_zM[i, :]
    view_zM_input = view_zM[i, :]
    xi = np.array([
        WV_input, OZ_input, AOT550_input, RAA_input, SZA_input, view_zM_input
    ])
    xi = xi.T
    xa = fn1(xi)
    xb = fn2(xi)
    xc = fn3(xi)
    y = xa * data[i, :] - xb
    SR = y / (1 + xc * y)
    return SR


with open('view_zM_JAPAN_05.dat', 'rb') as fp:
    view_zM = np.fromstring(fp.read()).reshape(6000, 6000)
with open('view_aM_JAPAN_05.dat', 'rb') as fp:
    view_aM = np.fromstring(fp.read()).reshape(6000, 6000)

###########################################################

# read LUT
outfile1 = "01_band3.csv"
outfile2 = "02_band3.csv"
outfile3 = "03_band3.csv"
X1 = np.loadtxt(outfile1, delimiter=",")
X2 = np.loadtxt(outfile2, delimiter=",")
X3 = np.loadtxt(outfile3, delimiter=",")

# reshape LUT
X1_reshape = X1.reshape(8, 5, 12, 17, 17, 19)  # water ozone AOT sza vza vaa
X2_reshape = X2.reshape(8, 5, 12, 17, 17, 19)
X3_reshape = X3.reshape(8, 5, 12, 17, 17, 19)
del X1, X2, X3

# SZA,SAZ,VZA interpolation
point = get_point()
xi, yi = np.ogrid[0:80:161j, 0:80:161j]  # 分别等分161份: xi为(1, 161) yi为(161, 1)
# 第一次插值
output = Parallel(n_jobs=-1)(
    delayed(griddata_inter)(X1_reshape, X2_reshape, X3_reshape, a, b, c, d)
    for a in range(len(water)) for b in range(len(ozone))
    for c in range(len(AOT)) for d in range(len(raa)))

X1_new_inter_reshape = np.array(output)[:, 0].reshape(8, 5, 12, 19, 161, 161)
X2_new_inter_reshape = np.array(output)[:, 1].reshape(8, 5, 12, 19, 161, 161)
X3_new_inter_reshape = np.array(output)[:, 2].reshape(8, 5, 12, 19, 161, 161)

del X1_reshape, X2_reshape, X3_reshape, output

# 第二次插值
sza_new = np.linspace(0, 80, 161)
vza_new = np.linspace(0, 80, 161)
# points=(water,ozone,AOT,raa,sza_new,vza_new)

fn1 = RegularGridInterpolator((water, ozone, AOT, raa, sza_new, vza_new),
                              X1_new_inter_reshape,
                              bounds_error=False,
                              fill_value=np.nan)
fn2 = RegularGridInterpolator((water, ozone, AOT, raa, sza_new, vza_new),
                              X2_new_inter_reshape,
                              bounds_error=False,
                              fill_value=np.nan)
fn3 = RegularGridInterpolator((water, ozone, AOT, raa, sza_new, vza_new),
                              X3_new_inter_reshape,
                              bounds_error=False,
                              fill_value=np.nan)

lat_x = np.linspace(50, 20, 6000)
lon_y = np.linspace(120, 150, 6000)

BAND = Hi8_band()

# 大气校正部分？

for k in range(len(MM)):
    for m in range(len(DD)):
        for i in range(len(HH)):
            for j in range(len(MIN)):
                start_time = T.time()
                make_folder_time_s = T.time()
                date = YYYY + MM[k] + DD[m] + HH[i] + MIN[j]
                time = date[-4:]
                print("start processing {}".format(date))
                # make dir
                folder_original = os.getcwd() + '/' + date + '_original'
                folder_AC = '/media/liwei/Data/AHI_AC_RESULT/' + date + '_AC'

                mkdir(folder_original)
                mkdir(folder_AC)
                make_folder_time_e = T.time()
                make_folder_time = make_folder_time_e - make_folder_time_s

                download_AOT_time_s = T.time()
                download_AOT(YYYY, MM[k], DD[m], HH[i], folder_original)
                download_AOT_time_e = T.time()
                download_AOT_time = download_AOT_time_e - download_AOT_time_s

                # 读取大气条件数据
                ATMOS_data_s = T.time()

                ds_oz_wv = xr.open_dataset(YYYY + MM[k] + ATMO_time(HH[i]) +
                                           '.nc')

                oz = ds_oz_wv['gtco3'][int(DD[m]) - 1, :, :]
                OZ = oz.interp(longitude=lon_y,
                               latitude=lat_x,
                               method="nearest")  # 插值
                OZ = OZ.values
                wv = ds_oz_wv['tcwv'][int(DD[m]) - 1, :, :]
                WV = wv.interp(longitude=lon_y,
                               latitude=lat_x,
                               method="nearest")
                WV = WV.values
                ds = xr.open_dataset('{}_original'.format(date) + '/H08_' +
                                     YYYY + MM[k] + DD[m] + '_' + HH[i] +
                                     '00_MSARPbet_ANL.00960_00480.nc')
                aot550 = ds['od550aer']
                AOT550 = aot550.interp(lon=lon_y, lat=lat_x, method="nearest")
                AOT550 = AOT550.values
                del oz, wv, aot550, ds_oz_wv, ds
                ATMOS_data_e = T.time()
                ATMOS_data_time = ATMOS_data_e - ATMOS_data_s
                print("OZ,AOT,WV finish")

                Hi_download_s = T.time()
                download_H8data(date)
                Hi_download_e = T.time()
                Hi_download_time = Hi_download_e - Hi_download_s

                print("data download finsih")

                if os.path.exists('{}_original'.format(date) + '/' + date +
                                  '.ext.01.fld.geoss'):
                    Hi_open_convert_s = T.time()
                    with open(
                            '{}_original'.format(date) + '/' + date +
                            '.ext.01.fld.geoss', 'rb') as fp:
                        data = np.fromstring(fp.read(), dtype='>u2').reshape(
                            24000, 24000)
                        data = data[2000:8000, 7000:13000]
                        data = DN2tbb(data)
                        data = data / 100
                    Hi_open_convert_e = T.time()
                    Hi_open_convert_time = Hi_open_convert_e - Hi_open_convert_s
                    print("data reading finish")

                    solar_s = T.time()

                    with open(
                            '/media/liwei/Data/Solar_zenith_angle/solar_zM_' +
                            date + '.dat', 'rb') as fp:
                        Solar_zM = np.fromstring(fp.read()).reshape(3000, 3000)
                    with open(
                            '/media/liwei/Data/Solar_azimuth_angle/solar_aM_' +
                            date + '.dat', 'rb') as fp:
                        Solar_aM = np.fromstring(fp.read()).reshape(3000, 3000)

                    Solar_aM = cv2.resize(np.array(Solar_aM), (6000, 6000),
                                          interpolation=cv2.INTER_NEAREST)
                    Solar_zM = cv2.resize(np.array(Solar_zM), (6000, 6000),
                                          interpolation=cv2.INTER_NEAREST)

                    RAA = abs(Solar_aM - view_aM)
                    RAA[RAA > 180] = 360 - RAA[RAA > 180]
                    solar_e = T.time()
                    solar_time = solar_e - solar_s
                    print("SZA,SAZ finish")
                    # 开始大气校正
                    # Atmosphere data Unit conversion
                    ATMOS_unit_s = T.time()
                    WV = WV / 10
                    OZ = OZ * 46.6975764  # 单位转换

                    OZ[OZ >= max(ozone)] = max(ozone) - (1 / 10000)  # 规范最大最小值
                    OZ[OZ <= min(ozone)] = min(ozone) + (1 / 10000)

                    WV[WV >= max(water)] = max(water) - (1 / 10000)
                    WV[WV <= min(water)] = min(water) + (1 / 10000)
                    AOT550[AOT550 >= max(AOT)] = max(AOT) - (1 / 10000)
                    AOT550[AOT550 <= min(AOT)] = min(AOT) + (1 / 10000)
                    ATMOS_unit_e = T.time()
                    ATMOS_unit_time = ATMOS_unit_e - ATMOS_unit_s
                    LUT_s = T.time()
                    SR = Parallel(n_jobs=-1)(delayed(calculate_6s_band3)(i)
                                             for i in range(6000))
                    LUT_e = T.time()
                    LUT_time = LUT_e - LUT_s
                    end_time = T.time()
                    TIME = end_time - start_time
                    print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(
                        TIME, TIME / 60, TIME / 3600))
                    SR = np.array(SR).reshape(6000, 6000)
                    SR_file = open(folder_AC + '/' + date + '_b03.dat', 'wb')
                    SR.astype('f4').tofile(SR_file)
                    SR_file.close()
                    remove_original_file(folder_original)
                    print("delete file finish")
                else:
                    print("file no exists")
                    pass
