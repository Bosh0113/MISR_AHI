import numpy
from MisrToolkit import MtkFile, MtkRegion
# import matplotlib.pyplot as plt
import netCDF4


misr_nc_filename = r'D:\Work_PhD\MISR_AHI_WS\220627\MISR_v2_v3\MISR_AM1_AS_LAND_P101_O092438_F08_0023.nc'

if __name__ == "__main__":
    roi_extent = [-23.264, 137.174, -23.430, 137.354]
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])

    # MISR v2
    print(28.969)

    # MISR v3
    misr_nc = netCDF4.Dataset(misr_nc_filename)
    misr_nc_44 = misr_nc.groups['4.4_KM_PRODUCTS']    
    misr_vza_var = misr_nc_44.groups['GEOMETRY'].variables['View_Zenith_Angle']
    misr_vza_scale = misr_vza_var.scale_factor
    misr_vza_offset = misr_vza_var.add_offset
    m_file = MtkFile(misr_nc_filename)
    m_grid44 = m_file.grid('4.4_KM_PRODUCTS')
    m_field44 = m_grid44.field('GEOMETRY/View_Zenith_Angle[5]')
    vza_dn = numpy.array(m_field44.read(roi_r).data())
    vza_dn = vza_dn.flatten()
    vza_dn = vza_dn[~numpy.isin(vza_dn, [65533, 65534, 65535])]
    print(vza_dn.mean())
    # print(misr_vza_scale)
    # print(misr_vza_offset)
    # vza_v3 = vza_dn*misr_vza_scale + numpy.ones_like(vza_dn)*misr_vza_offset
    # print(vza_v3.mean())

    # block_brf_dn = m_field11.read(52, 52)[0]
    # print(numpy.array(block_brf_dn).shape)
    # plt.imshow(block_brf_dn)
    # plt.colorbar()
    # plt.show()