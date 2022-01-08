import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


if __name__ == "__main__":
    region_filename = r'D:\Work_PhD\MISR_AHI_WS\220108\region4intercom.npy'
    onland_vza = numpy.load(region_filename)
    onland_vza = onland_vza * 1.
    onland_vza[onland_vza == 0.] = numpy.NaN

    m = Basemap(projection='cyl',
                resolution='c',
                llcrnrlon=85,
                llcrnrlat=-60,
                urcrnrlon=205,
                urcrnrlat=60)
    m.imshow(onland_vza,
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
    plt.title("Region for data inter-comparison")
    plt.show()
