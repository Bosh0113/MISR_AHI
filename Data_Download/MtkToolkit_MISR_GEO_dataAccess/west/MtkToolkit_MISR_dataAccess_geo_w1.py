# python 3.6
from MisrToolkit import MtkFile, MtkRegion, orbit_to_time_range, path_time_range_to_orbit_list
import re
import time
import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    for orbit_time in time_range:
        matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(orbit_time))
        yy = matchObj.group(1)
        mm = matchObj.group(2)
        dd = matchObj.group(3)

        t = str(yy) + '.' + str(mm) + '.' + str(dd)
        P = 'P' + (3-len(str(path)))*'0' + str(path)
        O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
        F = 'F' + '03'
        v = '0013'
        base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIB2GEOP.002'
        filename = 'MISR_AM1_GP_GMP_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'

        download_url = base_url + '/' + t + '/' + filename
        storage_path = folder + '/' + filename

        if os.path.exists(storage_path):
            try:
                m_file = MtkFile(storage_path)
            except Exception as e:
                print('Error: ' + download_url)
                print(e)
                urllib.request.urlretrieve(download_url, filename=storage_path)
        else:
            try:
                urllib.request.urlretrieve(download_url, filename=storage_path)
            except Exception as e:
                print('Error: ' + download_url)
                print(e)


if __name__ == "__main__":
    start = time.perf_counter()
    storage_folder = '/data01/people/beichen/data/MISR4AHI_GEO_2018/West'
    globe_r = MtkRegion(60, -180, -60, -155)
    start_t = '2018-01-01T00:00:00Z'
    end_t = '2018-02-28T23:59:59Z'
    pathList = globe_r.path_list
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
        for orbit in orbits:
            download_MISR_MIL2ASLS03_NC(storage_folder, path, orbit)

    end = time.perf_counter()
    print("Run time: ", end - start, 's')