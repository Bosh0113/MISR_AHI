import os
import re
import numpy
import urllib.request
from MisrToolkit import MtkRegion, MtkFile, path_time_range_to_orbit_list, orbit_to_path, orbit_to_time_range

WORK_SPACE = os.getcwd()

ROI_SIZE = 0.1
START_TIME = '2017-01-01T00:00:00Z'
END_TIME = '2017-12-31T23:59:59Z'
MISR_DATA_FOLDER = '/data01/people/beichen/data/MISR4AHI2015070120210630_3'

GRO_OBS_COND_TXT = 'MISR_VZA_VAA.txt'


def re_download_MISR_MIL2ASLS03_NC(folder, path, orbit):
    time_range = orbit_to_time_range(orbit)
    for orbit_time in time_range:
        matchObj = re.search(r'(\d+)-(\d+)-(\d+)T', str(orbit_time))
        yy = matchObj.group(1)
        mm = matchObj.group(2)
        dd = matchObj.group(3)

        t = str(yy) + '.' + str(mm) + '.' + str(dd)
        P = 'P' + (3 - len(str(path))) * '0' + str(path)
        O_ = 'O' + (6 - len(str(orbit))) * '0' + str(orbit)
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
            return 0.0, 0.0
        # MISR VAA
        roi_misr_vaa = 0.0
        vaa_field = m_grid.field('GEOMETRY/View_Azimuth_Angle[' + str(camera_idx) + ']')
        f_vaa_data = vaa_field.read(roi_r).data()
        f_vaa_data = numpy.array(f_vaa_data)
        roi_misr_vaa_list = f_vaa_data.flatten()
        roi_misr_vaa_list = roi_misr_vaa_list[roi_misr_vaa_list > 0.]
        print(roi_misr_vaa_list.tolist())
        # has available values?
        if len(roi_misr_vaa_list) > 0:
            roi_misr_vaa = roi_misr_vaa_list.mean()
        else:
            return 0.0, 0.0

        return roi_misr_vza, roi_misr_vaa

    else:
        return 0.0, 0.0
    

def roi_ray_match(roi_name, cood_point, path, camera_idx):
    print(roi_name)
    print(cood_point)
    # search full matching
    geocond_record_str = 'MISR_path\tMISR_orbit\tcamera_idx\tMISR_VZA\tMISR_VAA\n'

    lon4search = cood_point[0]
    lat4search = cood_point[1]
    # ROI extent (ullat, ullon, lrlat, lrlon)
    roi_extent = [lat4search + ROI_SIZE / 2, lon4search - ROI_SIZE / 2, lat4search - ROI_SIZE / 2, lon4search + ROI_SIZE / 2]
    
    roi_r = MtkRegion(roi_extent[0], roi_extent[1], roi_extent[2], roi_extent[3])
    orbits = path_time_range_to_orbit_list(path, START_TIME, END_TIME)
    for orbit in orbits:
        try:
            misr_vza, misr_vaa = get_misr_obs_angle(roi_extent, orbit, camera_idx)

            if misr_vza != 0.0:
                    # matched info
                    misr_roi_vza = '%.3f' % misr_vza
                    misr_roi_vaa = '%.3f' % misr_vaa
                    # matched info: MISR_path MISR_orbit camera_idx MISR_VZA MISR_VAA
                    record_item = str(path) + '\t' + str(orbit) + '\t' + str(camera_idx) + '\t' + str(misr_roi_vza) + '\t' + str(misr_roi_vaa)
                    print(record_item)
                    geocond_record_str += record_item + '\n'
        except Exception as e:
            print('orbit:', orbit)
            print(e)

    # save result as txt
    with open(os.path.join(WORK_SPACE, roi_name + '_' + GRO_OBS_COND_TXT), 'w') as f:
        f.write(geocond_record_str)


def main():
    roi_name = '102.25, -0.05'
    cood_point = [102.25, -0.05]
    path = 127
    camera_idx = 2
    roi_ray_match(roi_name, cood_point, path, camera_idx)


if __name__ == "__main__":
    main()