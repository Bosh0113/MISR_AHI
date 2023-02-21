# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, orbit_to_time_range, latlon_to_bls
import netCDF4
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.transforms as mtransforms
from scipy.stats import gaussian_kde, pearsonr
import math
import urllib.request
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

WORK_SPACE = os.getcwd()
MISR_NC_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'
MISR_TOA_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_TOA'

# https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
# LandCover=* ReferenceSRF=AHI TargetSRF=MISR Units=PseudoScaledRadiance Regression=Linear
# SR(AHI2MISR) = SR(AHI)*Slope+Offset
AHI2MISR_SBAF = {   # slope, offset
    '1_band3': [1.026, -0.003329],      # Evergreen Needleleaf Forest
    '1_band4': [1.008, 0.0009491],
    '2_band3': [0.989, -0.003679],      # Evergreen Broadleaf Forest
    '2_band4': [1.022, -0.0001949],
    '3_band3': [0.860, 0.002982],      # Deciduous Needleleaf Forest
    '3_band4': [1.011, 0.0001392],
    '4_band3': [1.098, -0.006525],   # Deciduous Broadleaf Forest
    '4_band4': [1.012, 0.006799],
    '5_band3': [1.059, -0.003622],   # Mixed Forests
    '5_band4': [1.012, 0.0002571],
    '6_band3': [1.175, -0.009857],      # Closed Shrublands
    '6_band4': [1.011, 0.006747],
    '7_band3': [1.113, -0.001823],   # Open Shrublands
    '7_band4': [1.008, 0.00004747],
    '8_band3': [1.100, -0.006074],      # Woody Savannas
    '8_band4': [1.019, -0.0001292],
    '9_band3': [1.135, -0.005705],      # Savannas
    '9_band4': [1.015, 0.0001604],
    '10_band3': [1.099, -0.002729],     # Grasslands
    '10_band4': [1.009, 0.0002536],
    '11_band3': [0.962, 0.0002027],      # Permanent Wetlands
    '11_band4': [1.015, 0.0001696],
    '12_band3': [1.099, -0.005707],     # Croplands
    '12_band4': [1.014, 0.00005678],
    '14_band3': [1.113, -0.005765],      # Cropland/Natual Vegation
    '14_band4': [1.015, 0.00005084],
    '16_band3': [1.111, -0.003603],      # Barren
    '16_band4': [1.010, -0.001242],
}


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0.
    else:
        y = o_value * scale + offset
        return y


def ahi_sr2misr_sr(ahi_sr_array, AHI2MISR_para):
    slope = AHI2MISR_para[0]
    offset = AHI2MISR_para[1]
    offset_array = numpy.ones_like(ahi_sr_array)
    offset_array = offset_array * offset
    return (ahi_sr_array - offset_array) / slope


def mapping(array, figure_title):
    plt.imshow(array)
    plt.title(figure_title)
    plt.colorbar()
    figure_folder = os.path.join(roi_folder_path, 'figure')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '.png')
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.savefig(fig_filename)
    print(fig_filename)
    # plt.show()
    plt.clf()


def add_right_cax(ax, pad, width):

    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(axpos.x1 + pad, axpos.y0, axpos.x1 + pad + width, axpos.y1)
    cax = ax.figure.add_axes(caxpos)

    return cax


def identifer(li):
    result = []
    for a in li:
        mean = numpy.nanmean(a)
        std = numpy.nanstd(a)
        down = mean - 3 * std
        up = mean + 3 * std
        n_a = numpy.where(a < down, numpy.nan, a)
        n_a = numpy.where(n_a > up, numpy.nan, n_a)
        result.append(n_a)
    return result


