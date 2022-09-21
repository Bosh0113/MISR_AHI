import os
import numpy

MISR_CAMERA_INDEX = {
    '0.0': [4],
    '26.1': [3, 5],
    '45.6': [2, 6],
    '60.0': [1, 7],
    '70.5': [0, 8]
}


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220920'
    MISRVZAs = [0.0, 26.1, 45.6, 60.0, 70.5]
    for vza_idx in range(len(MISRVZAs)):
        misr_vza_str = str(MISRVZAs[vza_idx])
        point_locations_npy_filename = os.path.join(workspace, misr_vza_str + '_point4search.npy')
        search_cood = numpy.load(point_locations_npy_filename)
        for cood_point in search_cood:
            lon4search = cood_point[0]
            lat4search = cood_point[1]
            camera_idx_array = MISR_CAMERA_INDEX[misr_vza_str]
            for camera_idx in camera_idx_array:
                # Full Match Screening
                pass
