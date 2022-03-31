# python 3.6
from MisrToolkit import MtkFile, MtkRegion


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\211204'
    hdf_filename = workspace + '/MISR_AM1_AS_LAND_P107_O085361_F07_0022.hdf'
    m = MtkFile(hdf_filename)
    
    # # Read Scale LandBRF & Offset LandBRF
    # subregParamsLnd_grid = m.grid('SubregParamsLnd')
    # min_landBRF = subregParamsLnd_grid.attr_get('Min LandBRF')
    # max_landBRF = subregParamsLnd_grid.attr_get('Max LandBRF')
    # scale_landBRF = subregParamsLnd_grid.attr_get('Scale LandBRF')
    # offset_landBRF = subregParamsLnd_grid.attr_get('Offset LandBRF')
    # print(min_landBRF, max_landBRF, scale_landBRF, offset_landBRF)

    # Read Blocks Time
    # print(m.block_metadata_list)
    # print(m.block_metadata_field_list('PerBlockMetadataTime'))
    # print(m.block_metadata_field_read('PerBlockMetadataTime', 'BlockCenterTime'))
    # print(len(m.block_metadata_field_read('PerBlockMetadataTime', 'BlockCenterTime')))
    blocks_time_list = m.block_metadata_field_read('PerBlockMetadataTime', 'BlockCenterTime')