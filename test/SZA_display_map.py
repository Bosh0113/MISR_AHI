from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy


if __name__ == "__main__":
    # path107 block62
    SZA_data_path = './Geo_62/SZA/SZA.npy'
    SZA62 = numpy.load(SZA_data_path)
        
    # mapping
    min_x = 22385550.0
    min_y = -581350.0
    max_x = 22526350.0
    max_y = -18150.0
    m = Basemap(
        width=563200,  # row of a block
        height=140800,  # col of a block
        projection='omerc',
        resolution='h',
        rsphere=6378137.0,  # from document
        lat_1=36.853725,  # block61 central point as 1
        lon_1=140.5796,
        lat_2=34.377775,  # block63 central point as 2
        lon_2=139.812025,
        lat_0=35.616525,
        lon_0=140.189875,
        # llcrnrx=min_x,
        # llcrnry=max_y,
        # urcrnrx=max_x,
        # urcrnry=min_y
    )
    min_x = 0
    min_y = 0
    max_x = 35200
    max_y = 8800
    extent = (min_x, max_x, max_y, min_y)

    SZA_fig_path = './SZA_map_png/SZA62.png'
    m.imshow(SZA62, origin='upper', extent=extent, cmap=plt.cm.jet, vmin=59, vmax=61)
    m.drawcoastlines(color='w', linewidth=0.8)
    # m.drawmapboundary(fill_color='whitesmoke')
    # m.fillcontinents(color='white', lake_color='whitesmoke', alpha=None)
    m.drawparallels(numpy.arange(35., 36.5, 0.5), labels=[1, 0, 0, 0], linewidth=0.1)  # draw parallels
    m.drawmeridians(numpy.arange(137., 143., 1.5), labels=[0, 0, 0, 1], linewidth=0.1)  # draw meridians
    plt.colorbar()
    # plt.savefig(SZA_fig_path)
    plt.show()