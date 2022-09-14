import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math

WORK_SPACE = r'D:\Work_PhD\MISR_AHI_WS\220909'


def mapping_scatter_all(x_3Darray, y_3Darray, color_array, ahi_obs_time_record, figure_title):
    max_axs = 0.5
    band_name = figure_title[-5:]
    if band_name == 'band3':
        max_axs = 0.3
    ax = plt.axes()
    for idx in range(len(x_3Darray)):
        x_2Darray = x_3Darray[idx]
        y_2Darray = y_3Darray[idx]
        color = color_array[idx]
        ahi_obs_time = ahi_obs_time_record[idx]
        plt.scatter(x_2Darray, y_2Darray, marker='o', edgecolors=[color], c='none', s=15, linewidths=0.5, label=ahi_obs_time[:8])

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
    plt.xlabel('MISR SR')
    plt.ylabel('AHI SR')
    plt.tick_params(labelsize=15)
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    # fig_filename = os.path.join(workspace, figure_title + '.png')
    # plt.savefig(fig_filename)
    plt.show()
    plt.clf()


if __name__ == "__main__":
    # roi_name = '0.0_60'
    # selected_times = ['201808300100', '201809150100', '201904110100']
    # roi_name = '0.0_120'
    # selected_times = ['201704050100', '201709120100', '201809150100', '201909180100']
    roi_name = '26.1_150'
    selected_times = ['201712240110', '201801090110', '201801250110', '201802260110', '201812180110', '201902130110']
    # roi_name = '45.6_10'
    # selected_times = ['201712210340']
    # roi_name = '45.6_20'
    # selected_times = ['201912080300']
    # roi_name = '60.0_80'
    # selected_times = ['201910230250']
    # roi_name = '60.0_130'
    # selected_times = ['201709180320', '201810160310', '201909080320', '201909240310', '201910100310']
    # roi_name = '60.0_200'
    # selected_times = ['201803140400']

    roi_matched_npy = os.path.join(WORK_SPACE, roi_name + '_matched_sr.npy')

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
            if ahi_obs_time_v in selected_times:
                r_index.append(idx)
        ahi_obs_time = [ahi_obs_time[i] for i in range(len(ahi_obs_time)) if (i in r_index)]
        roi_misr_record = [roi_misr_record[i] for i in range(len(roi_misr_record)) if (i in r_index)]
        roi_ahi_record = [roi_ahi_record[i] for i in range(len(roi_ahi_record)) if (i in r_index)]
        print('count:', len(ahi_obs_time))
        mapping_scatter_all(roi_misr_record, roi_ahi_record, color_s, ahi_obs_time, roi_name + '_' + band_name)
