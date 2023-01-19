import os
import numpy as np

ws = r'D:\Work_PhD\MISR_AHI_WS\230119'

ray_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
raa_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')
Ray_RAA_loc_txt = os.path.join(ws, 'Ray_RAA_loc.txt')

if __name__ == "__main__":
    ray_matches = np.load(ray_matched_record_50km_npy, allow_pickle=True)
    raa_matches = np.load(raa_matched_record_50km_npy, allow_pickle=True)

    ray_loc_str = []
    for ray_item in ray_matches:
        ray_loc = ray_item['location']
        ray_loc_str.append(str(ray_loc))

    Ray_RAA_locs = ''
    for raa_item in raa_matches:
        raa_loc_str = str(raa_item['location'])
        raa_loc = raa_item['location'].tolist()
        raa_matches = raa_item['matched_infos']
        camera_angle = []
        for raa_match in raa_matches:
            camera_idx = raa_match[2]
            if camera_idx not in camera_angle:
                camera_angle.append(camera_idx)
        if len(camera_angle) > 1:
            if raa_loc_str in ray_loc_str:
                if camera_angle.count("4"):
                    if len(camera_angle) == 3:
                        camera_angle.remove("4")
                        Ray_RAA_locs += str(raa_loc[0]) + ',' + str(raa_loc[1]) + ',' + ','.join(camera_angle) + ',' + str(len(raa_matches)) + '\n'
                else:
                    Ray_RAA_locs += str(raa_loc[0]) + ',' + str(raa_loc[1]) + ',' + ','.join(camera_angle) + ',' + str(len(raa_matches)) + '\n'
    with open(Ray_RAA_loc_txt, 'w') as f:
        f.write(Ray_RAA_locs)