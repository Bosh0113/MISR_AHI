import os
import re
import ssl
import urllib.request
import time
from MisrToolkit import MtkRegion, orbit_to_time_range, path_time_range_to_orbit_list, MtkFile

START_TIME = '2015-07-01T00:00:00Z'
END_TIME = '2021-07-01T23:59:59Z'

MISR_TOA_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_TOA'

ssl._create_default_https_context = ssl._create_unverified_context


def download_MISR_MIL2TCST02_HDF(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    time0 = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(time0))
    yy = matchObj.group(1)
    mm = matchObj.group(2)
    dd = matchObj.group(3)
    t = str(yy) + '.' + str(mm) + '.' + str(dd)
    P = 'P' + (3-len(str(path)))*'0' + str(path)
    O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
    F = 'F' + '05'
    v = '0011'
    base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2TCAL.002'
    filename = 'MISR_AM1_TC_ALBEDO_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'

    download_url = base_url + '/' + t + '/' + filename
    storage_path = folder + '/' + filename

    if os.path.exists(storage_path):
        return storage_path
    else:
        try:
            urllib.request.urlretrieve(download_url, filename=storage_path)
            print('Download: ' + download_url)
            return storage_path
        except Exception as e:
            print('Error: ' + download_url)
            print(e)
            return ''


def check_MISR_MIL2TCST02_HDF(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    time0 = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(time0))
    yy = matchObj.group(1)
    mm = matchObj.group(2)
    dd = matchObj.group(3)
    t = str(yy) + '.' + str(mm) + '.' + str(dd)
    P = 'P' + (3 - len(str(path))) * '0' + str(path)
    O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
    F = 'F' + '05'
    v = '0011'
    base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2TCAL.002'
    filename = 'MISR_AM1_TC_ALBEDO_' + P + '_' + O_ + '_' + F + '_' + v + '.hdf'

    download_url = base_url + '/' + t + '/' + filename

    time1 = time_range[1]
    matchObj1 = re.search(r'(\d+)-(\d+)-(\d+)T', str(time1))
    yy1 = matchObj1.group(1)
    mm1 = matchObj1.group(2)
    dd1 = matchObj1.group(3)
    t1 = str(yy1) + '.' + str(mm1) + '.' + str(dd1)
    download_url1 = base_url + '/' + t1 + '/' + filename

    storage_path = folder + '/' + filename

    if os.path.exists(storage_path):
        try:
            m_file = MtkFile(storage_path)
            return storage_path
        except Exception as e:
            print(e)
            try:
                urllib.request.urlretrieve(download_url, filename=storage_path)
                return storage_path
            except Exception as e:
                print('Error: ' + download_url)
                print(e)
                try:
                    urllib.request.urlretrieve(download_url1, filename=storage_path)
                    return storage_path
                except Exception as e:
                    print('Error: ' + download_url1)
                    print(e)
                    return ''
    else:
        print('No file:', storage_path)
        try:
            urllib.request.urlretrieve(download_url, filename=storage_path)
            return storage_path
        except Exception as e:
            print('Error: ' + download_url)
            print(e)
            try:
                urllib.request.urlretrieve(download_url1, filename=storage_path)
                return storage_path
            except Exception as e:
                print('Error: ' + download_url1)
                print(e)
                return ''


if __name__ == "__main__":
    start = time.perf_counter()
    ahi_r = MtkRegion(60, 85, -60, -155)
    pathList = ahi_r.path_list
    for path_idx in range(len(pathList)):
        path = pathList[path_idx]
        orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
        for orbit_idx in range(len(orbits)):
            orbit = orbits[orbit_idx]
            print('Orbit in Path: ' + str(orbit_idx + 1) + '/' + str(len(orbits)) + ' | Path: ' + str(path_idx + 1) + '/' + str(len(pathList)))
            download_MISR_MIL2TCST02_HDF(MISR_TOA_FOLDER, path, orbit)
    for path_idx in range(len(pathList)):
        path = pathList[path_idx]
        orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
        for orbit_idx in range(len(orbits)):
            orbit = orbits[orbit_idx]
            print('Orbit in Path: ' + str(orbit_idx + 1) + '/' + str(len(orbits)) + ' | Path: ' + str(path_idx + 1) + '/' + str(len(pathList)))
            check_MISR_MIL2TCST02_HDF(MISR_TOA_FOLDER, path, orbit)

    end = time.perf_counter()
    print("Run time: ", end - start, 's')
