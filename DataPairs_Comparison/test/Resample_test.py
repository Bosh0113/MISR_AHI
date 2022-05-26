# for python 3.6
import os
import json
from MisrToolkit import MtkRegion, MtkFile
import numpy
# from osgeo import osr, gdal

workspace = r'D:\Work_PhD\MISR_AHI_WS\220526\test'
AHI_b1_file = os.path.join(workspace, '201608230450.vis.01.fld.geoss')
MISR_hdf = os.path.join(workspace, 'MISR_AM1_AS_LAND_P140_O088727_F07_0022.hdf')
ROI_json = os.path.join(workspace, '70.5_200.json')

MISR_resolution = 1100
MISR_camera = 0
MISR_band = 0

MISR_ROI_OUTPUT = os.path.join(workspace, 'MISR_ROI_SRF.tif')
# test
MISR_ROI_LON = os.path.join(workspace, 'MISR_ROI_LON.tif')
MISR_ROI_LAT = os.path.join(workspace, 'MISR_ROI_LAT.tif')


def get_extent(polygon_points):
    ullat = polygon_points[0][1]
    ullon = polygon_points[0][0]
    lrlat = polygon_points[0][1]
    lrlon = polygon_points[0][0]

    for pt in polygon_points:
        lat = pt[1]
        lon = pt[0]
        if ullat < lat:
            ullat = lat
        if lrlat > lat:
            lrlat = lat
        # all polygon in eastern Earth
        if ullon > lon:
            ullon = lon
        if lrlon < lon:
            lrlon = lon
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    return [ullat, ullon, lrlat, lrlon]


def get_ahi_latlon(region_extent):
    p_size = 120 / 12000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    count_line = ymax_index - ymin_index
    count_sample = xmax_index - xmin_index
    roi_ahi_latlon = []
    for y in range(count_line):
        roi_ahi_samples = []
        for x in range(count_sample):
            lat = ullat_ahi - (ymin_index + y)*p_size - p_size/2
            lon = ullon_ahi + (xmin_index + x)*p_size + p_size/2
            roi_ahi_samples.append([lat, lon])
        roi_ahi_latlon.append(roi_ahi_samples)
    return roi_ahi_latlon


if __name__ == "__main__":
    with open(ROI_json, 'r', encoding='utf-8') as f:
        geoobj = json.load(f)
        polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
        roi_extent = get_extent(polygon_pts)
        print('roi_extent:', roi_extent)
        
        roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
        # paths = roi_r.path_list
        path = 140
        block_rs = roi_r.block_range(path)
        block_r = block_rs[0]
        m_file = MtkFile(MISR_hdf)
        m_grid = m_file.grid('SubregParamsLnd')
        m_field = m_grid.field('LandBRF[' + str(MISR_band) + ']'+'[' + str(MISR_camera) + ']')
        # m_grid = m_file.grid('RegParamsLnd')
        # m_field = m_grid.field('SolZenAng')
        # MISR_resolution = m_grid.resolution

        # get data in ROI with MtkRegion
        brf_roi_dataPlane = m_field.read(roi_r)
        brf_roi_dataArray = brf_roi_dataPlane.data()
        # print(brf_roi_dataArray)    # value is different with clipped from block...why???
        misr_roi_mapinfo = brf_roi_dataPlane.mapinfo()

        # get latlon of pixels of AHI
        roi_ahi_latlon = get_ahi_latlon(roi_extent)
        lat_ahi = roi_ahi_latlon[0][0][0]
        lon_ahi = roi_ahi_latlon[0][0][1]
        line_sample = misr_roi_mapinfo.latlon_to_ls(lat_ahi, lon_ahi)
        line_misr = round(line_sample[0])
        sample_misr = round(line_sample[1])
        misr_value = brf_roi_dataArray[line_misr][sample_misr]
        print(misr_value)

        # # Create tiff
        # misr_roi_latlon = misr_roi_mapinfo.create_latlon()
        # misr_roi_latlon = numpy.array(misr_roi_latlon)
        # misr_roi_lats = misr_roi_latlon[0]
        # misr_roi_lons = misr_roi_latlon[1]
        # misr_roi_width = brf_roi_dataArray.shape[1]
        # misr_roi_height = brf_roi_dataArray.shape[0]
        # lon_interval = misr_roi_lons[0][1] - misr_roi_lons[0][0]
        # ul_lon = misr_roi_lons[0][0] - lon_interval/2
        # lat_interval = 0 - (misr_roi_lats[0][0] - misr_roi_lats[1][0])
        # ul_lat = misr_roi_lats[0][0] - lat_interval/2
        # driver = gdal.GetDriverByName("GTiff")
        # # dst_ds = driver.Create(MISR_ROI_OUTPUT, xsize=misr_roi_width, ysize=misr_roi_height, bands=1, eType=gdal.GDT_Float32)
        # # dst_ds = driver.Create(MISR_ROI_LON, xsize=misr_roi_width, ysize=misr_roi_height, bands=1, eType=gdal.GDT_Float32)
        # dst_ds = driver.Create(MISR_ROI_LAT, xsize=misr_roi_width, ysize=misr_roi_height, bands=1, eType=gdal.GDT_Float32)
        # # Upper Left x, Eeast-West px resolution, rotation, Upper Left y, rotation, North-South px resolution
        # transform_para = [ul_lon, lon_interval, 0, ul_lat, 0, lat_interval]
        # print(transform_para)
        # dst_ds.SetGeoTransform(transform_para)
        # # Set CRS
        # srs = osr.SpatialReference()
        # srs.SetWellKnownGeogCS("WGS84")
        # dst_ds.SetProjection(srs.ExportToWkt())
        # # Write the band
        # dst_ds.GetRasterBand(1).SetNoDataValue(65533)   # optional if no-data transparent
        # # dst_ds.GetRasterBand(1).WriteArray(brf_roi_dataArray)
        # # dst_ds.GetRasterBand(1).WriteArray(misr_roi_lons)
        # dst_ds.GetRasterBand(1).WriteArray(misr_roi_lats)
        # del dst_ds
