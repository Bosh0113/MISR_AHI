import os
import numpy

WORK_SPACE = os.getcwd()
CLOUD_MASK_FOLDER = r'E:\MISR_AHI_WS\230317'

AHI_RESOLUTION = 0.02

CHECK_SIZE = 0.1
CLEAR_SKY_PIXEL = (CHECK_SIZE/AHI_RESOLUTION)**2


def find_nearest_index(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx


def get_roi_cloudmask_list(cloudmask_fd, roi_ct):
    center_lat = roi_ct[0]
    center_lon = roi_ct[1]
    roi_ullat = center_lat + CHECK_SIZE/2
    roi_ullon = center_lon - CHECK_SIZE/2
    roi_lrlat = center_lat - CHECK_SIZE/2
    roi_lrlon = center_lon + CHECK_SIZE/2
    ahi_lats = numpy.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
    ahi_lons = numpy.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)
    roi_cloudmask = cloudmask_fd[find_nearest_index(ahi_lats, roi_ullat):find_nearest_index(ahi_lats, roi_lrlat) + 1, find_nearest_index(ahi_lons, roi_ullon):find_nearest_index(ahi_lons, roi_lrlon) + 1]
    return roi_cloudmask


def read_cloudmask(date_str):
    cm_path = CLOUD_MASK_FOLDER + '/cloudmask/{}/AHIcm.v0.{}.dat'.format(date_str[:6], date_str)
    try:
        cloudmask = numpy.fromfile(cm_path, dtype=numpy.float32)
        cloudmask[cloudmask < 0.95] = 0.   # cloud
        cloudmask[cloudmask >= 0.95] = 1.
        cloudmask = cloudmask.reshape(6000, 6000)   # 0.02°
    except:
        cloudmask = numpy.zeros((6000, 6000))
    return cloudmask


def roi_is_clearsky(date_str, roi_lat_lon):
    ahi_cloudmask = read_cloudmask(date_str)
    roi_cloudmask = get_roi_cloudmask_list(ahi_cloudmask, roi_lat_lon)
    cm_v = roi_cloudmask.flatten()
    if len(cm_v[cm_v > 0]) > CLEAR_SKY_PIXEL:
        return 1
    else:
        return 0


if __name__ == "__main__":
    ahi_date = '201801010000'
    roi_ct = [38.95, 141.05]
    is_clearsky = roi_is_clearsky(ahi_date, roi_ct)
    print(is_clearsky)