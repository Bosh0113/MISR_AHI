import os
import numpy

ws = r'C:\Work\AHI_MISR\20230114'

ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')
raa_matched_record_npy = os.path.join(ws, 'AHI_MISR_RAA-matched_50km.npy')

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
    bar_record = [[],[],[],[],[],[],[],[],[],[],[],[]]    # latitude range
    for record_item in matched_record:
        roi_loc = record_item['location']
        roi_matched_info = record_item['matched_infos']
        roi_lat = roi_loc[1]
        camera_angle_idx = int(roi_matched_info[0][camera_idx_record_idx])
        camera_angle = CAMERA_ANGLE[camera_angle_idx]
        lat_array_idx =  int(12 - (roi_lat + 60) /10)   # 12 group with 10° internal
        bar_record[lat_array_idx].append(camera_angle)
    return bar_record


def main():
    ray_matched_record = numpy.load(ray_matched_record_npy, allow_pickle=True)
    raa_matched_record = numpy.load(raa_matched_record_npy, allow_pickle=True)

    ray_bar_record = get_bar_record(ray_matched_record, 2)
    raa_bar_record = get_bar_record(raa_matched_record, 1)
    print(ray_bar_record)
    print(raa_bar_record)


if __name__ == "__main__":
    main()