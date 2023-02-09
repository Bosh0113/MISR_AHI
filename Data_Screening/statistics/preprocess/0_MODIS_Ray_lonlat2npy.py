import os
import numpy

ws = r'H:\MISR_AHI_WS\230209'
o_loc_txt = os.path.join(ws, 'Ray_MODIS_land_lonlat.txt')
n_loc_npy = os.path.join(ws, 'Ray_MODIS_land_lonlat.npy')


if __name__ == "__main__":
    loc = []
    o_loc_info = numpy.loadtxt(o_loc_txt)
    # print(len(o_loc_info))
    for o_loc_item in o_loc_info:
        lon = round(float(o_loc_item[0]), 2)
        lat = round(float(o_loc_item[1]), 2)
        loc_item = [lon, lat]
        if loc_item not in loc:
            loc.append(loc_item)
    # print(len(loc))
    # print(loc)
    numpy.save(n_loc_npy, o_loc_info)