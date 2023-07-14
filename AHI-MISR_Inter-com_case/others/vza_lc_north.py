import os
import numpy

WORK_SPACE = os.getcwd()

def show_print(p_list):
    p_str = ''
    for p_s in p_list:
        p_str += str(p_s) + '\t'
    print(p_str)


if __name__ == "__main__":

    folder_l1_list = ['45']
    folder_l2_list = ['0', '1']
    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            lc_count = numpy.zeros((17,))
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_infos = roi_folder.split('_')
                roi_lat = float(roi_infos[2])
                if roi_lat > 0:
                    mcd_lc_idx = int(roi_infos[1])
                    ac_folder = os.path.join(folder_l2_path, roi_folder + '/AHI_AC_PARAMETER')
                    if os.path.exists(ac_folder):
                        obs_c = len(os.listdir(ac_folder))
                        lc_count[mcd_lc_idx] = lc_count[mcd_lc_idx] + obs_c
            lc_persent = numpy.zeros((17,))
            for lc_c_idx in range(len(lc_count)):
                lc_persent[lc_c_idx] = round(lc_count[lc_c_idx]/lc_count.sum()*100, 1)
            print(folder_l1, folder_l2)
            show_print([i for i in range(17)])
            show_print(lc_count)
            show_print(lc_persent)
