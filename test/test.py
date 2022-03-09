import numpy


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220226'
    raa_record_file = ws + '/RAA_MISR_AHITime_AHI.npy'
    raa_record = numpy.load(raa_record_file)
    for raa_item in raa_record:
        print('-MISR_RAA:', float(raa_item[0]), '-AHI_time:', raa_item[1], '-AHI_RAA:', float(raa_item[2]))