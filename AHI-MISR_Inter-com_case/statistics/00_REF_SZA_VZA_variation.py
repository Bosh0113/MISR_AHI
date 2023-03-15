import os
import numpy
import re
import matplotlib.pyplot as plt
from scipy.stats import linregress

WORK_SPACE = os.getcwd()

DEGREE_INTERNAL = 1


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def box_plot(all_data):
    fig, axs = plt.subplots()
    axs.grid(linestyle='--', linewidth=0.3)

    colors_map = ['green', 'blue', 'red']
    label_list = ['MISR SR', 'AHI TOA', 'AHI SR']
    for idx in range(len(all_data)):
        axs.boxplot(all_data[idx],
                    patch_artist=True,
                    showfliers=False,
                    boxprops=dict(facecolor=colors_map[idx],color=colors_map[idx], linewidth=0.5, alpha=0.2),
                    medianprops=dict(color=colors_map[idx], linewidth=1),
                    whiskerprops=dict(color=colors_map[idx], linewidth=0.5, alpha=0.3),
                    capprops=dict(color=colors_map[idx], linewidth=0.5, alpha=0.3))
    
    v_ahi_toa_record = all_data[0]
    v_ahi_sr_record = all_data[1]
    v_misr_sr_record = all_data[2]
    refer_sza_idx = numpy.arange(15, 80, DEGREE_INTERNAL)
    y_v_ahi_toa = numpy.zeros_like(refer_sza_idx)*1.
    y_v_ahi_sr = numpy.zeros_like(refer_sza_idx)*1.
    y_v_misr_sr = numpy.zeros_like(refer_sza_idx)*1.
    for v_item_idx in range(len(v_ahi_toa_record)):
        v_ahi_toa_item = v_ahi_toa_record[v_item_idx]
        if len(v_ahi_toa_item) > 0:
            v_ahi_toa_mean = round(numpy.median(v_ahi_toa_item), 3)
            y_v_ahi_toa[v_item_idx] = v_ahi_toa_mean
            v_ahi_sr_item = v_ahi_sr_record[v_item_idx]
            v_ahi_sr_mean = round(numpy.median(v_ahi_sr_item), 3)
            y_v_ahi_sr[v_item_idx] = v_ahi_sr_mean
            v_misr_sr_item = v_misr_sr_record[v_item_idx]
            v_misr_sr_mean = round(numpy.median(v_misr_sr_item), 3)
            y_v_misr_sr[v_item_idx] = v_misr_sr_mean

    y_v_ahi_toa[y_v_ahi_toa==0.] = numpy.NaN
    y_v_ahi_sr[y_v_ahi_sr==0.] = numpy.NaN
    y_v_misr_sr[y_v_misr_sr==0.] = numpy.NaN

    y_zip = [y_v_ahi_toa, y_v_ahi_sr, y_v_misr_sr]
    x_range = numpy.array([i for i in range((80-15)*int(1/DEGREE_INTERNAL))])
    for y_idx in range(len(y_zip)):
        y_data = y_zip[y_idx]
        mask_idx = ~numpy.isnan(y_data)
        v_slope, v_offset, v_r, v_p, v_std_err = linregress(x_range[mask_idx], y_data[mask_idx])
        print(v_slope, v_offset)
        y = v_slope*x_range+v_offset
        plt.plot(x_range, y, '--', color=colors_map[y_idx], label=label_list[y_idx], linewidth=0.8, alpha=0.5)

    axs.minorticks_on()
    x_minor_locator = plt.MultipleLocator(1)
    x_major_locator = plt.MultipleLocator(5)
    axs.xaxis.set_minor_locator(x_minor_locator)
    axs.xaxis.set_major_locator(x_major_locator)
    y_minor_locator = plt.MultipleLocator(0.01)
    y_major_locator = plt.MultipleLocator(0.05)
    axs.yaxis.set_minor_locator(y_minor_locator)
    axs.yaxis.set_major_locator(y_major_locator)

    axs.spines['right'].set_color('none')
    axs.spines['top'].set_color('none')

    axs.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=15)
    axs.tick_params(axis="x", which='major', length=5, direction='in', labelsize=15)
    axs.tick_params(axis="y", which='minor', length=5, direction='out', labelsize=15)
    axs.tick_params(axis="y", which='major', length=5, direction='out', labelsize=15)

    plt.xticks([i for i in range(0, (80-15), 5*int(1/DEGREE_INTERNAL))], numpy.arange(15, 80, 5*int(1/DEGREE_INTERNAL)))
    plt.xlim(5, 37.5)
    # plt.ylim(0.02, 0.375)
    # plt.ylim(0.13, 0.485)
    plt.xlabel('SZA (°), VZA ≈ 26°, RAA ≈ 30°', size=18)
    plt.ylabel('Reflectance', size=18)
    plt.legend(markerscale=2, loc=2, fontsize='x-large')
    plt.show()
    plt.clf()


if __name__ == "__main__":
    # folder_l1_list = ['26', '45', '60', '70']
    folder_l1_list = ['26']
    folder_l2_list = ['0']
    lc_type = '7'   # Open Shrublands
    # lc_type = '10'   # Grasslands

    ws_folder = os.path.join(WORK_SPACE, 'ref_sza_vza_variation_' + lc_type)
    if not os.path.exists(ws_folder):
        os.makedirs(ws_folder)

    record_str = ''
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
                v_misr_sr_record = []
                for i in range((80-15)*int(1/DEGREE_INTERNAL)):
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
                                    if roi_raa > 25. or roi_raa < 35.:
                                        # get v: AHI-TOA MISR-SR AHI-SR
                                        # AHI-TOA
                                        roi_toa_array = ac_record['roi_ahi_data']
                                        # AHI-SR MISR-SR
                                        roi_file_list = os.listdir(roi_folder_path)
                                        v_re = obs_time + '_' + band_label + r'_(\d+).npy'
                                        v_ahi_toa = None
                                        v_ahi_sr = None
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
                                                roi_toa_array = roi_toa_array * mask_array
                                                roi_ahi_toa = roi_toa_array.flatten()
                                                v_ahi_toa = roi_ahi_toa[~numpy.isnan(roi_ahi_toa)]
                                                # v_ahi_toa = round(numpy.array(roi_ahi_toa).mean(), 3)
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
                                            v_misr_sr_record_sza = v_misr_sr_record[rec_idx]
                                            v_misr_sr_record_sza = numpy.append(v_misr_sr_record_sza, v_misr_sr)
                                            v_misr_sr_record[rec_idx] = v_misr_sr_record_sza
                numpy.save(os.path.join(ws_folder, folder_l1 + '_' + folder_l2 + '_' + band_label + '_ref_sza_vza_variation.npy'), [v_misr_sr_record, v_ahi_toa_record, v_ahi_sr_record])
                # mapping
                # box_plot(numpy.array([v_misr_sr_record, v_ahi_toa_record, v_ahi_sr_record]))