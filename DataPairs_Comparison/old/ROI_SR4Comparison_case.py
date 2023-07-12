# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.transforms as mtransforms
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import gaussian_kde, pearsonr
import math

workspace = os.getcwd()
MISR_NC_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'
AHI_AC_FOLDER = os.path.join(workspace, 'AHI_AC_PARAMETER')

# https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
# LandCover=* ReferenceSRF=AHI TargetSRF=MISR Units=PseudoScaledRadiance Regression=Linear
# SR(AHI2MISR) = SR(AHI)*Slope+Offset
AHI2MISR_SBAF = {   # slope, offset
    # '0.0_0_band3': [1.135, -0.005705],      # Savannas
    # '0.0_0_band4': [1.015, 0.0001604],
    '0.0_0_band3': [1.100, -0.006074],      # Woody Savannas
    '0.0_0_band4': [1.019, -0.0001292],
    '0.0_1_band3': [0.989, -0.003679],      # Evergreen Broadleaf Forest
    '0.0_1_band4': [1.022, -0.0001949],
    '26.1_0_band3': [1.099, -0.002729],     # Grasslands
    '26.1_0_band4': [1.009, 0.0002536],
    '26.1_1_band3': [0.989, -0.003679],     # Evergreen Broadleaf Forest
    '26.1_1_band4': [1.022, -0.0001949],
    '45.6_0_band3': [1.099, -0.005707],     # Croplands
    '45.6_0_band4': [1.014, 0.00005678],
    '45.6_1_band3': [0.989, -0.003679],     # Evergreen Broadleaf Forest
    '45.6_1_band4': [1.022, -0.0001949],
    '60.0_0_0_band3': [1.099, -0.002729],   # Grasslands
    '60.0_0_0_band4': [1.009, 0.0002536],
    '60.0_1_0_band3': [1.098, -0.006525],   # Deciduous Broadleaf Forest
    '60.0_1_0_band4': [1.012, 0.006799],
    '70.5_0_0_band3': [1.113, -0.001823],   # Open Shrublands
    '70.5_0_0_band4': [1.008, 0.00004747],
    '70.5_1_0_band3': [1.059, -0.003622],   # Mixed Forests
    '70.5_1_0_band4': [1.012, 0.0002571],
    '60.0_0_1_band3': [1.099, -0.002729],   # Grasslands
    '60.0_0_1_band4': [1.009, 0.0002536],
    '60.0_1_1_band3': [1.059, -0.003622],   # Mixed Forests
    '60.0_1_1_band4': [1.012, 0.0002571],
    '70.5_0_1_band3': [1.113, -0.001823],   # Open Shrublands
    '70.5_0_1_band4': [1.008, 0.00004747],
    '70.5_1_1_band3': [1.059, -0.003622],   # Mixed Forests
    '70.5_1_1_band4': [1.012, 0.0002571],
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
    figure_folder = os.path.join(workspace, 'figure_SR')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '_sr.png')
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


