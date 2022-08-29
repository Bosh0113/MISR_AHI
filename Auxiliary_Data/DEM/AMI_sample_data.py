import xarray
import numpy
from osgeo import osr
from osgeo import gdal

AMI_RESOLUTION = 0.01       # degree

if __name__ == "__main__":
    ami_sample_nc = r'D:\Work_PhD\MISR_AHI_WS\220803\GK2A\gk2a_ami_le1b_ir087_fd020ge_202007150300.nc'
    tif_filename = r'D:\Work_PhD\MISR_AHI_WS\220803\gk2a_ami_le1b_ir087_fd020ge_202007150300.tif'

    ami_ds = xarray.open_dataset(ami_sample_nc)
    image_v = ami_ds['image_pixel_values']
    image_v = numpy.array(image_v)

    file_format = "GTiff"
    full_geotransform = [73.2, AMI_RESOLUTION, 0, 55, 0, -AMI_RESOLUTION]
    driver = gdal.GetDriverByName(file_format)
    pre_ds = driver.Create(tif_filename, 110*int(1./AMI_RESOLUTION), 110*int(1./AMI_RESOLUTION), 1, gdal.GDT_Int16)
    pre_ds.SetGeoTransform(full_geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    pre_ds.SetProjection(srs.ExportToWkt())
    pre_ds.GetRasterBand(1).SetNoDataValue(32768)
    pre_ds.GetRasterBand(1).WriteArray(image_v)
    del pre_ds