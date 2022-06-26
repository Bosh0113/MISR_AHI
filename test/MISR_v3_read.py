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
    block_time_array = misr_time_var[(block_no-1)*block_time_num:block_no*block_time_num]
    block_time_offset = round(block_time_array.mean())
    block_time_offset_s = timedelta(seconds=block_time_offset)
    block_time = misr_start_date + block_time_offset_s
    print(block_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    misr_nc.close()

    m_file = MtkFile(misr_nc_filename)
    m_grid11 = m_file.grid('1.1_KM_PRODUCTS')
    m_field11 = m_grid11.field('Bidirectional_Reflectance_Factor[0][0]')
    print(numpy.array(m_field11.read(52, 52)).shape)

    m_file = MtkFile(misr_nc_filename)
    m_grid44 = m_file.grid('4.4_KM_PRODUCTS')
    m_field44 = m_grid44.field('GEOMETRY/View_Zenith_Angle[0]')
    print(numpy.array(m_field44.read(52, 52)).shape)

    # block_brf_dn = m_field11.read(52, 52)[0]
    # print(numpy.array(block_brf_dn).shape)
    # plt.imshow(block_brf_dn)
    # plt.colorbar()
    # plt.show()