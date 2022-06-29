import numpy
import xarray
import os
from MisrToolkit import MtkFile, MtkRegion, orbit_to_path, latlon_to_bls
import netCDF4
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math

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


def get_raa(vaa, saa):
    raa = 0
    diff = abs(vaa - saa)
    if diff < 180:
        raa = diff
    else:
        raa = 360 - diff
    return raa


def get_misr_raa(misr_vaa, misr_saa):
    misr_raa = numpy.zeros_like(misr_vaa)
    for i in range(len(misr_vaa)):
        vaa = misr_vaa[i]
        saa = misr_saa[i]
        raa = get_raa(vaa, saa)
        misr_raa[i] = raa
    return misr_raa


def misr_obs_condition(r_extent, misrv3_nc_filename):
    roi_r = MtkRegion(r_extent[0], r_extent[1], r_extent[2], r_extent[3])
    m_file_ag = MtkFile(misrv3_nc_filename)
    m_grid44 = m_file_ag.grid('4.4_KM_PRODUCTS')
    m_field_vza = m_grid44.field('GEOMETRY/View_Zenith_Angle[4]')
    m_field_sza = m_grid44.field('GEOMETRY/Solar_Zenith_Angle')
    f_vza_data = m_field_vza.read(roi_r).data()
    roi_misr_vza_list = f_vza_data.flatten()
    roi_misr_vza_list = numpy.setdiff1d(roi_misr_vza_list, [-9999])
    roi_misr_vza = roi_misr_vza_list.mean()
    f_sza_data = m_field_sza.read(roi_r).data()
    roi_misr_sza_list = f_sza_data.flatten()
    roi_misr_sza_list = numpy.setdiff1d(roi_misr_sza_list, [-9999])
    roi_misr_sza = roi_misr_sza_list.mean()
    m_field_vaa = m_grid44.field('GEOMETRY/View_Azimuth_Angle[4]')
    m_field_saa = m_grid44.field('GEOMETRY/Solar_Azimuth_Angle')
    # in single array
    f_vaa_data = m_field_vaa.read(roi_r).data()
    roi_misr_vaa_list = f_vaa_data.flatten()
    f_saa_data = m_field_saa.read(roi_r).data()
    roi_misr_saa_list = f_saa_data.flatten()
    roi_misr_vaa_list = numpy.setdiff1d(roi_misr_vaa_list, [-9999])
    roi_misr_saa_list = numpy.setdiff1d(roi_misr_saa_list, [-9999])
    roi_misr_raa = 0
    if len(roi_misr_vaa_list) > 0:
        f_raa_data = get_misr_raa(roi_misr_vaa_list, roi_misr_saa_list)
        roi_misr_raa = f_raa_data.mean()
    return roi_misr_vza, roi_misr_sza, roi_misr_raa


def mapping(array, title):
    plt.imshow(array)
    plt.title(title)
    plt.colorbar()
    plt.show()


