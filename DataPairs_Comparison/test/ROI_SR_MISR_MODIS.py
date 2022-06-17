import numpy
import xarray
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import matplotlib.pyplot as plt

AHI_RESOLUTION = 0.01  # degree


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


# Get ROI Data from Rough Dataset with AHI Resolution (simple version)
def get_data_roi_ahi_reso(r_extent, data_v, lats, lons, o_resolution):
    r_ullat = r_extent[0]
    r_ullon = r_extent[1]
    r_lrlat = r_extent[2]
    r_lrlon = r_extent[3]

    ex_ds = xarray.Dataset(
        data_vars={
            "values": (("latitude", "longitude"), data_v),
        },
        coords={
            "latitude": lats,
            "longitude": lons
        },
    )

    ahi_lats = numpy.arange(60.-AHI_RESOLUTION/2, -60, -AHI_RESOLUTION)
    ahi_lons = numpy.arange(85.+AHI_RESOLUTION/2, 205, AHI_RESOLUTION)
    n_lats = ahi_lats[find_nearest_index(ahi_lats, r_ullat):find_nearest_index(ahi_lats, r_lrlat) + 1]
    n_lons = ahi_lons[find_nearest_index(ahi_lons, r_ullon):find_nearest_index(ahi_lons, r_lrlon) + 1]
    n_ex_ds = ex_ds.interp(longitude=n_lons, latitude=n_lats, method="nearest", kwargs={"fill_value": "extrapolate"})  # linear?
    n_ex_v = n_ex_ds["values"]
    return n_ex_v


def modis_angle_roi(r_extent, modis_tiff):    
    modis_ds = xarray.open_rasterio(modis_tiff)
    modis_scale_factor = modis_ds.scale_factor
    modis_add_offset = modis_ds.add_offset
    modis_res = modis_ds.res[0]
    lat = numpy.array(modis_ds['y'])
    lon = numpy.array(modis_ds['x'])
    vals_dn = numpy.array(modis_ds)[0]
    vals = vals_dn*float(modis_scale_factor) + float(modis_add_offset)
    modis_roi_ar_ds = get_data_roi_ahi_reso(r_extent, vals, lat, lon, modis_res)
    return modis_roi_ar_ds


def mapping(array, title):
    plt.imshow(array)
    plt.title(title)
    plt.colorbar()
    plt.show()
    

