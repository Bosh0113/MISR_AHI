import os

WORK_SPACE = os.getcwd()

if __name__ == "__main__":

    folder_l1_list = ['0', '26', '45', '60', '70']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_name = roi_folder
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                record4AHI_AC_npy = os.path.join(roi_folder_path, roi_name + '_4AC_record.npy')
                record4AHI_AC_txt = os.path.join(roi_folder_path, roi_name + '_4AC_record.txt')
                if os.path.exists(record4AHI_AC_npy):
                    os.remove(record4AHI_AC_npy)
                if os.path.exists(record4AHI_AC_txt):
                    os.remove(record4AHI_AC_txt)
                    