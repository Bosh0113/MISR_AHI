# from cProfile import label
# from threading import stack_size
# from turtle import position
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import seaborn

degree_count = 5

# MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
matched_npy_filename = r'E:\MISR_AHI_WS\230308\mapping\AHI_MISR_Ray-screened_10km.npy'


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def angle_count(matched_info, info_idx):
    angle_record = numpy.zeros((90*degree_count+1,))
    angle_list = numpy.arange(0, 90+1/degree_count, 1/degree_count)
    angle_list = angle_list * 1.
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        vza_paths = []
        vza_sums = []
        vza_counts = []
        for pt_matched_item in pt_matched_info:
            misr_path = pt_matched_item[0]
            if misr_path not in vza_paths:
                vza_paths.append(misr_path)
                vza_sums.append(0)
                vza_counts.append(0)
            vza_record_idx = vza_paths.index(misr_path)
            vza = float(pt_matched_item[info_idx])
            vza_sums[vza_record_idx] = vza_sums[vza_record_idx] + vza
            vza_counts[vza_record_idx] = vza_counts[vza_record_idx] + 1
        for vza_r_idx in range(len(vza_paths)):
            vza_mean = vza_sums[vza_r_idx]/vza_counts[vza_r_idx]
            vza_angle_idx = find_nearest_index(angle_list, vza_mean)
            angle_record[vza_angle_idx] = angle_record[vza_angle_idx] + 1
    return angle_record


def mapping(misr_angle_pixel_record, ahi_angle_pixel_record):
    x_range = numpy.arange(0, 90+1/degree_count, 1/degree_count)
    plt.plot(x_range, misr_angle_pixel_record, 'b-', linewidth=0.4, label='MISR VZA')
    plt.plot(x_range, ahi_angle_pixel_record, 'r-', linewidth=0.4, label='AHI VZA')
    plt.fill_between(x_range, misr_angle_pixel_record, alpha=0.5)
    plt.fill_between(x_range, ahi_angle_pixel_record, alpha=0.5)
    seaborn.distplot(misr_angle_pixel_record, hist=True, kde=True)
    plt.xlim(0, 90)
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid()
    plt.show()


def prepare_kde(o_list):
    n_list = numpy.array([])
    for angle_item_idx in range(len(o_list)):
        angle_v_count = o_list[angle_item_idx]
        angle_v = angle_item_idx/degree_count
        angle_ex = numpy.ones((int(angle_v_count),))
        angle_ex_list = angle_ex*angle_v
        n_list = numpy.append(n_list, angle_ex_list)
    return n_list


def kde_mapping(misr_angle_pixel_record, ahi_angle_pixel_record):
    kde_misr_list = prepare_kde(misr_angle_pixel_record)
    kde_ahi_list = prepare_kde(ahi_angle_pixel_record)

    f, ax1 = plt.subplots()
    f.set_size_inches(6, 4)
    f.set_dpi(100)
    ax1.grid(linestyle='--', linewidth=0.6)
    ax1.set_xlabel('VZA (°)', fontsize=18)

    ax1.hist(kde_misr_list, bins=numpy.arange(0, 90+1/degree_count, 1/degree_count), color='blueviolet', alpha=0.5, label='MISR VZA Count of Pixel')
    ax1.hist(kde_ahi_list, bins=numpy.arange(0, 90+1/degree_count, 1/degree_count), color='firebrick', alpha=0.5, label='AHI VZA Count of Pixel')
    ax1.minorticks_on()
    x_major_locator = plt.MultipleLocator(10)
    x_minor_locator = plt.MultipleLocator(1)
    y1_major_locator = plt.MultipleLocator(500)
    y1_minor_locator = plt.MultipleLocator(100)
    ax1.xaxis.set_major_locator(x_major_locator)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    ax1.yaxis.set_major_locator(y1_major_locator)
    ax1.yaxis.set_minor_locator(y1_minor_locator)
    ax1.tick_params(axis="y", which='minor', length=3, labelsize=10)
    ax1.tick_params(axis="y", which='major', length=5, labelsize=15)
    ax1.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
    sf1 = ScalarFormatter(useMathText=True)
    sf1.set_powerlimits((0,0))
    ax1.yaxis.set_major_formatter(sf1)
    ax1.yaxis.get_offset_text().set(size=15)
    ax1.tick_params(axis="x", which='minor', length=3, labelsize=10)
    ax1.tick_params(axis="x", which='major', length=5, labelsize=15)
    ax1.set_ylabel('Count of Pixel', fontsize=18)
    ax1.set_ylim(0, 3000)
    ax1.legend(loc=2, fontsize='large')

    ax2 = ax1.twinx()
    seaborn.distplot(kde_misr_list, bins=numpy.arange(0, 90+1/degree_count, 1/degree_count), ax=ax2, hist=False, kde=True, kde_kws={'linewidth':'1.0', 'color':'blue'}, label='MISR VZA Density of Distribution')
    seaborn.distplot(kde_ahi_list, bins=numpy.arange(0, 90+1/degree_count, 1/degree_count), ax=ax2, hist=False, kde=True, kde_kws={'linewidth':'1.0', 'color':'red'}, label='AHI VZA Density of Distribution')
    y2_major_locator = plt.MultipleLocator(0.015)
    y2_minor_locator = plt.MultipleLocator(0.005)
    ax2.yaxis.set_major_locator(y2_major_locator)
    ax2.yaxis.set_minor_locator(y2_minor_locator)
    ax2.tick_params(axis="y", which='minor', length=3, labelsize=10)
    ax2.tick_params(axis="y", which='major', length=5, labelsize=15)
    ax2.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
    sf2 = ScalarFormatter(useMathText=True)
    sf2.set_powerlimits((0,0))
    ax2.yaxis.set_major_formatter(sf2)
    ax2.yaxis.get_offset_text().set(size=15)
    ax2.set_ylabel('Density of Distribution', fontsize=18)
    ax2.set_ylim(0.0, 0.09)
    ax2.legend(loc=1, fontsize='large')


    plt.xlim(0, 90)
    plt.show()


def main():
    matched_info = numpy.load(matched_npy_filename, allow_pickle=True)

    misr_angle_pixel_record = angle_count(matched_info, 5)
    ahi_angle_pixel_record = angle_count(matched_info, 6)

    # mapping(misr_angle_pixel_record, ahi_angle_pixel_record)
    kde_mapping(misr_angle_pixel_record, ahi_angle_pixel_record)


if __name__ == "__main__":
    main()