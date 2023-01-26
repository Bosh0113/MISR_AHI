import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math


def mapping_scatter_individe(scatter_folder_path, x_2Darray, y_2Darray, color, ahi_obs_time, figure_title):
    max_axs = 0.5
    band_name = figure_title[-5:]
    if band_name == 'band3':
        max_axs = 0.3
    ax = plt.axes()
    plt.scatter(x_2Darray, y_2Darray, marker='o', edgecolors=[color], c='none', s=15, linewidths=0.5, label=ahi_obs_time[:8])
    # linear regression
    x_2Darray_np = numpy.array(x_2Darray)
    x_2Darray_np_1d = x_2Darray_np.flatten()
    x_2Darray_np_1d = x_2Darray_np_1d[~numpy.isnan(x_2Darray_np_1d)]
    y_2Darray_np = numpy.array(y_2Darray)
    y_2Darray_np_1d = y_2Darray_np.flatten()
    y_2Darray_np_1d = y_2Darray_np_1d[~numpy.isnan(y_2Darray_np_1d)]
    b, a = numpy.polyfit(x_2Darray_np_1d, y_2Darray_np_1d, deg=1)
    xseq = numpy.linspace(0, max_axs, num=100)
    ax.plot(xseq, a + b * xseq, color="k", lw=2)
    ax.plot(xseq, xseq, 'r--', alpha=0.5, linewidth=1)
    r2 = r2_score(x_2Darray_np_1d, y_2Darray_np_1d)
    rmse = math.sqrt(mean_squared_error(x_2Darray_np_1d, y_2Darray_np_1d))
    text = 'R^2=' + str(round(r2, 3)) + '\ny=' + str(round(b, 2)) + '*x+' + str(round(a, 3)) + '\nRMSE=' + str(round(rmse, 3))
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
    plt.xlabel('MISR')
    plt.ylabel('AHI')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    fig_filename = os.path.join(scatter_folder_path, figure_title + '.png')
    plt.savefig(fig_filename)
    # plt.show()
    plt.clf()


def main(workspace, roi_name):
    # remove noise data
    remove_times = []
    
    roi_matched_npy = os.path.join(workspace, roi_name + '_matched_sr.npy')
    scatter_folder = os.path.join(workspace, 'sr_scatter_figures')
    if not os.path.exists(scatter_folder):
        os.makedirs(scatter_folder)
    roi_matched_record = numpy.load(roi_matched_npy, allow_pickle=True)
    color_s = []
    for i in range(len(roi_matched_record[0]['ahi_obs_time'])):
        color_random = list(matplotlib.colors.XKCD_COLORS.items())[int(random.random() * 900)][1]
        color_s.append(color_random)
    for roi_matched_record_item in roi_matched_record:
        band_name = roi_matched_record_item['band_name']
        ahi_obs_time = roi_matched_record_item['ahi_obs_time']
        roi_misr_record = roi_matched_record_item['misr_sr_3d']
        roi_ahi_record = roi_matched_record_item['ahi_sr_3d']
        # noise data index
        r_index = []
        for idx in range(len(ahi_obs_time)):
            ahi_obs_time_v = ahi_obs_time[idx]
            if ahi_obs_time_v in remove_times:
                r_index.append(idx)
        ahi_obs_time = [ahi_obs_time[i] for i in range(len(ahi_obs_time)) if (i not in r_index)]
        roi_misr_record = [roi_misr_record[i] for i in range(len(roi_misr_record)) if (i not in r_index)]
        roi_ahi_record = [roi_ahi_record[i] for i in range(len(roi_ahi_record)) if (i not in r_index)]
        print('count:', len(ahi_obs_time))
        for idx in range(len(ahi_obs_time)):
            mapping_scatter_individe(scatter_folder, roi_misr_record[idx], roi_ahi_record[idx], color_s[idx], ahi_obs_time[idx], roi_name + '_' + ahi_obs_time[idx] + '_' + band_name)


if __name__ == "__main__":
    base_path = r'D:\Work_PhD\MISR_AHI_WS\230126\intercom_mapping'
    # # ray-matched
    # folder_names = ['0_0_Ray', '0_1_Ray', '26_0_Ray', '26_1_Ray', '45_0_Ray', '45_1_Ray', '60_0_Ray', '60_1_Ray', '70_0_Ray', '70_1_Ray']
    # roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0_0', '60.0_1_0', '70.5_0_0', '70.5_1_0']
    # RAA-matched
    folder_names = ['0_0_RAA', '0_1_RAA', '26_0_RAA', '26_1_RAA', '45_0_RAA', '45_1_RAA', '60_0_RAA', '60_1_RAA', '70_0_RAA', '70_1_RAA']
    roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0_1', '60.0_1_1', '70.5_0_1', '70.5_1_1']
    for idx in range(len(folder_names)):
        folder_name = folder_names[idx]
        roi_name = roi_names[idx]
        ws_path = os.path.join(base_path, folder_name)
        main(ws_path, roi_name)