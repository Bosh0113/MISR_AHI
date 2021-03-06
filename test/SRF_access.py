# python 3.7
from pyhdf.SD import SD, SDC
import numpy
import os

if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\211228'
    filename = workspace + '/MISR_AM1_AS_LAND_P107_O087225_F07_0022.hdf'
    hdf_file = SD(filename, SDC.READ)

    print(hdf_file.info())  # dataset num, attribute num

    # #-------------------Read Data------------------#
    # print("Attributes: ")
    # for idx, att in enumerate(hdf_file.attributes()):
    #     print(idx, att)

    # print("Datasets: ")
    # datasets_dic = hdf_file.datasets()
    # for idx, sds in enumerate(datasets_dic.keys()):
    #     print(idx, sds)

    #--------------------Save BRF-------------------#
    BRF_data_path = workspace + '/SRF_62/'
    if not os.path.exists(BRF_data_path):
        os.makedirs(BRF_data_path)
    sds_obj = hdf_file.select('LandBRF')
    data_BRF = sds_obj.get()
    block_num = 61  # 第62块
    data_BRF_b = data_BRF[block_num]
    data_BRF_b_t = data_BRF_b.T
    bands = numpy.arange(0, 4, 1)
    cameras = numpy.arange(0, 9, 1)
    for band_num in bands:
        band_str = str(band_num)
        for camera_num in cameras:
            camera_str = str(camera_num)
            data_BRF_bbc = data_BRF_b_t[camera_num, band_num, :, :]
            BRF_filename = BRF_data_path + 'b_' + band_str + '_c_' + camera_str + '.npy'
            numpy.save(BRF_filename, numpy.array(data_BRF_bbc.T))

    hdf_file.end()