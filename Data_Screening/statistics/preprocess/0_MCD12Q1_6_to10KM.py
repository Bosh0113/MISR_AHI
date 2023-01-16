import os
import numpy
from scipy import stats
import matplotlib.pyplot as plt

ws = os.getcwd()

MCD12Q1_006_1KM = os.path.join(ws, 'MCD12Q1.006.LC.CEReS_H8AHI.01km.MEAN.NA.ann.bsq.byt')
MCD12Q1_006_10KM_npy = os.path.join(ws, 'MCD12Q1_006_10km.npy')

ROI_DISTANCE = 0.1

if __name__ == "__main__":
    roi_lats = numpy.arange(60. - ROI_DISTANCE / 2, -60, -ROI_DISTANCE)
    roi_lons = numpy.arange(85. + ROI_DISTANCE / 2, 205, ROI_DISTANCE)

    modis_lc_10km = numpy.zeros((len(roi_lats), len(roi_lons)))
    size = int(1/ROI_DISTANCE)

    with open(MCD12Q1_006_1KM, 'rb') as fp:
        landcover = numpy.frombuffer(fp.read(), dtype='uint8').reshape(12000, 12000)
        lat_roi_idx = 0
        for lat_idx in range(len(roi_lats)):
            print(lat_idx, '/', len(roi_lats))
            lon_roi_idx = 0
            for lon_idx in range(len(roi_lons)):
                lc_2d = landcover[lat_roi_idx*size:(lat_roi_idx+1)*size, lon_roi_idx*size:(lon_roi_idx+1)*size]
                # print(lat_roi_idx*size, (lat_roi_idx+1)*size, lon_roi_idx*size, (lon_roi_idx+1)*size)
                # print(lc_2d)
                lc_1d = lc_2d.flatten()
                lc_mode = stats.mode(lc_1d)[0]
                modis_lc_10km[lat_idx][lon_idx] = lc_mode
                lon_roi_idx += 1
            lat_roi_idx += 1
    numpy.save(MCD12Q1_006_10KM_npy, modis_lc_10km)
    plt.imshow(modis_lc_10km)
    plt.show()
