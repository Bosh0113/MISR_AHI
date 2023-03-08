import numpy
import matplotlib.pyplot as plt

# MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
matched_npy_filename = r'E:\MISR_AHI_WS\230308\mapping\AHI_MISR_Ray-screened_10km.npy'


def pixel_count(matched_info, info_idx=2):
    angle_record = numpy.zeros((9,))
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        camera_all = []
        for pt_matched_item in pt_matched_info:
            camera_idx = int(pt_matched_item[info_idx])
            if camera_idx not in camera_all:
                camera_all.append(camera_idx)
        for camera_all_idx in camera_all:
            angle_record[camera_all_idx] = angle_record[camera_all_idx] + 1
    return angle_record


def obs_count(matched_info, info_idx=2):
    angle_record = numpy.zeros((9,))
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        camera_all = []
        for pt_matched_item in pt_matched_info:
            camera_idx = int(pt_matched_item[info_idx])
            camera_all.append(camera_idx)
        for camera_all_idx in camera_all:
            angle_record[camera_all_idx] = angle_record[camera_all_idx] + 1
    return angle_record


def mapping(misr_angle_pixel_record, ahi_angle_pixel_record):

    plt.plot(misr_angle_pixel_record)
    plt.plot(ahi_angle_pixel_record)
    plt.xlim(0, 8)
    plt.ylim(bottom=0)
    plt.show()


def main():
    matched_info = numpy.load(matched_npy_filename, allow_pickle=True)

    camera_pixel_record = pixel_count(matched_info)
    camera_obs_record = obs_count(matched_info)
    camera_freq_record = [round(camera_obs_record[idx]/camera_pixel_record[idx], 2) for idx in range(len(camera_pixel_record))]

    print('Camera Index: 0 1 2 3 4 5 6 7 8')
    print(list(camera_pixel_record))
    print(list(camera_obs_record))
    print(camera_freq_record)

    # mapping(camera_pixel_record, camera_obs_record)


if __name__ == "__main__":
    main()