import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math

# workspace = os.getcwd()
# workspace = r'D:\Work_PhD\MISR_AHI_WS\220712\26.1_150_scatters'
# workspace = r'D:\Work_PhD\MISR_AHI_WS\220712\45.6_10_scatters'
workspace = r'D:\Work_PhD\MISR_AHI_WS\220712\45.6_20_scatters'
# workspace = r'D:\Work_PhD\MISR_AHI_WS\220712\60.0_130_scatters'
# workspace = r'D:\Work_PhD\MISR_AHI_WS\220712\60.0_200_scatters'


def mapping_scatter_individe(x_2Darray, y_2Darray, color, ahi_obs_time, figure_title):
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
    plt.xlabel('AHI SR')
    plt.ylabel('MISR SR')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    fig_filename = os.path.join(workspace, figure_title + '.png')
    plt.savefig(fig_filename)
    # plt.show()
    plt.clf()


if __name__ == "__main__":
    # # 26.1_150
    # roi_name = '26.1_150'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\26.1_150_matched_sr.npy'
    # # 45.6_10
    # roi_name = '45.6_10'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_10_matched_sr.npy'
    # 45.6_20
    roi_name = '45.6_20'
    roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_20_matched_sr.npy'
    # # 60.0_130
    # roi_name = '60.0_130'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\60.0_130_matched_sr.npy'
    # # 60.0_200
    # roi_name = '60.0_200'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\60.0_200_matched_sr.npy'

    # remove noise data
    # remove_times = ['201701220110', '201704280110', '201705300110', '201707080140', '201710120140', '201711220110', '201711290110', '201712080110', '201712310110', '201806250120', '201811090110', '201811250110', '201812020110', '201901120110', '201906120130', '201907070120', '201909250110', '201910020140', '201911030140', '201911280110']   # 26.1_150 (Free-Sky)
    remove_times = []   # 45.6_10
    remove_times = []   # 45.6_20
    # remove_times = ['201704110330', '201709270320', '201710040320', '201710130310', '201710200320', '201804300330', '201808200340', '201809050320', '201809140330', '201810070320', '201811260320', '201812030310', '201812100320', '201812190310', '201902280340', '201904010330', '201905190340', '201909080320', '201909240310', '201910190310', '201910260310', '201911110310', '201911130320']   # 60.0_130 (Free-Sky)
    # remove_times = ['201701150350', '201701310400', '201702160420', '201703040420', '201705140430', '201709190400', '201710070400', '201711060340', '201711220340', '201801020350', '201802260400', '201805010420', '201809060400', '201811090340', '201811250340', '201812200350', '201812290400', '201901050350', '201902060410', '201903010400', '201904020410', '201904180420', '201905040420', '201909180410', '201909250400', '201910270340', '201911050350', '201911300350', '201912070350', '201912140350', '201912160350', '201912230350']   # 60.0_200 (Free-Sky)

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
            mapping_scatter_individe(roi_ahi_record[idx], roi_misr_record[idx], color_s[idx], ahi_obs_time[idx], roi_name + '_' + ahi_obs_time[idx] + '_' + band_name)
