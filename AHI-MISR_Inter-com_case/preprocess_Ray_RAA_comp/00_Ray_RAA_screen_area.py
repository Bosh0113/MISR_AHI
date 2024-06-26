import os
import numpy as np

ws = '/disk1/workspace/20230724'

raa_matched_record_50km_npy = os.path.join(ws, 'MISR_matched_record_10km_30S40S.npy')
Ray_RAA_loc_txt = os.path.join(ws, 'Ray_RAA_loc.txt')
common_loc_npy = os.path.join(ws, 'RAA_Ray_loc_10km.npy')


# get side of VAA-to-SAA (SAA as refer)
def get_side_RAA(vaa, saa):
    if saa < 180:
        if vaa > saa and vaa < saa + 180:
            return 1
        else:
            return -1
    if saa > 180:
        if vaa > saa - 180 and vaa < saa:
            return -1
        else:
            return 1


if __name__ == "__main__":
    raa_matches = np.load(raa_matched_record_50km_npy, allow_pickle=True)
    RAA_Ray_loc_record = []
    Ray_RAA_locs = ''
    for raa_item in raa_matches:
        raa_loc = raa_item['location'].tolist()
        raa_matches = raa_item['matched_infos']
        same_side = 0
        opposite_side = 0
        for raa_match in raa_matches:
            misr_vaa = raa_match[7]
            ahi_vaa = raa_match[8]
            misr_saa = raa_match[9]
            ahi_saa = raa_match[10]
            misr_dif = get_side_RAA(float(misr_vaa), float(misr_saa))
            ahi_dif = get_side_RAA(float(ahi_vaa), float(ahi_saa))
            if misr_dif*ahi_dif > 0:
                same_side += 1
            else:
                opposite_side += 1
        if same_side > 0 and opposite_side > 0:
            Ray_RAA_locs += str(raa_loc[0]) + ',' + str(raa_loc[1]) + ',' + str(len(raa_matches)) + '\n'
            RAA_Ray_loc_record.append(raa_item)
    np.save(common_loc_npy, np.array(RAA_Ray_loc_record))
    with open(Ray_RAA_loc_txt, 'w') as f:
        f.write(Ray_RAA_locs)