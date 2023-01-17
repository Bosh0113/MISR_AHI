import os
import math
import numpy as np
import matplotlib.pyplot as plt

# ws = r'C:\Work\AHI_MISR\20230114'
ws = r'D:\Work_PhD\MISR_AHI_WS\230116'

MCD12Q1_006_10KM_npy = os.path.join(ws, 'MCD12Q1_006_10km.npy')
ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
raa_matched_record_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')


def get_bar_data(lc_map, matched_record):
    lc_counts = np.zeros((17, ))
    for matched_info in matched_record:
        loc = matched_info['location']
        lon = loc[0]
        lat = loc[1]
        lc_lon_idx = int(lon - 85)
        lc_lat_idx = int(60 - lat)
        lc_code = int(lc_map[lc_lat_idx][lc_lon_idx])
        lc_counts[lc_code] = lc_counts[lc_code] + 1
    return lc_counts


# temp before updated value available
def temp_fuction(raa_bar_data, ray_bar_data):
    for item_idx in range(len(raa_bar_data)):
        raa_bar_v = raa_bar_data[item_idx]
        ray_bar_v = ray_bar_data[item_idx]
        if raa_bar_v < ray_bar_v:
            raa_bar_data[item_idx] = ray_bar_v + 1
    return raa_bar_data


def fig_mapping(ray_values, raa_values):
    # MCD12Q1 labels
    lc_labels = [
        'Water', 'Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest', 'Deciduous Needleleaf Forest', 'Deciduous Broadleaf Forest', 'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 'Woody Savannas', 'Savannas', 'Grasslands',
        'Permanent Wetlands', 'Croplands', 'Urban and Built-Up', 'Cropland/Natual Vegation', 'Snow and Ice', 'Barren'
    ]
    # colormap
    lc_colormap = ['#82D3FE', '#4B9347', '#5CD250', '#A0D353', '#9AFF97', '#84B480', '#F897D0', '#F4DEB9', '#EFE784', '#BBA337', '#EEAA59', '#649FDD', '#FBF271', '#FF3334', '#9B7140', '#CCFFFF', '#BFBFBF']

    value_max = 1500

    theta_internal = 0.01
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    fig.set_size_inches(6, 4)
    fig.set_dpi(100)

    for v_idx in range(len(ray_values)):
        # y-grid line
        ax.plot(np.arange(0, 2 * np.pi * 3 / 4, theta_internal), np.ones((len(np.arange(0, 2 * np.pi * 3 / 4, theta_internal)), )) * (v_idx + 1), linestyle=(5, (10, 3)), linewidth=1, alpha=0.5, color=lc_colormap[v_idx])
        # ray-value
        value = ray_values[v_idx]
        line_angle = (value / value_max) * (2 * np.pi * 3 / 4)
        theta = np.arange(0, line_angle, theta_internal)
        r = np.ones((len(np.arange(0, line_angle, theta_internal)), )) * (v_idx + 1)
        ax.plot(theta, r, color=lc_colormap[v_idx], linewidth=12)
        # raa-value
        value = raa_values[v_idx]
        line_angle = (value / value_max) * (2 * np.pi * 3 / 4)
        theta = np.arange(0, line_angle, theta_internal)
        r = np.ones((len(np.arange(0, line_angle, theta_internal)), )) * (v_idx + 1)
        ax.plot(theta, r, color=lc_colormap[v_idx], alpha=0.7, linewidth=12)

    ax.set_theta_offset(np.pi / 2)
    x_major_locator = plt.MultipleLocator(1 / 6 * np.pi)
    y1_major_locator = plt.MultipleLocator(value_max)
    ax.xaxis.set_major_locator(x_major_locator)
    ax.tick_params(axis="x", which='major', length=5, labelsize=10)
    ax.yaxis.set_major_locator(y1_major_locator)
    ax.set_thetamax(3 / 4 * 360)
    theta_array = np.arange(0, (2 * np.pi * 3 / 4) + 1 / 7 * np.pi, 1 / 6 * np.pi)
    theta_maj_labels = np.arange(0, value_max + value_max / 3, value_max / 3)
    label90 = r'$' + str(round(int(theta_maj_labels[1]) / math.pow(10, len(str(int(theta_maj_labels[1]))) - 1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[1]))) - 1) + '$'
    label180 = r'$' + str(round(int(theta_maj_labels[2]) / math.pow(10, len(str(int(theta_maj_labels[2]))) - 1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[2]))) - 1) + '$'
    label270 = r'$' + str(round(int(theta_maj_labels[3]) / math.pow(10, len(str(int(theta_maj_labels[3]))) - 1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[3]))) - 1) + '$'
    theta_labels = ['Count of Pixels: 0', '', '', label90, '', '', label180, '', '', label270]
    ax.set_xticks(theta_array, theta_labels)

    labels = []
    angles = [0, 0, 0, -90, 0, 0, 0, 0, 0, 0]
    offset_idx = -1
    offset_x = [0.25, 0, 0, 0, 0, 0, 0, 0, 0, -0.05]
    offset_y = [0.04, 0, 0, 0.06, 0, 0, 0.06, 0, 0, 0.1]
    for label, angle in zip(ax.get_xticklabels(), angles):
        offset_idx += 1
        x, y = label.get_position()
        lab = ax.text(x + offset_x[offset_idx], y + offset_y[offset_idx], label.get_text(), transform=label.get_transform(), ha=label.get_ha(), va=label.get_va())
        lab.set_rotation(angle)
        labels.append(lab)
    ax.set_xticklabels([])
    ax.spines["polar"].set_visible(False)

    ax.set_rticks(np.arange(1, 18, 1), lc_labels)
    ax.set_rlabel_position(0)

    ax.grid(linestyle='--', linewidth=0.6, axis='x')
    ax.yaxis.grid(False)

    plt.show()


def main():
    modis_lc = np.load(MCD12Q1_006_10KM_npy, allow_pickle=True)
    ray_matches = np.load(ray_matched_record_npy, allow_pickle=True)
    raa_matches = np.load(raa_matched_record_npy, allow_pickle=True)

    ray_bar_data = get_bar_data(modis_lc, ray_matches)
    raa_bar_data = get_bar_data(modis_lc, raa_matches)

    print(ray_bar_data)
    print(raa_bar_data)
    raa_bar_data = temp_fuction(raa_bar_data, ray_bar_data)

    fig_mapping(ray_bar_data, raa_bar_data)


if __name__ == "__main__":
    main()