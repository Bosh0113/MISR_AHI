import numpy
import matplotlib.pyplot as plt

# MISR_path MISR_orbit camera_idx MISR_roi_time AHI_roi_time MISR_VZA AHI_VZA MISR_VAA AHI_VAA Scattering_Angle(GEO-LEO)
matched_npy_filename = r'C:\Work\AHI_MISR\20221210\AHI_MISR_Ray-matched.npy'


def pixel_count(matched_info):
    angle_record = numpy.zeros((12,))
    for pt_item in matched_info:
        pt_location = pt_item['location']
        pt_lat = pt_location[1]
        if pt_lat <= 60 and pt_lat > 50:    # 60N-50N
            angle_record[0] = angle_record[0] + 1
        elif pt_lat <= 50 and pt_lat > 40:  # 50N-40N
            angle_record[1] = angle_record[1] + 1
        elif pt_lat <= 40 and pt_lat > 30:  # 40N-30N
            angle_record[2] = angle_record[2] + 1
        elif pt_lat <= 30 and pt_lat > 20:  # 30N-20N
            angle_record[3] = angle_record[3] + 1
        elif pt_lat <= 20 and pt_lat > 10:  # 20N-10N
            angle_record[4] = angle_record[4] + 1
        elif pt_lat <= 10 and pt_lat > 0:  # 10N-0
            angle_record[5] = angle_record[5] + 1
        elif pt_lat <= 0 and pt_lat > -10:    # 0-10S
            angle_record[6] = angle_record[6] + 1
        elif pt_lat <= -10 and pt_lat > -20:    # 10S-20S
            angle_record[7] = angle_record[7] + 1
        elif pt_lat <= -20 and pt_lat > -30:  # 20S-30S
            angle_record[8] = angle_record[8] + 1
        elif pt_lat <= -30 and pt_lat > -40:  # 30S-40S
            angle_record[9] = angle_record[9] + 1
        elif pt_lat <= -40 and pt_lat > -50:  # 40S-50S
            angle_record[10] = angle_record[10] + 1
        elif pt_lat <= -50 and pt_lat > -60:  # 50S-60S
            angle_record[11] = angle_record[11] + 1
    return angle_record

def obs_count(matched_info):
    angle_record = numpy.zeros((12,))
    for pt_item in matched_info:
        pt_matched_info = pt_item['matched_infos']
        pt_matched_count = len(pt_matched_info)
        pt_location = pt_item['location']
        pt_lat = pt_location[1]
        if pt_lat <= 60 and pt_lat > 50:    # 60N-50N
            angle_record[0] = angle_record[0] + pt_matched_count
        elif pt_lat <= 50 and pt_lat > 40:  # 50N-40N
            angle_record[1] = angle_record[1] + pt_matched_count
        elif pt_lat <= 40 and pt_lat > 30:  # 40N-30N
            angle_record[2] = angle_record[2] + pt_matched_count
        elif pt_lat <= 30 and pt_lat > 20:  # 30N-20N
            angle_record[3] = angle_record[3] + pt_matched_count
        elif pt_lat <= 20 and pt_lat > 10:  # 20N-10N
            angle_record[4] = angle_record[4] + pt_matched_count
        elif pt_lat <= 10 and pt_lat > 0:  # 10N-0
            angle_record[5] = angle_record[5] + pt_matched_count
        elif pt_lat <= 0 and pt_lat > -10:    # 0-10S
            angle_record[6] = angle_record[6] + pt_matched_count
        elif pt_lat <= -10 and pt_lat > -20:    # 10S-20S
            angle_record[7] = angle_record[7] + pt_matched_count
        elif pt_lat <= -20 and pt_lat > -30:  # 20S-30S
            angle_record[8] = angle_record[8] + pt_matched_count
        elif pt_lat <= -30 and pt_lat > -40:  # 30S-40S
            angle_record[9] = angle_record[9] + pt_matched_count
        elif pt_lat <= -40 and pt_lat > -50:  # 40S-50S
            angle_record[10] = angle_record[10] + pt_matched_count
        elif pt_lat <= -50 and pt_lat > -60:  # 50S-60S
            angle_record[11] = angle_record[11] + 1
    return angle_record


def mapping(misr_angle_pixel_record, ahi_angle_pixel_record):

    plt.plot(misr_angle_pixel_record)
    plt.plot(ahi_angle_pixel_record)
    plt.xlim(0, 12)
    plt.ylim(bottom=0)
    plt.show()


def main():
    matched_info = numpy.load(matched_npy_filename, allow_pickle=True)

    lat_pixel_record = pixel_count(matched_info)
    lat_obs_record = obs_count(matched_info)

    print('Range: 60N-50N 50N-40N 40N-30N 30N-20N 20N-10N 10N-0 0-10S 10S-20S 20S-30S 30S-40S 40S-50S 50S-60S')
    print(list(lat_pixel_record))
    print(list(lat_obs_record))

    # mapping(lat_pixel_record, lat_obs_record)


if __name__ == "__main__":
    main()