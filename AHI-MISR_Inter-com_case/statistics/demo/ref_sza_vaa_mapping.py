import numpy
import matplotlib.pyplot as plt

deme_npy = r'E:\MISR_AHI_WS\230310\box_plot\26_0_band3_ref_sza_vza_variation.npy'

DEGREE_INTERNAL = 1


def line_plot(all_data):
    v_ahi_toa_record = all_data[0]
    v_ahi_sr_record = all_data[1]
    v_misr_sr_record = all_data[2]
    refer_sza_idx = numpy.arange(15, 80, DEGREE_INTERNAL)
    y_v_ahi_toa = numpy.zeros_like(refer_sza_idx)*1.
    y_v_ahi_sr = numpy.zeros_like(refer_sza_idx)*1.
    y_v_misr_sr = numpy.zeros_like(refer_sza_idx)*1.
    for v_item_idx in range(len(v_ahi_toa_record)):
        v_ahi_toa_item = v_ahi_toa_record[v_item_idx]
        if len(v_ahi_toa_item) > 0:
            v_ahi_toa_mean = round(numpy.median(v_ahi_toa_item), 3)
            print(v_ahi_toa_mean)
            y_v_ahi_toa[v_item_idx] = v_ahi_toa_mean
            print(y_v_ahi_toa[v_item_idx])
            v_ahi_sr_item = v_ahi_sr_record[v_item_idx]
            v_ahi_sr_mean = round(numpy.median(v_ahi_sr_item), 3)
            y_v_ahi_sr[v_item_idx] = v_ahi_sr_mean
            v_misr_sr_item = v_misr_sr_record[v_item_idx]
            v_misr_sr_mean = round(numpy.median(v_misr_sr_item), 3)
            y_v_misr_sr[v_item_idx] = v_misr_sr_mean

    y_v_ahi_toa[y_v_ahi_toa==0.] = numpy.NaN
    y_v_ahi_sr[y_v_ahi_sr==0.] = numpy.NaN
    y_v_misr_sr[y_v_misr_sr==0.] = numpy.NaN
    f, ax = plt.subplots()
    print(y_v_ahi_toa)
    print(y_v_ahi_sr)
    print(y_v_misr_sr)
    ax.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_ahi_toa, label='AHI TOA')
    ax.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_ahi_sr, label='AHI SR')
    ax.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], y_v_misr_sr, label='MISR SR')
    plt.legend()
    plt.show()


def box_plot(all_data):
    fig, axs = plt.subplots()
    axs.boxplot(all_data)
    axs.set_title('Box plot')
    plt.show()


if __name__ == "__main__":
    npy_array = numpy.load(deme_npy, allow_pickle=True)
    line_plot(npy_array)
    # box_plot(npy_array[2])