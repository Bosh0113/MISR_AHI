from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy

i = 0


if __name__ == "__main__":
    # path107 block62
    BRF_data_path = './SRF_62/'
    bands = numpy.arange(0, 4, 1)
    cameras = numpy.arange(0, 9, 1)
    
    BRFs_b_c = []
    for band_num in bands:
        BRFs_b = []
        BRFs_b_im = []
        band_str = str(band_num)
        for camera_num in cameras:
            camera_str = str(camera_num)
            BRF_filename = BRF_data_path + 'b_' + band_str + '_c_' + camera_str + '.npy'
            BRF62_bbc = numpy.load(BRF_filename)
            BRFs_b.append(BRF62_bbc)
        BRFs_b_c.append(BRFs_b)
        
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
    max_x = 563200
    max_y = 140800
    extent = (min_x, max_x, max_y, min_y)

    BRF_fig_path = './SRF_map_png/'
    for band_num in bands:
        band_str = str(band_num)
        for camera_num in cameras:
            camera_str = str(camera_num)
            BRF_fig = BRF_fig_path + 'map_b_' + band_str + '_c_' + camera_str + '.png'
            m.imshow(BRFs_b_c[band_num][camera_num], origin='upper', extent=extent, cmap=plt.cm.jet, vmin=0, vmax=11000)
            m.drawcoastlines(color='w', linewidth=0.8)
            # m.drawmapboundary(fill_color='whitesmoke')
            # m.fillcontinents(color='white', lake_color='whitesmoke', alpha=None)
            m.drawparallels(numpy.arange(35., 36.5, 0.5), labels=[1, 0, 0, 0], linewidth=0.1)  # draw parallels
            m.drawmeridians(numpy.arange(137., 143., 1.5), labels=[0, 0, 0, 1], linewidth=0.1)  # draw meridians
            plt.savefig(BRF_fig)

    # m.imshow(BRFs_b_c[0][0], origin='upper', extent=extent, cmap=plt.cm.jet, vmin=0, vmax=11000)
    # m.drawcoastlines(color='w', linewidth=0.8)
    # # m.drawmapboundary(fill_color='whitesmoke')
    # # m.fillcontinents(color='white', lake_color='whitesmoke', alpha=None)
    # m.drawparallels(numpy.arange(35., 36.5, 0.5), labels=[1, 0, 0, 0], linewidth=0.1)  # draw parallels
    # m.drawmeridians(numpy.arange(137., 143., 1.5), labels=[0, 0, 0, 1], linewidth=0.1)  # draw meridians
    # plt.show()