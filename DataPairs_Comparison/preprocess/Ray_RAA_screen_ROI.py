import os
import numpy as np

ws = r'D:\Work_PhD\MISR_AHI_WS\230118'


ray_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
raa_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')

if __name__ == "__main__":
    ray_matches = np.load(ray_matched_record_50km_npy, allow_pickle=True)
    raa_matches = np.load(raa_matched_record_50km_npy, allow_pickle=True)

    ray_loc_str = []
    raa_loc_str = []
    for ray_item in ray_matches:
        ray_loc = ray_item['location']
        ray_loc_str.append(str(ray_loc))

    for raa_item in raa_matches:
        raa_loc = raa_item['location']
        raa_loc_str.append(str(raa_loc))

    for ray_loc_str_item in ray_loc_str:
        if ray_loc_str_item not in raa_loc_str:
            print(ray_loc_str_item)