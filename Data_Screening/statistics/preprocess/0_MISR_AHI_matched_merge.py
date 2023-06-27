import os
import numpy

misr_matched_info_folder = '/disk1/workspace/20230624/ray/parts'
merged_npy_filename = '/disk1/workspace/20230624/ray/AHI_MISR_Ray-matched_z2a10.npy'


def main():
    merged_list = []
    npy_list = os.listdir(misr_matched_info_folder)
    for npy_file in npy_list:
        npy_filename = os.path.join(misr_matched_info_folder, npy_file)
        npy_list = numpy.load(npy_filename, allow_pickle=True)
        merged_list.extend(npy_list)
    print(len(merged_list))
    numpy.save(merged_npy_filename, merged_list)


if __name__ == "__main__":
    main()