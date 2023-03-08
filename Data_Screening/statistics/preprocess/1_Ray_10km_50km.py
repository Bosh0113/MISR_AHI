import os
import numpy

ws = r'E:\MISR_AHI_WS\230308\Ray_screen_ScatterAng'
ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-screened_10km.npy')
ray_matched_record_npy_50km = os.path.join(ws, 'AHI_MISR_Ray-screened_50km.npy')

ROI_DISTANCE = 0.5
if __name__ == "__main__":
    roi_lats = numpy.arange(60. - ROI_DISTANCE / 2, -60, -ROI_DISTANCE)
    roi_lons = numpy.arange(85. + ROI_DISTANCE / 2, 205, ROI_DISTANCE)
    ray_matched_record = numpy.load(ray_matched_record_npy, allow_pickle=True)
    # print(len(ray_matched_record))
    ray_matched_record_50km = []
    for ray_matched_record_item in ray_matched_record:
        loc = ray_matched_record_item['location']
        loc_lon = round(loc[0], 2)
        loc_lat = round(loc[1], 2)
        if loc_lon in roi_lons and loc_lat in roi_lats:
            ray_matched_record_50km.append(ray_matched_record_item)
    # print(len(ray_matched_record_50km))
    numpy.save(ray_matched_record_npy_50km, numpy.array(ray_matched_record_50km))

# import os
# import numpy as np

# # ws = r'D:\Work_PhD\MISR_AHI_WS\230118'
# ws = r'C:\Work\AHI_MISR\20230119'


# ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched.npy')
# ray_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
# raa_matched_record_50km_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')

# if __name__ == "__main__":
#     ray_matches = np.load(ray_matched_record_npy, allow_pickle=True)
#     raa_matches = np.load(raa_matched_record_50km_npy, allow_pickle=True)
    
#     raa_loc_str = []
#     ray_record_50km = []
#     for raa_item in raa_matches:
#         raa_loc = raa_item['location']
#         raa_loc_str.append(str(raa_loc))
#     for ray_item in ray_matches:
#         ray_loc = ray_item['location']
#         if str(ray_loc) in raa_loc_str:
#             ray_record_50km.append(ray_item)
#     np.save(ray_matched_record_50km_npy, ray_record_50km)