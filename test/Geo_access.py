from pyhdf.SD import SD, SDC
import numpy
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filename = 'MISR_AM1_AS_LAND_P107_O085361_F07_0022.hdf'
    hdf_file = SD(filename, SDC.READ)

    print(hdf_file.info())

    #-------------------Read Data------------------#
    datasets_dic = hdf_file.datasets()
    for idx, sds in enumerate(datasets_dic.keys()):
        print(idx, sds)

    # #--------------------Save SZA-------------------#
    SZA_data_path = './Geo_62/SZA/'
    sds_obj = hdf_file.select('SolZenAng')
    data_SZA = sds_obj.get()
    block_num = 61  # 第62块
    data_SZA_b = data_SZA[block_num]
    SZA_filename = SZA_data_path + 'SZA.npy'
    numpy.save(SZA_filename, numpy.array(data_SZA_b))
    # plt.imshow(data_SZA_b, cmap=plt.cm.jet, vmin=59, vmax=61)
    # plt.show()