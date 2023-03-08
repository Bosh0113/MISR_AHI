import os
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

ws = r'E:\MISR_AHI_WS\230308\mapping'

ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-screened_50km.npy')
raa_matched_record_npy = os.path.join(ws, 'AHI_MISR_RAA-screened_50km.npy')

MISR_ANGLE = [0.0, 26.1, 45.6, 60.0, 70.5]

CAMERA_ANGLE = {
    0: 70.5,
    1: 60.0,
    2: 45.6,
    3: 26.1,
    4: 0.0,
    5: 26.1,
    6: 45.6,
    7: 60.0,
    8: 70.5
}


def get_bar_record(matched_record, camera_idx_record_idx):
    bar_record = [[], [], [], [], [], [], [], [], [], [], [], []]    # latitude range
    for record_item in matched_record:
        roi_loc = record_item['location']
        roi_matched_info = record_item['matched_infos']
        roi_lat = roi_loc[1]
        camera_angle_idx = int(roi_matched_info[0][camera_idx_record_idx])
        camera_angle = CAMERA_ANGLE[camera_angle_idx]
        lat_array_idx = int(12 - (roi_lat + 60) / 10)   # 12 group with 10° internal
        bar_record[lat_array_idx].append(camera_angle)
    return bar_record


def get_bar_data(bar_record):
    bar_data = []
    for bar_record_item in bar_record:
        bar_data_item = []
        for m_angle in MISR_ANGLE:
            angle_count = bar_record_item.count(m_angle)
            bar_data_item.append(angle_count)
        bar_data.append(bar_data_item)
    return bar_data


def mapping_double_bar_angle(ray_bar_data, raa_bar_data):
    f, ax1 = plt.subplots()
    f.set_size_inches(6, 4)
    f.set_dpi(100)

    bar_width = 0.35
    x_array = numpy.arange(1, 13, 1)
    ray_bar_data_T = numpy.array(ray_bar_data).T
    raa_bar_data_T = numpy.array(raa_bar_data).T
    # print(numpy.flipud(ray_bar_data_T))
    # print(numpy.flipud(raa_bar_data_T))

    ray_bottom_array = numpy.zeros((12,))
    raa_bottom_array = numpy.zeros((12,))
    bar_hatchs = ['..', '//', '\\\\', '/', '\\']
    bar_colors = ['lavenderblush', 'lavender', 'lightcyan', 'oldlace', 'mistyrose']
    bar_labels = ['0.0°', '26.1°', '45.6°', '60.0°', '70.5°']
    for bar_lat_idx in range(len(ray_bar_data_T)):
        ray_bar_lat = ray_bar_data_T[bar_lat_idx]
        raa_bar_lat = raa_bar_data_T[bar_lat_idx]
        ax1.bar(x_array - bar_width/2, ray_bar_lat, width=bar_width, color=bar_colors[bar_lat_idx], bottom=ray_bottom_array, edgecolor='black', hatch=bar_hatchs[bar_lat_idx], label=bar_labels[bar_lat_idx])
        ax1.bar(x_array + bar_width/2, raa_bar_lat, width=bar_width, color=bar_colors[bar_lat_idx], bottom=raa_bottom_array, edgecolor='black', hatch=bar_hatchs[bar_lat_idx])
        ray_bottom_array = ray_bottom_array + ray_bar_lat
        raa_bottom_array = raa_bottom_array + raa_bar_lat

    # mapping
    ax1.grid(linestyle='--', linewidth=0.6, axis='y')
    ax1.set_xlabel('Latitude Ranges', fontsize=18)
    ax1.minorticks_on()
    x_minor_locator = plt.MultipleLocator(1)
    x_major_locator = plt.MultipleLocator(1)
    y1_minor_locator = plt.MultipleLocator(20)
    y1_major_locator = plt.MultipleLocator(100)
    x_labels = ['60°N-50°N', '50°N-40°N', '40°N-30°N', '30°N-20°N', '20°N-10°N', '10°N-0°', '0°-10°S', '10°S-20°S', '20°S-30°S', '30°S-40°S', '40°S-50°S', '50°S-60°S']
    ax1.set_xticks(x_array, x_labels)
    ax1.tick_params(axis='x', rotation=20)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    ax1.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_major_locator(y1_major_locator)
    ax1.yaxis.set_minor_locator(y1_minor_locator)
    ax1.tick_params(axis="y", which='minor', length=3, labelsize=10)
    ax1.tick_params(axis="y", which='major', length=5, labelsize=15)
    ax1.ticklabel_format(style='sci', scilimits=(0, 0), axis='y')
    sf1 = ScalarFormatter(useMathText=True)
    sf1.set_powerlimits((0, 0))
    ax1.yaxis.set_major_formatter(sf1)
    ax1.yaxis.get_offset_text().set(size=15)
    ax1.tick_params(axis="x", which='minor', length=3, labelsize=10)
    ax1.tick_params(axis="x", which='major', length=5, labelsize=10)
    ax1.set_ylabel('Count of Pixel', fontsize=18)
    ax1.set_ylim(0, 1600)
    ax1.legend(loc=1, fontsize='large', title='Camera angle of MISR')
    # 2K monitor
    plt.show()


def main():
    ray_matched_record = numpy.load(ray_matched_record_npy, allow_pickle=True)
    raa_matched_record = numpy.load(raa_matched_record_npy, allow_pickle=True)

    ray_bar_record = get_bar_record(ray_matched_record, 2)
    raa_bar_record = get_bar_record(raa_matched_record, 2)

    ray_bar_data = get_bar_data(ray_bar_record)
    raa_bar_data = get_bar_data(raa_bar_record)

    mapping_double_bar_angle(ray_bar_data, raa_bar_data)


if __name__ == "__main__":
    main()
