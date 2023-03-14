import os
import numpy
import shutil

WORK_SPACE = os.getcwd()

DIFF_VZA_THRESHOLD = 1.
DIFF_VAA_THRESHOLD = 5.


def get_raa(aa1, aa2):
    raa = 0
    diff = abs(aa1 - aa2)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def is_vza_vaa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa):
    if abs(misr_vza - ahi_vza) <= DIFF_VZA_THRESHOLD:
        diff_vaa = get_raa(misr_vaa, ahi_vaa)
        if diff_vaa <= DIFF_VAA_THRESHOLD:
            return True
        else:
            return False
    else:
        return False


if __name__ == "__main__":

    folder_l1_list = ['26', '45', '60', '70']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_name = roi_folder
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                ac_npy_folder = os.path.join(roi_folder_path, 'AHI_AC_PARAMETER')
                if os.path.exists(ac_npy_folder):
                    matched_record_npy = os.path.join(roi_folder_path, roi_name + '_matched_record.npy')
                    matched_record = numpy.load(matched_record_npy, allow_pickle=True)
                    if len(matched_record) > 0:
                        matched_roi_info = matched_record[0]
                        roi_misr_infos = matched_roi_info['roi_misr_infos']
                        for roi_misr_info in roi_misr_infos:
                            matched_info = roi_misr_info['matched_info']
                            ahi_obs_time = matched_info[4]
                            misr_vza = float(matched_info[5])
                            ahi_vza = float(matched_info[6])
                            misr_vaa = float(matched_info[7])
                            ahi_vaa = float(matched_info[8])
                            if not is_vza_vaa_matched(misr_vza, misr_vaa, ahi_vza, ahi_vaa):
                                print(ahi_obs_time, misr_vza, ahi_vza, misr_vaa, ahi_vaa)
                                ac_b3_npy = os.path.join(ac_npy_folder, ahi_obs_time + '_ac_band3.npy')
                                if os.path.exists(ac_b3_npy):
                                    os.remove(ac_b3_npy)
                                ac_b4_npy = os.path.join(ac_npy_folder, ahi_obs_time + '_ac_band4.npy')
                                if os.path.exists(ac_b4_npy):
                                    os.remove(ac_b4_npy)
                    ac_file_list = os.listdir(ac_npy_folder)
                    if len(ac_file_list) < 1:
                        shutil.rmtree(roi_folder_path)
                else:
                    print('remove:', roi_folder_path)
                    shutil.rmtree(roi_folder_path)


                    