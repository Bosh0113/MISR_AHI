import re
from MisrToolkit import orbit_to_time_range


if __name__ == "__main__":
    hdf = 'MISR_AM1_AS_LAND_P107_O087225_F07_0022.hdf'
    matchObj = re.search(r'O(\d+)_F', hdf)
    orbit_str = matchObj.group(1)
    misr_time = orbit_to_time_range(int(orbit_str))
    print(misr_time)