def linear_regression(x_array, y_array):
    max_v = max(x_array.max(), y_array.max())
    ticks_max = max_v + 0.02*2
    fig, ax = plt.subplots()
    ax.scatter(x_array, y_array, alpha=0.7, edgecolors="k")
    b, a = numpy.polyfit(x_array, y_array, deg=1)
    # print('slope:', b, '; intercept:', a)
    xseq = numpy.linspace(0, ticks_max, num=100)
    ax.plot(xseq, a + b * xseq, color="k", lw=2)
    ax.plot(xseq, xseq, 'r--', label='line 1', alpha=0.5, linewidth=1)
    minorLocator = MultipleLocator(0.02)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.yaxis.set_minor_locator(minorLocator)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.xticks(numpy.arange(0, ticks_max, 0.1))
    plt.yticks(numpy.arange(0, ticks_max, 0.1))
    plt.xlim((0, ticks_max))
    plt.ylim((0, ticks_max))
    plt.xlabel('MISR SR')
    plt.ylabel('MODIS SR')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    r2 = r2_score(x_array, y_array)
    rmse = math.sqrt(mean_squared_error(x_array, y_array))
    # print(r2)
    # print(rmse)
    text = 'R^2=' + str(round(r2, 3)) + '\ny=' + str(round(b, 2)) + '*x+' + str(round(a, 3)) + '\nRMSE=' + str(round(rmse, 3))
    plt.text(x=0.01, y=ticks_max-0.02*3, s=text, fontsize=12)
    plt.show()


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220615'

    # roi_extent: (ullat, ullon, lrlat, lrlon)
    # roi_extent = [-13.322, 135.360, -13.497, 135.540]
    roi_extent = [-13.322, 135.060, -13.497, 135.240]

    # MOD09A1061 folder
    modis_folder = os.path.join(ws, '0_120_buff_MOD09A1061')

    # MOD09A1061 Obs. condition
    vza_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_vzen.tif')
    sza_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_szen.tif')
    raa_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_raz.tif')
    # modis vza roi
    vza_modis_roi_ar_ds = modis_angle_roi(roi_extent, vza_modis_tiff)
    vza_modis_roi_ar = numpy.array(vza_modis_roi_ar_ds)
    vza_modis_roi_ar1 = vza_modis_roi_ar.flatten()
    vza_modis_roi_ar1 = vza_modis_roi_ar1[vza_modis_roi_ar1 >= 0]
    vza_modis_roi = vza_modis_roi_ar1.mean()
    vza_modis_roi_ar_ds.close()
    # print('MODIS VZA:', vza_modis_roi)
    # modis sza roi
    sza_modis_roi_ar_ds = modis_angle_roi(roi_extent, sza_modis_tiff)
    sza_modis_roi_ar = numpy.array(sza_modis_roi_ar_ds)
    sza_modis_roi_ar1 = sza_modis_roi_ar.flatten()
    sza_modis_roi_ar1 = sza_modis_roi_ar1[sza_modis_roi_ar1 >= 0]
    sza_modis_roi = sza_modis_roi_ar1.mean()
    sza_modis_roi_ar_ds.close()
    # print('MODIS SZA:', sza_modis_roi)
    # modis raa roi
    raa_modis_roi_ar_ds = modis_angle_roi(roi_extent, raa_modis_tiff)
    raa_modis_roi_ar = numpy.array(raa_modis_roi_ar_ds)
    raa_modis_roi_ar1 = raa_modis_roi_ar.flatten()
    raa_modis_roi_ar1 = raa_modis_roi_ar1[raa_modis_roi_ar1 >= 0]
    raa_modis_roi = raa_modis_roi_ar1.mean()
    raa_modis_roi_ar_ds.close()
    # print('MODIS RAA:', raa_modis_roi)

    # MOD09A1061 Surface Reflectance
    sr3_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_b01.tif')     # MODIS band1 <-> MISR band3
    sr4_modis_tiff = os.path.join(modis_folder, 'MOD09A1.061_sur_refl_b02.tif')     # MODIS band2 <-> MISR band4
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
    vza_misr_roi, sza_misr_roi, raa_misr_roi = misr_obs_condition(roi_extent, misr_nc_filename)     # MISR observation condition
    print('MODIS VZA:', round(vza_modis_roi), ' | MISR VZA:', round(vza_misr_roi))
    print('MODIS SZA:', round(sza_modis_roi), ' | MISR SZA:', round(sza_misr_roi))
    print('MODIS RAA:', round(raa_modis_roi), ' | MISR RAA:', round(raa_misr_roi))
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

    # # mapping
    # mapping(sr3_modis_roi, 'ROI_0.0_120 SR MODIS Band1')
    # mapping(sr4_modis_roi, 'ROI_0.0_120 SR MODIS Band2')
    # mapping(sr3_misr_roi, 'ROI_0.0_120 SR MISR Band3')
    # mapping(sr4_misr_roi, 'ROI_0.0_120 SR MISR Band4')
    # linear regression
    linear_regression(sr3_misr_roi.flatten()/1.038, sr3_modis_roi.flatten())
    linear_regression(sr4_misr_roi.flatten()/0.997, sr4_modis_roi.flatten())

    # print(sr3_misr_roi.shape)
