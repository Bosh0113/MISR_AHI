import os
import numpy

ws = r'D:\Work_PhD\MISR_AHI_WS\230119\ROI_matches_whichRAA\14'


# get side of VAA-to-SAA (SAA as refer)
def get_side_RAA(vaa, saa):
    if saa < 180:
        if vaa > saa and vaa < saa + 180:
            return 1
        else:
            return -1
    if saa > 180:
        if vaa > saa - 180 and vaa < saa:
            return -1
        else:
            return 1


if __name__ == "__main__":
    # roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0_0', '45.6_1_0', '60.0_0_0', '60.0_1_0', '70.5_0_0', '70.5_1_0', '45.6_0_1', '45.6_1_1', '60.0_0_1', '60.0_1_1', '70.5_0_1', '70.5_1_1']
    # roi_names = ['0.0_0', '0.0_1', '26.1_0', '26.1_1', '45.6_0', '45.6_1', '60.0_0_0', '60.0_1_0', '70.5_0_0', '70.5_1_0', '60.0_0_1', '60.0_1_1', '70.5_0_1', '70.5_1_1']
    # roi_names = ['45.6_0', '45.6_1', '60.0_1_0']
    roi_names = ['45.6_0', '60.0_1_0']
    for roi_name in roi_names:
        same_side_record = []
        opposite_side_record = []
        matched_record_npy = os.path.join(ws, roi_name + '_matched_record.npy')
        matched_records = numpy.load(matched_record_npy, allow_pickle=True)
        matched_infos = matched_records[0]['roi_misr_infos']
        for matched_items in matched_infos:
            matched_item = matched_items['matched_info']
            misr_vaa = matched_item[7]
            ahi_vaa = matched_item[8]
            misr_saa = matched_item[9]
            ahi_saa = matched_item[10]
            misr_dif = get_side_RAA(float(misr_vaa), float(misr_saa))
            ahi_dif = get_side_RAA(float(ahi_vaa), float(ahi_saa))
            if misr_dif*ahi_dif > 0:
                same_side_record.append(matched_item)
            else:
                opposite_side_record.append(matched_item)
            txt_str = roi_name + '\n'
            tab_str = 'misr_path misr_orbit misr_camera_index misr_block_time ahi_time misr_vza ahi_vza misr_vaa ahi_vaa misr_saa ahi_saa misr_raa ahi_raa misr_sza ahi_sza scattering_angle_raa'
            txt_str += tab_str + '\n'
            txt_str += 'RAAs at same side\n'
            for same_side_record_item in same_side_record:
                for same_side_info_item in same_side_record_item:
                    txt_str += same_side_info_item + '\t'
                txt_str += '\n'
            txt_str += 'RAAs at opposite sides\n'
            for opposite_side_record_item in opposite_side_record:
                for opposite_side_info_item in opposite_side_record_item:
                    txt_str += opposite_side_info_item + '\t'
                txt_str += '\n'
            # save result as txt
            with open(os.path.join(ws, roi_name + '_RAA.txt'), 'w') as f:
                f.write(txt_str)