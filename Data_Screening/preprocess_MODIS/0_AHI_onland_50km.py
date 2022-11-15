import os
import numpy
import global_land_mask as globe
import time

ws = os.getcwd()
npy_filename = os.path.join(ws, 'AHI_180_50km_onland.npy')
lonlat_npy_filename = os.path.join(ws, 'AHI_180_50km_onland_lonlat.npy')

INTERNAL_DEGREE = 0.5   # 10km

if __name__ == "__main__":
    start = time.perf_counter()
    ahi_lats = numpy.arange(60. - INTERNAL_DEGREE / 2, -60, -INTERNAL_DEGREE)
    ahi_lons = numpy.arange(85. + INTERNAL_DEGREE / 2, 180, INTERNAL_DEGREE)    # 只东半球，180-205暂不算
    ahi_onland = numpy.zeros((len(ahi_lats), len(ahi_lons)))
    ahi_onland_lonlat = []
    count = 0
    total_count = len(ahi_lats)*len(ahi_lons)
    for lat_idx in range(len(ahi_lats)):
        for lon_idx in range(len(ahi_lons)):
            count+=1
            print(str(count) + '/' + str(total_count))
            lat = ahi_lats[lat_idx]
            lon = ahi_lons[lon_idx]
            is_island = globe.is_land(lat, lon)
            if is_island:
                ahi_onland[lat_idx][lon_idx] = 1
                ahi_onland_lonlat.append([lon, lat])
    
    numpy.save(npy_filename, ahi_onland)
    numpy.save(lonlat_npy_filename, ahi_onland_lonlat)
    end = time.perf_counter()
    print("Run time: ", end - start, 's')
