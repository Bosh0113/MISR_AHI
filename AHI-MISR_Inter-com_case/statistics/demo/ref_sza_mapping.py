import numpy
import matplotlib.pyplot as plt
from scipy.stats import linregress

deme_npy = r'E:\MISR_AHI_WS\230310\box_plot\45_0_band3_ref_sza_vza_variation.npy'
# deme_npy = r'E:\MISR_AHI_WS\230310\box_plot\26_0_band4_ref_sza_vza_variation.npy'

DEGREE_INTERNAL = 1


def line_plot(all_data):
    v_misr_sr_record = all_data[0]
    v_ahi_toa_record = all_data[1]
    v_ahi_sr_record = all_data[2]
    refer_sza_idx = numpy.arange(15, 80, DEGREE_INTERNAL)
    y_v_ahi_toa = numpy.zeros_like(refer_sza_idx)*1.
    y_v_ahi_sr = numpy.zeros_like(refer_sza_idx)*1.
    y_v_misr_sr = numpy.zeros_like(refer_sza_idx)*1.
    for v_item_idx in range(len(v_ahi_toa_record)):
        v_ahi_toa_item = v_ahi_toa_record[v_item_idx]
        if len(v_ahi_toa_item) > 0:
            v_ahi_toa_mean = round(numpy.median(v_ahi_toa_item), 3)
            y_v_ahi_toa[v_item_idx] = v_ahi_toa_mean
            v_ahi_sr_item = v_ahi_sr_record[v_item_idx]
            v_ahi_sr_mean = round(numpy.median(v_ahi_sr_item), 3)
            y_v_ahi_sr[v_item_idx] = v_ahi_sr_mean
            v_misr_sr_item = v_misr_sr_record[v_item_idx]
            v_misr_sr_mean = round(numpy.median(v_misr_sr_item), 3)
            y_v_misr_sr[v_item_idx] = v_misr_sr_mean

    y_v_ahi_toa[y_v_ahi_toa==0.] = numpy.NaN
    y_v_ahi_sr[y_v_ahi_sr==0.] = numpy.NaN
    y_v_misr_sr[y_v_misr_sr==0.] = numpy.NaN
    f, axs = plt.subplots()
    # print(y_v_ahi_toa)
    # print(y_v_ahi_sr)
    # print(y_v_misr_sr)
    axs.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_misr_sr, label='MISR SR')
    axs.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_ahi_toa, label='AHI TOA')
    axs.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_ahi_sr, label='AHI SR')
    plt.legend()
    plt.show()
    plt.clf()


def box_plot(all_data):
    fig, axs = plt.subplots()
    axs.grid(linestyle='--', linewidth=0.3)

    colors_map = ['green', 'blue', 'red']
    label_list = ['MISR SR', 'AHI TOA', 'AHI SR']
    for idx in range(len(all_data)):
        axs.boxplot(all_data[idx],
                    patch_artist=True,
                    showfliers=False,
                    boxprops=dict(facecolor=colors_map[idx],color=colors_map[idx], linewidth=0.5, alpha=0.2),
                    medianprops=dict(color=colors_map[idx], linewidth=1),
                    whiskerprops=dict(color=colors_map[idx], linewidth=0.5, alpha=0.3),
                    capprops=dict(color=colors_map[idx], linewidth=0.5, alpha=0.3))
    
    v_ahi_toa_record = all_data[0]
    v_ahi_sr_record = all_data[1]
    v_misr_sr_record = all_data[2]
    refer_sza_idx = numpy.arange(15, 80, DEGREE_INTERNAL)
    y_v_ahi_toa = numpy.zeros_like(refer_sza_idx)*1.
    y_v_ahi_sr = numpy.zeros_like(refer_sza_idx)*1.
    y_v_misr_sr = numpy.zeros_like(refer_sza_idx)*1.
    for v_item_idx in range(len(v_ahi_toa_record)):
        v_ahi_toa_item = v_ahi_toa_record[v_item_idx]
        if len(v_ahi_toa_item) > 0:
            v_ahi_toa_mean = round(numpy.median(v_ahi_toa_item), 3)
            y_v_ahi_toa[v_item_idx] = v_ahi_toa_mean
            v_ahi_sr_item = v_ahi_sr_record[v_item_idx]
            v_ahi_sr_mean = round(numpy.median(v_ahi_sr_item), 3)
            y_v_ahi_sr[v_item_idx] = v_ahi_sr_mean
            v_misr_sr_item = v_misr_sr_record[v_item_idx]
            v_misr_sr_mean = round(numpy.median(v_misr_sr_item), 3)
            y_v_misr_sr[v_item_idx] = v_misr_sr_mean

    y_v_ahi_toa[y_v_ahi_toa==0.] = numpy.NaN
    y_v_ahi_sr[y_v_ahi_sr==0.] = numpy.NaN
    y_v_misr_sr[y_v_misr_sr==0.] = numpy.NaN

    y_zip = [y_v_ahi_toa, y_v_ahi_sr, y_v_misr_sr]
    x_range = numpy.array([i for i in range((80-15)*int(1/DEGREE_INTERNAL))])
    for y_idx in range(len(y_zip)):
        y_data = y_zip[y_idx]
        mask_idx = ~numpy.isnan(y_data)
        v_slope, v_offset, v_r, v_p, v_std_err = linregress(x_range[mask_idx], y_data[mask_idx])
        print(v_slope, v_offset, v_r, v_p, v_std_err)
        y = v_slope*x_range+v_offset
        plt.plot(x_range, y, '--', color=colors_map[y_idx], label=label_list[y_idx], linewidth=0.8, alpha=0.5)

    axs.minorticks_on()
    x_minor_locator = plt.MultipleLocator(1)
    x_major_locator = plt.MultipleLocator(5)
    axs.xaxis.set_minor_locator(x_minor_locator)
    axs.xaxis.set_major_locator(x_major_locator)
    y_minor_locator = plt.MultipleLocator(0.01)
    y_major_locator = plt.MultipleLocator(0.05)
    axs.yaxis.set_minor_locator(y_minor_locator)
    axs.yaxis.set_major_locator(y_major_locator)

    axs.spines['right'].set_color('none')
    axs.spines['top'].set_color('none')

    axs.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=15)
    axs.tick_params(axis="x", which='major', length=5, direction='in', labelsize=15)
    axs.tick_params(axis="y", which='minor', length=5, direction='out', labelsize=15)
    axs.tick_params(axis="y", which='major', length=5, direction='out', labelsize=15)

    plt.xticks([i for i in range(0, (80-15), 5*int(1/DEGREE_INTERNAL))], numpy.arange(15, 80, 5*int(1/DEGREE_INTERNAL)))
    plt.xlim(5, 37.5)
    plt.ylim(0.02, 0.375)
    # plt.ylim(0.13, 0.485)
    plt.xlabel('SZA (°), VZA ≈ 26°, RAA ≈ 30°', size=18)
    plt.ylabel('Reflectance', size=18)
    plt.legend(markerscale=2, loc=2, fontsize='x-large')
    plt.show()


if __name__ == "__main__":
    npy_array = numpy.load(deme_npy, allow_pickle=True)
    print(npy_array)
    # line_plot(npy_array)
    box_plot(npy_array)