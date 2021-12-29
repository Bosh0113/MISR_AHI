import numpy
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap


def BRF_TrueValue(o_BRF, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    t_BRF = []
    for i in range(len(o_BRF)):
        t_BRF_item = []
        for j in range(len(o_BRF[0])):
            o_value = o_BRF[i][j]
            if o_value in [fill, underflow, overflow]:
                t_BRF_item.append(0)
            else:
                x = math.floor(o_value/2)
                y = x*scale + offset
                t_BRF_item.append(y)
        t_BRF.append(t_BRF_item)
    return t_BRF


if __name__ == "__main__":
    BRF_npy_path = r'D:\Work_PhD\MISR_AHI_WS\211204\SRF_62\b_3_c_8.npy'
    BRF_data = numpy.load(BRF_npy_path)
    
    # # original values
    # plt.imshow(BRF_data, cmap=plt.cm.jet, vmin=0, vmax=11000)
    # plt.title('Original values in LandBRF 2016-01-15 Band 4 Camera 9')
    # plt.colorbar()
    # plt.show()

    # true values
    scale_landBRF = 0.0001526065170764923
    offset_landBRF = 0.0
    BRF_tv = BRF_TrueValue(BRF_data, scale_landBRF, offset_landBRF)
    plt.imshow(BRF_tv, cmap=plt.cm.jet, vmin=0.0, vmax=1.0)
    plt.title('True values in LandBRF 2016-01-15 Band 4 Camera 9')
    plt.colorbar()
    plt.show()
            
    # # mapping
    # inclination = 1.7157253262878522  # SOM_parameters.som_orbit.i
    # in_pi = math.pi * inclination
    # b_lat = 35.616525
    # b_lon = 140.189875
    # m = Basemap(
    #     width=563200,  # row of a block
    #     height=140800,  # col of a block
    #     projection='omerc',
    #     resolution='h',
    #     rsphere=6378137.0,  # from document
    #     lat_1=b_lat+in_pi,
    #     lon_1=b_lon+in_pi,
    #     lat_2=b_lat-in_pi,
    #     lon_2=b_lon-in_pi,
    #     lat_0=b_lat,
    #     lon_0=b_lon,
    # )
    # min_x = 0
    # min_y = 0
    # max_x = 563200
    # max_y = 140800
    # extent = (min_x, max_x, max_y, min_y)

    # m.imshow(BRF_tv, origin='upper', extent=extent, cmap=plt.cm.jet, vmin=0.0, vmax=1.0)
    # m.drawcoastlines(color='w', linewidth=0.8)
    # # m.drawmapboundary(fill_color='whitesmoke')
    # # m.fillcontinents(color='white', lake_color='whitesmoke', alpha=None)
    # m.drawparallels(numpy.arange(35., 36.5, 0.5), labels=[1, 0, 0, 0], linewidth=0.1)  # draw parallels
    # m.drawmeridians(numpy.arange(137., 143., 1.5), labels=[0, 0, 0, 1], linewidth=0.1)  # draw meridians
    # plt.show()