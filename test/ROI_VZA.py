# 使用python 3.6
from MisrToolkit import *
import numpy

start_t = '2016-05-01T00:00:00Z'
end_t = '2016-05-31T23:59:59Z'

ahi_vza_bin = r'D:\Work_PhD\MISR_AHI_WS\220103\202201010000.sat.zth.fld.4km.bin'


def get_region_ahi_vza(region_extent):
    ahi_vza_DN = numpy.fromfile(ahi_vza_bin, dtype='>f4')
    ahi_vza_DN = ahi_vza_DN.reshape(3000, 3000)
    p_size = 120 / 3000
    ullon_ahi = 85
    ullat_ahi = 60
    ymin_index = round(((region_extent[0] - ullat_ahi) * -1 ) / p_size)
    xmin_index = round((region_extent[1] - ullon_ahi) / p_size)
    ymax_index = round(((region_extent[2] - ullat_ahi) * -1 ) / p_size)
    xmax_index = round((region_extent[3] - ullon_ahi) / p_size)
    # print(ymin_index, xmin_index, ymax_index, xmax_index)
    roi_vza = ahi_vza_DN[ymin_index:ymax_index, xmin_index:xmax_index]
    return roi_vza


if __name__ == "__main__":
    # filename_HDF = 'D:/Work_PhD/MISR/test\MISR_AM1_AS_LAND_P107_O085361_F07_0022.hdf'
    # m = MtkFile(filename_HDF)
    # print(m.attr_list)

    ws = r'D:\Work_PhD\MISR_AHI_WS\220213\MISR'
    roi_extent = [43.625, 90.772, 43.495, 90.952]   # 70.5
    print('ROI 70.5-130')

    ahi_vza = get_region_ahi_vza(roi_extent)
    print('mean vza of ROI in AHI data:', ahi_vza.mean())

    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    pathList = roi_r.path_list
    for path in pathList:
        orbits = path_time_range_to_orbit_list(path, start_t, end_t)
        for orbit in orbits:
            P = 'P' + (3-len(str(path)))*'0' + str(path)
            O = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
            F = 'F' + '07'
            v = '0022'
            hdf_filename = ws + '/MISR_AM1_AS_LAND_' + P + '_' + O + '_' + F + '_' + v + '.hdf'
            m_file = MtkFile(hdf_filename)
            m_grid = m_file.grid('RegParamsLnd')
            m_field1 = m_grid.field('ViewZenAng[0]')
            m_field9 = m_grid.field('ViewZenAng[8]')
            f_vza_data1 = m_field1.read(roi_r).data()
            max_vza1 = f_vza_data1.max()
            if max_vza1 > -9999:
                # print(hdf_filename)
                print('path:', path, '--', 'orbit:', orbit)
                print(orbit_to_time_range(orbit))
                print('camera 1 vza in MISR data:', max_vza1)
            f_vza_data9 = m_field1.read(roi_r).data()
            max_vza9 = f_vza_data9.max()
            if max_vza9 > -9999:
                # print(hdf_filename)
                print('path:', path, '--', 'orbit:', orbit)
                print(orbit_to_time_range(orbit))
                print('camera 9 vza in MISR data:', max_vza9)