# python 3.6
from MisrToolkit import *
import numpy
import time
import matplotlib.pyplot as plt

if __name__ == "__main__":
    start = time.perf_counter()

    workspace = r'D:\Work_PhD\MISR_AHI_WS\211204'
    hdf_filename = workspace + '/MISR_AM1_AS_LAND_P107_O085361_F07_0022.hdf'

    # # AHI观测范围所涉及MISR的Path
    # r = MtkRegion(60, 85, -60, -155)
    # print(r.path_list)

    # 读取MISR的HDF数据
    m = MtkFile(hdf_filename)
    # print(m.grid_list)
    g = m.grid('SubregParamsLnd')
    # print(g.field_list)
    # print(g.field_dims('LandBRF'))
    f = g.field('LandBRF[3][8]')  # NBandDim NCamDim
    cu_lat_lon = [35.62975746548003, 140.0981452753069]  # Chiba-U
    print('Location: ', str(cu_lat_lon))
    resolution = 1100
    paths = latlon_to_path_list(cu_lat_lon[0], cu_lat_lon[1])
    for path in paths:
        black, line, sample = latlon_to_bls(path, 1100, cu_lat_lon[0],
                                            cu_lat_lon[1])
        print('Path: ', path, '-Block: ', black, '-Line: ', round(line),
              '-Sample: ', round(sample))
        f_data = f.read(black, black)  # Block 62
        block_data = f_data[0]
        # print(f_data.shape)
        BRF_o_value = block_data[round(line)][round(sample)]
        print('LandBRF DN value: ', BRF_o_value)
        # plt.imshow(block_data)
        # plt.show()

    end = time.perf_counter()
    print("Run time: ", end - start, 's')