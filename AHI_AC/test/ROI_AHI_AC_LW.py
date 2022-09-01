import numpy as np
import time as T
from joblib import Parallel, delayed
from scipy.interpolate import RegularGridInterpolator
import os
import datetime
import cv2
from ftplib import FTP
import xarray as xr
import subprocess
import datetime as dt

target = '/data01/people/liwei/Data/AHI_Validation/'

SZA_PATH = '/data01/GEO/INPUT/ANGLE/Solar_Zenith_Angle_u2/'
SAA_PATH = '/data01/GEO/INPUT/ANGLE/Solar_Azimuth_Angle_u2/'
VZA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Zenith_Angle/AHI_VZA_10.dat'
VAA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Azimuth_Angle/AHI_VAA_10.dat'

LUT_PATH = '/data01/GEO/INPUT/LUT/'
CAMS_PATH = '/data01/GEO/INPUT/ATMOSPHERE/'
DN_PATH = '/data01/GEO/INPUT/'
CAMS_AERO_PATH = '/data01/GEO/INPUT/AEROSOL_TYPE/'
AL_PATH = '/data01/GEO/INPUT/ELEVATION_GEO/AHI/MERIT_DEM_AHI_10km.dat'

sza = np.linspace(0, 80, 17)
vza = np.linspace(0, 80, 17)
water = np.linspace(0, 7, 8)
ozone = np.linspace(0.2, 0.4, 5)
AOT = np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0])
raa = np.linspace(0, 180, 19)
al = np.linspace(0, 8, 5)
aero_type = np.array([0, 1])


class AHI_angle:

    def __init__(self, date):
        self.date = date

    def read_angle_data(self):

        AHI_date = self.date[4:11]

        sza_file_name = 'AHI_SZA_2020{}5.dat'.format(AHI_date)
        saa_file_name = 'AHI_SAA_2020{}5.dat'.format(AHI_date)

        with open(SZA_PATH + sza_file_name, 'rb') as fp:
            AHI_SZA = np.frombuffer(fp.read(), dtype='u2').reshape(3000, 3000)[row_u_4KM:row_u_4KM + row_4KM, col_l_4KM:col_l_4KM + col_4KM] / 100
            AHI_SZA = cv2.resize(np.array(AHI_SZA, dtype='float64'), (row_AHI, col_AHI), interpolation=cv2.INTER_NEAREST)

        with open(SAA_PATH + saa_file_name, 'rb') as fp:
            AHI_SAA = np.frombuffer(fp.read(), dtype='u2').reshape(3000, 3000)[row_u_4KM:row_u_4KM + row_4KM, col_l_4KM:col_l_4KM + col_4KM] / 100
            AHI_SAA = cv2.resize(np.array(AHI_SAA, dtype='float64'), (row_AHI, col_AHI), interpolation=cv2.INTER_NEAREST)

        return AHI_SZA, AHI_SAA


class CAMS_data:

    def __init__(self, YYYY, MM, DD, HH, MIN):
        self.YYYY = YYYY
        self.MM = MM
        self.DD = DD
        self.HH = HH
        self.MIN = MIN

    def read_CAMS(self, lat, lon):

        dtime = dt.datetime(int(self.YYYY), int(self.MM), int(self.DD), int(self.HH), int(self.MIN) + 5)
        ds = xr.open_dataset(CAMS_PATH + self.YYYY + self.MM + self.DD + '.nc')
        ds = ds.interp(time=dtime, method='linear')
        ds = ds.interp(longitude=lon, latitude=lat, method="nearest")

        OZ = ds['gtco3'].values
        WV = ds['tcwv'].values
        AOT550 = ds['aod550'].values
        #         Atmosphere data Unit conversion
        WV = WV / 10
        OZ = OZ * 46.6975764

        #         Processing water vapor and ozone max and min
        OZ[OZ >= max(ozone)] = max(ozone) - (1 / 10000)
        OZ[OZ <= min(ozone)] = min(ozone) + (1 / 10000)
        WV[WV >= max(water)] = max(water) - (1 / 10000)
        WV[WV <= min(water)] = min(water) + (1 / 10000)
        AOT550[AOT550 >= max(AOT)] = max(AOT) - (1 / 10000)
        AOT550[AOT550 <= min(AOT)] = min(AOT) + (1 / 10000)

        return np.array(OZ).reshape(row_AHI, col_AHI), np.array(WV).reshape(row_AHI, col_AHI), np.array(AOT550).reshape(row_AHI, col_AHI)

    def read_CAMS_AERO(self, lat ,lon):

        dtime = dt.datetime(int(self.YYYY), int(self.MM), int(self.DD), int(self.HH), int(self.MIN) + 5)

        ds = xr.open_dataset(CAMS_AERO_PATH + self.YYYY + self.MM + self.DD + '.nc')
        ds = ds.interp(time=dtime, method='linear')
        ds = ds.interp(longitude=lon, latitude=lat, method="nearest")

        bc = ds['bcaod550'].values
        du = ds['duaod550'].values
        om = ds['omaod550'].values
        ss = ds['ssaod550'].values
        su = ds['suaod550'].values

        DL_6S = np.array(du)
        SL_6S = np.array(su) + np.array(bc)
        OC_6S = np.array(ss)
        WS_6S = np.array(om)

        Total = DL_6S + SL_6S + OC_6S + WS_6S

        precent_DL_6S = DL_6S / Total
        precent_SL_6S = SL_6S / Total
        precent_OC_6S = OC_6S / Total
        precent_WS_6S = WS_6S / Total
        P = np.dstack((precent_DL_6S, precent_WS_6S, precent_OC_6S, precent_SL_6S))
        Aerosol_type = np.where(np.amax(P, axis=2) == precent_OC_6S, 1, 0)

        return Aerosol_type


