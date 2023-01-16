import os
import numpy
import matplotlib.pyplot as plt

ws = r'C:\Work\AHI_MISR\20230114'

MCD12Q1_006_10KM_npy = os.path.join(ws, 'MCD12Q1_006_10km.npy')
ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
raa_matched_record_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')
# ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched.npy')

MCD12Q1_LC_Labels = ['Water', 'Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest', 'Deciduous Needleleaf Forest', 'Deciduous Broadleaf Forest', 'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 'Woody Savannas', 'Savannas', 'Grasslands', 'Permanent Wetlands', 'Croplands', 'Urban and Built-Up', 'Cropland/Natual Vegation', 'Snow and Ice', 'Barren']

LC_SIZE = 0.1


def get_bar_data(lc_map, matched_record):
    lc_counts = numpy.zeros((17,))
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


def main():
    modis_lc = numpy.load(MCD12Q1_006_10KM_npy, allow_pickle=True)
    ray_matches = numpy.load(ray_matched_record_npy, allow_pickle=True)
    raa_matches = numpy.load(raa_matched_record_npy, allow_pickle=True)

    ray_bar_data = get_bar_data(modis_lc, ray_matches)
    raa_bar_data = get_bar_data(modis_lc, raa_matches)

    print(ray_bar_data)
    print(raa_bar_data)
    raa_bar_data = temp_fuction(raa_bar_data, ray_bar_data)

    # mapping
    f, ax1 = plt.subplots()
    f.set_size_inches(6, 4)
    f.set_dpi(100)
    bar_width = 0.35
    x_array = numpy.arange(0, 17, 1)
    ax1.bar(x_array - bar_width/2, ray_bar_data, width=bar_width, label='Ray-matches')
    ax1.bar(x_array + bar_width/2, raa_bar_data, width=bar_width, label='Ray-matches')

    # 2K monitor
    plt.show()


if __name__ == "__main__":
    main()