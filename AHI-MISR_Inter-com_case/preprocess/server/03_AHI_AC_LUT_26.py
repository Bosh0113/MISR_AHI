import numpy as np
import time as T
from joblib import Parallel, delayed
from scipy.interpolate import RegularGridInterpolator
import os
import datetime
import cv2
import xarray as xr
import subprocess
import datetime as dt
import shutil

WORK_SPACE = os.getcwd()
# AC temp workspace
TEMP_FOLDER = '/data01/people/beichen/workspace/20230215/AC_temp'

SZA_PATH = '/data01/GEO/INPUT/ANGLE/Solar_Zenith_Angle_u2/'
SAA_PATH = '/data01/GEO/INPUT/ANGLE/Solar_Azimuth_Angle_u2/'
VZA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Zenith_Angle/AHI_VZA_10.dat'
VAA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Azimuth_Angle/AHI_VAA_10.dat'

LUT_PATH = '/data01/GEO/INPUT/LUT/'
CAMS_PATH = '/data01/GEO/INPUT/ATMOSPHERE/'
DN_PATH = '/data01/GEO/INPUT/'
CAMS_AERO_PATH = '/data01/GEO/INPUT/AEROSOL_TYPE/'
AL_PATH = '/data01/GEO/INPUT/ELEVATION_GEO/AHI/MERIT_DEM_AHI_10km.dat'

ROI_SIZE = 0.02
ROI_OFFSET_DIS = ROI_SIZE/2

sza = np.linspace(0, 80, 17)
vza = np.linspace(0, 80, 17)
water = np.linspace(0, 7, 8)
ozone = np.linspace(0.2, 0.4, 5)
AOT = np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0])
raa = np.linspace(0, 180, 19)
al = np.linspace(0, 8, 5)
aero_type = np.array([0, 1])

AHI_RESOLUTION = 0.01
AHI_DATA_RESOLUTION = 0.01  # degree: band3 0.005, band4 0.01
PIXEL_NUM = 12000
AHI_DATA_PIXEL_NUM = 12000  # band3: 12000, band4 24000
FN_1 = None
FN_2 = None
FN_3 = None


class AHI_angle:

    def __init__(self, date):
        self.date = date

    def read_angle_data(self, r_extent):
        r_ullat = r_extent[0]
        r_ullon = r_extent[1]
        r_lrlat = r_extent[2]
        r_lrlon = r_extent[3]

        AHI_date = self.date[4:11]

        sza_file_name = 'AHI_SZA_2020{}5.dat'.format(AHI_date)
        saa_file_name = 'AHI_SAA_2020{}5.dat'.format(AHI_date)

        ahi_lats = np.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
        ahi_lons = np.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)

        with open(SZA_PATH + sza_file_name, 'rb') as fp:
            AHI_SZA = np.frombuffer(fp.read(), dtype='u2').reshape(3000, 3000)
            AHI_SZA = cv2.resize(np.array(AHI_SZA, dtype='float64'), (PIXEL_NUM, PIXEL_NUM), interpolation=cv2.INTER_NEAREST)
            AHI_SZA = AHI_SZA[find_nearest_index(ahi_lats, r_ullat):find_nearest_index(ahi_lats, r_lrlat) + 1, find_nearest_index(ahi_lons, r_ullon):find_nearest_index(ahi_lons, r_lrlon) + 1] / 100

        with open(SAA_PATH + saa_file_name, 'rb') as fp:
            AHI_SAA = np.frombuffer(fp.read(), dtype='u2').reshape(3000, 3000)
            AHI_SAA = cv2.resize(np.array(AHI_SAA, dtype='float64'), (PIXEL_NUM, PIXEL_NUM), interpolation=cv2.INTER_NEAREST)
            AHI_SAA = AHI_SAA[find_nearest_index(ahi_lats, r_ullat):find_nearest_index(ahi_lats, r_lrlat) + 1, find_nearest_index(ahi_lons, r_ullon):find_nearest_index(ahi_lons, r_lrlon) + 1] / 100

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

    def read_CAMS_AERO(self, lat, lon):

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

    def LUT_interpolation_band4(self):
        X1 = np.loadtxt(self.LUT_path + "01_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        X2 = np.loadtxt(self.LUT_path + "02_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        X3 = np.loadtxt(self.LUT_path + "03_band4.csv", delimiter=",").reshape(2, 8, 12, 5, 17, 17, 19)
        # return X1, X2, X3

        fn1 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X1, bounds_error=False, fill_value=np.nan)
        fn2 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X2, bounds_error=False, fill_value=np.nan)
        fn3 = RegularGridInterpolator((aero_type, water, AOT, al, sza, vza, raa), X3, bounds_error=False, fill_value=np.nan)
        return fn1, fn2, fn3

    def LUT_interpolation_band3(self):
        X1 = np.loadtxt(self.LUT_path + "01_band3.csv", delimiter=",").reshape(2, 8, 5, 12, 5, 17, 17, 19)
        X2 = np.loadtxt(self.LUT_path + "02_band3.csv", delimiter=",").reshape(2, 8, 5, 12, 5, 17, 17, 19)
        X3 = np.loadtxt(self.LUT_path + "03_band3.csv", delimiter=",").reshape(2, 8, 5, 12, 5, 17, 17, 19)
        # return X1, X2, X3

        fn1 = RegularGridInterpolator((aero_type, water, ozone, AOT, al, sza, vza, raa), X1, bounds_error=False, fill_value=np.nan)
        fn2 = RegularGridInterpolator((aero_type, water, ozone, AOT, al, sza, vza, raa), X2, bounds_error=False, fill_value=np.nan)
        fn3 = RegularGridInterpolator((aero_type, water, ozone, AOT, al, sza, vza, raa), X3, bounds_error=False, fill_value=np.nan)
        return fn1, fn2, fn3


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
    xa = FN_1(xi)
    xb = FN_2(xi)
    xc = FN_3(xi)
    ahi_toa = AHI_data[i, :]
    y = xa * ahi_toa - xb
    SR = y / (1 + xc * y)
    return (ahi_toa, xa, xb, xc, SR)


