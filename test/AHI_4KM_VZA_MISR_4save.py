import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def screening_AHI_VZA_margin(o_data, mid_degree, margin=1.0):
    a_data = numpy.copy(o_data)
    a_data[((0 <= a_data) & (a_data < (mid_degree - margin))) |
           (((mid_degree + margin) < a_data) & (a_data < 90.0))] = .0
    return a_data


def screening_AHI_minmaxVZA(o_data, minVZA, maxVZA):
    a_data = numpy.copy(o_data)
    a_data[((0 <= a_data) & (a_data < minVZA)) |
           ((maxVZA < a_data) & (a_data < 90.0))] = .0
    return a_data


def mapping(data4map, mid_degree, margin=1.0):
    # map
    m = Basemap(projection='cyl',
                resolution='c',
                llcrnrlon=85,
                llcrnrlat=-60,
                urcrnrlon=205,
                urcrnrlat=60)
    m.imshow(data4map,
             vmin=0,
             vmax=90,
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
    plt.title("AHI VZA on" + str(mid_degree) + "° with margin of " +
              str(margin) + "°, 202201010000")
    plt.colorbar().set_label('DN', size=15)
    plt.show()


def mapping_notMargin(data4map, vza):
    # map
    m = Basemap(projection='cyl',
                resolution='c',
                llcrnrlon=85,
                llcrnrlat=-60,
                urcrnrlon=205,
                urcrnrlat=60)
    m.imshow(data4map,
             vmin=0,
             vmax=90,
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
    plt.title("AHI VZA on MISR " + str(vza) + "° swath scale, 202201010000")
    plt.colorbar().set_label('DN', size=15)
    plt.show()


# MISR与AHI的VZA包括海洋的匹配范围
if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220103'
    bin_filename = workspace + '/202201010000.sat.zth.fld.4km.bin'
    # dtype='>u2' for 	2 byte “unsigned short” binary data without any hearder and footer information, with “big endian” byte order
    # dtype='>f4' for 	4 byte “float” binary data with “big endian” byte order.
    data_DN = numpy.fromfile(bin_filename, dtype='>f4')
    data_DN = data_DN.reshape(3000, 3000)
    # MISR_vza = [26.1, 45.6, 60.0, 70.5]
    MISR_vza = [0, 26.1, 45.6, 60.0, 70.5]
    minVZAs = [0, 25.6, 45.1, 59.5, 70.0]
    maxVZAs = [21.78, 32.30, 47.64, 60.64, 70.68]
    # storage_path = r'D:\Work_PhD\MISR_AHI_WS\220107'
    storage_path = r'D:\Work_PhD\MISR_AHI_WS\220127'
    # for vza in MISR_vza:
    for index in range(len(minVZAs)):
        # data_scr = screening_AHI_VZA_margin(data_DN, vza, 1.0)
        # vza_filename = storage_path + '/AHI_vza_1margin_' + str(vza) + '.npy'
        data_scr = screening_AHI_minmaxVZA(data_DN, minVZAs[index], maxVZAs[index])
        vza_filename = storage_path + '/AHI_vza_MISR_' + str(MISR_vza[index]) + '.npy'
        numpy.save(vza_filename, data_scr)
        data_scr[data_scr == 0.] = numpy.NaN
        # mapping(data_scr, vza)
        mapping_notMargin(data_scr, minVZAs[index])
