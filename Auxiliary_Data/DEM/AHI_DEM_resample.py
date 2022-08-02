import os
import numpy


AHI_EXTENT = ['n60', 'e085', 's60', 'w155']     # lulat, lulon, rblat, rblon


def get_dem_tiffs():
    tif_suffix = '_dem.tif'
    s_lats = range(60, 0, -5)
    s_lat_strs = []
    for s_lat in s_lats:
        s_lat_str = 's' + (2 - len(str(s_lat))) * '0' + str(s_lat)
        s_lat_strs.append(s_lat_str)
    n_lats = range(0, 60, 5)
    n_lat_strs = []
    for n_lat in n_lats:
        n_lat_str = 'n' + (2 - len(str(n_lat))) * '0' + str(n_lat)
        n_lat_strs.append(n_lat_str)
    tile_lat_indexs = s_lat_strs + n_lat_strs
    # print(tile_lat_indexs)
    e_lons = range(85, 180, 5)
    e_lon_strs = []
    for e_lon in e_lons:
        e_lon_str = 'e' + (3 - len(str(e_lon))) * '0' + str(e_lon)
        e_lon_strs.append(e_lon_str)
    w_lons = range(180, 155, -5)
    w_lon_strs = []
    for w_lon in w_lons:
        w_lon_str = 'w' + (3 - len(str(w_lon))) * '0' + str(w_lon)
        w_lon_strs.append(w_lon_str)
    tile_lon_indexs = e_lon_strs + w_lon_strs
    # print(tile_lon_indexs)
    tif_tiles_files = []
    for tile_lat_index in tile_lat_indexs:
        for tile_lon_index in tile_lon_indexs:
            tif_tiles_file = tile_lat_index + tile_lon_index + tif_suffix
            tif_tiles_files.append(tif_tiles_file)
    print(tif_tiles_files)


if __name__ == "__main__":
    get_dem_tiffs()