import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math

workspace = os.getcwd()


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
    plt.xlabel('AHI SR')
    plt.ylabel('MISR SR')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    # fig_filename = os.path.join(workspace, figure_title + '.png')
    # plt.savefig(fig_filename)
    plt.show()
    plt.clf()


if __name__ == "__main__":
    # # 26.1_150
    # roi_name = '26.1_150'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\26.1_150_matched_sr.npy'
    # 45.6_60
    roi_name = '45.6_60'
    roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_60_matched_sr.npy'

    # full matched time
    # full_times = ['201701060110', '201701220110', '201702070110', '201702230110', '201703110110', '201703270110', '201704120110', '201704280110', '201705140110', '201705300110', '201706150110', '201707010110', '201707170110', '201708020110', '201708180110', '201709030110', '201709190110', '201710050110', '201710210110', '201711060110', '201711220110', '201712080110', '201712240110', '201801090110', '201801250110', '201802100110', '201802260110', '201803140110', '201803300110', '201804150110', '201805010110', '201805170110', '201806020110', '201806180110', '201807040110', '201807200110', '201808050110', '201808210110', '201809060110', '201809220110', '201810080110', '201810240110', '201811090110', '201811250110', '201812110110', '201812270110', '201901120110', '201901280110', '201902130110', '201903010110', '201903170110', '201904020110', '201904180110', '201905040110', '201905200110', '201906050110', '201906210110', '201907070120', '201907230110', '201908080110', '201908240110', '201909090110', '201909250110', '201910110110', '201910270110', '201911120110', '201911280110', '201912140110', '201912300110']   # 26.1_150
    full_times = ['201701140130', '201701300130', '201702150130', '201703030130', '201703190130', '201704040130', '201704200130', '201705060130', '201705220130', '201706070130', '201706230130', '201707090130', '201707250140', '201708100140', '201708260140', '201709110140', '201709270140', '201710130130', '201710290130', '201711140130', '201711300130', '201712160130', '201801010130', '201801170130', '201802020130', '201802180130', '201803060130', '201803220140', '201804070140', '201804230140', '201805090140', '201805250140', '201806100140', '201806260140', '201807120140', '201807280140', '201808130140', '201808290140', '201809140130', '201809300140', '201810160140', '201811010140', '201811170140', '201812030130', '201812190130', '201901040130', '201901200130', '201902050130', '201902210130', '201903090130', '201903250130', '201904100130', '201904260130', '201905120130', '201905280130', '201906130130', '201906290130', '201907150130', '201907310130', '201908160130', '201909010130', '201909170130', '201910030130', '201910190130', '201911040130', '201911200130', '201912060130', '201912220130', '201709020140', '201709180140', '201710040140', '201804300140', '201805160140', '201806010140', '201809210140', '201810070140', '201810230140', '201811080140']   # 45.6_60

    # remove noise data
    remove_times = ['201701220110', '201704280110', '201705300110', '201707080140', '201710120140', '201711220110', '201711290110', '201712080110', '201712310110', '201806250120', '201811090110', '201811250110', '201812020110', '201901120110', '201906120130', '201907070120', '201909250110', '201910020140', '201911030140', '201911280110']   # 26.1_150 (Free-Sky)
    # remove_times = ['201704040130', '201704200130', '201705310110', '201802020130', '201803150100', '201805250140', '201806190110', '201810250100', '201812030130', '201902050130', '201903180100', '201904100130', '201904190100', '201906130130', '201909170130', '201911040130']   # 45.6_60

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
        print('total count:', len(ahi_obs_time))
        # full matched data index
        f_index = []
        for idx in range(len(ahi_obs_time)):
            ahi_obs_time_v = ahi_obs_time[idx]
            if ahi_obs_time_v in full_times:
                f_index.append(idx)
        ahi_obs_time = [ahi_obs_time[i] for i in range(len(ahi_obs_time)) if (i in f_index)]
        roi_misr_record = [roi_misr_record[i] for i in range(len(roi_misr_record)) if (i in f_index)]
        roi_ahi_record = [roi_ahi_record[i] for i in range(len(roi_ahi_record)) if (i in f_index)]
        print('full matched count:', len(ahi_obs_time))
        # noise data index
        r_index = []
        for idx in range(len(ahi_obs_time)):
            ahi_obs_time_v = ahi_obs_time[idx]
            if ahi_obs_time_v in remove_times:
                r_index.append(idx)
        ahi_obs_time = [ahi_obs_time[i] for i in range(len(ahi_obs_time)) if (i not in r_index)]
        roi_misr_record = [roi_misr_record[i] for i in range(len(roi_misr_record)) if (i not in r_index)]
        roi_ahi_record = [roi_ahi_record[i] for i in range(len(roi_ahi_record)) if (i not in r_index)]
        print('full matched free-sky count:', len(ahi_obs_time))
        mapping_scatter_all(roi_ahi_record, roi_misr_record, color_s, ahi_obs_time, roi_name + '_' + band_name)
