import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, pearsonr
from sklearn.metrics import mean_squared_error
import numpy as np
import math
import os

# SAVE_FIGURE_FLAG = True
SAVE_FIGURE_FLAG = False

# WORK_SPACE = r'D:\Work_PhD\MISR_AHI_WS\230126\intercom_mapping\0_0_RAA'
# roi_name = '0.0_0'
# selected_times = ['201910200050']   # 99	105515	4	201910200054	201910200050	1.931	5.804	284.169	325.081	108.915	109.069	175.254	143.988	19.937	19.686	175.728
WORK_SPACE = r'D:\Work_PhD\MISR_AHI_WS\230126\intercom_mapping\0_0_Ray'
roi_name = '0.0_0'
selected_times = ['201810010100']   # 99	99923	4	201810010055	201810010100	4.100	5.804	282.781	325.081	87.955	87.443	165.174	122.361	19.986	17.591	176.056


def identifer(li):
    result = []
    for a in li:
        mean = np.nanmean(a)
        std = np.nanstd(a)
        down = mean - 3 * std
        up = mean + 3 * std
        n_a = np.where(a < down, np.nan, a)
        n_a = np.where(n_a > up, np.nan, n_a)
        result.append(n_a)
    return result


def add_right_cax(ax, pad, width):

    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(axpos.x1 + pad, axpos.y0, axpos.x1 + pad + width, axpos.y1)
    cax = ax.figure.add_axes(caxpos)

    return cax


def make_fig(roi_name, X, Y, band_name, axis_min=0.0, axis_max=0.5):

    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')

    k, b = np.polyfit(X, Y, deg=1)
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = np.vstack([X, Y])
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

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

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
    if SAVE_FIGURE_FLAG:
        fig.savefig(os.path.join(WORK_SPACE, '{} '.format(roi_name) + band_label[band_name] + ' SR.jpg'), dpi=1000, bbox_inches='tight')
    else:
        plt.show()
    plt.clf()


if __name__ == "__main__":

    roi_matched_npy = os.path.join(WORK_SPACE, roi_name + '_matched_sr.npy')

    roi_matched_record = np.load(roi_matched_npy, allow_pickle=True)

    for roi_matched_record_item in roi_matched_record:
        misr4show = []
        ahi4show = []
        band_name = roi_matched_record_item['band_name']
        ahi_obs_time = roi_matched_record_item['ahi_obs_time']
        roi_misr_record = roi_matched_record_item['misr_sr_3d']
        roi_ahi_record = roi_matched_record_item['ahi_sr_3d']
        # noise data index
        r_index = []
        for idx in range(len(ahi_obs_time)):
            ahi_obs_time_v = ahi_obs_time[idx]
            if ahi_obs_time_v in selected_times:
                r_index.append(idx)
        ahi_obs_time = [ahi_obs_time[i] for i in range(len(ahi_obs_time)) if (i in r_index)]
        roi_misr_record = [roi_misr_record[i] for i in range(len(roi_misr_record)) if (i in r_index)]
        roi_ahi_record = [roi_ahi_record[i] for i in range(len(roi_ahi_record)) if (i in r_index)]
        x_3Darray_np = np.array(roi_misr_record)
        x_3Darray_np_1d = x_3Darray_np.flatten()
        x_3Darray_np_1d = x_3Darray_np_1d[~np.isnan(x_3Darray_np_1d)]
        y_3Darray_np = np.array(roi_ahi_record)
        y_3Darray_np_1d = y_3Darray_np.flatten()
        y_3Darray_np_1d = y_3Darray_np_1d[~np.isnan(y_3Darray_np_1d)]
        misr4show.extend(x_3Darray_np_1d)
        ahi4show.extend(y_3Darray_np_1d)
        # filter
        slope_array = list(np.array(ahi4show)/np.array(misr4show))
        slope_array_filtered = np.array(identifer([slope_array])[0])
        array1_n = (slope_array_filtered*0+1)*np.array(misr4show)
        array2_n = (slope_array_filtered*0+1)*np.array(ahi4show)
        array_x = array1_n[~np.isnan(array1_n)]
        array_y = array2_n[~np.isnan(array2_n)]

        make_fig(roi_name, array_x, array_y, band_name)
