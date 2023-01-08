from cProfile import label
from threading import stack_size
from turtle import position
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import seaborn


# MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
matched_npy_filename = r'C:\Work\AHI_MISR\20221210\AHI_MISR_Ray-matched.npy'


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def frequency_count(matched_info):
    freq_record = numpy.zeros((60,))
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        matched_count = len(pt_matched_info)
        record_idx = matched_count - 1
        freq_record[record_idx] = freq_record[record_idx] + 1
    return freq_record


def kde_mapping(pixel_record):

    f, ax1 = plt.subplots()
    f.set_size_inches(6, 4)
    f.set_dpi(100)
    ax1.grid(linestyle='--', linewidth=0.6)
    ax1.set_xlabel('Count of Matched data pairs', fontsize=18)
    ax1.bar(numpy.arange(1, 61), pixel_record)
    ax1.minorticks_on()
    x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(1)
    y1_major_locator = plt.MultipleLocator(1000)
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
    ax1.set_ylim(0, 13000)
    # ax1.legend(loc=2, fontsize='large')

    plt.xlim(0, 60)
    plt.show()


def main():
    matched_info = numpy.load(matched_npy_filename, allow_pickle=True)

    pixel_record = frequency_count(matched_info)

    kde_mapping(pixel_record)


if __name__ == "__main__":
    main()