def mapping_scatter(ahi_arrray, misr_array, figure_title, type, axis_min=0.0, axis_max=0.5):
    misr4show = []
    ahi4show = []
    x_3Darray_np_1d = misr_array.flatten()
    x_3Darray_np_1d = x_3Darray_np_1d[~numpy.isnan(x_3Darray_np_1d)]
    y_3Darray_np_1d = ahi_arrray.flatten()
    y_3Darray_np_1d = y_3Darray_np_1d[~numpy.isnan(y_3Darray_np_1d)]
    misr4show.extend(x_3Darray_np_1d)
    ahi4show.extend(y_3Darray_np_1d)
    # filter
    slope_array = list(numpy.array(ahi4show)/numpy.array(misr4show))
    slope_array_filtered = numpy.array(identifer([slope_array])[0])
    array1_n = (slope_array_filtered*0+1)*numpy.array(misr4show)
    array2_n = (slope_array_filtered*0+1)*numpy.array(ahi4show)
    X = array1_n[~numpy.isnan(array1_n)]
    Y = array2_n[~numpy.isnan(array2_n)]

    figure_folder = os.path.join(roi_folder_path, 'figure_scatter')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '.png')

    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')

    k, b = numpy.polyfit(X, Y, deg=1)
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = numpy.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = numpy.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = numpy.vstack([X, Y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=8)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=8)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    ax1.set_xticks(numpy.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(numpy.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    band_label = {
        'band3': 'Band3',
        'band4': 'Band4',
    }

    ax1.set_ylabel("AHI  " + type + " " + band_label[band_name], fontsize=12)
    ax1.set_xlabel("MISR  " + type + " " + band_label[band_name], fontsize=12)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')
    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.3

    r_, p = pearsonr(X, Y)
    p_str = '%.3e' % p

    # print('count of pixel: ', N)
    # label_str = label_str = 'N = {}\nRMSE = {}\ny = {}x + {}'.format(N, round(rmse, 3), round(k, 2), round(b, 2))
    # if b < 0:
    #     label_str = 'N = {}\nRMSE = {}\ny = {}x - {}'.format(N, round(rmse, 3), round(k, 2), abs(round(b, 2)))
    # label_str = label_str = 'Pearson correlation = {}\n(p-value = {})\ny = {}x + {}\nRMSE = {}\n'.format(round(r_, 2), p_str, round(k, 2), round(b, 2), round(rmse, 3))
    # if b < 0:
    #     label_str = label_str = 'Pearson correlation = {}\n(p-value = {})\ny = {}x - {}\nRMSE = {}\n'.format(round(r_, 2), p_str, round(k, 2), abs(round(b, 2)), round(rmse, 3))
    label_str = label_str = 'Pearson correlation = {}\ny = {}x + {}\nRMSE = {}\n'.format(round(r_, 2), round(k, 2), round(b, 2), round(rmse, 3))
    if b < 0:
        label_str = label_str = 'Pearson correlation = {}\ny = {}x - {}\nRMSE = {}\n'.format(round(r_, 2), round(k, 2), abs(round(b, 2)), round(rmse, 3))

    ax1.text(text_x, text_y, s=label_str, fontsize=12)

    cax = add_right_cax(ax1, pad=0.01, width=0.03)
    cb = fig.colorbar(im, cax=cax)
    # cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    fig.savefig(fig_filename, dpi=1000, bbox_inches='tight')
    print(fig_filename)
    plt.close(fig)
    plt.clf()


def download_MISR_MIL2TCST02_HDF(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    time0 = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(time0))
    yy = matchObj.group(1)
    mm = matchObj.group(2)
    dd = matchObj.group(3)
    t = str(yy) + '.' + str(mm) + '.' + str(dd)
    P = 'P' + (3 - len(str(path))) * '0' + str(path)
    O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
    F = 'F' + '05'
    v = '0011'
    base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2TCAL.002'
    filename = 'MISR_AM1_TC_ALBEDO_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'

    download_url = base_url + '/' + t + '/' + filename

    time1 = time_range[1]
    matchObj1 = re.search(r'(\d+)-(\d+)-(\d+)T', str(time1))
    yy1 = matchObj1.group(1)
    mm1 = matchObj1.group(2)
    dd1 = matchObj1.group(3)
    t1 = str(yy1) + '.' + str(mm1) + '.' + str(dd1)
    download_url1 = base_url + '/' + t1 + '/' + filename

    storage_path = folder + '/' + filename

    if os.path.exists(storage_path):
        try:
            m_file = MtkFile(storage_path)
            return storage_path
        except Exception as e:
            print(e)
            try:
                urllib.request.urlretrieve(download_url, filename=storage_path)
                return storage_path
            except Exception as e:
                print('Error: ' + download_url)
                print(e)
                try:
                    urllib.request.urlretrieve(download_url1, filename=storage_path)
                    return storage_path
                except Exception as e:
                    print('Error: ' + download_url1)
                    print(e)
                    return ''
    else:
        print('No file:', storage_path)
        try:
            urllib.request.urlretrieve(download_url, filename=storage_path)
            return storage_path
        except Exception as e:
            print('Error: ' + download_url)
            print(e)
            try:
                urllib.request.urlretrieve(download_url1, filename=storage_path)
                return storage_path
            except Exception as e:
                print('Error: ' + download_url1)
                print(e)
                return ''


def record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, misr_hdf_filename, ahi_ac_npy, AHI2MISR_para):
    ac_info = numpy.load(ahi_ac_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    roi_ahi_toa = ac_info['roi_ahi_data']
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(misr_orbit)
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
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']' + '[' + str(misr_camera_index) + ']')
    
    # MISR TOA HDF
    m_file = MtkFile(misr_hdf_filename)
    m_grid22 = m_file.grid('ReflectingLevelParameters_2.2_km')
    misr_resolution = m_grid22.resolution
    toa_field = m_grid22.field('BRFTop_Mean[' + str(band_index) + ']' + '[' + str(misr_camera_index) + ']')  # band, camera

    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    roi_misr_toa = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            try:
                misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
                block_llv3 = misr_blsv3[0]
                b_lat_idxv3 = round(misr_blsv3[1])
                b_lon_idxv3 = round(misr_blsv3[2])

                misr_bls_toa = latlon_to_bls(misr_path, misr_resolution, lat, lon)
                block_ll_toa = misr_bls_toa[0]
                b_lat_idx_toa = round(misr_bls_toa[1])
                b_lon_idx_toa = round(misr_bls_toa[2])

                block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
                roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
                roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)

                block_brf_dn_toa = toa_field.read(block_ll_toa, block_ll_toa)[0]
                roi_brf_t_toa = block_brf_dn_toa[b_lat_idx_toa][b_lon_idx_toa]

                roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3
                roi_misr_toa[lat_index][lon_index] = roi_brf_t_toa
            except Exception as e:
                roi_misr_brfv3[lat_index][lon_index] = 0.
                roi_misr_toa[lat_index][lon_index] = 0.

    # if any cloud-free obs. is existed
    if len(roi_misr_brfv3[roi_misr_brfv3 > 0.0]) > 5:
        # MISR BRF v3
        roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_misr_sr_' + str(misr_camera_index)
        mapping(roi_misr_brfv3, figure_title)
        # SR(AHI2MISR)
        mask_array = numpy.zeros_like(roi_misr_brfv3)
        mask_array[roi_misr_brfv3 > 0.0] = 1.
        mask_array[mask_array == 0.0] = numpy.NaN
        ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_para)
        ahi_sr_misr = ahi_sr_misr * mask_array
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_ahi_sr_' + str(misr_camera_index)
        mapping(ahi_sr_misr, figure_title)
        # # y=SR(MISR) / x=SR(AHI)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_scatter_sr_' + str(misr_camera_index)
        mapping_scatter(ahi_sr_misr, roi_misr_brfv3, figure_title, 'SR')

        # MISR TOA
        roi_misr_toa[roi_misr_toa <= 0.0] = numpy.NaN
        roi_misr_toa = roi_misr_toa * mask_array
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_misr_toa_' + str(misr_camera_index)
        mapping(roi_misr_toa, figure_title)
        # TOA(AHI2MISR)
        roi_ahi_toa = roi_ahi_toa * mask_array
        mask_toa_array = numpy.zeros_like(roi_misr_toa)
        mask_toa_array[roi_misr_toa > 0.0] = 1.
        mask_toa_array[mask_toa_array == 0.0] = numpy.NaN
        roi_ahi_toa = roi_ahi_toa * mask_toa_array
        ahi_toa_misr = ahi_sr2misr_sr(roi_ahi_toa, AHI2MISR_para)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_ahi_toa_' + str(misr_camera_index)
        mapping(ahi_toa_misr, figure_title)
        # # y=TOA(MISR) / x=TOA(AHI)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_scatter_toa_' + str(misr_camera_index)
        mapping_scatter(ahi_toa_misr, roi_misr_toa, figure_title, 'TOA')

        # record as npy file
        record_info = [{
            'roi_name': roi_name,
            'band_index': band_index,
            'misr_orbit': misr_orbit,
            'misr_camera_index': misr_camera_index,
            'misr_toa': roi_misr_toa,
            'ahi_toa': roi_ahi_toa,
            'ahi_toa2misr': ahi_toa_misr,
            'misr_v3': roi_misr_brfv3,
            'ahi_sr': roi_ahi_sr,
            'ahi_sr2misr': ahi_sr_misr
        }]
        file_path = os.path.join(roi_folder_path, ahi_obs_time + '_band' + str(band_index + 1) + '_' + str(misr_camera_index) + '.npy')
        numpy.save(file_path, record_info)
        return roi_misr_brfv3, ahi_sr_misr, roi_misr_toa, ahi_toa_misr
    return [], [], [], []


