import numpy as np
import xarray

if __name__ == "__main__":
    nc_file = r'D:\Work_PhD\MISR_AHI_WS\220309\ozone_201601010000.nc'
    ds = xarray.open_dataset(nc_file)
    print(ds)