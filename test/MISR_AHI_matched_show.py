import os
import numpy

ws = r'C:\Work\AHI_MISR\20221210'
# ws = r'C:\Work\AHI_MISR\20230104'
merged_npy_filename = os.path.join(ws, 'AHI_MISR_Ray-matched.npy')


def main():
    txt_str = ''
    npy_list = numpy.load(merged_npy_filename, allow_pickle=True)
    for record in npy_list:
        pt = record['location']
        txt_str += str(round(pt[0], 2)) + '\t' + str(round(pt[1], 2)) + '\n'
        matched = record['matched_infos']
        for matched_item in matched:
            for mactch_r in matched_item:
                txt_str += mactch_r + '\t'
            txt_str += '\n'
    # save result as txt
    with open(os.path.join(ws, 'AHI_MISR_Ray-matched.txt'), 'w') as f:
        f.write(txt_str)


if __name__ == "__main__":
    main()