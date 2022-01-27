import numpy


def compress_onland_npy():
    MISRVZAs = [0, 26.1, 45.6, 60.0, 70.5]
    storage_path = r'D:\Work_PhD\MISR_AHI_WS\220127'
    for vza in MISRVZAs:
        vza_onland_filename = storage_path + '/AHI_MISR_inter-com_region_degree_' + str(vza) + '.npy'
        vza_onland = numpy.load(vza_onland_filename)
        vza_onland_index = []
        for y in range(len(vza_onland)):
            for x in range(len(vza_onland[0])):
                if vza_onland[x][y]:
                    index = [x, y]
                    vza_onland_index.append(index)
        onland_compress_filename = storage_path + '/AHI_MISR_icr_compress_4KM_' + str(vza) + '.npy'
        vza_onland_index = numpy.array(vza_onland_index)
        numpy.save(onland_compress_filename, vza_onland_index)


if __name__ == "__main__":
    compress_onland_npy()