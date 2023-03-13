import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, pearsonr
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import math
import os

# SAVE_FIGURE_FLAG = True
SAVE_FIGURE_FLAG = False

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\0_0_RAA'
roi_name = '0.0_0'
selected_times = ['201811090100']   # 100	100491	4	201811090101	201811090100	4.350	4.856	282.738	339.564	126.915	128.221	155.823	148.657	22.290	21.463	179.235
matched_camera_idx = ['4']
WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\0_0_Ray'
roi_name = '0.0_0'
selected_times = ['201905200100']   # 100	103287	4	201905200100	201905200100	3.300	4.856	283.062	339.564	41.224	39.745	118.161	60.181	31.892	31.245	175.821
matched_camera_idx = ['4']

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\0_1_RAA'
roi_name = '0.0_1'
selected_times = ['201805150110']   # 102	97899	4	201805150113	201805150110	0.406	3.559	184.831	38.540	44.388	43.951	71.334	5.412	30.100	29.892	176.586
matched_camera_idx = ['4']
WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\0_1_Ray'
roi_name = '0.0_1'
selected_times = ['201811070110']   # 102	100462	4	201811070113	201811070110	0.647	3.559	111.216	38.540	128.060	128.694	50.446	90.155	23.056	22.675	176.911
matched_camera_idx = ['4']

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\26_0_RAA'
roi_name = '26.1_0'
selected_times = ['201912240140']   # 106	106462	5	201912240143	201912240140	26.533	25.742	179.186	34.263	106.085	106.473	73.101	72.210	24.662	23.438	179.117
matched_camera_idx = ['5']
WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\26_0_Ray'
roi_name = '26.1_0'
selected_times = ['201802040140']   # 106	96443	3	201802040140	201802040140	27.720	25.742	32.084	34.263	90.143	89.761	58.059	55.498	28.167	26.999	177.711
matched_camera_idx = ['3']

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\26_1_RAA'
roi_name = '26.1_1'
selected_times = ['201701210020']   # 93	95350	5	201711210024	201711210020	26.413	26.916	203.475	337.931	89.515	89.008	113.960	111.077	20.314	19.218	178.612
matched_camera_idx = ['5']
WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\26_1_Ray'
roi_name = '26.1_1'
selected_times = ['201911180030']   # 94	105937	3	201911180026	201911180030	29.681	26.916	342.200	337.931	86.536	85.050	104.336	107.118	18.963	16.837	176.937
matched_camera_idx = ['3']

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\45_0_RAA'
roi_name = '45.6_0'
selected_times = ['201705200210']   # 110	92657	2	201705200207	201705200210	46.353	45.517	22.719	36.207	30.422	28.601	7.703	7.606	59.621	58.884	179.161
matched_camera_idx = ['2']
WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\45_0_Ray'
roi_name = '45.6_0'
selected_times = ['201811080200']   # 109	100477	2	201811080201	201811080200	47.988	45.517	33.863	36.207	60.339	59.330	26.477	23.123	28.795	28.282	176.527
matched_camera_idx = ['2']

WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\45_1_RAA'
roi_name = '45.6_1'
selected_times = ['201904240210']   # 110	102909	2	201904240207	201904240210	47.094	47.416	28.888	36.853	35.460	33.698	6.572	3.155	55.033	54.261	177.47
matched_camera_idx = ['2']
WORK_SPACE = r'E:\MISR_AHI_WS\230211\intercom_mapping\45_1_Ray'
roi_name = '45.6_1'
selected_times = ['201902190200']   # 110	101977	2	201902190207	201902190200	47.162	47.416	29.344	36.853	60.216	61.043	30.872	24.190	38.110	38.663	175.084
matched_camera_idx = ['2']

# ###########################################################################

# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\60_0_RAA'
# roi_name = '60.0_0_1'
# selected_times = ['201910190320']   # 124	105502	7	201910190319	201910190320	60.373	60.196	189.155	148.716	166.926	168.704	22.229	19.988	58.914	58.700	178.045
# matched_camera_idx = ['7']
# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\60_0_Ray'
# roi_name = '60.0_0_0'
# selected_times = ['201905120130']   # 108	103171	7	201905120139	201905120130	60.456	60.202	188.750	182.312	158.925	157.193	29.825	25.119	36.042	36.283	175.904
# matched_camera_idx = ['7']

# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\60_1_RAA'
# roi_name = '60.0_1_1'
# selected_times = ['201801210440']   # 136	96241	7	201801210439	201801210440	60.416	60.315	200.353	114.420	155.993	158.097	44.360	43.676	52.209	51.489	179.397
# matched_camera_idx = ['7']
# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\60_1_Ray'
# roi_name = '60.0_1_0'
# selected_times = ['201905130050']   # 99	103185	7	201905130043	201905130050	60.200	64.655	195.038	201.720	163.189	167.717	31.849	34.003	37.505	37.033	175.153
# matched_camera_idx = ['7']

# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\70_0_RAA'
# roi_name = '70.5_0_1'
# selected_times = ['201709040450']   # 139	94217	8	201709040453	201709040450	70.873	71.271	204.122	130.354	165.805	167.140	38.317	36.786	45.501	45.343	178.498
# matched_camera_idx = ['8']
# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\70_0_Ray'
# roi_name = '70.5_0_0'
# selected_times = ['201907070050']   # 100	103986	8	201907070049	201907070050	70.738	70.347	204.761	204.647	167.614	170.459	37.147	34.188	37.712	37.452	177.183
# matched_camera_idx = ['8']

# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\70_1_RAA'
# roi_name = '70.5_1_1'
# selected_times = ['201804200430']   # 135	97537	8	201804200429	201804200430	70.600	70.311	194.006	134.505	161.578	164.673	32.429	30.169	42.687	42.293	177.851
# matched_camera_idx = ['8']
# WORK_SPACE = r'D:\MISR_AHI_WS\230211\intercom_mapping\70_1_Ray'
# roi_name = '70.5_1_0'
# selected_times = ['201906140040']   # 99	103651	8	201906140044	201906140040	70.600	67.267	200.656	203.832	164.294	165.370	36.362	38.461	34.420	34.325	176.135
# matched_camera_idx = ['8']


def identifer(data):
    down,up = np.nanpercentile(data,[25,75])
    IQR = up-down
    lower_limit = down - 2*IQR
    upper_limit = up + 2*IQR
    result = np.where(data > upper_limit,np.nan, data)
    result = np.where(result < lower_limit,np.nan, result)
    return result


def add_right_cax(ax, pad, width):

    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(axpos.x1 + pad, axpos.y0, axpos.x1 + pad + width, axpos.y1)
    cax = ax.figure.add_axes(caxpos)

    return cax


def make_fig_bk(roi_name, X, Y, band_name, axis_min=0.0, axis_max=0.5):

    if band_name == 'band3':
        axis_max = 0.3

    fig = plt.figure(figsize=(4, 4))
    ax1 = fig.add_subplot(111, aspect='equal')
    ax1.grid(linestyle='--', linewidth=0.3)

    k, b = np.polyfit(X, Y, deg=1)
    rmse = math.sqrt(mean_squared_error(X, Y))
    N = len(X)

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    g_x, g_y = np.mgrid[axis_min:axis_max:500j, axis_min:axis_max:500j]
    positions = np.vstack([g_x.ravel(), g_y.ravel()])
    values = np.vstack([X, Y])
    kernel = gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, g_x.shape)

    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=8)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=8)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=8)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    band_label = {
        'band3': 'Band3',
        'band4': 'Band4',
    }

    ax1.set_ylabel("AHI Surface Reflectance " + band_label[band_name], fontsize=12)
    ax1.set_xlabel("MISR Surface Reflectance " + band_label[band_name], fontsize=12)

    ax1.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r, extent=[axis_min, axis_max, axis_min, axis_max], alpha=0.8, zorder=0)
    ax1.plot(x, y, color='k', linewidth=1.2, linestyle='-.', zorder=1)
    ax1.plot(xx, yy, color='r', linewidth=1, linestyle='-', zorder=2)
    ax1.plot(X, Y, 'k.', markersize=2, zorder=4)

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.3

    r_, p = pearsonr(X, Y)
    p_str = '%.3e' % p
    
    label_str = label_str = 'ROI name: {}\ny = {}x + {}\nRMSE = {}\nr = {}\n'.format(roi_name, round(k, 2), round(b, 2), round(rmse, 3), round(r_, 2))
    if b < 0:
        label_str = label_str = 'ROI name: {}\ny = {}x - {}\nRMSE = {}\nr = {}\n'.format(roi_name, round(k, 2), abs(round(b, 2)), round(rmse, 3), round(r_, 2))

    ax1.text(text_x, text_y, s=label_str, fontsize=12)

    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    if SAVE_FIGURE_FLAG:
        fig.savefig(os.path.join(WORK_SPACE, '{} '.format(roi_name) + band_label[band_name] + ' SR.jpg'), dpi=1000, bbox_inches='tight')
    else:
        plt.show()
    plt.close(fig)
    plt.clf()


if __name__ == "__main__":
    # read individe record
    band_names = ['band3', 'band4']
    for band_name in band_names:
        roi_misr_record = []
        roi_ahi_record = []
        for idx in range(len(selected_times)):
            selected_time = selected_times[idx]
            camera_idx = matched_camera_idx[idx]
            npy_filename = os.path.join(WORK_SPACE, selected_time + '_' + band_name + '_' + camera_idx + '.npy')
            roi_record = np.load(npy_filename, allow_pickle=True)[0]
            roi_misr_item = roi_record['misr_v3']
            roi_misr_record.append(roi_misr_item)
            roi_ahi_item = roi_record['ahi_sr2misr']
            roi_ahi_record.append(roi_ahi_item)
        
        misr4show = []
        ahi4show = []
        x_3Darray_np = np.array(roi_misr_record)
        x_3Darray_np_1d = x_3Darray_np.flatten()
        x_3Darray_np_1d = x_3Darray_np_1d[~np.isnan(x_3Darray_np_1d)]
        y_3Darray_np = np.array(roi_ahi_record)
        y_3Darray_np_1d = y_3Darray_np.flatten()
        y_3Darray_np_1d = y_3Darray_np_1d[~np.isnan(y_3Darray_np_1d)]
        misr4show.extend(x_3Darray_np_1d)
        ahi4show.extend(y_3Darray_np_1d)
        # filter
        slope_array = list(np.array(ahi4show)/np.array(misr4show))
        slope_array_filtered = np.array(identifer([slope_array])[0])
        array1_n = (slope_array_filtered*0+1)*np.array(misr4show)
        array2_n = (slope_array_filtered*0+1)*np.array(ahi4show)
        array_x = array1_n[~np.isnan(array1_n)]
        array_y = array2_n[~np.isnan(array2_n)]

        make_fig_bk(roi_name, array_x, array_y, band_name)