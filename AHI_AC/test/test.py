import numpy


if __name__ == "__main__":
    ac_filename = r'D:\Work_PhD\MISR_AHI_WS\220527\AHI_AC_PARAMETER\201608230450_ac_band3.npy'
    ac_record = numpy.load(ac_filename, allow_pickle=True)[0]
    roi_sr = ac_record['roi_ahi_sr']
    print(roi_sr)
    print(numpy.array(roi_sr).shape)