def calculate_6s_band3(i):
    Aero_input = Aerosol_type[i, :]
    WV_input = WV[i, :]
    OZ_input = OZ[i, :]
    AOT550_input = AOT550[i, :]
    RAA_input = RAA[i, :]
    SZA_input = AHI_SZA[i, :]
    VZA_input = AHI_VZA[i, :]
    AL_input = AHI_AL[i, :]
    xi = np.array([Aero_input, WV_input, OZ_input, AOT550_input, AL_input, SZA_input, VZA_input, RAA_input])
    xi = xi.T
    xa = FN_1(xi)
    xb = FN_2(xi)
    xc = FN_3(xi)
    ahi_toa = AHI_data[i, :]
    y = xa * ahi_toa - xb
    SR = y / (1 + xc * y)
    return (ahi_toa, xa, xb, xc, SR)


def DN2TBB_band3(data):
    LUT = np.loadtxt(DN_PATH + 'count2tbb_v102/ext.01')
    return LUT[data, 1]


def DN2TBB_band4(data):
    LUT = np.loadtxt(DN_PATH + 'count2tbb_v102/vis.03')
    return LUT[data, 1]


def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


# main()
if __name__ == "__main__":
    FN_1_band3, FN_2_band3, FN_3_band3 = LUT_interpolation(LUT_PATH).LUT_interpolation_band3()
    FN_1_band4, FN_2_band4, FN_3_band4 = LUT_interpolation(LUT_PATH).LUT_interpolation_band4()
    
    folder_l1_list = ['26']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                roi_infos = roi_folder.split('_')
                roi_lc_idx = roi_infos[1]
                if roi_lc_idx not in ['0', '13', '15']:   # water urban snow
                    roi_name = roi_folder
                    roi_c_lon = float(roi_infos[3])
                    riu_c_lat = float(roi_infos[2])
                    # roi_extent: (ullat, ullon, lrlat, lrlon)
                    roi_extent = [riu_c_lat + ROI_OFFSET_DIS, roi_c_lon - ROI_OFFSET_DIS, riu_c_lat - ROI_OFFSET_DIS, roi_c_lon + ROI_OFFSET_DIS]
                    valuable_record_npy = os.path.join(roi_folder_path, roi_name + '_4AC_record.npy')
                    if os.path.exists(valuable_record_npy):
                        valuable_record = np.load(valuable_record_npy, allow_pickle=True)
                        ahi_obs_times = []
                        for valuable_record_item in valuable_record:
                            ahi_obs_time = valuable_record_item[4]
                            ahi_obs_times.append(ahi_obs_time)

                            for band_name in ['band3', 'band4']:

                                for date in ahi_obs_times:
                                    try:
                                        ahi_data_time = date
                                        ahi_data_folder1 = ahi_data_time[:6]
                                        ahi_data_folder2 = ahi_data_folder1[:8]
                                        ahi_saa_path = ''
                                        if band_name == 'band3':
                                            ahi_saa_filename = ahi_data_time + '.ext.01.fld.geoss.bz2'
                                            ahi_saa_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/EXT/' + ahi_saa_filename
                                        elif band_name == 'band4':
                                            ahi_saa_filename = ahi_data_time + '.vis.03.fld.geoss.bz2'
                                            ahi_saa_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/VIS/' + ahi_saa_filename

                                        ahi_server_path = '/data01/people/beichen/data/AHI_V2019_2017010120191231/hmwr829gr.cr.chiba-u.ac.jp' + ahi_saa_path

                                        if not os.path.exists(TEMP_FOLDER):
                                            os.makedirs(TEMP_FOLDER)
                                        local_file = TEMP_FOLDER + '/' + ahi_saa_filename
                                        if not os.path.exists(local_file[:-4]):
                                            shutil.copy(ahi_server_path, local_file)
                                            p = subprocess.Popen('lbzip2 -d {}'.format(local_file), shell=True)
                                            p.communicate()
                                    except Exception as e:
                                        print(e)

                                if band_name == 'band3':
                                    AHI_DATA_RESOLUTION = 0.005
                                    AHI_DATA_PIXEL_NUM = 24000
                                    FN_1 = FN_1_band3
                                    FN_2 = FN_2_band3
                                    FN_3 = FN_3_band3
                                elif band_name == 'band4':
                                    AHI_DATA_RESOLUTION = 0.01
                                    AHI_DATA_PIXEL_NUM = 12000
                                    FN_1 = FN_1_band4
                                    FN_2 = FN_2_band4
                                    FN_3 = FN_3_band4

                                roi_ullat = roi_extent[0]
                                roi_ullon = roi_extent[1]
                                roi_lrlat = roi_extent[2]
                                roi_lrlon = roi_extent[3]
                                ahi_lats = np.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
                                ahi_lons = np.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)
                                n_lats = ahi_lats[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1]
                                n_lons = ahi_lons[find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
                                row_AHI = len(n_lats)
                                col_AHI = len(n_lons)

                                VZA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Zenith_Angle/AHI_VZA_10.dat'
                                VAA_PATH = '/data01/GEO/INPUT/ANGLE/Viewer_Azimuth_Angle/AHI_VAA_10.dat'
                                AL_PATH = '/data01/GEO/INPUT/ELEVATION_GEO/AHI/MERIT_DEM_AHI_10km.dat'

                                with open(VZA_PATH, 'rb') as fp:
                                    AHI_VZA = np.frombuffer(fp.read(), dtype='u2').reshape(PIXEL_NUM, PIXEL_NUM)[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1,
                                                                                                                find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
                                    AHI_VZA = AHI_VZA / 100
                                with open(VAA_PATH, 'rb') as fp:
                                    AHI_VAA = np.frombuffer(fp.read(), dtype='u2').reshape(PIXEL_NUM, PIXEL_NUM)[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1,
                                                                                                                find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
                                    AHI_VAA = AHI_VAA / 100
                                with open(AL_PATH, 'rb') as fp:
                                    AHI_AL = np.frombuffer(fp.read(), dtype='u2').reshape(PIXEL_NUM, PIXEL_NUM)[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1,
                                                                                                                find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
                                    AHI_AL = AHI_AL / 1000
                                    AHI_AL[AHI_AL >= max(al)] = max(al) - (1 / 10000)
                                    AHI_AL[AHI_AL <= min(al)] = min(al) + (1 / 10000)

                                for ahi_obs_t in ahi_obs_times:
                                    start_time = T.time()
                                    ahi_obs_t_obj = datetime.datetime.strptime(ahi_obs_t, "%Y%m%d%H%M")
                                    YYYY, MM, DD, HH, MIN, date = Time_split(ahi_obs_t_obj)
                                    print("Start processing {}".format(date))
                                    # Download AHI
                                    file_suffix = ''
                                    if band_name == 'band3':
                                        file_suffix = '/{}.ext.01.fld.geoss'
                                    elif band_name == 'band4':
                                        file_suffix = '/{}.vis.03.fld.geoss'
                                    ahi_data_filename = TEMP_FOLDER + file_suffix.format(date)
                                    if os.path.exists(ahi_data_filename):
                                        data = None
                                        with open(ahi_data_filename, 'rb') as fp:
                                            data = np.frombuffer(fp.read(), dtype='>u2').reshape(AHI_DATA_PIXEL_NUM, AHI_DATA_PIXEL_NUM)
                                            if band_name == 'band3':
                                                data = DN2TBB_band3(data)
                                            elif band_name == 'band4':
                                                data = DN2TBB_band4(data)
                                            data = data / 100

                                        AHI_data = None
                                        if band_name == 'band3':
                                            ahi_lats_3 = np.arange(60. - AHI_DATA_RESOLUTION / 2, -60, -AHI_DATA_RESOLUTION)
                                            ahi_lons_3 = np.arange(85. + AHI_DATA_RESOLUTION / 2, 205, AHI_DATA_RESOLUTION)
                                            ex_ds = xr.Dataset(
                                                data_vars={
                                                    "values": (("latitude", "longitude"), data),
                                                },
                                                coords={
                                                    "latitude": ahi_lats_3,
                                                    "longitude": ahi_lons_3
                                                },
                                            )
                                            n_ex_ds = ex_ds.interp(longitude=n_lons, latitude=n_lats, method="linear", kwargs={"fill_value": "extrapolate"})
                                            AHI_data = n_ex_ds['values']
                                        else:
                                            AHI_data = data[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1, find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]

                                        # Solar angle
                                        print('Start reading Angle data')
                                        AHI_SZA, AHI_SAA = AHI_angle(date).read_angle_data(roi_extent)

                                        RAA = abs(AHI_SAA - AHI_VAA)
                                        RAA[RAA > 180] = 360 - RAA[RAA > 180]

                                        print('Angle data read finished')
                                        print('Start reading Atmospheric data')
                                        OZ, WV, AOT550 = CAMS_data(YYYY, MM, DD, HH, MIN).read_CAMS(n_lats, n_lons)
                                        Aerosol_type = CAMS_data(YYYY, MM, DD, HH, MIN).read_CAMS_AERO(n_lats, n_lons)
                                        print('Atmospheric data read finished')

                                        results = None
                                        if band_name == 'band3':
                                            results = Parallel(n_jobs=5)(delayed(calculate_6s_band3)(i) for i in range(row_AHI))
                                        elif band_name == 'band4':
                                            results = Parallel(n_jobs=5)(delayed(calculate_6s_band4)(i) for i in range(row_AHI))
                                        X = np.array(results)
                                        AHI_TOA = X[:, 0]
                                        Xa = X[:, 1]
                                        Xb = X[:, 2]
                                        Xc = X[:, 3]
                                        SR = X[:, 4]
                                        # Save file and remove download input data
                                        ahi_data_roi = np.array(AHI_TOA).reshape(row_AHI, col_AHI)
                                        ac_roi_xa = np.array(Xa).reshape(row_AHI, col_AHI)
                                        ac_roi_xb = np.array(Xb).reshape(row_AHI, col_AHI)
                                        ac_roi_xc = np.array(Xc).reshape(row_AHI, col_AHI)
                                        roi_ahi_sr = np.array(SR).reshape(row_AHI, col_AHI)

                                        # record AC SR
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

                                        record_info = [{
                                            'obs_time': ahi_obs_t,
                                            'roi_lats': n_lats,
                                            'roi_lons': n_lons,
                                            'roi_vza': AHI_VZA,
                                            'roi_sza': AHI_SZA,
                                            'roi_raa': RAA,
                                            'roi_aot': AOT550,
                                            'roi_aero_type': Aerosol_type,
                                            'roi_oz': OZ,
                                            'roi_wv': WV,
                                            'roi_ac_fa': [],
                                            'roi_ac_xa': ac_roi_xa,
                                            'roi_ac_xb': ac_roi_xb,
                                            'roi_ac_xc': ac_roi_xc,
                                            'roi_ahi_data': ahi_data_roi,
                                            'roi_ahi_sr': roi_ahi_sr,
                                        }]

                                        folder_path = os.path.join(roi_folder_path, 'AHI_AC_PARAMETER')
                                        if not os.path.exists(folder_path):
                                            os.makedirs(folder_path)
                                        record_npy = os.path.join(folder_path, ahi_obs_t + '_ac_' + band_name + '.npy')
                                        np.save(record_npy, record_info)

                                        end_time = T.time()
                                        TIME = end_time - start_time
                                        print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(TIME, TIME / 60, TIME / 3600))