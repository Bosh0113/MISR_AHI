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
    # # 0.0_50
    # roi_name = '0.0_50'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\0.0_50_matched_sr.npy'
    # # 0.0_60
    # roi_name = '0.0_60'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\0.0_60_matched_sr.npy'
    # # 0.0_120
    # roi_name = '0.0_120'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\0.0_120_matched_sr.npy'
    # # 45.6_10
    # roi_name = '45.6_10'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_10_matched_sr.npy'
    # # 45.6_20
    # roi_name = '45.6_20'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_20_matched_sr.npy'
    # 45.6_60
    roi_name = '45.6_60'
    roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\45.6_60_matched_sr.npy'
    # # 60.0_80
    # roi_name = '60.0_80'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\60.0_80_matched_sr.npy'
    # # 60.0_130
    # roi_name = '60.0_130'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\60.0_130_matched_sr.npy'
    # # 60.0_200
    # roi_name = '60.0_200'
    # roi_matched_npy = r'D:\Work_PhD\MISR_AHI_WS\220629\60.0_200_matched_sr.npy'

    # remove noise data
    remove_times = []
    # remove_times = ['201706220040', '201907140100', '201912140100']     # 0.0_50
    # remove_times = ['201708110040']     # 0.0_60
    # remove_times = []   # 0.0_120
    # remove_times = ['201701030350', '201701100350', '201702110410', '201706030350', '201706190340', '201707050350', '201707210350', '201710250350', '201711260320', '201712280340', '201801130350', '201801290350', '201805210350', '201807010350', '201811290320', '201811060340', '201812240340', '201901090400', '201902010350', '201906020350', '201906090350', '201907110350', '201910150340', '201910240400', '201911090340', '201911160330', '201911250340', '201912020330', '201912110340', '201912180330']   # 45.6_10
    # remove_times = ['201701230310', '201710220310', '201711230310', '201712020300', '201712180320', '201712250310', '201802110320', '201811190300', '201811260310', '201812120310', '201909260310', '201911290300', '201912080300', '201912310310']   # 45.6_20
    remove_times = ['201704040130', '201704200130', '201705310110', '201802020130', '201803150100', '201805250140', '201806190110', '201810250100', '201812030130', '201902050130', '201903180100', '201904100130', '201904190100', '201906130130', '201909170130', '201911040130']   # 45.6_60
    # remove_times = ['201710170250', '201710260300', '201711110300', '201711180250', '201810200250', '201910230250']  # 60.0_80
    # remove_times = ['201704110330', '201709270320', '201710040320', '201710130310', '201710200320', '201710220330', '201710290310', '201804300330', '201808200340', '201809050320', '201809140330', '201809300320', '201810070320', '201810160310', '201811010310', '201811100320', '201811240320', '201811260320', '201812030310', '201812100320', '201812190310', '201902280340', '201904010330', '201905190340', '201909080320',  '201910190310', '201910260310', '201911110310', '201911130320']   # 60.0_130
    # remove_times = ['201701060400', '201701080410', '201701150350', '201701310400', '201702160420', '201702230400', '201703040420', '201703110400', '201704280420', '201705140430', '201709190400', '201710050400', '201710070400', '201710140350', '201710210350', '201710230350', '201710300350', '201711060340', '201711080350', '201711150350', '201711220340', '201711240350', '201712010350', '201712100350', '201712170350', '201712240400', '201712260350', '201801020350', '201801090400', '201801110410', '201801180350', '201802030410', '201802100400', '201802260400', '201803140400', '201803300410', '201804150410', '201805010420', '201805100420', '201805170430', '201809060400', '201810010400', '201810080400', '201809220400', '201810100400', '201810170400', '201810240340', '201811020400', '201811090340', '201811110350', '201811180350', '201811250340', '201811270350', '201812040350', '201812110350', '201812130350', '201812200350', '201812270400', '201812290400', '201901050350', '201901120400', '201901140410', '201901210350', '201901280400', '201902060410', '201902220420', '201903010400', '201903170400', '201904020410', '201904180420', '201905040420', '201905200430', '201909180410', '201909250400', '201910040350', '201910110400', '201910130400', '201910200350', '201910270340', '201910290350', '201911050350', '201911140350', '201911210350', '201911280340', '201911300350', '201912070350', '201912140350', '201912160350', '201912230350', '201912300400']  # 60.0_200 unknown

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
        mapping_scatter_all(roi_ahi_record, roi_misr_record, color_s, ahi_obs_time, roi_name + '_' + band_name)
