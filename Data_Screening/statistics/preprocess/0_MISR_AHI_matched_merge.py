import os
import numpy

misr_matched_info_folder = r'D:\Work_PhD\MISR_AHI_WS\230118\RAA_50km\parts'
merged_npy_filename = r'D:\Work_PhD\MISR_AHI_WS\230118\RAA_50km\AHI_MISR_RAA-matched_50km.npy'


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