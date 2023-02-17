import os
import math
import numpy as np
import matplotlib.pyplot as plt

ws = r'D:\MISR_AHI_WS\230217'

MCD12Q1_006_10KM_npy = os.path.join(ws, 'MCD12Q1_006_10km.npy')
ray_matched_record_npy = os.path.join(ws, 'Ray_MODIS_land_lonlat_10km.npy')

LC_SIZE = 0.1


def get_tab_data(lc_map, matched_record):
    lc_counts = np.zeros((17, ))
    for matched_info in matched_record:
        loc = matched_info
        lon = loc[0]
        lat = loc[1]
        lc_lon_idx = int((lon - 85)/LC_SIZE)
        lc_lat_idx = int((60 - lat)/LC_SIZE)
        lc_code = int(lc_map[lc_lat_idx][lc_lon_idx])
        lc_counts[lc_code] = lc_counts[lc_code] + 1
    return lc_counts


def tab_show(ray_values):
    # MCD12Q1 labels
    lc_labels = [
        'Water', 'Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest', 'Deciduous Needleleaf Forest', 'Deciduous Broadleaf Forest', 'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 'Woody Savannas', 'Savannas', 'Grasslands',
        'Permanent Wetlands', 'Croplands', 'Urban and Built-Up', 'Cropland/Natual Vegation', 'Snow and Ice', 'Barren'
    ]
    
    for idx in range(len(ray_values)):
        if ray_values[idx] > 0.0:
            print(lc_labels[idx], int(ray_values[idx]))
    # Water 517
    # Evergreen Broadleaf Forest 8383
    # Woody Savannas 2836
    # Savannas 321
    # Grasslands 57
    # Permanent Wetlands 294
    # Croplands 386
    # Urban and Built-Up 100
    # Cropland/Natual Vegation 639
    # Barren 2


def main():
    modis_lc = np.load(MCD12Q1_006_10KM_npy, allow_pickle=True)
    ray_matches = np.load(ray_matched_record_npy, allow_pickle=True)

    ray_tab_data = get_tab_data(modis_lc, ray_matches)

    tab_show(ray_tab_data)


if __name__ == "__main__":
    main()