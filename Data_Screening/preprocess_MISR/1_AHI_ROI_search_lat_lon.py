import os
import numpy
import xarray
import time
# import matplotlib.pyplot as plt

ANGLE_RESOLUTION = 0.04
ROI_DISTANCE = 0.1

if __name__ == "__main__":
    start = time.perf_counter()
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220926'
    MISRVZAs = [0.0, 26.1, 45.6, 60.0, 70.5]

    ahi_lats = numpy.arange(60. - ANGLE_RESOLUTION / 2, -60, -ANGLE_RESOLUTION)
    ahi_lons = numpy.arange(85. + ANGLE_RESOLUTION / 2, 205, ANGLE_RESOLUTION)

    roi_lats = numpy.arange(60. - ROI_DISTANCE / 2, -60, -ROI_DISTANCE)
    roi_lons = numpy.arange(85. + ROI_DISTANCE / 2, 205, ROI_DISTANCE)

    for vza_idx in range(len(MISRVZAs)):
        npy_filename = os.path.join(workspace, str(MISRVZAs[vza_idx]) + '_onland_mid_lat.npy')
        search_region = numpy.load(npy_filename)

        # # mapping check
        # search_region = search_region * 1.
        # search_region[search_region == 0] = numpy.nan
        # plt.imshow(search_region, interpolation='none')
        # plt.show()
        # plt.clf()

        ex_ds = xarray.Dataset(
            data_vars={
                "values": (("latitude", "longitude"), search_region),
            },
            coords={
                "latitude": ahi_lats,
                "longitude": ahi_lons
            },
        )
        n_ex_ds = ex_ds.interp(longitude=roi_lons, latitude=roi_lats, method="nearest")

        n_ex_v_2d = numpy.array(n_ex_ds["values"])
        n_ex_v_1d = n_ex_v_2d.flatten()
        n_ex_lat = numpy.array(n_ex_ds["latitude"])
        n_ex_lon = numpy.array(n_ex_ds["longitude"])
        n_ex_lat_2d = numpy.tile(n_ex_lat, (1, len(n_ex_lon))).reshape(len(n_ex_lat), len(n_ex_lon)).T
        n_ex_lat_1d = n_ex_lat_2d.flatten()
        n_ex_lon_2d = numpy.tile(n_ex_lon, (len(n_ex_lat), 1))
        n_ex_lon_1d = n_ex_lon_2d.flatten()

        search_idx = numpy.where(n_ex_v_1d == 1)[0]

        lat4search = []
        lon4search = []
        for i in range(len(n_ex_lat_1d)):
            if i in search_idx:
                lat4search.append(n_ex_lat_1d[i])
                lon4search.append(n_ex_lon_1d[i])

        # points for search
        search_cood = []
        for idx in range(len(lat4search)):
            lat = lat4search[idx]
            lon = lon4search[idx]
            point_cood = [lon, lat]     # lon, lat
            search_cood.append(point_cood)
        # print(len(search_cood))
        point_locations_npy_filename = os.path.join(workspace, str(MISRVZAs[vza_idx]) + '_point4search_' + str(ROI_DISTANCE) + '.npy')
        numpy.save(point_locations_npy_filename, numpy.array(search_cood))

    end = time.perf_counter()
    print("Run time: ", end - start, 's')