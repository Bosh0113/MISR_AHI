# 使用python 3.6
from MisrToolkit import *

if __name__ == "__main__":
    filename_HDF = 'D:/Work_PhD/MISR/test\MISR_AM1_AS_LAND_P107_O085361_F07_0022.hdf'
    m = MtkFile(filename_HDF)
    print(m.attr_list)