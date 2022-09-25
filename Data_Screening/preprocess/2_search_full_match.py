import os
import numpy
import re
import urllib.request
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_path, orbit_to_time_range

ROI_SIZA = 0.12
MISR_CAMERA_INDEX = {
    '0.0': [4],
    '26.1': [3, 5],
    '45.6': [2, 6],
    '60.0': [1, 7],
    '70.5': [0, 8]
}

START_TIME = '2017-01-01T00:00:00Z'
END_TIME = '2017-12-31T23:59:59Z'

MISR_DATA_FOLDER = '/disk1/Data/MISR4AHI2015070120210630_3'
AHI_VZA_BIN = '/disk1/Data/AHI/VZA/202201010000.sat.zth.fld.4km.bin'
AHI_VAA_BIN = '/disk1/Data/AHI/VAA/202201010000.sat.azm.fld.4km.bin'


def re_download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    s_time = time_range[0]
    matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(s_time))
    yy = matchObj.group(1)
    mm = matchObj.group(2)
    dd = matchObj.group(3)

    t = str(yy) + '.' + str(mm) + '.' + str(dd)
    P = 'P' + (3-len(str(path)))*'0' + str(path)
    O_ = 'O' + (6-len(str(orbit)))*'0' + str(orbit)
    F = 'F' + '08'
    v = '0023'
    base_url = 'https://opendap.larc.nasa.gov/opendap/MISR/MIL2ASLS.003'
    filename = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'

    download_url = base_url + '/' + t + '/' + filename
    storage_path = folder + '/' + filename

    try:
        urllib.request.urlretrieve(download_url, filename=storage_path)
    except Exception as e:
        print('Error: ' + download_url)
        print(e)


def get_misr_filename(orbit):
    path = orbit_to_path(orbit)
    P = 'P' + (3 - len(str(path))) * '0' + str(path)
    O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
    F = 'F' + '08'
    v = '0023'
    misr_v3_nc_file = 'MISR_AM1_AS_LAND_' + P + '_' + O_ + '_' + F + '_' + v + '.nc'
    misr_nc_filename = MISR_DATA_FOLDER + '/' + misr_v3_nc_file

    return misr_nc_filename


def get_misr_obs_angle(roi_extent, orbit, camera_idx):
    misr_filename = get_misr_filename(orbit)
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    if os.path.exists(misr_filename):
        m_file = None
        file_read_flag = 1
        while file_read_flag == 1:
            try:
                m_file = MtkFile(misr_filename)
                file_read_flag = 0
            except Exception as e:
                print(e)
                path = orbit_to_path(orbit)
                misr_v3_nc_file = misr_filename.split('/')[(len(misr_filename.split('/')))]
                print('re-download:', misr_v3_nc_file)
                re_download_MISR_MIL2ASLS03_NC(MISR_DATA_FOLDER, path, orbit)
        m_grid = m_file.grid('4.4_KM_PRODUCTS')
        # MISR VZA
        roi_misr_vza = 0.0
        vza_field = m_grid.field('GEOMETRY/View_Zenith_Angle[' + str(camera_idx) + ']')
        f_vza_data = vza_field.read(roi_r).data()
        f_vza_data = numpy.array(f_vza_data)
        # in single array
        roi_misr_vza_list = f_vza_data.flatten()
        roi_misr_vza_list = roi_misr_vza_list[roi_misr_vza_list > 0.]
        # has available values?
        if len(roi_misr_vza_list) > 0:
            roi_misr_vza = roi_misr_vza_list.mean()
        else:
            0.0, 0.0
        # MISR VAA
        vaa_field = m_grid.field('GEOMETRY/View_Azimuth_Angle[' + str(camera_idx) + ']')
        f_vaa_data = vaa_field.read(roi_r).data()
        f_vaa_data = numpy.array(f_vaa_data)
        roi_misr_vaa_list = f_vaa_data.flatten()
        roi_misr_vaa_list = roi_misr_vaa_list[roi_misr_vaa_list > 0.]
        # has available values?
        if len(roi_misr_vza_list) > 0:
            roi_misr_vaa = roi_misr_vaa_list.mean()
        else:
            0.0, 0.0

        return roi_misr_vza, roi_misr_vaa

    else:
        return 0.0, 0.0


def get_ahi_obs_angle():
    pass
    # return ahi_vza, ahi_vaa


def main():
    workspace = r'D:\Work_PhD\MISR_AHI_WS\220920'
    MISRVZAs = [0.0, 26.1, 45.6, 60.0, 70.5]
    for vza_idx in range(len(MISRVZAs)):
        misr_vza_str = str(MISRVZAs[vza_idx])
        point_locations_npy_filename = os.path.join(workspace, misr_vza_str + '_point4search.npy')
        search_cood = numpy.load(point_locations_npy_filename)
        for cood_point in search_cood:
            lon4search = cood_point[0]
            lat4search = cood_point[1]
            # ROI extent (ullat, ullon, lrlat, lrlon)
            roi_extent = [lat4search + ROI_SIZA/2, lon4search - ROI_SIZA/2, lat4search - ROI_SIZA/2, lon4search + ROI_SIZA/2]
            # Full Match Screening
            roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
            pathList = roi_r.path_list
            for path in pathList:
                orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
                for orbit in orbits:
                    camera_idx_array = MISR_CAMERA_INDEX[misr_vza_str]
                    for camera_idx in camera_idx_array:
                        misr_vza, misr_vaa = get_misr_obs_angle(roi_extent, orbit, camera_idx)
                        if misr_vza != 0.0:
                            ahi_vza, ahi_vaa = get_ahi_obs_angle(roi_extent)


if __name__ == "__main__":
    main()
