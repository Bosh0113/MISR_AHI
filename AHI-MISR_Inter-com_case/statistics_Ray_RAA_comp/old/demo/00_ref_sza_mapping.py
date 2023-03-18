import os
import numpy
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
import math

ws = r'E:\MISR_AHI_WS\230318\ref_raa_variation_7_random_south'

DEGREE_INTERNAL = 0.5

raa_min = 0
raa_max = 180


def identifer(data):
    down, up = numpy.nanpercentile(data, [25, 75])
    IQR = up-down
    lower_limit = down - 2*IQR
    upper_limit = up + 2*IQR
    result = numpy.where(data > upper_limit, numpy.nan, data)
    result = numpy.where(result < lower_limit, numpy.nan, result)
    return result


def consistency_para(all_data):

    x_array = all_data[0]
    y_array = all_data[1]
    slope_array = numpy.zeros_like(x_array)*1.
    r_array = numpy.zeros_like(x_array)*1.
    rmse_array = numpy.zeros_like(x_array)*1.
    for v_idx in range(len(x_array)):
        # x_list = x_array[v_idx]
        # y_list = y_array[v_idx]
        X = x_array[v_idx]
        Y = y_array[v_idx]

        # if len(x_list) > 5:
        if len(X) > 5:
            X = numpy.sort(X)
            Y = numpy.sort(Y)
            # filter
            slope_a = [Y[i]/X[i] for i in range(len(X))]
            slope_array_filtered = numpy.array(identifer([slope_a])[0])
            array1_n = (slope_array_filtered*0+1)*numpy.array(X)
            array2_n = (slope_array_filtered*0+1)*numpy.array(Y)
            x_list = array1_n[~numpy.isnan(array1_n)]
            y_list = array2_n[~numpy.isnan(array2_n)]

            k, b = numpy.polyfit(x_list, y_list, deg=1)
            r_, p = pearsonr(x_list, y_list)
            rmse = math.sqrt(mean_squared_error(x_list, y_list))
            slope_array[v_idx] = k
            r_array[v_idx] = r_
            rmse_array[v_idx] = rmse
    return slope_array, r_array, rmse_array


def raa_ray_plot(raa_data, ray_data):
    slope_raa, r_raa, rmse_raa = consistency_para(raa_data)
    slope_ray, r_ray, rmse_ray = consistency_para(ray_data)
    # display_array = [slope_raa, r_raa, rmse_raa, slope_ray, r_ray, rmse_ray]
    # label_list = ['slope_raa', 'slope_ray']
    # display_array = [slope_raa, slope_ray]
    # label_list = ['r_raa', 'r_ray']
    # display_array = [r_raa, r_ray]
    label_list = ['rmse_raa', 'rmse_ray']
    display_array = [rmse_raa, rmse_ray]
    for idx in range(len(display_array)):
        display_list = display_array[idx]
        plt.plot(display_list, label=label_list[idx])
    # plt.xlim(15, 40)
    plt.xlim(30, 120)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    band_str = 'band3'
    # band_str = 'band4'
    raa_npy = os.path.join(ws, '26_0_' + band_str + '_ref_raa_variation_RAA.npy')
    ray_npy = os.path.join(ws, '26_0_' + band_str + '_ref_raa_variation_Ray.npy')
    raa_npy_array = numpy.load(raa_npy, allow_pickle=True)
    ray_npy_array = numpy.load(ray_npy, allow_pickle=True)
    raa_ray_plot(raa_npy_array, ray_npy_array)