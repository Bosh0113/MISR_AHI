import xarray

CAMS_pixel_size = 0.75


def get_region_ozone(a_array, a_lulon, a_lulat, r_extent):
    print('Extent:', r_extent)
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    ullat = r_extent[0]
    ullon = r_extent[1]
    lrlat = r_extent[2]
    lrlon = r_extent[3]
    min_x = round((ullon - a_lulon) / CAMS_pixel_size)
    max_x = round((lrlon - a_lulon) / CAMS_pixel_size)
    min_y = round((a_lulat - ullat) / CAMS_pixel_size)
    max_y = round((a_lulat - lrlat) / CAMS_pixel_size)
    r_ozone = a_array[min_y:max_y + 1, min_x:max_x + 1]
    print('ROI ozone (kg/m^2):', r_ozone.shape)
    print(r_ozone)
    mean_r_ozone = r_ozone.mean()
    print('ROI mean ozone (kg/m^2):', round(mean_r_ozone, 3))
    ozone_6s_input = round(mean_r_ozone * 46.6975764, 3)
    print('ROI mean ozone (cm-atm):', ozone_6s_input)
    return ozone_6s_input


def read_ozone(ozone_nc_filename):
    ds = xarray.open_dataset(nc_file)
    # print(ds)
    # gtco3 (time, latitude, longitude) float32 ...
    ozone_array = ds['gtco3'].data[0]
    ullon = ds['longitude'].data[0]
    ullat = ds['latitude'].data[0]
    # print('ullon:', ullon, '- ullat:', ullat)
    return ozone_array, ullon, ullat


def get_region_water(a_array, a_lulon, a_lulat, r_extent):
    print('Extent:', r_extent)
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    ullat = r_extent[0]
    ullon = r_extent[1]
    lrlat = r_extent[2]
    lrlon = r_extent[3]
    min_x = round((ullon - a_lulon) / CAMS_pixel_size)
    max_x = round((lrlon - a_lulon) / CAMS_pixel_size)
    min_y = round((a_lulat - ullat) / CAMS_pixel_size)
    max_y = round((a_lulat - lrlat) / CAMS_pixel_size)
    r_water = a_array[min_y:max_y + 1, min_x:max_x + 1]
    print('ROI water vapour (kg/m^2):', r_water.shape)
    print(r_water)
    mean_r_water = r_water.mean()
    print('ROI mean water vapour (kg/m^2):', round(mean_r_water, 3))
    water_vapour_6s_input = round(mean_r_water / 10, 3)
    print('ROI mean water vapour (g/cm^2):', water_vapour_6s_input)
    return water_vapour_6s_input


def read_water_vapour(water_nc_filename):
    ds = xarray.open_dataset(nc_file)
    # print(ds)
    # tcwv (time, latitude, longitude) float32 ...
    water_array = ds['tcwv'].data[0]
    ullon = ds['longitude'].data[0]
    ullat = ds['latitude'].data[0]
    # print('ullon:', ullon, '- ullat:', ullat)
    return water_array, ullon, ullat


if __name__ == "__main__":
    nc_file = r'D:\Work_PhD\MISR_AHI_WS\220309\ozone_201601010000.nc'
    ozone_ahi, minlon, maxlat = read_ozone(nc_file)
    # ROI demo '26.1_50':
    print('ROI:', '26.1_50')
    roi_extent = [1.804, 117.288, 1.623, 117.468]
    get_region_ozone(ozone_ahi, minlon, maxlat, roi_extent)
