import os
import numpy
import time
import global_land_mask as globe

# import matplotlib.pyplot as plt


def AHI_pixel_is_land(x_index, y_index, m_size=3000):
    offset = 120. / m_size
    lon = 85. + (offset * (x_index + 1 / 2))
    if lon > 180:
        lon = lon - 360.
    lat = 60. - offset * (y_index + 1 / 2)
    return globe.is_land(lat, lon)


def screening_AHI_VZA_with_angle_scale(vza_data, min_vza, max_vza):
    a_data = numpy.copy(vza_data)
    a_data[~((a_data >= min_vza) & (max_vza > a_data))] = 0.
    a_data[a_data > 0.] = 1.
    return a_data


if __name__ == "__main__":
    start = time.perf_counter()
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220920'
    bin_filename = os.path.join(workspace, '202201010000.sat.zth.fld.4km.bin')
    MISRVZAs = [0.0, 26.1, 45.6, 60.0, 70.5]
    minVZAs = [0.0, 25.6, 45.1, 59.5, 70.0]
    maxVZAs = [21.78, 32.30, 47.64, 60.64, 70.68]

    VZA_pixel_count = 3000
    for idx in range(len(MISRVZAs)):
        data_DN = numpy.fromfile(bin_filename, dtype='>f4')
        data_DN = data_DN.reshape(VZA_pixel_count, VZA_pixel_count)
        vza_region = screening_AHI_VZA_with_angle_scale(data_DN, minVZAs[idx], maxVZAs[idx])
        
        # vza_region[vza_region == 0] = numpy.nan
        # plt.imshow(vza_region, interpolation='none')
        # plt.show()
        # plt.clf()

        # onland
        onland_vza = numpy.zeros_like(vza_region)
        for lat_idx in range(len(vza_region)):
            # mid-latitude
            if lat_idx < VZA_pixel_count / 4 or lat_idx > VZA_pixel_count / 4 * 3:
                for lon_idx in range(len(vza_region[0])):
                    if vza_region[lat_idx][lon_idx] == 0.:
                        onland_vza[lat_idx][lon_idx] = 0
                    else:
                        island = AHI_pixel_is_land(lon_idx, lat_idx)
                        if island:
                            onland_vza[lat_idx][lon_idx] = 1
                        else:
                            onland_vza[lat_idx][lon_idx] = 0
            else:
                onland_vza[lat_idx][lon_idx] = 0
        # save region
        npy_filename = os.path.join(workspace, str(MISRVZAs[idx]) + '_onland_mid_lat.npy')
        numpy.save(npy_filename, numpy.array(onland_vza))
    end = time.perf_counter()
    print("Run time: ", end - start, 's')
