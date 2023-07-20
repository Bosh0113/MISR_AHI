import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt

WORK_SPACE = '/disk1/workspace/20230707/03_Ray_RAA'

PIXEL_PAIRS_MAX = 500
# MONTH_LABEL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# southern earth
MONTH_LABEL = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']


def display_pts_b3_b4(sr_list, slope_list, r_list, rmse_list, match_type):
    plt.figure(figsize=(8,6))
    ax = plt.axes()
    ax.grid(linestyle='--', linewidth=0.3)
#     ax.set_title(match_type + '-matches', loc='left', fontstyle='oblique', fontsize='medium')

    color_s = ['#FF4500', '#8B0000']
    # no-data mask
    f_temp = sr_list[0]
    f_temp = numpy.insert(f_temp, [0, len(f_temp)], [f_temp[-1:], f_temp[0]])
    if match_type == 'RAA':
        for sr_idx in range(len(f_temp)):
            if f_temp[sr_idx] <= 0:
                ax.axvline(sr_idx-1, color='whitesmoke', linewidth=50.0)
    # display values
    band_labels = ['Band3', 'Band4']
    for idx in range(len(band_labels)):
        band_label = band_labels[idx]
        
        sr_month = sr_list[idx]
        sr_month[sr_month <= 0] = numpy.nan
        sr_month = numpy.insert(sr_month, [0, len(sr_month)], [sr_month[-1:], sr_month[0]])
        
        slope_month = slope_list[idx]
        slope_month[slope_month <= 0] = numpy.nan
        r_month = r_list[idx]
        r_month[r_month <= 0] = numpy.nan
        rmse_month = rmse_list[idx]
        rmse_month[rmse_month <= 0] = numpy.nan
        

        ax.plot([i for i in range(-1,13,1)], sr_month, '-', color=color_s[idx], label=band_label + '_LSR')
        ax.plot([i for i in range(12)], slope_month, '1', color=color_s[idx], label=band_label + '_Slope', markersize=20)
        ax.plot([i for i in range(12)], r_month, '_', color=color_s[idx], label=band_label + '_r', markersize=10)
        ax.plot([i for i in range(12)], rmse_month, 'x', color=color_s[idx], label=band_label + '_RMSE', markersize=5)
    

    ax.minorticks_on()
    x_minor_locator = plt.MultipleLocator(1)
    x_major_locator = plt.MultipleLocator(1)
    ax.xaxis.set_minor_locator(x_minor_locator)
    ax.xaxis.set_major_locator(x_major_locator)
    y_minor_locator = plt.MultipleLocator(0.1)
    y_major_locator = plt.MultipleLocator(0.1)
    ax.yaxis.set_minor_locator(y_minor_locator)
    ax.yaxis.set_major_locator(y_major_locator)

    ax.tick_params(axis="x", which='minor', length=5, direction='out', labelsize=12)
    ax.tick_params(axis="x", which='major', length=5, direction='out', labelsize=12)
    ax.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=12)
    ax.tick_params(axis="y", which='major', length=5, direction='in', labelsize=12)

    plt.xticks([i for i in range(12)], MONTH_LABEL)
    plt.xlim((-0.5, 11.5))
    plt.ylim((0.0, 1.08))
    plt.xlabel('Month', size=14)
    plt.ylabel('AHI-MISR LSR, Slope, r & RMSE', size=14)
    plt.legend(markerscale=0.5, loc=10, bbox_to_anchor=[0.5, 0.50], ncol=2)
    plt.savefig(WORK_SPACE + '/VZA26_Ray_month.png', dpi=600)
    # plt.savefig(WORK_SPACE + '/VZA26_RAA_month.png', dpi=600)
    # plt.show()
    plt.clf()


def show_para(mon_para, match_type):
    sr_list = mon_para[0]
    slope_list = mon_para[1]
    r_list = mon_para[2]
    rmse_list = mon_para[3]
    
    sr_w2w = numpy.hstack((sr_list[:, 6:], sr_list[:, :6]))
    slope_w2w = numpy.hstack((slope_list[:, 6:], slope_list[:, :6]))
    r_w2w = numpy.hstack((r_list[:, 6:], r_list[:, :6]))
    rmse_w2w = numpy.hstack((rmse_list[:, 6:], rmse_list[:, :6]))
    
    display_pts_b3_b4(sr_w2w, slope_w2w, r_w2w, rmse_w2w, match_type)


if __name__ == "__main__":
    ray_month_para_npy = os.path.join(WORK_SPACE, '26_Ray_sr_slope_r_rmse_offset.npy')
    raa_month_para_npy = os.path.join(WORK_SPACE, '26_RAA_sr_slope_r_rmse_offset.npy')

    ray_month_para = numpy.load(ray_month_para_npy, allow_pickle=True)
    raa_month_para = numpy.load(raa_month_para_npy, allow_pickle=True)

    show_para(ray_month_para, 'Ray')
    # show_para(raa_month_para, 'RAA')

    