import csv
import matplotlib.pyplot as plt

# BRF_type = 'BRF TOC'
# BRF_index = 4
BRF_type = 'BRF TOC(NIR)'
BRF_index = 5
# BRF_type = 'BRF TOA'
# BRF_index = 6
# VZAs = [30, 40, 50, 60]
VZA = 60
RAAs = [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180]
# SZAs = [10, 20, 30, 40, 45, 55, 60, 75, 80, 90]
SZA = 55
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
    mapping_RAA = []
    mapping_SRF = []
    for csv_index in range(len(csv_paths)):
        csv_path = csv_paths[csv_index]
        csv_reader = csv.reader(open(o_needle_csv))
        line_index = 0
        type_RAA = []
        type_SRF = []
        for line_data in csv_reader:
            # if not title
            if line_index > 0:
                SZA_c = int(line_data[0])
                VZA_c = int(line_data[1])
                LAI_c_str = line_data[3]
                if VZA_c == VZA and SZA_c == SZA and LAI_c_str == LAIs[csv_index]:
                    RAA = int(line_data[2])
                    if RAA in RAAs:
                        type_RAA.append(RAA)
                        type_SRF.append(float(line_data[BRF_index]))
            line_index += 1
        mapping_RAA.append(type_RAA[:])
        mapping_SRF.append(type_SRF[:])

    line_colors = ['g^-', 'c>-', 'mv-', 'y<-', 'b.-']

    for index in range(len(type_names)):
        type_name = type_names[index]
        type_LAI = LAIs[index]
        type_RAA = mapping_RAA[index][:]
        type_SRF = mapping_SRF[index][:]
        line_color = line_colors[index]
        type_label = type_name + " LAI=" + LAIs[index]
        plt.plot(type_RAA, type_SRF, line_color, label=type_label)

    plt.grid(which="major",
             axis="x",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.grid(which="major",
             axis="y",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.xlabel('RAA')
    plt.ylabel(BRF_type)
    plt.title('SZA=' + str(SZA) + ' VZA=' + str(VZA))
    # plt.ylim(0, 1.5)
    # plt.xlim(20, 40)
    plt.legend()
    plt.show()
