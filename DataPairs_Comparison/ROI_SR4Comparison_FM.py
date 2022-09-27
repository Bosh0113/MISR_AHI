# for python 3.6
import os
from MisrToolkit import MtkFile, orbit_to_path, latlon_to_bls
import netCDF4
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, r2_score
import math

workspace = os.getcwd()
MISR_NC_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'
AHI_AC_FOLDER = os.path.join(workspace, 'AHI_AC_PARAMETER')

# https://www-pm.larc.nasa.gov/cgi-bin/site/showdoc?mnemonic=SBAF
# LandCover=* ReferenceSRF=AHI TargetSRF=MISR Units=PseudoScaledRadiance Regression=Linear
# SR(MISR2AHI) = SR(MISR)*Slope+Offset
AHI2MISR_SBAF = {   # slope offset
    '45_1_band1': [1.002, 0.01074],
    '45_1_band2': [0.962, -0.00243],
    '45_1_band3': [1.026, -0.003329],
    '45_1_band4': [1.008, 0.0009491],
    '45_2_band1': [1.057, 0.008603],
    '45_2_band2': [0.842, 0.0045],
    '45_2_band3': [1.011, -0.003679],
    '45_2_band4': [1.022, -0.0001949],
    '60_1_band1': [1.043, 0.006883],
    '60_1_band2': [0.968, -0.002409],
    '60_1_band3': [1.100, -0.006074],
    '60_1_band4': [1.019, -0.0001292],
    '60_2_band1': [1.034, 0.004636],
    '60_2_band2': [1.126, -0.005602],
    '60_2_band3': [1.175, -0.009857],
    '60_2_band4': [1.011, 0.0006747],
    '70_1_band1': [0.977, 0.008145],
    '70_1_band2': [1.011, 0.0008929],
    '70_1_band3': [1.099, -0.002729],
    '70_1_band4': [1.009, 0.0002536],
}


def BRF_TrueValue(o_value, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    if o_value in [fill, underflow, overflow]:
        return 0.
    else:
        y = o_value*scale + offset
        return y


def ahi_sr2misr_sr(ahi_sr_array, AHI2MISR_para):
    slope = AHI2MISR_para[0]
    offset = AHI2MISR_para[1]
    offset_array = numpy.ones_like(ahi_sr_array)
    offset_array = offset_array * offset
    return (ahi_sr_array - offset_array)/slope


def mapping(array, figure_title):
    plt.imshow(array)
    plt.title(figure_title)
    plt.colorbar()
    figure_folder = os.path.join(workspace, 'figure')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '.png')
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.savefig(fig_filename)
    print(fig_filename)
    # plt.show()
    plt.clf()


def mapping_scatter(x_arrray, y_array, figure_title):
    plt.scatter(x_arrray, y_array)
    plt.title(figure_title)
    plt.xlim((0, 0.5))
    plt.ylim((0, 0.5))
    plt.xlabel('AHI SR')
    plt.ylabel('MISR SR')
    figure_folder = os.path.join(workspace, 'figure_scatter')
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
    fig_filename = os.path.join(figure_folder, figure_title + '.png')
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.savefig(fig_filename)
    plt.clf()
    print(fig_filename)


