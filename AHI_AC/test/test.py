import numpy
import matplotlib.pyplot as plt


def mapping(array):
    plt.imshow(array)
    plt.colorbar()
    plt.show()


def band_SR(xa, xb, xc, obs_r):
    y = xa * obs_r - xb
    sr = y / (1 + xc * y)
    return sr


def calculate_SR(roi_xa, roi_xb, roi_xc, roi_obs_r):
    roi_sr = numpy.zeros_like(roi_xa)
    for lat in range(len(roi_xa)):
        for lon in range(len(roi_xa[0])):
            xa = roi_xa[lat][lon]
            xb = roi_xb[lat][lon]
            xc = roi_xc[lat][lon]
            obs_r = roi_obs_r[lat][lon]
            roi_sr[lat][lon] = band_SR(xa, xb, xc, obs_r)
    return roi_sr


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220602\70_80'
    ac_filename = ws + '/201610130340_ac_band1.npy'
    ac_txt_filename = ws + '/201610130340_ac_band1.txt'
    ac_record = numpy.load(ac_filename, allow_pickle=True)[0]

    # with open(ac_txt_filename, 'w') as f:
    #     f.write(str(ac_record))

    # roi_aot = ac_record['roi_aot']
    # roi_oz = ac_record['roi_oz']
    # roi_wv = ac_record['roi_wv']
    # fa_array = ac_record['roi_ac_fa']
    # xb_array = ac_record['roi_ac_xb']
    # xc_array = ac_record['roi_ac_xc']
    # roi_data = ac_record['roi_ahi_data']
    # roi_ahi_sr = ac_record['roi_ahi_sr']
    # mapping(roi_aot)
    # mapping(roi_oz)
    # mapping(roi_wv)
    # mapping(fa_array)
    # mapping(xb_array)
    # mapping(xc_array)
    # mapping(roi_data)
    # mapping(roi_ahi_sr)
    # mapping(roi_ahi_sr + roi_data)
    # print(calculate_SR(fa_array, xb_array, xc_array, roi_data))
