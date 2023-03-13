import os
import numpy

ws = r'E:\MISR_AHI_WS\230308\Ray_screen_ScatterAng'
merged_npy_filename = os.path.join(ws, 'AHI_MISR_Ray-screened_50km.npy')


def main():
    txt_str = ''
    npy_list = numpy.load(merged_npy_filename, allow_pickle=True)
    for record in npy_list:
        pt = record['location']
        matched_info = record['matched_infos'][0]
        txt_str += str(round(pt[0], 2)) + ',' + str(round(pt[1], 2)) + ',' + matched_info[0] + '\n'
    # save result as txt
    with open(os.path.join(ws, 'AHI_MISR_Ray-matched_orbits_50km.txt'), 'w') as f:
        f.write(txt_str)


if __name__ == "__main__":
    main()