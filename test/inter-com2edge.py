import numpy
from osgeo import gdal


if __name__ == "__main__":
    # npy to asc
    ws = r'D:\Work_PhD\MISR_AHI_WS\220127'
    # intercom_npy = ws + '/region4intercom.npy'
    # intercom = numpy.load(intercom_npy)
    # intercom_asc = ws + '/region4intercom.asc'
    # numpy.savetxt(intercom_asc, intercom, fmt='%1d')
    
    # MISR_vza = [0, 26.1, 45.6, 60.0, 70.5]
    # for vza in MISR_vza:
    #     vza_onland_filename = ws + '/AHI_vza_MISR_' + str(vza) + '.npy'
    #     npy = numpy.load(vza_onland_filename)
    #     asc_filename = ws + '/AHI_vza_MISR_' + str(vza) + '.asc'
    #     npy[npy > 0] = 1
    #     numpy.savetxt(asc_filename, npy, fmt='%1d')

    # MISR_vza = [0, 26.1, 45.6, 60.0, 70.5]
    # for vza in MISR_vza:
    #     vza_onland_filename = ws + '/AHI_MISR_inter-com_region_degree_' + str(vza) + '.npy'
    #     npy = numpy.load(vza_onland_filename)
    #     asc_filename = ws + '/AHI_MISR_inter-com_region_degree_' + str(vza) + '.asc'
    #     npy[npy > 0] = 1
    #     numpy.savetxt(asc_filename, npy, fmt='%1d')

    # asc to tif (ArcMap)
    # tif to shp (ArcMap)
    # shp to kmz (ArcMap)
    # kmz to kml (Google Earth)
    