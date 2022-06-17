import numpy
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220614\26_10'
    time = 201510070250
    # ws = r'D:\Work_PhD\MISR_AHI_WS\220614\70_80'
    # time = 201610130340
    bands = range(0, 4)
    for band in bands:
        npy_filename = ws + '/' + str(time) + '_sr_band' + str(band + 1) + '.npy'
        record_obj = numpy.load(npy_filename, allow_pickle=True)[0]
        misr_sr_v3 = record_obj['misr_v3']
        misr_sr_v3 = misr_sr_v3.flatten()
        misr_sr_v3 = misr_sr_v3[~numpy.isnan(misr_sr_v3)]
        ahi_sr_misr = record_obj['ahi_sr2misr']
        ahi_sr_misr = ahi_sr_misr.flatten()
        ahi_sr_misr = ahi_sr_misr[~numpy.isnan(ahi_sr_misr)]
        print(r2_score(ahi_sr_misr, misr_sr_v3))
        print(mean_squared_error(ahi_sr_misr, misr_sr_v3))
        plt.scatter(ahi_sr_misr, misr_sr_v3)
        plt.show()
