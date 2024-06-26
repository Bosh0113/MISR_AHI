# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, orbit_to_time_range, latlon_to_bls
import netCDF4
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.linear_model import LinearRegression
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
    return ahi_sr_array * slope + offset_array


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


def identifer(data):
    down,up = numpy.nanpercentile(data,[0,75])
    IQR = up-down
    lower_limit = down - 1.5*IQR
    upper_limit = up + 1.5*IQR
    result = numpy.where(data > upper_limit,numpy.nan, data)
    result = numpy.where(result < lower_limit,numpy.nan, result)
    return result


def mapping_scatter(Y, X, figure_title='demo', band_name='band3', axis_min=0.0, axis_max=0.5):
    # filter

    if band_name == 'band3':
        axis_max = 0.3

    lim_x = numpy.copy(X)
    lim_y = numpy.copy(Y)
    lim_x[lim_x > axis_max] = numpy.nan
    lim_y[lim_y > axis_max] = numpy.nan
    lim_mask = (lim_x*lim_y)*0+1
    temp_x = lim_x*lim_mask
    temp_y = lim_y*lim_mask
    temp_x = temp_x[~numpy.isnan(temp_x)]
    temp_y = temp_y[~numpy.isnan(temp_y)]
    diff_array = abs(numpy.array(temp_y)-numpy.array(temp_x))/abs(numpy.minimum(numpy.array(temp_x), numpy.array(temp_y)))
    diff_array_filtered = numpy.array(identifer(diff_array))
    show_x = (diff_array_filtered*0+1)*temp_x
    show_y = (diff_array_filtered*0+1)*temp_y
    X = show_x[~numpy.isnan(show_x)]
    Y = show_y[~numpy.isnan(show_y)]
    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')
    ax1.grid(linestyle='--', linewidth=0.3)

    model = LinearRegression()
    x = X.reshape(-1, 1)
    model.fit(x, Y)
    y_pred = model.predict(x)
    xx = numpy.arange(axis_min, axis_max + 0.1, 0.05)
    k = model.coef_[0]
    b = model.intercept_
    yy = k * xx + b

    # rmse = math.sqrt(mean_squared_error(X, Y))
    rmse = math.sqrt(mean_squared_error(Y, y_pred))
    bias = numpy.mean(y_pred - Y)
    print('bias:', bias)

    N = len(X)
    x = numpy.arange(axis_min, axis_max + 1)
    y = 1 * x
    xx = numpy.arange(axis_min, axis_max + 0.1, 0.05)

#     g_x, g_y = numpy.mgrid[axis_min:axis_max:500j, axis_min:axis_max:500j]
#     positions = numpy.vstack([g_x.ravel(), g_y.ravel()])
#     values = numpy.vstack([X, Y])
#     kernel = gaussian_kde(values)
#     Z = numpy.reshape(kernel(positions).T, g_x.shape)

    # Calculate the point density
    xy = numpy.vstack([X, Y])
    z = gaussian_kde(xy)(xy)
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.scatter(X, Y, marker='o', c=z, s=10, cmap='jet')
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)
    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=15)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=15)
    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=15)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=15)
    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')
    ax1.spines['left'].set_linewidth(1)
    ax1.spines['bottom'].set_linewidth(1)
    ax1.set_xticks(numpy.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(numpy.arange(axis_min + 0.1, axis_max + 0.1, 0.1))
    band_label = {
        'band3': 'Band3',
        'band4': 'Band4',
    }
    ax1.set_ylabel("AHI LSR", fontsize=15)
    ax1.set_xlabel("MISR LSR", fontsize=15)
#     ax1.imshow(numpy.rot90(Z), cmap=plt.cm.gist_earth_r, extent=[axis_min, axis_max, axis_min, axis_max], alpha=0.8, zorder=0)
#     ax1.plot(X, Y, 'k.', markersize=0.5, alpha=0.8, zorder=4)
    ax1.plot(x, y, color='k', linewidth=1, linestyle='-', zorder=1)
    ax1.plot(xx, yy, color='r', linewidth=1, linestyle='-.', zorder=2)
    r_, p = pearsonr(X, Y)
    p_str = '%.3e' % p
    label_str = label_str = 'y = {}x + {}\nRMSE = {}\nr = {}\n'.format(round(k, 2), round(b, 2), round(rmse, 3), round(r_, 2))
    if b < 0:
        label_str = label_str = 'y = {}x - {}\nRMSE = {}\nr = {}\n'.format(round(k, 2), abs(round(b, 2)), round(rmse, 3), round(r_, 2))
    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.35
    ax1.text(text_x, text_y, s=label_str, fontsize=18)
    band_label = band_label[band_name]
    text_x2 = axis_min + (axis_max - axis_min) * 0.7
    text_y2 = axis_min + (axis_max - axis_min) * 0.1
    if band_name == 'band3':
        ax1.text(text_x2, text_y2, color='red', s=band_label, fontsize=18)
    else:
        ax1.text(text_x2, text_y2, color='firebrick', s=band_label, fontsize=18)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)

    figure_folder = os.path.join(roi_folder_path, 'figure_scatter')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '.png')

    fig.savefig(fig_filename, dpi=1000, bbox_inches='tight')
    print(fig_filename)
    plt.close(fig)
    plt.clf()

    # plt.show()
    # slope r RMSE
    return k, r_, rmse


