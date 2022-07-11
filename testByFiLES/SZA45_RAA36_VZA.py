import csv
import numpy
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from matplotlib.ticker import MultipleLocator

# BRF_type = 'BRF TOC'
# BRF_index = 4
BRF_type = 'BRF TOC(NIR)'
BRF_index = 5
# BRF_type = 'BRF TOA'
# BRF_index = 6
VZAs = [30, 40, 50, 60]
# RAAs = [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180]
RAA = 36
# SZAs = [10, 20, 30, 40, 45, 55, 60, 75, 80, 90]
SZA = 45
# land cover type
type_names = ['Droadleaved', 'Needleleaved', 'Cropland', 'Grassland', 'Sparse vegetation']
# LAIs = ['0.01', '0.1', '0.5', '1', '2', '3', '4', '5', '6', '7']
LAIs = ['5', '4', '3', '1', '0.5']

if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220524\LUT_FLiES'
    o_broad_csv = ws + '/LUT_open-broadleaved.csv'
    o_needle_csv = ws + '/LUT_open-needleleaved.csv'
    crop_csv = ws + '/LUT_rice.csv'
    grass_csv = ws + '/LUT_grassland.csv'
    sparse_csv = ws + '/LUT_sparse-forest.csv'
    csv_paths = [o_broad_csv, o_needle_csv, crop_csv, grass_csv, sparse_csv]
    mapping_VZA = []
    mapping_SRF = []
    for csv_index in range(len(csv_paths)):
        csv_path = csv_paths[csv_index]
        csv_reader = csv.reader(open(o_needle_csv))
        line_index = 0
        type_VZA = []
        type_SRF = []
        for line_data in csv_reader:
            # if not title
            if line_index > 0:
                SZA_c = int(line_data[0])
                RAA_c = int(line_data[2])
                LAI_c_str = line_data[3]
                if RAA_c == RAA and SZA_c == SZA and LAI_c_str == LAIs[csv_index]:
                    VZA = int(line_data[1])
                    if VZA in VZAs:
                        type_VZA.append(VZA)
                        type_SRF.append(float(line_data[BRF_index]))
            line_index += 1
        mapping_VZA.append(type_VZA[:])
        mapping_SRF.append(type_SRF[:])

    line_colors = ['g-', 'c-', 'm-', 'y-', 'b-']

    ax = plt.axes()
    for index in range(len(type_names)):
        type_name = type_names[index]
        type_LAI = LAIs[index]
        type_VZA = mapping_VZA[index][:]
        type_SRF = mapping_SRF[index][:]
        line_color = line_colors[index]
        type_label = type_name + " LAI=" + LAIs[index]

        interp_model = make_interp_spline(type_VZA, type_SRF)

        xs = numpy.linspace(30, 60, 500)
        ys = interp_model(xs)

        plt.plot(xs, ys, line_color, label=type_label, alpha=0.7, linewidth=1.5)
        
    plt.xlabel('VZA (°)')
    plt.ylabel(BRF_type)
    plt.title('SZA=' + str(SZA) + '°' + ' RAA=' + str(RAA) + '°')
    x_minorLocator = MultipleLocator(1.)
    x_majorLocator = MultipleLocator(5.)
    y_minorLocator = MultipleLocator(0.005)
    y_majorLocator = MultipleLocator(0.01)
    ax.xaxis.set_minor_locator(x_minorLocator)
    ax.xaxis.set_major_locator(x_majorLocator)
    ax.yaxis.set_minor_locator(y_minorLocator)
    ax.yaxis.set_major_locator(y_majorLocator)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.grid(which='both', linestyle='--', alpha=0.3, linewidth=0.5)
    plt.xlim((30, 60))
    plt.ylim((0.225, 0.345))
    plt.legend()
    plt.show()
