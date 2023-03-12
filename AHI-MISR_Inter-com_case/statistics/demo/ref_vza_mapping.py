import os
import numpy
import matplotlib.pyplot as plt
from scipy.stats import linregress

ws = r'E:\MISR_AHI_WS\230310\ref_sza_vza_variation_10'

DEGREE_INTERNAL = 1


def box_plot(all_data):

    fig, axs = plt.subplots()
    axs.grid(linestyle='--', linewidth=0.3, axis='x')

    colors_map = ['black', 'grey', 'chocolate', 'peachpuff', 'olivedrab', 'lightgreen', 'rebeccapurple', 'violet']
    label_list = ['MISR SR (VZA≈26°)', 'AHI SR (VZA≈26°)',
                  'MISR SR (VZA≈45°)', 'AHI SR (VZA≈45°)',
                  'MISR SR (VZA≈60°)', 'AHI SR (VZA≈60°)',
                  'MISR SR (VZA≈70°)', 'AHI SR (VZA≈70°)']
    for idx in range(len(all_data)):
        axs.boxplot(all_data[idx],
                    vert=False,
                    patch_artist=True,
                    showfliers=False,
                    widths=0.4,
                    boxprops=dict(facecolor='white',color=colors_map[idx], linewidth=0.5, alpha=0.2),
                    medianprops=dict(color=colors_map[idx], linewidth=4),
                    whiskerprops=dict(color=colors_map[idx], linestyle='--', linewidth=0.5, alpha=0.3),
                    capprops=dict(color=colors_map[idx], linewidth=0.5, alpha=0.))
        axs.plot([i for i in range((80-15)*int(1/DEGREE_INTERNAL))], [-10 for i in range((80-15)*int(1/DEGREE_INTERNAL))], color=colors_map[idx], label=label_list[idx])

    axs.minorticks_on()
    y_minor_locator = plt.MultipleLocator(1)
    y_major_locator = plt.MultipleLocator(5)
    axs.yaxis.set_minor_locator(y_minor_locator)
    axs.yaxis.set_major_locator(y_major_locator)
    x_minor_locator = plt.MultipleLocator(0.02)
    x_major_locator = plt.MultipleLocator(0.1)
    axs.xaxis.set_minor_locator(x_minor_locator)
    axs.xaxis.set_major_locator(x_major_locator)

    axs.spines['right'].set_color('none')
    axs.spines['top'].set_color('none')

    axs.tick_params(axis="x", which='minor', length=5, direction='out', labelsize=15)
    axs.tick_params(axis="x", which='major', length=5, direction='out', labelsize=15)
    axs.tick_params(axis="y", which='minor', length=5, direction='out', labelsize=15)
    axs.tick_params(axis="y", which='major', length=5, direction='out', labelsize=15)

    plt.yticks([i for i in range(0, (80-15), 5*int(1/DEGREE_INTERNAL))], numpy.arange(15, 80, 5*int(1/DEGREE_INTERNAL)))
    plt.ylim(12.5, 51.5)
    # plt.xlim(-0.06, 1.175)    # band3 all
    plt.xlim(-0.06, 0.595)  # band3 display
    # plt.xlim(0.04, 0.695)   # band4 display
    plt.ylabel('SZA (°), RAA ≈ 30°', size=18)
    plt.xlabel('Reflectance on Band3 of AHI', size=18)   # band3
    # plt.xlabel('Reflectance on Band4 of AHI', size=18) # band4
    plt.legend(markerscale=2, loc=7, fontsize='medium')   # band3
    # plt.legend(markerscale=2, loc=3, fontsize='medium') # band4
    plt.show()


def main():
    o_data = []
    vza_angle = ['26', '45', '60', '70']
    bands = ['band3', 'band4']
    band_str = 'band3'
    # band_str = 'band4'
    for vza_str in vza_angle:
        demo_npy = os.path.join(ws, vza_str + '_0_' + band_str + '_ref_sza_vza_variation.npy')
        all_data = numpy.load(demo_npy, allow_pickle=True)
        misr_sr_data = all_data[0].tolist()
        ahi_sr_data = all_data[2].tolist()
        o_data.append(misr_sr_data)
        o_data.append(ahi_sr_data)
    show_data = numpy.copy(o_data)
    for sza_idx in range(0, (80-15), int(1/DEGREE_INTERNAL)):
        v_count = 0
        for vza_g_idx in range(0, 8, 2):
            pt_vs = o_data[vza_g_idx][sza_idx]
            if len(pt_vs) > 8: # meaningful count
                v_count += 1
        if v_count < 2:
            for vza_g_idx in range(0, 8, 1):
                show_data[vza_g_idx][sza_idx] = []

    box_plot(show_data)


if __name__ == "__main__":
    main()