def record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_para):
    ac_info = numpy.load(ahi_ac_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(misr_orbit)
    # MISR v3 netCDF4
    misr_nc = None
    try:
        misr_nc = netCDF4.Dataset(misr_nc_filename)
    except Exception as e:
        return [], []
    misr_nc_11 = misr_nc.groups['1.1_KM_PRODUCTS']
    misr_brf_var = misr_nc_11.variables['Bidirectional_Reflectance_Factor']
    misr_brf_scalev3 = misr_brf_var.scale_factor
    misr_brf_offsetv3 = misr_brf_var.add_offset
    misr_nc.close()
    m_file2 = MtkFile(misr_nc_filename)
    m_grid11 = m_file2.grid('1.1_KM_PRODUCTS')
    misr_resolutionv3 = m_grid11.resolution
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']' + '[' + str(misr_camera_index) + ']')

    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            try:
                misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
                block_llv3 = misr_blsv3[0]
                b_lat_idxv3 = round(misr_blsv3[1])
                b_lon_idxv3 = round(misr_blsv3[2])

                block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
                roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
                roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)

                roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3
            except Exception as e:
                roi_misr_brfv3[lat_index][lon_index] = 0.

    # if any cloud-free obs. is existed
    if len(roi_misr_brfv3[roi_misr_brfv3 == 0.0]) < 1:
        # MISR BRF v3
        roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_misr_sr_' + str(misr_camera_index)
        # mapping(roi_misr_brfv3, figure_title)
        # SR(AHI2MISR)
        mask_array = numpy.zeros_like(roi_misr_brfv3)
        mask_array[roi_misr_brfv3 > 0.0] = 1.
        mask_array[mask_array == 0.0] = numpy.NaN
        ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_para)
        ahi_sr_misr = ahi_sr_misr * mask_array
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_ahi_sr_' + str(misr_camera_index)
        # mapping(ahi_sr_misr, figure_title)
        # # y=SR(MISR) / x=SR(AHI)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_scatter_sr_' + str(misr_camera_index)
        # try:
        #     mapping_scatter(ahi_sr_misr, roi_misr_brfv3, figure_title, 'band'+str(band_index + 1))
        # except:
        #     pass

        # record as npy file
        record_info = [{
            'roi_name': roi_name,
            'band_index': band_index,
            'misr_orbit': misr_orbit,
            'misr_camera_index': misr_camera_index,
            'misr_v3': roi_misr_brfv3,
            'ahi_sr': roi_ahi_sr,
            'ahi_sr2misr': ahi_sr_misr
        }]
        file_path = os.path.join(roi_folder_path, ahi_obs_time + '_band' + str(band_index + 1) + '_' + str(misr_camera_index) + '.npy')
        numpy.save(file_path, record_info)
        return roi_misr_brfv3, ahi_sr_misr
    return [], []


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

    roi_misr_sr, roi_ahi_sr_misr = record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_para)
    return roi_misr_sr, roi_ahi_sr_misr


if __name__ == "__main__":
    band_names = ['band3', 'band4']
    # folder_l1_list = ['0', '26', '45']
    # folder_l2_list = ['0', '1']
    folder_l1_list = ['26']
    folder_l2_list = ['0']

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
                                ahi_obs_time_record = []
                                roi_matched_misr_roi = {}
                                for roi_misr_info in roi_misr_infos:
                                    misr_path_orbit_camera = roi_misr_info['misr_path_orbit_camera']
                                    matched_info = roi_misr_info['matched_info']
                                    ahi_obs_time = matched_info[4]
                                    AHI_AC_FOLDER = os.path.join(roi_folder_path, 'AHI_AC_PARAMETER')
                                    ahi_ac_npy = os.path.join(AHI_AC_FOLDER, str(ahi_obs_time) + '_ac_' + band_name + '.npy')
                                    if os.path.exists(ahi_ac_npy):
                                        roi_misr_sr, roi_ahi_sr = get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy)
                                        if len(roi_misr_sr) > 0:
                                            roi_misr_sr_record.append(roi_misr_sr)
                                            roi_ahi_sr_record.append(roi_ahi_sr)
                                            ahi_obs_time_record.append(str(ahi_obs_time))
                                        # print(str(ahi_obs_time) + '_' + band_name)
                                roi_matched_misr_roi['band_name'] = band_name
                                roi_matched_misr_roi['ahi_obs_time'] = ahi_obs_time_record
                                roi_matched_misr_roi['misr_sr_3d'] = roi_misr_sr_record
                                roi_matched_misr_roi['ahi_sr_3d'] = roi_ahi_sr_record
                                roi_matched_misr_roi_s.append(roi_matched_misr_roi)
                            break
                    numpy.save(os.path.join(roi_folder_path, roi_name + '_matched.npy'), roi_matched_misr_roi_s)
