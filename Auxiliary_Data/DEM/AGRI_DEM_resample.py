import numpy
import xarray
from osgeo import osr
from osgeo import gdal


AGRI_EXTENT = ['n60', 'e044', 's60', 'e164']     # ullat, ullon, lrlat, lrlon

AGRI_RESOLUTION = 0.01      # degree


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
    e_lons = range(40, 165, 5)
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


def clip_resampled_dem(merged_dem_tif, resample_dem_tif):
    dem_ds = xarray.open_rasterio(merged_dem_tif)
    argi_lats = numpy.arange(60. - AGRI_RESOLUTION / 2, -60, -AGRI_RESOLUTION)
    argi_lons = numpy.arange(44. + AGRI_RESOLUTION / 2, 164, AGRI_RESOLUTION)
    res_ds = dem_ds.interp(x=argi_lons, y=argi_lats, method="nearest", kwargs={"fill_value": "extrapolate"})
    dem_array = numpy.array(res_ds[0])
    no_data_value = -9999
    file_format = "GTiff"
    full_geotransform = [44., AGRI_RESOLUTION, 0, 60, 0, -AGRI_RESOLUTION]
    driver = gdal.GetDriverByName(file_format)
    pre_ds = driver.Create(resample_dem_tif, 120*int(1./AGRI_RESOLUTION), 120*int(1./AGRI_RESOLUTION), 1, gdal.GDT_Float32)
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
    # python gdal_merge.py -o input.tif output.tif
    # gdal_translate -t_srs EPSG:4326 -tr 0.01 0.01 -r average  input.tif output.tif
    clip_resampled_dem(ws + '/merged_dem4AGRI_1km.tif', ws + '/MERIT_DEM_AGRI_1km.tif')