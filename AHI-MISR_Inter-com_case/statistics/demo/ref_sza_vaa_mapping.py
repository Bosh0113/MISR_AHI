import numpy
import matplotlib
import matplotlib.pyplot as plt

deme_npy = r'E:\MISR_AHI_WS\230310\26_0_band3_ref_sza_vza_variation.npy'


if __name__ == "__main__":
    npy_array = numpy.load(deme_npy, allow_pickle=True)

    f, ax = plt.subplots()
    ax.plot([i for i in range((80-15)*2)], npy_array[0], label='AHI TOA')
    ax.plot([i for i in range((80-15)*2)], npy_array[1], label='AHI SR')
    ax.plot([i for i in range((80-15)*2)], npy_array[2], label='MISR SR')
    plt.legend()
    plt.show()
