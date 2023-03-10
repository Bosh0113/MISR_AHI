# for python 3.6
import os
import numpy
import shutil

WORK_SPACE = os.getcwd()


if __name__ == "__main__":

    folder_l1_list = ['0', '26', '45']
    folder_l2_list = ['0', '1']

    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                roi_infos = roi_folder.split('_')
                roi_name = roi_folder
                misr_vza_str = roi_infos[0]
                misr_ray_matched_npy_filename = os.path.join(roi_folder_path, roi_name + '_matched_record.npy')

                matched_record = numpy.load(misr_ray_matched_npy_filename, allow_pickle=True)
                roi_valuable_record = []
                record_str = ''
                if len(matched_record) > 0:
                    matched_roi_info = matched_record[0]
                    roi_misr_infos = matched_roi_info['roi_misr_infos']
                    for roi_misr_info in roi_misr_infos:
                        matched_info = roi_misr_info['matched_info']
                        is_valuable = 1
                        if is_valuable:
                            roi_valuable_record.append(matched_info)
                            record_str += str(matched_info) + '\n'
                    if len(roi_valuable_record) > 0:
                        record4AHI_AC_npy = os.path.join(roi_folder_path, roi_name + '_4AC_record.npy')
                        numpy.save(record4AHI_AC_npy, numpy.array(roi_valuable_record))    # save result as txt
                        with open(os.path.join(roi_folder_path, roi_name + '_4AC_record.txt'), 'w') as f:
                            f.write(record_str)
                    else:
                        shutil.rmtree(roi_folder_path)
