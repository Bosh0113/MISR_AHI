import os
import numpy
import re
import random
from scipy.stats import gaussian_kde, pearsonr
from sklearn.metrics import mean_squared_error, r2_score
import math
import matplotlib.pyplot as plt

WORK_SPACE = os.getcwd()

PIXEL_PAIRS_MAX = 300

MONTH_LABEL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

MONTH_SOUTH2NORTH = {    # south -> north
    '01': '07',
    '02': '08',
    '03': '09',
    '04': '10',
    '05': '11',
    '06': '12',
    '07': '01',
    '08': '02',
    '09': '03',
    '10': '04',
    '11': '05',
    '12': '06'
}


def identifer(data):
    down,up = numpy.nanpercentile(data,[0,75])
    IQR = up-down
    lower_limit = down - 1.5*IQR
    upper_limit = up + 1.5*IQR
    result = numpy.where(data > upper_limit,numpy.nan, data)
    result = numpy.where(result < lower_limit,numpy.nan, result)
    return result


def mapping_scatter(Y, X, figure_title='demo', band_name='band3', axis_min=0.0, axis_max=0.5):
    # filter

    if band_name == 'band3':
        axis_max = 0.3

    lim_x = numpy.copy(X)
    lim_y = numpy.copy(Y)
    lim_x[lim_x > axis_max] = numpy.nan
    lim_y[lim_y > axis_max] = numpy.nan
    lim_mask = (lim_x*lim_y)*0+1
    temp_x = lim_x*lim_mask
    temp_y = lim_y*lim_mask
    temp_x = temp_x[~numpy.isnan(temp_x)]
    temp_y = temp_y[~numpy.isnan(temp_y)]

    diff_array = abs(numpy.array(temp_y)-numpy.array(temp_x))/abs(numpy.minimum(numpy.array(temp_x), numpy.array(temp_y)))
    diff_array_filtered = numpy.array(identifer(diff_array))
    show_x = (diff_array_filtered*0+1)*temp_x
    show_y = (diff_array_filtered*0+1)*temp_y
    X = show_x[~numpy.isnan(show_x)]
    Y = show_y[~numpy.isnan(show_y)]
    
    k, b = numpy.polyfit(X, Y, deg=1)
    rmse = math.sqrt(mean_squared_error(X, Y))
    r_, p = pearsonr(X, Y)

    # slope r RMSE
    return k, r_, rmse, b


