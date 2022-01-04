import numpy
import matplotlib.pyplot as plt


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220103'
    bin2109_filename = workspace + '/202111010000.sat.zth.fld.4km.bin'
    bin2201_filename = workspace + '/202201010000.sat.zth.fld.4km.bin'
    data1_DN = numpy.fromfile(bin2109_filename, dtype='>f4')
    data2_DN = numpy.fromfile(bin2201_filename, dtype='>f4')
    data1_DN = data1_DN.reshape(3000, 3000)
    data2_DN = data2_DN.reshape(3000, 3000)
    data_DN = data2_DN - data1_DN
    plt.imshow(data_DN)
    plt.title('VZA DN differ value: 202201010000 - 202111010000')
    plt.colorbar()
    plt.show()