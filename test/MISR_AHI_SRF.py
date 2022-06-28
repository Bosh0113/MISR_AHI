import csv
import numpy
import matplotlib.pyplot as plt

if __name__ == "__main__":
    csv_filename = r'D:\Work_PhD\MISR_AHI_WS\220627\AHI_MISR_SRF.csv'
    srf_record = []
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        for item in reader:
            srf_item = numpy.array(item)
            srf_item = srf_item[srf_item != '']
            srf_record.append(srf_item.astype(float))
    # remove same keys
    srf4mapping = []
    for idx in range(0, 8*2, 2):
        srf_record_obj = {}
        wl_array = srf_record[idx]
        srf_array = srf_record[idx+1]
        for srf_idx in range(len(wl_array)):
            srf_record_obj[str(wl_array[srf_idx])] = srf_array[srf_idx]
        srf4mapping.append(srf_record_obj)
    srf_array_mapping = []
    for srf_record_obj in srf4mapping:
        srf_array_mapping.append(numpy.array(list(srf_record_obj.keys())).astype(float))
        srf_array_mapping.append(numpy.array(list(srf_record_obj.values())))
    # mapping
    for idx in range(0, 8, 2):
        plt.plot(srf_array_mapping[idx], srf_array_mapping[idx+1], 'b-', linewidth=0.8)
    for idx in range(8, 8*2, 2):
        plt.plot(srf_array_mapping[idx], srf_array_mapping[idx+1], 'r--', linewidth=0.8)
    plt.grid(b=True, which='major', axis='y', linewidth=0.5, alpha=0.5)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Relative spectral Response')
    plt.xlim((380.0, 930.0))
    plt.ylim((0.0, 1.05))
    plt.show()