import numpy
from MisrToolkit import MtkFile
# import matplotlib.pyplot as plt
import netCDF4
from datetime import datetime, timedelta


misr_nc_filename = r'D:\Work_PhD\MISR_AHI_WS\220609\26.1_10\MISR_AM1_AS_LAND_P117_O084051_F08_0023.nc'

if __name__ == "__main__":

    misr_nc = netCDF4.Dataset(misr_nc_filename)
    misr_nc_11 = misr_nc.groups['1.1_KM_PRODUCTS']
    misr_brf_var = misr_nc_11.variables['Bidirectional_Reflectance_Factor']
    misr_brf_scale = misr_brf_var.scale_factor
    misr_brf_offset = misr_brf_var.add_offset

    misr_nc_44 = misr_nc.groups['4.4_KM_PRODUCTS']
    misr_block_var = misr_nc_44.variables['Block_Number']
    misr_time_var = misr_nc_44.variables['Time']
    misr_units = misr_time_var.units
    start_time = misr_units[14:-8]+'Z'
    print(start_time)
    misr_start_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    block_time_num = int(len(misr_time_var[:])/len(misr_block_var[:]))
    block_no = 52
    blocks = numpy.array(misr_block_var[:])
    block_time_s = numpy.argmax(blocks == block_no-1)
    block_time_e = numpy.argmax(blocks == block_no)
    block_time_array = misr_time_var[block_time_s*block_time_num:block_time_e*block_time_num]
    block_time_offset = round(block_time_array.mean())
    block_time_offset_s = timedelta(seconds=block_time_offset)
    camera_idx = 8
    camera_time_offset_s = timedelta(seconds=int((7*60)/4*(camera_idx-4)))
    block_time = misr_start_date + block_time_offset_s + camera_time_offset_s
    print(block_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    
    misr_vza_var = misr_nc_44.groups['GEOMETRY'].variables['View_Zenith_Angle']
    misr_vza_scale = misr_vza_var.scale_factor
    misr_vza_offset = misr_vza_var.add_offset
    misr_vaa_var = misr_nc_44.groups['GEOMETRY'].variables['View_Azimuth_Angle']
    misr_vaa_scale = misr_vaa_var.scale_factor
    misr_vaa_offset = misr_vaa_var.add_offset
    misr_nc.close()

    m_file = MtkFile(misr_nc_filename)
    m_grid11 = m_file.grid('1.1_KM_PRODUCTS')
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[0][0]')
    print(numpy.array(m_field11.read(52, 52)).shape)

    m_file = MtkFile(misr_nc_filename)
    m_grid44 = m_file.grid('4.4_KM_PRODUCTS')
    m_field44 = m_grid44.field('GEOMETRY/View_Zenith_Angle[0]')
    vza_dn = numpy.array(m_field44.read(52, 52))
    vza_dn = vza_dn.flatten()
    vza_dn = vza_dn[~numpy.isin(vza_dn, [65533, 65534, 65535])]
    print(vza_dn*misr_vza_scale + numpy.ones_like(vza_dn)*misr_vza_offset)

    # block_brf_dn = m_field11.read(52, 52)[0]
    # print(numpy.array(block_brf_dn).shape)
    # plt.imshow(block_brf_dn)
    # plt.colorbar()
    # plt.show()