class LUT_interpolation:

    def __init__(self, LUT_PATH):
        self.LUT_path = LUT_PATH

    def LUT_interpolation(self):
        X1 = np.loadtxt(self.LUT_path + "01_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        X2 = np.loadtxt(self.LUT_path + "02_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        X3 = np.loadtxt(self.LUT_path + "03_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        # return X1, X2, X3

        fn1 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X1, bounds_error=False, fill_value=np.nan)
        fn2 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X2, bounds_error=False, fill_value=np.nan)
        fn3 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X3, bounds_error=False, fill_value=np.nan)
        return fn1, fn2, fn3


fn1, fn2, fn3 = LUT_interpolation(LUT_PATH).LUT_interpolation()


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def Time_split(time):
    YYYY = time.strftime('%Y')
    MM = time.strftime('%m')
    DD = time.strftime('%d')
    HH = time.strftime('%H')
    MIN = time.strftime('%M')
    date = YYYY + MM + DD + HH + MIN
    return YYYY, MM, DD, HH, MIN, date


def calculate_6s_band4(i):
    Aero_input = Aerosol_type[i, :]
    WV_input = WV[i, :]
    AOT550_input = AOT550[i, :]
    RAA_input = RAA[i, :]
    SZA_input = AHI_SZA[i, :]
    VZA_input = AHI_VZA[i, :]
    AL_input = AHI_AL[i, :]
    xi = np.array([Aero_input, WV_input, AOT550_input, AL_input, SZA_input, VZA_input, RAA_input])
    xi = xi.T
    xa = fn1(xi)
    xb = fn2(xi)
    xc = fn3(xi)
    y = xa * AHI_data[i, :] - xb
    SR = y / (1 + xc * y)
    return SR


def DN2TBB(data):
    LUT = np.loadtxt(DN_PATH + 'count2tbb_v102/vis.03')
    return LUT[data, 1]


# main()
YYYY = '2020'

site_name = 'ROI 1'
site = [16.75, 96.5]

# site_name = 'ROI 3'
# site = [27,96.5] # ROI 3

# site_name = 'ROI 6'
# site = [46,114]

# site_name = 'ROI 8'
# site = [42.990,107.043]

# site_name = 'ROI 9'
# site = [41.7,104.6]

# site_name = 'ROI 10'
# site = [49.6,119.4]

# site_name = 'ROI 11'
# site = [40.74,102.48]

# site_name = 'ROI 12'
# site = [43.72,115.59]

res = 0.01

u_lat, d_lat = site[0] + 0.06, site[0] - 0.06
l_lon, r_lon = site[1] - 0.06, site[1] + 0.06

row_AHI = round((u_lat - d_lat) / res)
col_AHI = round((r_lon - l_lon) / res)

row_u_AHI = round((60 - u_lat) / res)
col_l_AHI = round((l_lon - 85) / res)

lat_x = np.linspace(u_lat, d_lat + res, row_AHI)
lon_y = np.linspace(l_lon, r_lon - res, col_AHI)

