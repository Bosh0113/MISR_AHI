# python 3.6
from MisrToolkit import MtkRegion, orbit_to_time_range, path_time_range_to_orbit_list
import re
import time
import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def download_MISR_MIL2ASLS02_HDF(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    for orbit_time in time_range:
        matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(orbit_time))
        yy = matchObj.group(1)
        mm = matchObj.group(2)
        dd = matchObj.group(3)
        
        t = str(yy) + '.' + str(mm) + '.' + str(dd)
        P = 'P' + (3-len(str(path)))*'0' + str(path)
        O = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
        F = 'F' + '07'
        v = '0022'
        base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2ASLS.002'
        filename = 'MISR_AM1_AS_LAND_' + P + '_' + O + '_' + F + '_' + v + '.hdf'

        download_url = base_url + '/' + t + '/' + filename
        storage_path = folder + '/' + filename

        if os.path.exists(storage_path):
            pass
        else:
            try:
                urllib.request.urlretrieve(download_url, filename=storage_path)
            except Exception as e:
                print('Error: ' + download_url)
                print(e)


if __name__ == "__main__":
    start = time.perf_counter()
    # storage_folder = r'E:\Data_PhD\MISR4AHI'
    storage_folder = '/home/beichen/disk1/data/MISR4AHI2015070120170601'
    ahi_r = MtkRegion(60, 85, -60, -155)
    start_t = '2015-07-01T00:00:00Z'
    end_t = '2017-06-01T23:59:59Z'
    pathList = ahi_r.path_list
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
        for orbit in orbits:
            download_MISR_MIL2ASLS02_HDF(storage_folder, path, orbit)

    end = time.perf_counter()
    print("Run time: ", end - start, 's')