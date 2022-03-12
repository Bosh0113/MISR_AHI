from PIL import Image
import numpy
import os

dem_pixel_size = 5. / 6000

dem_folder = r'D:\Work_PhD\MISR_AHI_WS\220309\dem'

roi_extents = {
    '0.0_50': [-3.349, 136.322, -3.529, 136.502],
    '0.0_60': [-13.723, 142.529, -13.899, 142.709],
    '0.0_120': [-14.399, 142.376, -14.574, 142.556],
    '26.1_10': [17.253, 121.631, 17.081, 121.811],
    '26.1_50': [1.804, 117.288, 1.623, 117.468],
    '26.1_150': [-23.264, 137.174, -23.43, 137.354],
    '45.6_10': [14.266, 103.136, 14.091, 103.315],
    '45.6_20': [32.09, 115.95, 31.937, 116.13],
    '45.6_60': [39.79, 141.501, 39.651, 141.681],
    '60.0_80': [51.851, 131.586, 51.739, 131.766],
    '60.0_130': [35.475, 98.872, 35.328, 99.052],
    '60.0_200': [42.99, 107.043, 42.858, 107.223],
    '70.5_80': [59.637, 117.273, 59.545, 117.452],
    '70.5_130': [43.625, 90.772, 43.495, 90.952],
    '70.5_200': [47.325, 94.329, 47.203, 94.508]
}

roi_demFiles = {
    '0.0_50': 's05e135_dem.tif',
    '0.0_60': 's15e140_dem.tif',
    '0.0_120': 's15e140_dem.tif',
    '26.1_10': 'n15e120_dem.tif',
    '26.1_50': 'n00e115_dem.tif',
    '26.1_150': 's25e135_dem.tif',
    '45.6_10': 'n10e100_dem.tif',
    '45.6_20': 'n30e115_dem.tif',
    '45.6_60': 'n35e140_dem.tif',
    '60.0_80': 'n50e130_dem.tif',
    '60.0_130': 'n35e095_dem.tif',
    '60.0_200': 'n40e105_dem.tif',
    '70.5_80': 'n55e115_dem.tif',
    '70.5_130': 'n40e090_dem.tif',
    '70.5_200': 'n45e090_dem.tif'
}


def get_lulon_lulat(dem_file):
    lulat = 0
    ldlat_str = dem_file[:3]
    # print(dem_file)
    ldlat = 0
    if ldlat_str[0] == 's':
        ldlat = float(ldlat_str[1:3]) * -1
    elif ldlat_str[0] == 'n':
        ldlat = float(ldlat_str[1:3])
    lulat = ldlat + 5.
    lulon = float(dem_file[4:7])
    # print(lulon, lulat)
    return lulon, lulat


def region_altitude(a_array, a_lulon, a_lulat, r_extent):
    print('Extent:', r_extent)
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    ullat = r_extent[0]
    ullon = r_extent[1]
    lrlat = r_extent[2]
    lrlon = r_extent[3]
    min_x = round((ullon - a_lulon) / dem_pixel_size)
    max_x = round((lrlon - a_lulon) / dem_pixel_size)
    min_y = round((a_lulat - ullat) / dem_pixel_size)
    max_y = round((a_lulat - lrlat) / dem_pixel_size)
    r_altitude = a_array[min_y:max_y, min_x:max_x]
    print('ROI altitude (meter):', r_altitude.shape)
    print(r_altitude)
    mean_r_altitude = r_altitude.mean()
    print('ROI mean altitude (meter):', round(mean_r_altitude, 3))
    print('ROI mean altitude (kilometer):', round(mean_r_altitude / 1000, 3))


def get_roi_altitude(roi_name):
    print('**************')
    print('ROI:', roi_name)
    tif_file = roi_demFiles[roi_name]
    tif_file_path = os.path.join(dem_folder, tif_file)
    # 6000 * 6000 pixel in 4-byte float, little endian [meter]
    with open(tif_file_path, 'rb') as tf:
        dem_tif = Image.open(tf)
        dem_array = numpy.array(dem_tif, dtype=numpy.float32)
        d_lulon, d_lulat = get_lulon_lulat(tif_file)
        roi_extent = roi_extents[roi_name]
        region_altitude(dem_array, d_lulon, d_lulat, roi_extent)


if __name__ == "__main__":
    # for roi in roi_extents.keys():
    #     get_roi_altitude(roi)
    roi = '70.5_200'
    print('ROI:', roi)
    tif_file = roi_demFiles[roi]
    tif_file_path = os.path.join(dem_folder, tif_file)
    # 6000 * 6000 pixel in 4-byte float, little endian [meter]
    dem_tif = Image.open(tif_file_path)
    dem_array = numpy.array(dem_tif, dtype=numpy.float32)
    d_lulon, d_lulat = get_lulon_lulat(tif_file)
    roi_extent = roi_extents[roi]
    region_altitude(dem_array, d_lulon, d_lulat, roi_extent)