if __name__ == "__main__":

    folder_type_list = ['RAA', 'Ray']
    folder_l1_list = ['26']
    folder_l2_list = ['0', '1']

    for folder_type in folder_type_list:
        folder_type_path = os.path.join(WORK_SPACE, folder_type)
        for folder_l1 in folder_l1_list:
            folder_l1_path = os.path.join(folder_type_path, folder_l1)
            month_slope_b3 = numpy.zeros((12,))
            month_r_b3 = numpy.zeros((12,))
            month_rmse_b3 = numpy.zeros((12,))
            month_offset_b3 = numpy.zeros((12,))
            month_slope_b4 = numpy.zeros((12,))
            month_r_b4 = numpy.zeros((12,))
            month_rmse_b4 = numpy.zeros((12,))
            month_offset_b4 = numpy.zeros((12,))
            for month_idx in range(len(MONTH_LABEL)):
                month = MONTH_LABEL[month_idx]
                # each png
                misr_SR_band3_item_list = []
                ahi_SR_band3_item_list = []
                misr_SR_band4_item_list = []
                ahi_SR_band4_item_list = []
                for folder_l2 in folder_l2_list:
                    folder_l2_path = os.path.join(folder_l1_path, folder_l2)
                    roi_folder_list = os.listdir(folder_l2_path)
                    for roi_folder in roi_folder_list:
                        roi_infos = roi_folder.split('_')
                        roi_lat = float(roi_infos[2])
                        
                        is_south_roi = 0
                        if roi_lat < 0:
                            is_south_roi = 1

                        roi_folder_path = os.path.join(folder_l2_path, roi_folder)
                        roi_file_list = os.listdir(roi_folder_path)
                        roi_misr_SR_band3_list = []
                        roi_ahi_SR_band3_list = []
                        roi_misr_SR_band4_list = []
                        roi_ahi_SR_band4_list = []
                        for roi_file in roi_file_list:
                            matchObj = re.search(r'(\d+)_band(\d+)_(\d+).npy', str(roi_file))
                            if matchObj:
                                ahi_time_str = matchObj.group(1)
                                band_str = matchObj.group(2)
                                # camera_idx_str = matchObj.group(3)

                                obs_month = ahi_time_str[4:6]
                                if is_south_roi:
                                    obs_month = MONTH_SOUTH2NORTH[obs_month]
                                obs_month_idx = int(obs_month) - 1

                                if obs_month_idx == month_idx:
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

                print('Random NO.:', PIXEL_PAIRS_MAX)
                print(folder_l1)
                print('MISR_SR_Band3_NO.', 'AHI_SR_Band3_NO.', 'MISR_SR_Band4_NO.', 'AHI_SR_Band4_NO.')
                print(len(misr_SR_band3_item_list), len(ahi_SR_band3_item_list), len(misr_SR_band4_item_list), len(ahi_SR_band4_item_list))

                if len(misr_SR_band3_item_list) > PIXEL_PAIRS_MAX:
                    # random pairs mapping
                    index_array = random.sample([idx for idx in range(len(misr_SR_band3_item_list))], PIXEL_PAIRS_MAX)
                    index_array = numpy.sort(index_array).tolist()

                    misr_SR_band3_pts = numpy.array(misr_SR_band3_item_list)
                    show_misr_sr_b3 = misr_SR_band3_pts[index_array]
                    ahi_SR_band3_pts = numpy.array(ahi_SR_band3_item_list)
                    show_ahi_sr_b3 = ahi_SR_band3_pts[index_array]
                    figure_title = folder_l1 + '_b3' + '_' + str(month_idx) + month + '_' + str(PIXEL_PAIRS_MAX)
                    slope_b3, r_b3, rmse_b3, offset_b3 = mapping_scatter(show_ahi_sr_b3, show_misr_sr_b3, figure_title, 'band3')
                    month_slope_b3[month_idx] = round(slope_b3, 2)
                    month_r_b3[month_idx] = round(r_b3, 2)
                    month_rmse_b3[month_idx] = round(rmse_b3, 3)
                    month_offset_b3[month_idx] = round(offset_b3, 2)

                    misr_SR_band4_pts = numpy.array(misr_SR_band4_item_list)
                    show_misr_sr_b4 = misr_SR_band4_pts[index_array]
                    ahi_SR_band4_pts = numpy.array(ahi_SR_band4_item_list)
                    show_ahi_sr_b4 = ahi_SR_band4_pts[index_array]
                    figure_title = folder_l1 + '_b4' + '_' + str(month_idx) + month + '_' + str(PIXEL_PAIRS_MAX)
                    slope_b4, r_b4, rmse_b4, offset_b4 = mapping_scatter(show_ahi_sr_b4, show_misr_sr_b4, figure_title, 'band4')
                    month_slope_b4[month_idx] = round(slope_b4, 2)
                    month_r_b4[month_idx] = round(r_b4, 2)
                    month_rmse_b4[month_idx] = round(rmse_b4, 3)
                    month_offset_b4[month_idx] = round(offset_b4, 2)
                
                else:
                    # all pairs mapping
                    pairs_no = len(misr_SR_band3_item_list)
                    if pairs_no > 3:

                        misr_SR_band3_pts = numpy.array(misr_SR_band3_item_list)
                        ahi_SR_band3_pts = numpy.array(ahi_SR_band3_item_list)
                        figure_title = folder_l1 + '_b3' + '_' + str(month_idx) + month + '_' + str(pairs_no)
                        slope_b3, r_b3, rmse_b3, offset_b3 = mapping_scatter(ahi_SR_band3_pts, misr_SR_band3_pts, figure_title, 'band3')
                        month_slope_b3[month_idx] = round(slope_b3, 2)
                        month_r_b3[month_idx] = round(r_b3, 2)
                        month_rmse_b3[month_idx] = round(rmse_b3, 3)
                        month_offset_b3[month_idx] = round(offset_b3, 2)

                        misr_SR_band4_pts = numpy.array(misr_SR_band4_item_list)
                        ahi_SR_band4_pts = numpy.array(ahi_SR_band4_item_list)
                        figure_title = folder_l1 + '_b4' + '_' + str(month_idx) + month + '_' + str(pairs_no)
                        slope_b4, r_b4, rmse_b4, offset_b4 = mapping_scatter(ahi_SR_band4_pts, misr_SR_band4_pts, figure_title, 'band4')
                        month_slope_b4[month_idx] = round(slope_b4, 2)
                        month_r_b4[month_idx] = round(r_b4, 2)
                        month_rmse_b4[month_idx] = round(rmse_b4, 3)
                        month_offset_b4[month_idx] = round(offset_b4, 2)
            print('Slope, r, RMSE, Offset')

            print(month_slope_b3)
            print(month_r_b3)
            print(month_rmse_b3)
            print(month_offset_b3)

            print(month_slope_b4)
            print(month_r_b4)
            print(month_rmse_b4)
            print(month_offset_b4)

            slope_list = [month_slope_b3, month_slope_b4]
            r_list = [month_r_b3, month_r_b4]
            rmse_list = [month_rmse_b3, month_rmse_b4]
            offest_list = [month_offset_b3, month_offset_b4]

            numpy.save(os.path.join(WORK_SPACE, folder_l1 + '_' + folder_type + '_slope_r_rmse_offset.npy'), [slope_list, r_list, rmse_list, offest_list])