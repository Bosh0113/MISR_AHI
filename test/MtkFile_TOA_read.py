# python 3.6
from MisrToolkit import MtkFile, MtkRegion
import matplotlib.pyplot as plt
import numpy


if __name__ == "__main__":
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220707'
    # 20170115
    hdf_filename = workspace + '/MISR_AM1_TC_ALBEDO_P131_O090838_F05_0011.hdf'

    # ROI_name: 60.0_200
    roi_extent = [41.350, 104.490, 41.218, 104.670]

    m_file = MtkFile(hdf_filename)
    m_grid22 = m_file.grid('ReflectingLevelParameters_2.2_km')
    toa_field = m_grid22.field('BRFTop_Mean[2][1]')  # band, camera
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    toa_roi = toa_field.read(roi_r).data()

    toa_roi_1d = numpy.array(toa_roi).flatten()
    toa_roi_1d = toa_roi_1d[toa_roi_1d > 0.]
    print(toa_roi_1d.mean())

    toa_roi[~(toa_roi > 0.)] = numpy.NaN
    plt.imshow(toa_roi)
    plt.colorbar()
    plt.show()