def record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_para):
    ac_info = numpy.load(ahi_ac_npy, allow_pickle=True)[0]
    roi_lats = ac_info['roi_lats']
    roi_lons = ac_info['roi_lons']
    roi_ahi_sr = ac_info['roi_ahi_sr']
    roi_ahi_toa = ac_info['roi_ahi_data']
    # print(roi_ahi_sr)
    misr_path = orbit_to_path(misr_orbit)
    # MISR v3 netCDF4
    misr_nc = netCDF4.Dataset(misr_nc_filename)
    misr_nc_11 = misr_nc.groups['1.1_KM_PRODUCTS']
    misr_brf_var = misr_nc_11.variables['Bidirectional_Reflectance_Factor']
    misr_brf_scalev3 = misr_brf_var.scale_factor
    misr_brf_offsetv3 = misr_brf_var.add_offset
    misr_nc.close()
    m_file2 = MtkFile(misr_nc_filename)
    m_grid11 = m_file2.grid('1.1_KM_PRODUCTS')
    misr_resolutionv3 = m_grid11.resolution
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[' + str(band_index) + ']'+'[' + str(misr_camera_index) + ']')
    # MISR data at ROI
    roi_misr_brfv3 = numpy.zeros_like(roi_ahi_sr)
    for lat_index in range(len(roi_lats)):
        for lon_index in range(len(roi_lons)):
            lat = roi_lats[lat_index]
            lon = roi_lons[lon_index]
            misr_blsv3 = latlon_to_bls(misr_path, misr_resolutionv3, lat, lon)
            block_llv3 = misr_blsv3[0]
            b_lat_idxv3 = round(misr_blsv3[1])
            b_lon_idxv3 = round(misr_blsv3[2])
            block_brf_dnv3 = m_field11.read(block_llv3, block_llv3)[0]
            roi_brf_dnv3 = block_brf_dnv3[b_lat_idxv3][b_lon_idxv3]
            roi_brf_tv3 = BRF_TrueValue(roi_brf_dnv3, misr_brf_scalev3, misr_brf_offsetv3)
            roi_misr_brfv3[lat_index][lon_index] = roi_brf_tv3

    # if any cloud-free obs. is existed
    if roi_misr_brfv3.max() > 0.0:
        # MISR BRF v3
        roi_misr_brfv3[roi_misr_brfv3 <= 0.0] = numpy.NaN
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_misr_sr'
        mapping(roi_misr_brfv3, figure_title)

        mask_array = numpy.copy(roi_misr_brfv3)
        mask_array[mask_array > 0.0] = 1.

        # # TOA(AHI)
        # ahi_toa_misr = roi_ahi_toa*mask_array
        # figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_ahi_toa'
        # mapping(ahi_toa_misr, figure_title)

        # SR(AHI2MISR)
        ahi_sr_misr = ahi_sr2misr_sr(roi_ahi_sr, AHI2MISR_para)
        # print(ahi_sr_misr)
        ahi_sr_misr = ahi_sr_misr*mask_array
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_ahi_sr'
        mapping(ahi_sr_misr, figure_title)

        # # y=SR(MISR) / x=SR(AHI)
        figure_title = roi_name + '_' + ahi_obs_time + '_band_' + str(band_index + 1) + '_scatter_sr'
        mapping_scatter(ahi_sr_misr, roi_misr_brfv3, figure_title)

        # record as npy file
        record_info = [
            {
                'roi_name': roi_name,
                'band_index': band_index,
                'misr_orbit': misr_orbit,
                'misr_camera_index': misr_camera_index,
                'misr_v3': roi_misr_brfv3,
                'ahi_toa': roi_ahi_toa,
                'ahi_sr': roi_ahi_sr,
                'ahi_sr2misr': ahi_sr_misr
            }
        ]
        file_path = os.path.join(workspace, ahi_obs_time + '_sr_band' + str(band_index + 1) + '.npy')
        numpy.save(file_path, record_info)
        return roi_misr_brfv3, ahi_sr_misr
    return [], []


def get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy):
    misr_path_orbit = misr_path_orbit_camera[:12]
    misr_orbit = int(misr_path_orbit[-6:])
    band_index = int(ahi_ac_npy[-5:-4]) - 1
    band_name = 'band' + str(band_index + 1)
    AHI2MISR_para = AHI2MISR_SBAF[roi_name + '_' + band_name]
    misr_camera_index = int(misr_path_orbit_camera[-1:])
    ahi_obs_time = ahi_ac_npy[-25:-13]
    misr_nc_filename = os.path.join(MISR_NC_FOLDER, 'MISR_AM1_AS_LAND_' + misr_path_orbit + '_F08_0023.nc')
    roi_misr_sr, roi_ahi_sr_misr = record_roi_misr_ahi(roi_name, band_index, misr_orbit, misr_camera_index, ahi_obs_time, misr_nc_filename, ahi_ac_npy, AHI2MISR_para)
    return roi_misr_sr, roi_ahi_sr_misr


