import os
import numpy
import re

WORK_SPACE = os.getcwd()


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


if __name__ == "__main__":
    folder_l1_list = ['26', '45', '60', '70']
    folder_l2_list = ['0']

    ws_folder = os.path.join(WORK_SPACE, 'ref_sza_vza_variation')
    if not os.path.exists(ws_folder):
        os.makedirs(ws_folder)

    record_str = ''
    refer_sza_idx = numpy.arange(15, 80, 0.5)
    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            # stat
            band_labels = ['band3', 'band4']
            band_label = 'band3'
            print(folder_l1, folder_l2)
            v_ahi_toa_record = []
            v_ahi_sr_record = []
            v_misr_sr_record = []
            for i in range((80-15)*2):  # 0.5 internal
                v_ahi_toa_record.append([])
                v_ahi_sr_record.append([])
                v_misr_sr_record.append([])
            # max_sza = 0
            # min_sza = 90
            # max_raa = 0
            # min_raa = 180
            for roi_folder in roi_folder_list:
                roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                roi_infos = roi_folder.split('_')
                roi_lc_idx = roi_infos[1]   # land cover idx
                ac_record_path = os.path.join(roi_folder_path, 'AHI_AC_PARAMETER')
                if os.path.exists(ac_record_path):
                    ac_list = os.listdir(ac_record_path)
                    for ac_npy in ac_list:
                        band_re = r'(\S+)' + band_label + '.npy'
                        ac_matchObj = re.search(band_re, ac_npy)
                        if ac_matchObj:
                            ac_npy_path = os.path.join(ac_record_path, ac_npy)
                            ac_record = numpy.load(ac_npy_path, allow_pickle=True)[0]
                            obs_time = ac_record['obs_time']
                            roi_vza_array = ac_record['roi_vza']
                            roi_vza = round(roi_vza_array.mean(), 3)
                            roi_sza_array = ac_record['roi_sza']
                            roi_sza = round(roi_sza_array.mean(), 3)
                            roi_raa_array = ac_record['roi_raa']
                            roi_raa = round(roi_raa_array.mean(), 3)

                #             if roi_sza > max_sza:
                #                 max_sza = roi_sza
                #             if roi_sza < min_sza:
                #                 min_sza = roi_sza
                #             if roi_raa > max_raa:
                #                 max_raa = roi_raa
                #             if roi_raa < min_raa:
                #                 min_raa = roi_raa
                            if roi_raa > 25. or roi_raa < 35.:
                                # get v: AHI-TOA MISR-SR AHI-SR
                                # AHI-TOA
                                roi_toa_array = ac_record['roi_ahi_data']
                                v_ahi_toa = round(numpy.array(roi_toa_array).mean(), 3)
                                # AHI-SR MISR-SR
                                roi_file_list = os.listdir(roi_folder_path)
                                v_re = obs_time + '_' + band_label + r'_(\d+).npy'
                                v_ahi_sr = None
                                v_misr_sr = None
                                for roi_file in roi_file_list:
                                    v_matchObj = re.search(v_re, roi_file)
                                    if v_matchObj:
                                        v_record_npy = os.path.join(roi_folder_path, roi_file)
                                        v_record = numpy.load(v_record_npy, allow_pickle=True)[0]
                                        roi_ahi_sr = v_record['ahi_sr2misr']
                                        v_ahi_sr = round(numpy.array(roi_ahi_sr).mean(), 3)
                                        roi_misr_sr = v_record['misr_v3']
                                        v_misr_sr = round(numpy.array(roi_misr_sr).mean(), 3)
                                        break

                                rec_idx = find_nearest_index(refer_sza_idx, roi_sza)
                                # Value y
                                if (v_ahi_sr is not None) and (v_misr_sr is not None):
                                    v_ahi_toa_record_sza = v_ahi_toa_record[rec_idx]
                                    v_ahi_toa_record_sza.append(v_ahi_toa)
                                    v_ahi_toa_record[rec_idx] = v_ahi_toa_record_sza
                                    v_ahi_sr_record_sza = v_ahi_sr_record[rec_idx]
                                    v_ahi_sr_record_sza.append(v_ahi_sr)
                                    v_ahi_sr_record[rec_idx] = v_ahi_sr_record_sza
                                    v_misr_sr_record_sza = v_misr_sr_record[rec_idx]
                                    v_misr_sr_record_sza.append(v_misr_sr)
                                    v_misr_sr_record[rec_idx] = v_misr_sr_record_sza

            y_v_ahi_toa = numpy.zeros_like(refer_sza_idx)
            y_v_ahi_sr = numpy.zeros_like(refer_sza_idx)
            y_v_misr_sr = numpy.zeros_like(refer_sza_idx)
            record_str += folder_l1 + '_' + folder_l2 + '_' + band_label + '\n'
            v_ahi_toa_str =''
            v_ahi_sr_str =''
            v_misr_sr_str =''
            for v_item_idx in range(len(v_ahi_toa_record)):
                v_ahi_toa_item = v_ahi_toa_record[v_item_idx]
                v_ahi_toa_mean = round(numpy.array(v_ahi_toa_item).mean(), 3)
                y_v_ahi_toa[v_item_idx] = v_ahi_toa_mean
                v_ahi_toa_str += str(v_ahi_toa_mean) + '\t'
                v_ahi_sr_item = v_ahi_sr_record[v_item_idx]
                v_ahi_sr_mean = round(numpy.array(v_ahi_sr_item).mean(), 3)
                y_v_ahi_sr[v_item_idx] = v_ahi_sr_mean
                v_ahi_sr_str += str(v_ahi_sr_mean) + '\t'
                v_misr_sr_item = v_misr_sr_record[v_item_idx]
                v_misr_sr_mean = round(numpy.array(v_misr_sr_item).mean(), 3)
                y_v_misr_sr[v_item_idx] = v_misr_sr_mean
                v_misr_sr_str += str(v_misr_sr_mean) + '\t'
            
            record_str += v_ahi_toa_str + '\n' + v_ahi_sr_str + '\n' + v_misr_sr_str + '\n'
            print(y_v_ahi_toa)
            print(y_v_ahi_sr)
            print(y_v_misr_sr)
            numpy.save(os.path.join(ws_folder, folder_l1 + '_' + folder_l2 + '_' + band_label + '_ref_sza_vza_variation.npy'), numpy.array([y_v_ahi_toa, y_v_ahi_sr, y_v_misr_sr]))

            # print('sza', min_sza, max_sza)
            # print('raa', min_raa, max_raa)
    # save result as txt
    with open(os.path.join(ws_folder, 'ref_sza_vza_variation.txt'), 'w') as f:
        f.write(record_str)