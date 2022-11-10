import os
import numpy


WORK_SPACE = os.getcwd()


def get_full_matched_count(misr_camera_angle, record_npy_filename):
    count_record_txt_filename = os.path.join(WORK_SPACE, misr_camera_angle + '_full_matched_point_info.txt')
    info_record_str = ''
    matched_record_array = numpy.load(record_npy_filename, allow_pickle=True)
    for matched_record in matched_record_array:
        pt_location = matched_record['location']
        pt_lon = pt_location[0]
        pt_lat = pt_location[1]
        full_matched_record_array = matched_record['matched_infos']
        pt_full_match_count = len(full_matched_record_array)
        pt_lon = '%.3f' % pt_lon
        pt_lat = '%.3f' % pt_lat
        info_record_str += str(pt_lon) + ',' + str(pt_lat) + ',' + str(pt_full_match_count) + '\n'
    # save result as txt
    with open(count_record_txt_filename, 'w') as f:
        f.write(info_record_str)


if __name__ == "__main__":
    misr_camera_angles = ['0.0', '26.1', '45.6', '60.0', '70.5']
    for misr_camera_angle in misr_camera_angles:
        record_npy_filename = os.path.join(WORK_SPACE, misr_camera_angle + '_matched_record.npy')
        get_full_matched_count(misr_camera_angle, record_npy_filename)
