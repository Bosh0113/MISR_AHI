import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import time


def get_ahi_raa(vaa, saa):
    raa = 0
    diff = abs(vaa - saa)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def display_ahi_raa(vaa_ahi, saa_ahi):
    raa_ahi = numpy.zeros_like(vaa_ahi)
    for i in range(len(raa_ahi)):
        raa_ahi[i] = get_ahi_raa(vaa_ahi[i], saa_ahi[i])
    raa_ahi = raa_ahi.reshape(3000, 3000)
    # map
    m = Basemap(projection='cyl',
                resolution='c',
                llcrnrlon=85,
                llcrnrlat=-60,
                urcrnrlon=205,
                urcrnrlat=60)
    m.imshow(raa_ahi,
             vmin=0,
             vmax=180,
             extent=(85, 205, -60, 60),
             interpolation="None",
             origin="upper",
             cmap='jet')
    m.drawcoastlines(color='k', linewidth=0.5)
    m.drawparallels(numpy.arange(-60, 60.1, 30),
                    labels=[1, 0, 0, 0],
                    linewidth=0.1)  # draw parallels
    m.drawmeridians(numpy.arange(85, 205.1, 30),
                    labels=[0, 0, 0, 1],
                    linewidth=0.1)  # draw meridians
    plt.title('RAA DN value: 201601112300')
    plt.colorbar().set_label('DN', size=15)
    plt.show()


def get_location_ahi_raa(lon, lat, ahi_vaa, ahi_saa):
    ahi_vaa = ahi_vaa.reshape(3000, 3000)
    ahi_saa = ahi_saa.reshape(3000, 3000)
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    y_index = round(((lat - ullat_ahi) * -1) / p_size)
    x_index = round((lon - ullon_ahi) / p_size)
    loc_vaa = ahi_vaa[y_index][x_index]
    loc_saa = ahi_saa[y_index][x_index]
    loc_raa = get_ahi_raa(loc_vaa, loc_saa)

    return loc_raa


def get_region_ahi_raa(region_extent, ahi_vaa, ahi_saa):
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)

    ahi_vaa = ahi_vaa.reshape(3000, 3000)
    ahi_saa = ahi_saa.reshape(3000, 3000)
    roi_vaa = ahi_vaa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]
    roi_saa = ahi_saa[ymin_index:ymax_index + 1, xmin_index:xmax_index + 1]

    roi_raa = numpy.zeros_like(roi_vaa)
    for y in range(len(roi_vaa)):
        for x in range(len(roi_vaa[0])):
            vaa = roi_vaa[y][x]
            saa = roi_saa[y][x]
            raa = get_ahi_raa(vaa, saa)
            roi_raa[y][x] = raa

    return roi_raa


if __name__ == "__main__":
    start = time.perf_counter()
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220218'
    ahi_vaa_bin = workspace + '/AHI_VAA/202201010000.sat.azm.fld.4km.bin'
    ahi_saa_bin = workspace + '/201601112300.sun.azm.fld.4km.bin'
    # dtype='>u2' for 	2 byte “unsigned short” binary data without any hearder and footer information, with “big endian” byte order
    # dtype='>f4' for 	4 byte “float” binary data with “big endian” byte order.
    ahi_vaa_dn = numpy.fromfile(ahi_vaa_bin, dtype='>f4')
    ahi_saa_dn = numpy.fromfile(ahi_saa_bin, dtype='>f4')

    # roi_pt = (140.098, 35.630)
    # print('location:', roi_pt)
    # loc_ahi_raa = get_location_ahi_raa(roi_pt[0], roi_pt[1], ahi_vaa_dn, ahi_saa_dn)
    # print('AHI RAA:', str(loc_ahi_raa) + '°')

    roi_region = [43.625, 90.772, 43.495, 90.952]
    print('ROI extent:', roi_region)
    roi_ahi_raa = get_region_ahi_raa(roi_region, ahi_vaa_dn, ahi_saa_dn)
    print('AHI RAA at ROI:')
    print(roi_ahi_raa)
    print('mean AHI RAA at ROI:', str(roi_ahi_raa.mean()) + '°')

    end = time.perf_counter()
    print("Run time: ", end - start, 's')

    # display_ahi_raa(ahi_vaa_dn, ahi_saa_dn)