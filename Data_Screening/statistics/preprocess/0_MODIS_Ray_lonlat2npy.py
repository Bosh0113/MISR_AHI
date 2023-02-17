import os
import numpy

ws = r'D:\MISR_AHI_WS\230217'
o_loc_txt = os.path.join(ws, 'Ray_MYD09_land_lonlat_10km.txt')
n_loc_npy = os.path.join(ws, 'Ray_MYD09_land_lonlat_10km.npy')


if __name__ == "__main__":
    loc = []
    o_loc_info = numpy.loadtxt(o_loc_txt)
    print(len(o_loc_info))
    for o_loc_item in o_loc_info:
        lon = round(float(o_loc_item[1]), 2)
        lat = round(float(o_loc_item[0]), 2)
        loc_item = [lon, lat]
        if loc_item not in loc:
            loc.append(loc_item)
    print(len(loc))
    print(loc[0])
    numpy.save(n_loc_npy, numpy.array(loc))