import numpy

if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220401\VZA001_RAA3_SZA1h_c5'
    matched_record_npy = ws + '/VZA001_RAA3_SZA1h_c5.npy'
    matched_records = numpy.load(matched_record_npy, allow_pickle=True)
    roi_matched_info = []
    for matched_record in matched_records:
        roi_item = {}
        roi_name = matched_record['roi_name']
        roi_item['roi_name'] = roi_name
        misr_ahi = matched_record['misr_ahi']
        misr_count = 0
        ahi_count = numpy.zeros(5)
        for misr_ahi_info in misr_ahi:
            misr_count += 1
            path_orbit_camera = misr_ahi_info['path_orbit_camera']
            ahi_matched = misr_ahi_info['ahi_matched']
            ahi_count[len(ahi_matched) - 1] += 1

        roi_item['misr_count'] = misr_count
        ahi_total = 0
        for i in range(5):
            roi_item['misr_ahi_count' + str(i + 1)] = ahi_count[i]
            ahi_total += ahi_count[i] * (i + 1)
        roi_item['misr_ahi_count_total'] = ahi_total
        roi_matched_info.append(roi_item)
    print(roi_matched_info)