if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220615'

    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [-13.322, 135.360, -13.497, 135.540]

    # MOD09A1061 folder
    modis_folder = os.path.join(ws, '0_120_buff_MOD09A1061')

    # # MOD09A1061 Obs. condition
    # vza_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_vzen.tif')
    # sza_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_szen.tif')
    raa_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_raz.tif')
    # # modis vza roi
    # vza_modis_roi_ar_ds = modis_angle_roi(roi_extent, vza_modis_tiff)
    # vza_modis_roi_ar = numpy.array(vza_modis_roi_ar_ds)
    # vza_modis_roi_ar1 = vza_modis_roi_ar.flatten()
    # vza_modis_roi_ar1 = vza_modis_roi_ar1[vza_modis_roi_ar1 >= 0]
    # vza_modis_roi = vza_modis_roi_ar1.mean()
    # vza_modis_roi_ar_ds.close()
    # print('MODIS VZA:', vza_modis_roi)
    # # modis sza roi
    # sza_modis_roi_ar_ds = modis_angle_roi(roi_extent, sza_modis_tiff)
    # sza_modis_roi_ar = numpy.array(sza_modis_roi_ar_ds)
    # sza_modis_roi_ar1 = sza_modis_roi_ar.flatten()
    # sza_modis_roi_ar1 = sza_modis_roi_ar1[sza_modis_roi_ar1 >= 0]
    # sza_modis_roi = sza_modis_roi_ar1.mean()
    # sza_modis_roi_ar_ds.close()
    # print('MODIS SZA:', sza_modis_roi)
    # # modis raa roi
    # raa_modis_roi_ar_ds = modis_angle_roi(roi_extent, raa_modis_tiff)
    # raa_modis_roi_ar = numpy.array(raa_modis_roi_ar_ds)
    # raa_modis_roi_ar1 = raa_modis_roi_ar.flatten()
    # raa_modis_roi_ar1 = raa_modis_roi_ar1[raa_modis_roi_ar1 >= 0]
    # raa_modis_roi = raa_modis_roi_ar1.mean()
    # raa_modis_roi_ar_ds.close()
    # print('MODIS RAA:', raa_modis_roi)

    # MOD09A1061 Surface Reflectance
    sr3_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_b03.tif')
    sr4_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_b04.tif')
    sr3_modis_roi_ar_ds = modis_angle_roi(roi_extent, sr3_modis_tiff)
    sr4_modis_roi_ar_ds = modis_angle_roi(roi_extent, sr4_modis_tiff)
    sr3_modis_roi = numpy.array(sr3_modis_roi_ar_ds)
    sr4_modis_roi = numpy.array(sr4_modis_roi_ar_ds)

    lons = numpy.array(sr4_modis_roi_ar_ds['longitude'])
    lats = numpy.array(sr4_modis_roi_ar_ds['latitude'])

    # MIL2ASLS.003 folder
    misr_folder = os.path.join(ws, '0_120_misr_20160928')
    # MIL2ASLS.003 BRF
    misr_nc_filename = os.path.join(misr_folder, 'MISR_AM1_AS_LAND_P104_O089249_F08_0023.nc')
    misr_nc_ds = netCDF4.Dataset(misr_nc_filename)
    misr_nc_11 = misr_nc_ds.groups['1.1_KM_PRODUCTS']
    misr_brf_var = misr_nc_11.variables['Bidirectional_Reflectance_Factor']
    misr_brf_scalev3 = misr_brf_var.scale_factor
    misr_brf_offsetv3 = misr_brf_var.add_offset
    misr_nc_ds.close()
    m_file2 = MtkFile(misr_nc_filename)
    misr_orbit = m_file2.orbit
    misr_path = orbit_to_path(misr_orbit)
    m_grid11 = m_file2.grid('1.1_KM_PRODUCTS')
    misr_resolutionv3 = m_grid11.resolution
    m_field_b3_c5 = m_grid11.field('Bidirectional_Reflectance_Factor[2][4]')    # band_index, camera_index
    m_field_b4_c5 = m_grid11.field('Bidirectional_Reflectance_Factor[3][4]')    # band_index, camera_index
    
    sr3_misr_roi = numpy.ones((len(lats), len(lons)))
    sr4_misr_roi = numpy.ones((len(lats), len(lons)))
    misr_v3_nodata = [65532, 65533, 65534, 65535]
    for lat_idx in range(len(lats)):
        for lon_idx in range(len(lons)):
            lat = lats[lat_idx]
            lon = lons[lon_idx]
            misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
            block_llv3 = misr_blsv3[0]
            b_lat_idxv3 = round(misr_blsv3[1])
            b_lon_idxv3 = round(misr_blsv3[2])
            block_brf_b3_dnv3 = m_field_b3_c5.read(block_llv3, block_llv3)[0]
            block_brf_b4_dnv3 = m_field_b4_c5.read(block_llv3, block_llv3)[0]
            roi_brf_b3_dnv3 = block_brf_b3_dnv3[b_lat_idxv3][b_lon_idxv3]
            roi_brf_b4_dnv3 = block_brf_b4_dnv3[b_lat_idxv3][b_lon_idxv3]
            roi_brf_b3_tv3 = roi_brf_b3_dnv3 * misr_brf_scalev3 + misr_brf_offsetv3
            roi_brf_b4_tv3 = roi_brf_b4_dnv3 * misr_brf_scalev3 + misr_brf_offsetv3
            if roi_brf_b3_dnv3 in misr_v3_nodata:
                roi_brf_b3_tv3 = numpy.NaN
            if roi_brf_b4_dnv3 in misr_v3_nodata:
                roi_brf_b4_tv3 = numpy.NaN
            sr3_misr_roi[lat_idx][lon_idx] = roi_brf_b3_tv3
            sr4_misr_roi[lat_idx][lon_idx] = roi_brf_b4_tv3
    
    # mapping
    mapping(sr3_modis_roi, 'ROI_0.0_120 SR MODIS Band3')
    mapping(sr4_modis_roi, 'ROI_0.0_120 SR MODIS Band4')
    mapping(sr3_misr_roi, 'ROI_0.0_120 SR MISR Band3')
    mapping(sr4_misr_roi, 'ROI_0.0_120 SR MISR Band4')
    
    # print(sr3_misr_roi.shape)