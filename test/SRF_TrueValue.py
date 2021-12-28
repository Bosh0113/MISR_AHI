import numpy
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math


def BRF_TrueValue(o_BRF, scale, offset):
    fill = 65533
    underflow = 65534
    overflow = 65535

    t_BRF = []
    for i in range(len(o_BRF)):
        t_BRF_item = []
        for j in range(len(o_BRF[0])):
            o_value = o_BRF[i][j]
            if o_value in [fill, underflow, overflow]:
                t_BRF_item.append(0)
            else:
                x = math.floor(o_value/2)
                y = x*scale + offset
                t_BRF_item.append(y)
        t_BRF.append(t_BRF_item)
    return t_BRF


if __name__ == "__main__":
    BRF_npy_path = r'D:\Work_PhD\MISR_AHI_WS\211204\SRF_62\b_3_c_8.npy'
    BRF_data = numpy.load(BRF_npy_path)
    
    # original values
    plt.imshow(BRF_data, cmap=plt.cm.jet, vmin=0, vmax=11000)
    plt.title('Original values in LandBRF 2016-01-15 Band 4 Camera 9')
    plt.colorbar()
    plt.show()

    # true values
    scale_landBRF = 0.0001526065170764923
    offset_landBRF = 0.0
    BRF_tv = BRF_TrueValue(BRF_data, scale_landBRF, offset_landBRF)
    plt.imshow(BRF_tv, cmap=plt.cm.jet, vmin=0.0, vmax=1.0)
    plt.title('True values in LandBRF 2016-01-15 Band 4 Camera 9')
    plt.colorbar()
    plt.show()