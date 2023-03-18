import os
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt

WORK_SPACE = r'E:\MISR_AHI_WS\230319'

PIXEL_PAIRS_MAX = 500
MONTH_LABEL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def display_pts(bots, labels):
    mapping_folder = os.path.join(WORK_SPACE, 'month_scatter')
    figure_folder = os.path.join(mapping_folder, str(PIXEL_PAIRS_MAX))
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)

    color_s = []
    for i in range(len(bots)):
        color_random = list(matplotlib.colors.XKCD_COLORS.items())[int(random.random()*900)][1]
        color_s.append(color_random)

    f, ax = plt.subplots()
    f.set_size_inches(12, 8)
    f.set_dpi(200)

    # ax = plt.axes()
    ax.grid(linestyle='--', linewidth=0.3)
    for idx in range(len(bots)):
        pts = bots[idx]
        ax.plot([i for i in range(12)], pts, '1', color=color_s[idx], label=labels[idx], markersize=25)

    ax.minorticks_on()
    x_minor_locator = plt.MultipleLocator(1)
    x_major_locator = plt.MultipleLocator(1)
    ax.xaxis.set_minor_locator(x_minor_locator)
    ax.xaxis.set_major_locator(x_major_locator)
    y_minor_locator = plt.MultipleLocator(0.1)
    y_major_locator = plt.MultipleLocator(0.1)
    ax.yaxis.set_minor_locator(y_minor_locator)
    ax.yaxis.set_major_locator(y_major_locator)

    ax.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=15)
    ax.tick_params(axis="x", which='major', length=5, direction='in', labelsize=15)
    ax.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=15)
    ax.tick_params(axis="y", which='major', length=5, direction='in', labelsize=15)

    plt.xticks([i for i in range(12)], MONTH_LABEL)
    plt.xlim((-0.5, 11.5))
    plt.ylim((0.02, 1.02))
    plt.xlabel('Month', size=18)
    plt.ylabel('AHI-MISR SR Slope', size=18)
    plt.legend(markerscale=0.5)
    plt.savefig(os.path.join(figure_folder, 'month_slope.png'))
    # plt.show()
    plt.clf()

def show_para(mon_para, match_type):
    slope_list = mon_para[0]
    r_list = mon_para[1]
    rmse_list = mon_para[2]

    band_labels = ['Band3', 'Band4']
    for idx in range(len(band_labels)):
        band_label = band_labels[idx]
        slope_month = slope_list[idx]
        r_month = r_list[idx]
        rmse_month = rmse_list[idx]
        print(match_type, band_label)
        print(slope_month)
        print(r_month)
        print(rmse_month)
    pass


if __name__ == "__main__":
    raa_month_para_npy = os.path.join(WORK_SPACE, '26_RAA_slope_r_rmse.npy')
    ray_month_para_npy = os.path.join(WORK_SPACE, '26_Ray_slope_r_rmse.npy')

    raa_month_para = numpy.load(raa_month_para_npy, allow_pickle=True)
    ray_month_para = numpy.load(ray_month_para_npy, allow_pickle=True)

    show_para(raa_month_para, 'RAA')
    show_para(ray_month_para, 'Ray')

    