import numpy
import matplotlib.pyplot as plt

MISR_VZA = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
AHI_SUBPOINT_LON = 140.7
AHI_SUBPOINT_LON_IDX = round((AHI_SUBPOINT_LON - 85.)/0.04)-1
AHI_SUBPOINT_LAT_IDX = 1499


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


if __name__ == "__main__":
    misr_vza_ahi = numpy.zeros((3000, 3000))
    workspace = r'D:\PhD_Workspace\MISR_AHI_WS\221210'
    bin_vza_filename = workspace + '/201706160000.sat.zth.fld.4km.bin'

    misr_camera_AHI_npy = workspace + '/AHI_VZA.npy'
    data_DN = numpy.fromfile(bin_vza_filename, dtype='>f4')
    data_DN = data_DN.reshape(3000, 3000)

    for lat_idx in range(len(data_DN)):
        data_row = data_DN[lat_idx]
        data_row_l = data_row[:AHI_SUBPOINT_LON_IDX+1]
        data_row_r = data_row[AHI_SUBPOINT_LON_IDX:]
        for misr_vza in MISR_VZA:
            l_idx = find_nearest_index(data_row_l, misr_vza)
            r_idx = find_nearest_index(data_row_r, misr_vza)
            if l_idx != AHI_SUBPOINT_LON_IDX and l_idx != AHI_SUBPOINT_LON_IDX-1:
                misr_vza_ahi[lat_idx][l_idx] = 1
            if r_idx != 0:
                all_r_idx = r_idx + AHI_SUBPOINT_LON_IDX
                misr_vza_ahi[lat_idx][all_r_idx] = 1

    data_DN_T = data_DN.T
    misr_vza_ahi = misr_vza_ahi.T
    for lat_idx in range(len(data_DN_T)):
        data_row = data_DN_T[lat_idx]
        data_row_l = data_row[:AHI_SUBPOINT_LAT_IDX+1]
        data_row_r = data_row[AHI_SUBPOINT_LAT_IDX:]
        for misr_vza in MISR_VZA:
            l_idx = find_nearest_index(data_row_l, misr_vza)
            r_idx = find_nearest_index(data_row_r, misr_vza)
            if l_idx != AHI_SUBPOINT_LAT_IDX:
                misr_vza_ahi[lat_idx][l_idx] = 1
            if r_idx != 0:
                all_r_idx = r_idx + AHI_SUBPOINT_LAT_IDX
                misr_vza_ahi[lat_idx][all_r_idx] = 1
    misr_vza_ahi = misr_vza_ahi.T

    numpy.save(misr_camera_AHI_npy, misr_vza_ahi)

    plt.imshow(misr_vza_ahi, interpolation=None)
    plt.colorbar()
    plt.show()