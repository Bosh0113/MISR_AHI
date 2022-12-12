import os
import numpy
import matplotlib.pyplot as plt

degree_count = 2

# MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
matched_npy_filename = r'C:\Work\AHI_MISR\20221210\AHI_MISR_Ray-matched.npy'


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def angle_count(matched_info, info_idx):
    angle_record = numpy.zeros((360*degree_count+1,))
    angle_list = numpy.arange(0, 360+1/degree_count, 1/degree_count)
    angle_list = angle_list * 1.
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        vaa_sum = 0.
        for pt_matched_item in pt_matched_info:
            vaa = float(pt_matched_item[info_idx])
            vaa_sum += vaa
        vaa_mean = vaa_sum/len(pt_matched_info)
        vaa_angle_idx = find_nearest_index(angle_list, vaa_mean)
        angle_record[vaa_angle_idx] = angle_record[vaa_angle_idx] + 1
    return angle_record


def mapping(misr_angle_pixel_record, ahi_angle_pixel_record):

    plt.plot(misr_angle_pixel_record)
    plt.plot(ahi_angle_pixel_record)
    plt.xlim(0, 360*degree_count)
    plt.ylim(bottom=0)
    plt.show()


def main():
    matched_info = numpy.load(matched_npy_filename, allow_pickle=True)

    misr_angle_pixel_record = angle_count(matched_info, 7)
    ahi_angle_pixel_record = angle_count(matched_info, 8)
    print(misr_angle_pixel_record.max())
    print(ahi_angle_pixel_record.max())

    mapping(misr_angle_pixel_record, ahi_angle_pixel_record)


if __name__ == "__main__":
    main()