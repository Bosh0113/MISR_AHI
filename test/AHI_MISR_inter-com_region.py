import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def mapping(storage, data4map, mid_degree, margin=1.0):
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
             cmap=plt.cm.cool)
    m.drawcoastlines(color='k', linewidth=0.5)
    m.drawparallels(numpy.arange(-60, 60.1, 30),
                    labels=[1, 0, 0, 0],
                    linewidth=0.1)  # draw parallels
    m.drawmeridians(numpy.arange(85, 205.1, 30),
                    labels=[0, 0, 0, 1],
                    linewidth=0.1)  # draw meridians
    plt.title("AHI " + str(mid_degree) + "° VZA on land with margin of " +
              str(margin) + "°")
    plt.savefig(storage)
    plt.show()


def mapping_notMargin(storage, data4map, vza):
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
             cmap=plt.cm.cool)
    m.drawcoastlines(color='k', linewidth=0.5)
    m.drawparallels(numpy.arange(-60, 60.1, 30),
                    labels=[1, 0, 0, 0],
                    linewidth=0.1)  # draw parallels
    m.drawmeridians(numpy.arange(85, 205.1, 30),
                    labels=[0, 0, 0, 1],
                    linewidth=0.1)  # draw meridians
    plt.title("AHI VZA on MISR " + str(vza) + "° swath scale")
    plt.savefig(storage)
    plt.show()


if __name__ == "__main__":
    # storage_path = r'D:\Work_PhD\MISR_AHI_WS\220107'
    storage_path = r'D:\Work_PhD\MISR_AHI_WS\220127'
    region_onland_filename = storage_path + '/region4intercom.npy'
    re_onland = numpy.load(region_onland_filename)
    # MISR_vza = [26.1, 45.6, 60.0, 70.5]
    MISR_vza = [0, 26.1, 45.6, 60.0, 70.5]
    for vza in MISR_vza:
        # vza_filename = storage_path + '/AHI_vza_1margin_' + str(vza) + '.npy'
        vza_filename = storage_path + '/AHI_vza_MISR_' + str(vza) + '.npy'
        data_vza = numpy.load(vza_filename)
        vza_onland = []
        for i in range(len(re_onland)):
            for j in range(len(re_onland[0])):
                if re_onland[i][j] == 1 and data_vza[i][j] != 0.:
                    vza_onland.append(1)
                else:
                    vza_onland.append(0)
        vza_onland = numpy.array(vza_onland)
        vza_onland = vza_onland.reshape(3000, 3000)
        vza_onland_filename = storage_path + '/AHI_MISR_inter-com_region_degree_' + str(vza) + '.npy'
        numpy.save(vza_onland_filename, vza_onland)
        # mapping
        pto_path = storage_path + "/AHI_MISR_inter-com_region_degree" + str(vza) + ".png"
        vza_onland = vza_onland * 1.
        vza_onland[vza_onland == 0.] = numpy.NaN
        mapping_notMargin(pto_path, vza_onland, vza)
    