row_4KM = round((u_lat - d_lat) / 0.04)
col_4KM = round((r_lon - l_lon) / 0.04)

row_u_4KM = round((60 - u_lat) / 0.04)
col_l_4KM = round((l_lon - 85) / 0.04)

with open(VZA_PATH, 'rb') as fp:
    AHI_VZA = np.frombuffer(fp.read(), dtype='u2').reshape(12000, 12000)[row_u_AHI:row_u_AHI + row_AHI, col_l_AHI:col_l_AHI + col_AHI]
    AHI_VZA = AHI_VZA / 100
with open(VAA_PATH, 'rb') as fp:
    AHI_VAA = np.frombuffer(fp.read(), dtype='u2').reshape(12000, 12000)[row_u_AHI:row_u_AHI + row_AHI, col_l_AHI:col_l_AHI + col_AHI]
    AHI_VAA = AHI_VAA / 100
with open(AL_PATH, 'rb') as fp:
    AHI_AL = np.frombuffer(fp.read(), dtype='u2').reshape(12000, 12000)[row_u_AHI:row_u_AHI + row_AHI, col_l_AHI:col_l_AHI + col_AHI]
    AHI_AL = AHI_AL / 1000
    AHI_AL[AHI_AL >= max(al)] = max(al) - (1 / 10000)
    AHI_AL[AHI_AL <= min(al)] = min(al) + (1 / 10000)

d_ahi = []
ws = ''

for date in d_ahi:
    ahi_data_time = date
    ahi_data_folder1 = ahi_data_time[:6]
    ahi_data_folder2 = ahi_data_folder1[:8]
    ahi_saa_filename = ahi_data_time + '.vis.03.fld.geoss.bz2'
    ahi_saa_path = '/gridded/FD/V20151105/' + ahi_data_folder1 + '/VIS/' + ahi_saa_filename
    ftp_dl_url = 'ftp://hmwr829gr.cr.chiba-u.ac.jp' + ahi_saa_path
    print(ftp_dl_url)
    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()
    local_file = ws + '/' + ahi_saa_filename
    with open(local_file, 'wb') as f:
        ftp.retrbinary('RETR ' + ahi_saa_path, f.write, 1024 * 1024)
    p = subprocess.Popen('lbzip2 -d {}'.format(local_file), shell=True)
    p.communicate()

ftp.close()

for date_start in d_ahi:
    start_time = T.time()
    date_time_now = dt.datetime.strptime(date_start, "%Y-%m-%d %H:%M")
    # date_dl_str = date_time_now.strftime("%Y-%m-%d %H:%M" )
    YYYY, MM, DD, HH, MIN, date = Time_split(date_time_now)
    print("start processing {}".format(date))
    # make dir
    folder_AC = target + date + '_AC/'
    mkdir(folder_AC)
    # Download AHI
    with open(ws + '/{}.vis.03.fld.geoss'.format(date), 'rb') as fp:
        data = np.frombuffer(fp.read(), dtype='>u2').reshape(12000, 12000)
        data = DN2TBB(data)
        data = data / 100

    AHI_data = data[row_u_AHI:row_u_AHI + row_AHI, col_l_AHI:col_l_AHI + col_AHI]

    # Solar angle
    print('Start reading Angle data')
    AHI_SZA, AHI_SAA = AHI_angle(date).read_angle_data()

    RAA = abs(AHI_SAA - AHI_VAA)
    RAA[RAA > 180] = 360 - RAA[RAA > 180]

    print('Angle data read finished')
    print('Start reading Atmospheric data')
    OZ, WV, AOT550 = CAMS_data(YYYY, MM, DD, HH, MIN).read_CAMS(lat_x, lon_y)
    Aerosol_type = CAMS_data(YYYY, MM, DD, HH, MIN).read_CAMS_AERO(lat_x, lon_y)
    print('Atmospheric data read finished')

    SR = Parallel(n_jobs=-1)(delayed(calculate_6s_band4)(i) for i in range(row_AHI))
    # Save file and remove download input data
    SR = np.array(SR).reshape(row_AHI, col_AHI)

    
    SR_file = open(folder_AC + '/' + date + '_' + site_name + '_b04.dat', 'wb')
    SR.astype('f4').tofile(SR_file)
    SR_file.close()
    #                 remove_original_file(folder_original)
    end_time = T.time()
    TIME = end_time - start_time
    print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(TIME, TIME / 60, TIME / 3600))
    print("delete file finish")