def mapping_scatter(ahi_arrray, misr_array, figure_title, axis_min=0.0, axis_max=0.5):
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

    figure_folder = os.path.join(workspace, 'figure_scatter_sr')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '_sr.png')

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

    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    ax1.set_xticks(numpy.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(numpy.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    band_label = {
        'band3': 'Band3',
        'band4': 'Band4',
    }

    ax1.set_ylabel("AHI Surface Reflectance " + band_label[band_name], fontsize=12)
    ax1.set_xlabel("MISR Surface Reflectance " + band_label[band_name], fontsize=12)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.3

    v, p = pearsonr(X, Y)
    p_str = '%.3e' % p

    # print('count of pixel: ', N)
    # label_str = label_str = 'N = {}\nRMSE = {}\ny = {}x + {}'.format(N, round(rmse, 3), round(k, 2), round(b, 2))
    # if b < 0:
    #     label_str = 'N = {}\nRMSE = {}\ny = {}x - {}'.format(N, round(rmse, 3), round(k, 2), abs(round(b, 2)))
    label_str = label_str = 'Pearson correlation = {}\n(p-value = {})\ny = {}x + {}\nRMSE = {}\n'.format(round(v, 2), p_str, round(k, 2), round(b, 2), round(rmse, 3))
    if b < 0:
        label_str = label_str = 'Pearson correlation = {}\n(p-value = {})\ny = {}x - {}\nRMSE = {}\n'.format(round(v, 2), p_str, round(k, 2), abs(round(b, 2)), round(rmse, 3))

    ax1.text(text_x, text_y, s=label_str, fontsize=12)

    cax = add_right_cax(ax1, pad=0.01, width=0.03)
    cb = fig.colorbar(im, cax=cax)
    # cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    fig.savefig(fig_filename, dpi=1000, bbox_inches='tight')
    print(fig_filename)
    plt.clf()


def record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index,
                        ahi_obs_time, misr_nc_filename, ahi_ac_npy,
                        AHI2MISR_para):
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
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' +
                               str(band_index) + ']' + '[' +
                               str(misr_camera_index) + ']')
    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            try:
                misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat,
                                           lon)
                block_llv3 = misr_blsv3[0]
                b_lat_idxv3 = round(misr_blsv3[1])
                b_lon_idxv3 = round(misr_blsv3[2])
                block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
                roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
                roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3,
                                            misr_brf_offsetv3)
                roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3
            except Exception as e:
                roi_misr_brfv3[lat_index][lon_index] = 0.

    # if any cloud-free obs. is existed
    if roi_misr_brfv3.max() > 0.0:
        # MISR BRF v3
        roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(
            band_index + 1) + '_misr_sr'
        mapping(roi_misr_brfv3, figure_title)

        mask_array = numpy.copy(roi_misr_brfv3)
        mask_array[mask_array > 0.0] = 1.
        # SR(AHI2MISR)
        ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_para)
        # print(ahi_sr_misr)
        ahi_sr_misr = ahi_sr_misr * mask_array
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(
            band_index + 1) + '_ahi_sr'
        mapping(ahi_sr_misr, figure_title)

        # # y=SR(MISR) / x=SR(AHI)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(
            band_index + 1) + '_scatter_sr'
        mapping_scatter(ahi_sr_misr, roi_misr_brfv3, figure_title)

        # record as npy file
        record_info = [{
            'roi_name': roi_name,
            'band_index': band_index,
            'misr_orbit': misr_orbit,
            'misr_camera_index': misr_camera_index,
            'misr_v3': roi_misr_brfv3,
            'ahi_toa': roi_ahi_toa,
            'ahi_sr': roi_ahi_sr,
            'ahi_sr2misr': ahi_sr_misr
        }]
        file_path = os.path.join(
            workspace,
            ahi_obs_time + '_sr_band' + str(band_index + 1) + '.npy')
        numpy.save(file_path, record_info)
        return roi_misr_brfv3, ahi_sr_misr
    return [], []


def get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy):
    misr_path_orbit = misr_path_orbit_camera[:12]
    misr_orbit = int(misr_path_orbit[-6:])
    band_index = int(ahi_ac_npy[-5:-4]) - 1
    band_name = 'band' + str(band_index + 1)
    AHI2MISR_para = AHI2MISR_SBAF[roi_name + '_' + band_name]
    misr_camera_index = int(misr_path_orbit_camera[-1:])
    ahi_obs_time = ahi_ac_npy[-25:-13]
    misr_nc_filename = os.path.join(MISR_NC_FOLDER, 'MISR_AM1_AS_LAND_' + misr_path_orbit + '_F08_0023.nc')
    roi_misr_sr, roi_ahi_sr_misr = record_roi_misr_ahi(
        roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time,
        misr_nc_filename, ahi_ac_npy, AHI2MISR_para)
    return roi_misr_sr, roi_ahi_sr_misr


