import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt

WORK_SPACE = r'E:\PhD_Workspace\MISR_AHI_WS\230319'

PIXEL_PAIRS_MAX = 500
MONTH_LABEL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def display_pts_b3_b4(slope_list, r_list, rmse_list, match_type):
    plt.figure(figsize=(8,6))
    ax = plt.axes()
    ax.grid(linestyle='--', linewidth=0.3)
    ax.set_title(match_type + '-matches', loc='left', fontstyle='oblique', fontsize='medium')

    color_s = ['#FF4500', '#8B0000']
    
    band_labels = ['Band3', 'Band4']
    for idx in range(len(band_labels)):
        band_label = band_labels[idx]
        slope_month = slope_list[idx]
        slope_month[slope_month <= 0] = -10
        r_month = r_list[idx]
        rmse_month = rmse_list[idx]
        rmse_month[rmse_month <= 0] = -10
        # print(match_type, band_label)
        # print(slope_month)
        # print(r_month)
        # print(rmse_month)

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
    plt.ylim((0.0, 1.05))
    plt.xlabel('Month', size=14)
    plt.ylabel('AHI-MISR LSR Slope, r & RMSE', size=14)
    plt.legend(markerscale=0.5, loc=10, bbox_to_anchor=[0.5, 0.25], ncol=2)
    # plt.savefig(r'E:\PhD_Workspace\MISR_AHI_WS\230502\VZA26_Ray_month.png', dpi=600)
    plt.savefig(r'E:\PhD_Workspace\MISR_AHI_WS\230502\VZA26_RAA_month.png', dpi=600)
    # plt.show()
    plt.clf()


def show_para(mon_para, match_type):
    slope_list = mon_para[0]
    r_list = mon_para[1]
    rmse_list = mon_para[2]
    display_pts_b3_b4(slope_list, r_list, rmse_list, match_type)


if __name__ == "__main__":
    ray_month_para_npy = os.path.join(WORK_SPACE, '26_Ray_slope_r_rmse.npy')
    raa_month_para_npy = os.path.join(WORK_SPACE, '26_RAA_slope_r_rmse.npy')

    ray_month_para = numpy.load(ray_month_para_npy, allow_pickle=True)
    raa_month_para = numpy.load(raa_month_para_npy, allow_pickle=True)

    # show_para(ray_month_para, 'Ray')
    show_para(raa_month_para, 'RAA')

    