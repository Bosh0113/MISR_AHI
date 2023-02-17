import os
import numpy

ws = r'D:\MISR_AHI_WS\230217'

mod_ray_npy = os.path.join(ws, 'Ray_MOD09_land_lonlat_10km.npy')
myd_ray_npy = os.path.join(ws, 'Ray_MYD09_land_lonlat_10km.npy')
modis_ray_npy = os.path.join(ws, 'Ray_MODIS_land_lonlat_10km.npy')


def main():
    mod_lonlat_list = numpy.load(mod_ray_npy, allow_pickle=True)
    mod_lonlat_list = mod_lonlat_list.tolist()
    print('ahi-mod:', len(mod_lonlat_list))
    myd_lonlat_list = numpy.load(myd_ray_npy, allow_pickle=True)
    myd_lonlat_list = myd_lonlat_list.tolist()
    print('ahi-myd:', len(myd_lonlat_list))
    print('no-combine:', len(mod_lonlat_list) + len(myd_lonlat_list))
    merge_lonlat_list = numpy.copy(mod_lonlat_list)
    merge_lonlat_list = merge_lonlat_list.tolist()
    lonlat_str_list = []
    for mod_lonlat in mod_lonlat_list:
        lonlat_str_list.append(str(mod_lonlat))
    for idx in range(len(myd_lonlat_list)):
        myd_lonlat = myd_lonlat_list[idx]
        if str(myd_lonlat) in lonlat_str_list:
            pass
        else:
            lonlat_str_list.append(str(myd_lonlat))
            merge_lonlat_list.append(myd_lonlat)
    print('ahi-modis:', len(merge_lonlat_list))
    numpy.save(modis_ray_npy, merge_lonlat_list)
    merge_lonlat_str = ''
    for lonlat in merge_lonlat_list:
        lon = lonlat[0]
        lat = lonlat[1]
        merge_lonlat_str += str(lon) + ' ' + str(lat) + '\n'
    with open(os.path.join(ws, 'Ray_MODIS_land_lonlat_10km.txt'), 'w') as f:
        f.write(merge_lonlat_str)


if __name__ == "__main__":
    main()