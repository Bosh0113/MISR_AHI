import os
import random
import matplotlib
import matplotlib.pyplot as plt

WORK_SPACE = os.getcwd()
# WORK_SPACE = r'E:\MISR_AHI_WS\230304'

MONTH_LABEL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def display_pts(bots, labels):
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
    plt.savefig(os.path.join(WORK_SPACE, 'month_slope.png'))
    # plt.show()
    plt.clf()


if __name__ == "__main__":
    slope_list = [
        [0.49,0.58,0.62,0.65,0.7,0.68,0.69,0.7,0.61,0.5,0.43,0.51],
        [0.57,0.62,0.65,0.8,0.97,0.85,0.85,0.87,0.84,0.69,0.47,0.67],
        [0.17,0.31,0.54,0.56,0.13,0.68,0.66,0.,0.42,0.54,0.14,0.33],
        [0.08,0.52,0.77,0.84,0.36,0.91,0.98,0.,0.39,0.83,0.26,0.43],
        [0.,0.35,0.56,0.68,0.57,0.47,0.97,1.22,0.63,0.32,0.25,0.34],
        [0.,0.34,0.59,0.82,0.9,0.73,0.84,0.78,0.78,0.21,0.27,0.38]
    ]
    slope_labels = [
        '26_0_band3', '26_0_band4',
        '45_0_band3', '45_0_band4',
        '45_1_band3', '45_1_band4'
    ]

    display_pts(slope_list, slope_labels)