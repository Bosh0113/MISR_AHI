import os
import numpy
import re
import matplotlib.pyplot as plt
from scipy.stats import linregress
import random

WORK_SPACE = os.getcwd()

DEGREE_INTERNAL = 1
PIXEL_PAIRS_MAX = 50


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


# random
def array_random_count(o_array):
    n_array = []
    for array_item_idx in range(len(o_array)):
        array_item = o_array[array_item_idx]
        if len(array_item) > PIXEL_PAIRS_MAX:
            # random pairs mapping
            index_array = random.sample([idx for idx in range(len(array_item))], PIXEL_PAIRS_MAX)
            index_array = numpy.sort(index_array).tolist()
            array_item = array_item[index_array]
        n_array.append(array_item)
    return n_array


if __name__ == "__main__":
    folder_l1_list = ['26']
    lc_type = '7'   # Open Shrublands
    # folder_l1_list = ['45']
    # lc_type = '12'   # Croplands
    folder_l2_list = ['0']

    ws_folder = os.path.join(WORK_SPACE, 'ref_sza_vza_variation_' + lc_type + '_random_south_toa_sr')
    if not os.path.exists(ws_folder):
        os.makedirs(ws_folder)

    refer_sza_idx = numpy.arange(15, 80, DEGREE_INTERNAL)
    for folder_l1 in folder_l1_list:
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            # stat
            band_labels = ['band3', 'band4']
            for band_label in band_labels:
                print(folder_l1, folder_l2, band_label)
                v_ahi_toa_record = []
                v_ahi_sr_record = []
                v_misr_toa_record = []
                v_misr_sr_record = []
                for i in range((80-15)*int(1/DEGREE_INTERNAL)):
                    v_ahi_toa_record.append([])
                    v_ahi_sr_record.append([])
                    v_misr_toa_record.append([])
                    v_misr_sr_record.append([])
                # max_sza = 0
                # min_sza = 90
                # max_raa = 0
                # min_raa = 180
                for roi_folder in roi_folder_list:
                    roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                    roi_infos = roi_folder.split('_')
                    roi_lat = float(roi_infos[2])
                    if roi_lat < 0:
                        roi_lc_idx = roi_infos[1]   # land cover idx
                        if roi_lc_idx == lc_type:
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
                                        if roi_raa > 5. and roi_raa < 35.:  # RAA=20±15
                                            # get v: AHI-TOA MISR-SR AHI-SR
                                            # AHI-TOA
                                            roi_toa_array = ac_record['roi_ahi_data']
                                            # AHI-SR MISR-SR
                                            roi_file_list = os.listdir(roi_folder_path)
                                            v_re = obs_time + '_' + band_label + r'_(\d+).npy'
                                            v_ahi_toa = None
                                            v_ahi_sr = None
                                            v_misr_toa = None
                                            v_misr_sr = None
                                            for roi_file in roi_file_list:
                                                v_matchObj = re.search(v_re, roi_file)
                                                if v_matchObj:
                                                    v_record_npy = os.path.join(roi_folder_path, roi_file)
                                                    v_record = numpy.load(v_record_npy, allow_pickle=True)[0]
                                                    roi_ahi_sr = numpy.array(v_record['ahi_sr2misr']).flatten()
                                                    v_ahi_sr = roi_ahi_sr[~numpy.isnan(roi_ahi_sr)]
                                                    # v_ahi_sr = round(roi_ahi_sr.mean(), 3)
                                                    roi_misr_sr_array = numpy.array(v_record['misr_v3'])
                                                    roi_misr_sr = roi_misr_sr_array.flatten()
                                                    v_misr_sr = roi_misr_sr[~numpy.isnan(roi_misr_sr)]
                                                    # v_misr_sr = round(roi_misr_sr.mean(), 3)
                                                    mask_array = numpy.zeros_like(roi_misr_sr_array)
                                                    mask_array[roi_misr_sr_array > 0.0] = 1.
                                                    mask_array[mask_array == 0.0] = numpy.NaN
                                                    
                                                    roi_ahi_toa_array = numpy.array(v_record['ahi_toa2misr'])
                                                    roi_misr_toa_array = numpy.array(v_record['misr_toa'])
                                                    roi_ahi_toa_array = roi_ahi_toa_array * mask_array
                                                    roi_ahi_toa = roi_ahi_toa_array.flatten()
                                                    v_ahi_toa = roi_ahi_toa[~numpy.isnan(roi_ahi_toa)]
                                                    roi_misr_toa_array = roi_misr_toa_array * mask_array
                                                    roi_misr_toa = roi_misr_toa_array.flatten()
                                                    v_misr_toa = roi_misr_toa[~numpy.isnan(roi_misr_toa)]
                                                    break

                                            rec_idx = find_nearest_index(refer_sza_idx, roi_sza)
                                            # Value y
                                            if (v_ahi_sr is not None) and (v_misr_sr is not None):
                                                v_ahi_toa_record_sza = v_ahi_toa_record[rec_idx]
                                                v_ahi_toa_record_sza = numpy.append(v_ahi_toa_record_sza, v_ahi_toa)
                                                v_ahi_toa_record[rec_idx] = v_ahi_toa_record_sza
                                                v_ahi_sr_record_sza = v_ahi_sr_record[rec_idx]
                                                v_ahi_sr_record_sza = numpy.append(v_ahi_sr_record_sza, v_ahi_sr)
                                                v_ahi_sr_record[rec_idx] = v_ahi_sr_record_sza
                                                v_misr_toa_record_sza = v_misr_toa_record[rec_idx]
                                                v_misr_toa_record_sza = numpy.append(v_misr_toa_record_sza, v_misr_sr)
                                                v_misr_toa_record[rec_idx] = v_misr_toa_record_sza
                                                v_misr_sr_record_sza = v_misr_sr_record[rec_idx]
                                                v_misr_sr_record_sza = numpy.append(v_misr_sr_record_sza, v_misr_sr)
                                                v_misr_sr_record[rec_idx] = v_misr_sr_record_sza
                # random
                v_misr_toa_record = array_random_count(v_misr_toa_record)
                v_misr_sr_record = array_random_count(v_misr_sr_record)
                v_ahi_toa_record = array_random_count(v_ahi_toa_record)
                v_ahi_sr_record = array_random_count(v_ahi_sr_record)
                # save
                numpy.save(os.path.join(ws_folder, folder_l1 + '_' + folder_l2 + '_' + band_label + '_ref_sza_vza_variation.npy'), [v_misr_toa_record, v_misr_sr_record, v_ahi_toa_record, v_ahi_sr_record])