import os
import numpy
import re

WORK_SPACE = os.getcwd()

PIXEL_PAIRS_MAX = 4000

if __name__ == "__main__":

    folder_l1_list = ['0', '26', '45', '60', '70']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            # each png
            misr_SR_band3_item_list = []
            ahi_SR_band3_item_list = []
            misr_SR_band4_item_list = []
            ahi_SR_band4_item_list = []
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                roi_file_list = os.listdir(roi_folder_path)
                roi_misr_SR_band3_list = []
                roi_ahi_SR_band3_list = []
                roi_misr_SR_band4_list = []
                roi_ahi_SR_band4_list = []
                for roi_file in roi_file_list:
                    matchObj = re.search(r'(\d+)_band(\d+)_(\d+).npy', str(roi_file))
                    if matchObj:
                        # ahi_time_str = matchObj.group(1)
                        band_str = matchObj.group(2)
                        # camera_idx_str = matchObj.group(3)
                        SR_npy_path = os.path.join(roi_folder_path, roi_file)
                        ROI_SR_pair = numpy.load(SR_npy_path, allow_pickle=True)[0]
                        misr_sr = ROI_SR_pair['misr_v3']
                        ahi_sr = ROI_SR_pair['ahi_sr2misr']
                        x_3Darray_np_1d = misr_sr.flatten()
                        x_3Darray_np_1d = x_3Darray_np_1d[~numpy.isnan(x_3Darray_np_1d)]
                        y_3Darray_np_1d = ahi_sr.flatten()
                        y_3Darray_np_1d = y_3Darray_np_1d[~numpy.isnan(y_3Darray_np_1d)]
                        if band_str == '3':
                            roi_misr_SR_band3_list.extend(x_3Darray_np_1d)
                            roi_ahi_SR_band3_list.extend(y_3Darray_np_1d)
                        if band_str == '4':
                            roi_misr_SR_band4_list.extend(x_3Darray_np_1d)
                            roi_ahi_SR_band4_list.extend(y_3Darray_np_1d)
                    # keep pixel count same
                    if len(roi_misr_SR_band3_list) == len(roi_misr_SR_band4_list):
                        misr_SR_band3_item_list.extend(roi_misr_SR_band3_list)
                        ahi_SR_band3_item_list.extend(roi_ahi_SR_band3_list)
                        misr_SR_band4_item_list.extend(roi_misr_SR_band4_list)
                        ahi_SR_band4_item_list.extend(roi_ahi_SR_band4_list)

            print(folder_l1, folder_l2)
            print(len(misr_SR_band3_item_list), len(ahi_SR_band3_item_list), len(misr_SR_band4_item_list), len(ahi_SR_band4_item_list))