def get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy):
    misr_path_orbit = misr_path_orbit_camera[:12]
    misr_path = int(misr_path_orbit[1:4])
    misr_orbit = int(misr_path_orbit[-6:])
    band_index = int(ahi_ac_npy[-5:-4]) - 1
    band_name = 'band' + str(band_index + 1)
    roi_infos = roi_folder.split('_')
    roi_lc_idx = roi_infos[1]
    AHI2MISR_para = AHI2MISR_SBAF[roi_lc_idx + '_' + band_name]
    misr_camera_index = int(misr_path_orbit_camera[-1:])
    ahi_obs_time = ahi_ac_npy[-25:-13]
    misr_nc_filename = os.path.join(MISR_NC_FOLDER, 'MISR_AM1_AS_LAND_' + misr_path_orbit + '_F08_0023.nc')
    misr_hdf_filename = download_MISR_MIL2TCST02_HDF(MISR_TOA_FOLDER, misr_path, misr_orbit)

    roi_misr_sr, roi_ahi_sr_misr, roi_misr_toa, roi_ahi_toa_misr = record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, misr_hdf_filename, ahi_ac_npy, AHI2MISR_para)
    return roi_misr_sr, roi_ahi_sr_misr, roi_misr_toa, roi_ahi_toa_misr


if __name__ == "__main__":
    band_names = ['band3', 'band4']
    folder_l1_list = ['0', '26', '45', '60', '70']
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
                    matched_record_npy = os.path.join(roi_folder_path, roi_name + '_matched_record.npy')
                    matched_record = numpy.load(matched_record_npy, allow_pickle=True)
                    roi_matched_misr_roi_s = []
                    for matched_roi_info in matched_record:
                        roi_name_re = matched_roi_info['roi_name']
                        if roi_name == roi_name_re:
                            roi_misr_infos = matched_roi_info['roi_misr_infos']
                            for band_name in band_names:
                                roi_misr_sr_record = []
                                roi_ahi_sr_record = []
                                roi_misr_toa_record = []
                                roi_ahi_toa_record = []
                                ahi_obs_time_record = []
                                roi_matched_misr_roi = {}
                                for roi_misr_info in roi_misr_infos:
                                    misr_path_orbit_camera = roi_misr_info['misr_path_orbit_camera']
                                    matched_info = roi_misr_info['matched_info']
                                    ahi_obs_time = matched_info[4]
                                    AHI_AC_FOLDER = os.path.join(roi_folder_path, 'AHI_AC_PARAMETER')
                                    ahi_ac_npy = os.path.join(AHI_AC_FOLDER, str(ahi_obs_time) + '_ac_' + band_name + '.npy')
                                    if os.path.exists(ahi_ac_npy):
                                        roi_misr_sr, roi_ahi_sr, roi_misr_toa, roi_ahi_toa = get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy)
                                        if len(roi_misr_sr) > 0:
                                            roi_misr_sr_record.append(roi_misr_sr)
                                            roi_ahi_sr_record.append(roi_ahi_sr)
                                            ahi_obs_time_record.append(str(ahi_obs_time))
                                        # print(str(ahi_obs_time) + '_' + band_name)
                                roi_matched_misr_roi['band_name'] = band_name
                                roi_matched_misr_roi['ahi_obs_time'] = ahi_obs_time_record
                                roi_matched_misr_roi['misr_sr_3d'] = roi_misr_sr_record
                                roi_matched_misr_roi['ahi_sr_3d'] = roi_ahi_sr_record
                                roi_matched_misr_roi['misr_toa_3d'] = roi_misr_toa_record
                                roi_matched_misr_roi['ahi_toa_3d'] = roi_ahi_toa_record
                                roi_matched_misr_roi_s.append(roi_matched_misr_roi)
                            break
                    numpy.save(os.path.join(roi_folder_path, roi_name + '_matched.npy'), roi_matched_misr_roi_s)