def mapping_scatter_all(x_3Darray, y_3Darray, color_array, ahi_obs_time_record,
                        figure_title):
    max_axs = 0.5
    ax = plt.axes()
    for idx in range(len(x_3Darray)):
        x_2Darray = x_3Darray[idx]
        y_2Darray = y_3Darray[idx]
        color = color_array[idx]
        ahi_obs_time = ahi_obs_time_record[idx]
        plt.scatter(x_2Darray,
                    y_2Darray,
                    marker='o',
                    edgecolors=[color],
                    c='none',
                    s=15,
                    linewidths=0.5,
                    label=ahi_obs_time[:8])
    # linear regression
    x_3Darray_np = numpy.array(x_3Darray)
    x_3Darray_np_1d = x_3Darray_np.flatten()
    x_3Darray_np_1d = x_3Darray_np_1d[~numpy.isnan(x_3Darray_np_1d)]
    y_3Darray_np = numpy.array(y_3Darray)
    y_3Darray_np_1d = y_3Darray_np.flatten()
    y_3Darray_np_1d = y_3Darray_np_1d[~numpy.isnan(y_3Darray_np_1d)]
    b, a = numpy.polyfit(x_3Darray_np_1d, y_3Darray_np_1d, deg=1)
    xseq = numpy.linspace(0, max_axs, num=100)
    ax.plot(xseq, a + b * xseq, color="k", lw=2)
    ax.plot(xseq, xseq, 'r--', alpha=0.5, linewidth=1)
    r2 = r2_score(x_3Darray_np_1d, y_3Darray_np_1d)
    rmse = math.sqrt(mean_squared_error(x_3Darray_np_1d, y_3Darray_np_1d))
    text = 'R^2=' + str(round(r2, 3)) + '\ny=' + str(round(
        b, 2)) + '*x+' + str(round(a, 3)) + '\nRMSE=' + str(round(rmse, 3))
    plt.text(x=0.01, y=max_axs - max_axs / 5, s=text, fontsize=12)

    plt.title(figure_title)
    minorLocator = MultipleLocator(0.02)
    majorLocator = MultipleLocator(0.1)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.yaxis.set_minor_locator(minorLocator)
    ax.xaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_locator(majorLocator)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.xlim((0, max_axs))
    plt.ylim((0, max_axs))
    plt.xlabel('AHI SR')
    plt.ylabel('MISR SR')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    fig_filename = os.path.join(workspace, figure_title + '_sr.png')
    plt.savefig(fig_filename)
    # plt.show()
    plt.clf()


if __name__ == "__main__":
    band_names = ['band3', 'band4']
    # ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0_0', '60.0_0_1', '60.0_1_0', '60.0_1_1', '70.5_0_0', '70.5_0_1', '70.5_1_0', '70.5_1_1']
    roi_name = '0.0_0'
    matched_record_npy = os.path.join(workspace, roi_name + '_matched_record.npy')
    matched_record = numpy.load(matched_record_npy, allow_pickle=True)
    roi_matched_misr_roi_s = []
    for matched_roi_info in matched_record:
        roi_name_re = matched_roi_info['roi_name']
        if roi_name == roi_name_re:
            roi_misr_infos = matched_roi_info['roi_misr_infos']
            for band_name in band_names:
                roi_misr_record = []
                roi_ahi_record = []
                ahi_obs_time_record = []
                roi_matched_misr_roi = {}
                for roi_misr_info in roi_misr_infos:
                    misr_path_orbit_camera = roi_misr_info[
                        'misr_path_orbit_camera']
                    matched_info = roi_misr_info['matched_info']
                    ahi_obs_time = matched_info[4]
                    ahi_ac_npy = os.path.join(
                        AHI_AC_FOLDER,
                        str(ahi_obs_time) + '_ac_' + band_name + '.npy')
                    if os.path.exists(ahi_ac_npy):
                        roi_misr, roi_ahi = get_roi_misr_ahi(
                            roi_name, misr_path_orbit_camera, ahi_ac_npy)
                        if len(roi_misr) > 0:
                            roi_misr_record.append(roi_misr)
                            roi_ahi_record.append(roi_ahi)
                            ahi_obs_time_record.append(str(ahi_obs_time))
                        # print(str(ahi_obs_time) + '_' + band_name)
                roi_matched_misr_roi['band_name'] = band_name
                roi_matched_misr_roi['ahi_obs_time'] = ahi_obs_time_record
                roi_matched_misr_roi['misr_sr_3d'] = roi_misr_record
                roi_matched_misr_roi['ahi_sr_3d'] = roi_ahi_record
                roi_matched_misr_roi_s.append(roi_matched_misr_roi)
            break
    color_s = []
    for i in range(len(roi_matched_misr_roi_s[0]['ahi_obs_time']) * 2):
        color_random = list(matplotlib.colors.XKCD_COLORS.items())[int(
            random.random() * 900)][1]
        color_s.append(color_random)
    for roi_matched_record_item in roi_matched_misr_roi_s:
        band_name = roi_matched_record_item['band_name']
        ahi_obs_time = roi_matched_record_item['ahi_obs_time']
        roi_misr_record = roi_matched_record_item['misr_sr_3d']
        roi_ahi_record = roi_matched_record_item['ahi_sr_3d']
        mapping_scatter_all(roi_ahi_record, roi_misr_record, color_s,
                            ahi_obs_time, roi_name + '_' + band_name)
    numpy.save(os.path.join(workspace, roi_name + '_matched_sr.npy'),
               roi_matched_misr_roi_s)