def mapping_scatter_all(x_3Darray, y_3Darray, color_array, ahi_obs_time_record, figure_title):
    max_axs = 0.5
    ax = plt.axes()
    for idx in range(len(x_3Darray)):
        x_2Darray = x_3Darray[idx]
        y_2Darray = y_3Darray[idx]
        color = color_array[idx]
        ahi_obs_time = ahi_obs_time_record[idx]
        plt.scatter(x_2Darray, y_2Darray, marker='o', edgecolors=[color], c='none', s=15, linewidths=0.5, label=ahi_obs_time[:8])
    # linear regression
    x_3Darray_np = numpy.array(x_3Darray)
    x_3Darray_np_1d = x_3Darray_np.flatten()
    x_3Darray_np_1d = x_3Darray_np_1d[~numpy.isnan(x_3Darray_np_1d)]
    y_3Darray_np = numpy.array(y_3Darray)
    y_3Darray_np_1d = y_3Darray_np.flatten()
    y_3Darray_np_1d = y_3Darray_np_1d[~numpy.isnan(y_3Darray_np_1d)]
    b, a = numpy.polyfit(x_3Darray_np_1d, y_3Darray_np_1d, deg=1)
    xseq = numpy.linspace(0, max_axs, num=100)
    ax.plot(xseq, a + b * xseq, color="k", lw=2)
    ax.plot(xseq, xseq, 'r--', alpha=0.5, linewidth=1)
    r2 = r2_score(x_3Darray_np_1d, y_3Darray_np_1d)
    rmse = math.sqrt(mean_squared_error(x_3Darray_np_1d, y_3Darray_np_1d))
    text = 'R^2=' + str(round(r2, 3)) + '\ny=' + str(round(b, 2)) + '*x+' + str(round(a, 3)) + '\nRMSE=' + str(round(rmse, 3))
    plt.text(x=0.01, y=max_axs-max_axs/5, s=text, fontsize=12)

    plt.title(figure_title)
    minorLocator = MultipleLocator(0.02)
    majorLocator = MultipleLocator(0.1)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.yaxis.set_minor_locator(minorLocator)
    ax.xaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_locator(majorLocator)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.xlim((0, max_axs))
    plt.ylim((0, max_axs))
    plt.xlabel('AHI SR')
    plt.ylabel('MISR SR')
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.legend(loc='lower right')
    fig_filename = os.path.join(workspace, figure_title + '.png')
    plt.savefig(fig_filename)
    # plt.show()
    plt.clf()


if __name__ == "__main__":
    misr_misr_vza = '45.6'
    roi_name = '45_1'
    # misr_misr_vza = '45.6'
    # roi_name = '45_2'
    # misr_misr_vza = '60.0'
    # roi_name = '60_1'
    # misr_misr_vza = '60.0'
    # roi_name = '60_2'
    # misr_misr_vza = '70.5'
    # roi_name = '70_1'

    band_names = ['band3', 'band4']
    matched_record_npy = os.path.join(workspace, misr_misr_vza + '_matched_record.npy')
    matched_record = numpy.load(matched_record_npy, allow_pickle=True)
    roi_matched_misr_roi_s = []
    for matched_roi_info in matched_record:
        roi_name_re = matched_roi_info['roi_name']
        if roi_name == roi_name_re:
            roi_misr_infos = matched_roi_info['roi_misr_infos']
            for band_name in band_names:
                roi_misr_record = []
                roi_ahi_record = []
                ahi_obs_time_record = []
                roi_matched_misr_roi = {}
                for roi_misr_info in roi_misr_infos:
                    misr_path_orbit_camera = roi_misr_info['misr_path_orbit_camera']
                    matched_info = roi_misr_info['matched_info']
                    ahi_obs_time = matched_info[4]
                    ahi_ac_npy = os.path.join(AHI_AC_FOLDER, str(ahi_obs_time) + '_ac_' + band_name + '.npy')
                    if os.path.exists(ahi_ac_npy):
                        roi_misr, roi_ahi = get_roi_misr_ahi(roi_name, misr_path_orbit_camera, ahi_ac_npy)
                        if len(roi_misr) > 0:
                            roi_misr_record.append(roi_misr)
                            roi_ahi_record.append(roi_ahi)
                            ahi_obs_time_record.append(str(ahi_obs_time))
                        print(str(ahi_obs_time) + '_' + band_name)
                roi_matched_misr_roi['band_name'] = band_name
                roi_matched_misr_roi['ahi_obs_time'] = ahi_obs_time_record
                roi_matched_misr_roi['misr_sr_3d'] = roi_misr_record
                roi_matched_misr_roi['ahi_sr_3d'] = roi_ahi_record
                roi_matched_misr_roi_s.append(roi_matched_misr_roi)
            break
    color_s = []
    for i in range(len(roi_matched_misr_roi_s[0]['ahi_obs_time'])):
        color_random = list(matplotlib.colors.XKCD_COLORS.items())[int(random.random()*900)][1]
        color_s.append(color_random)
    for roi_matched_record_item in roi_matched_misr_roi_s:
        band_name = roi_matched_record_item['band_name']
        ahi_obs_time = roi_matched_record_item['ahi_obs_time']
        roi_misr_record = roi_matched_record_item['misr_sr_3d']
        roi_ahi_record = roi_matched_record_item['ahi_sr_3d']
        mapping_scatter_all(roi_ahi_record, roi_misr_record, color_s, ahi_obs_time, roi_name + '_' + band_name)
    numpy.save(os.path.join(workspace, roi_name + '_matched_sr.npy'), roi_matched_misr_roi_s)
