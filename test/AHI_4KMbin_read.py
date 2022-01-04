import numpy
import matplotlib.pyplot as plt


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220103'
    bin_filename = workspace + '/202201010000.sat.zth.fld.4km.bin'
    # dtype='>u2' for 	2 byte “unsigned short” binary data without any hearder and footer information, with “big endian” byte order
    # dtype='>f4' for 	4 byte “float” binary data with “big endian” byte order.
    data_DN = numpy.fromfile(bin_filename, dtype='>f4')
    data_DN = data_DN.reshape(3000, 3000)
    plt.imshow(data_DN, vmin=0, vmax=90, extent=(85, 205, -60, 60), interpolation="None", origin="upper")
    plt.title('VZA DN value: 202201010000')
    plt.colorbar().set_label('DN', size=15)
    plt.xlabel("longitude", size=15)
    plt.ylabel("latitude", size=15)
    # plt.grid(True)
    plt.show()