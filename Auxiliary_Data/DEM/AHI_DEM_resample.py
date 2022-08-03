import numpy
import xarray
from osgeo import osr
from osgeo import gdal


AHI_EXTENT = ['n60', 'e085', 's60', 'w155']     # ullat, ullon, lrlat, lrlon

AHI_RESOLUTION = 0.01       # degree


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


def get_dem_tiffs_e():
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
    tile_lon_indexs = e_lon_strs
    # print(tile_lon_indexs)
    tif_tiles_files = []
    for tile_lat_index in tile_lat_indexs:
        for tile_lon_index in tile_lon_indexs:
            tif_tiles_file = tile_lat_index + tile_lon_index + tif_suffix
            tif_tiles_files.append(tif_tiles_file)
    print(tif_tiles_files)


def get_dem_tiffs_w():
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
    w_lons = range(180, 155, -5)
    w_lon_strs = []
    for w_lon in w_lons:
        w_lon_str = 'w' + (3 - len(str(w_lon))) * '0' + str(w_lon)
        w_lon_strs.append(w_lon_str)
    tile_lon_indexs = w_lon_strs
    # print(tile_lon_indexs)
    tif_tiles_files = []
    for tile_lat_index in tile_lat_indexs:
        for tile_lon_index in tile_lon_indexs:
            tif_tiles_file = tile_lat_index + tile_lon_index + tif_suffix
            tif_tiles_files.append(tif_tiles_file)
    print(tif_tiles_files)


def show_merged_dem_info(merged_dem_tif):
    dem_ds = xarray.open_rasterio(merged_dem_tif)
    lat_array = numpy.array(dem_ds['y'])
    lon_array = numpy.array(dem_ds['x'])
    print(len(lat_array), len(lon_array))
    print(lat_array[0], lon_array[0])
    print(lat_array.max(), lon_array.min(), lat_array.min(), lon_array.max())


def clip_resampled_dem(merged_dem_tif, resample_dem_tif):
    dem_ds = xarray.open_rasterio(merged_dem_tif)
    argi_lats = numpy.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
    argi_lons = numpy.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)
    res_ds = dem_ds.interp(x=argi_lons, y=argi_lats, method="nearest", kwargs={"fill_value": "extrapolate"})
    dem_array = numpy.array(res_ds[0])
    no_data_value = -9999
    file_format = "GTiff"
    full_geotransform = [85., AHI_RESOLUTION, 0, 60, 0, -AHI_RESOLUTION]
    driver = gdal.GetDriverByName(file_format)
    pre_ds = driver.Create(resample_dem_tif, 120*int(1./AHI_RESOLUTION), 120*int(1./AHI_RESOLUTION), 1, gdal.GDT_Float32)
    pre_ds.SetGeoTransform(full_geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    pre_ds.SetProjection(srs.ExportToWkt())
    pre_ds.GetRasterBand(1).SetNoDataValue(no_data_value)
    pre_ds.GetRasterBand(1).WriteArray(dem_array)
    del pre_ds


if __name__ == "__main__":
    ws = '/data01/people/beichen/workspace/20220803'

    # get_dem_tiffs()
    # get_dem_tiffs_e()
    # get_dem_tiffs_w()
    # show_merged_dem_info('/data01/people/beichen/workspace/20220803/merged_dem4AHI.tif')
    # python gdal_merge.py -o input.tif output.tif
    # gdal_translate -t_srs EPSG:4326 -tr 0.01 0.01 -r average  input.tif output.tif
    clip_resampled_dem(ws + '/merged_dem4AHI_1km.tif', ws + '/MERIT_DEM_AHI_1km.tif')