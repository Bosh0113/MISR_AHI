import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import global_land_mask as globe


def AHI_pixel_is_land(x_index, y_index, m_size=3000):
    offset = 120. / m_size
    lon = 85. + (offset * (x_index + 1 / 2))
    if lon > 180:
        lon = lon - 360.
    lat = 60. - offset * (y_index + 1 / 2)
    return globe.is_land(lat, lon)


def screening_AHI_VZA_similar_MISR(o_data, margin):
    # MISR_vza = [26.1, 45.6, 60.0, 70.5]
    a_data = numpy.copy(o_data)
    a_data[((0 <= a_data) & (a_data <
                             (26.1 - margin))) | (((26.1 + margin) < a_data) &
                                                  (a_data < (45.6 - margin))) |
           (((45.6 + margin) < a_data) & (a_data < (60.0 - margin))) |
           (((60.0 + margin) < a_data) & (a_data < (70.5 - margin))) |
           (((70.5 + margin) < a_data) & (a_data < 90.0))] = 0.
    return a_data


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220103'
    bin_filename = workspace + '/202201010000.sat.zth.fld.4km.bin'
    # dtype='>u2' for 	2 byte “unsigned short” binary data without any hearder and footer information, with “big endian” byte order
    # dtype='>f4' for 	4 byte “float” binary data with “big endian” byte order.
    data_DN = numpy.fromfile(bin_filename, dtype='>f4')
    data_DN = data_DN.reshape(3000, 3000)
    # AHI, MISR at similar VZA with margin of 1 degree
    data_DN = screening_AHI_VZA_similar_MISR(data_DN, 1.0)
    # land area with similar VZA
    onland_vza = []
    for i in range(len(data_DN)):
        for j in range(len(data_DN[0])):
            if data_DN[i][j] == 0.:
                onland_vza.append(0)
            else:
                island = AHI_pixel_is_land(j, i)
                if island:
                    onland_vza.append(1)
                else:
                    onland_vza.append(0)
    onland_vza = numpy.array(onland_vza)
    onland_vza = onland_vza.reshape(3000, 3000)

    # region_filename = r'D:\Work_PhD\MISR_AHI_WS\220107\region4intercom.npy'
    # numpy.save(region_filename, numpy.array(onland_vza))
    # onland_vza = numpy.load(region_filename)
    onland_vza = onland_vza * 1.
    onland_vza[onland_vza == 0.] = numpy.NaN

    m = Basemap(projection='cyl',
                resolution='c',
                llcrnrlon=85,
                llcrnrlat=-60,
                urcrnrlon=205,
                urcrnrlat=60)
    m.imshow(
        onland_vza,
        extent=(85, 205, -60, 60),
        interpolation="None",
        origin="upper",
        cmap=plt.cm.cool
    )
    m.drawcoastlines(color='k', linewidth=0.5)
    m.drawparallels(numpy.arange(-60, 60.1, 30),
                    labels=[1, 0, 0, 0],
                    linewidth=0.1)  # draw parallels
    m.drawmeridians(numpy.arange(85, 205.1, 30),
                    labels=[0, 0, 0, 1],
                    linewidth=0.1)  # draw meridians
    plt.title("Region for data inter-comparison")
    plt.show()