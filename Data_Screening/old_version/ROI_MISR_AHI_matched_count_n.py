import numpy

if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220714'
    matched_record_npy = ws + '/MISR_AHI_matched_info_vza002raa10sza30min.npy'
    matched_records = numpy.load(matched_record_npy, allow_pickle=True)
    roi_matched_info = []
    for matched_record in matched_records:
        roi_item = {}
        roi_name = matched_record['roi_name']
        roi_item['roi_name'] = roi_name
        misr_ahi = matched_record['roi_misr_infos']
        misr_count = len(misr_ahi)
        roi_item['misr_count'] = misr_count
        print(roi_item)
        roi_matched_info.append(roi_item)
    # print(roi_matched_info)
