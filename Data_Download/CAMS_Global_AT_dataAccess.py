import cdsapi
import os
from datetime import datetime, timedelta

DATA_TYPE = ['black_carbon_aerosol_optical_depth_550nm', 'dust_aerosol_optical_depth_550nm', 'organic_matter_aerosol_optical_depth_550nm', 'sea_salt_aerosol_optical_depth_550nm', 'sulphate_aerosol_optical_depth_550nm']
TIME_RANGE = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']

STORAGE_FOLDER = '/disk1/Data/CAMS1521_AT'


def CAMS_download(v_type, d_range, t_range, nc_path):
    try:
        c = cdsapi.Client()
        c.retrieve(
            'cams-global-reanalysis-eac4', {
                'variable': v_type,
                'date': d_range,
                'time': t_range,
                'format': 'netcdf',
            }, nc_path)
        print(nc_path, '-> download')
    except Exception as e:
        print('Error: ' + nc_path)
        print(e)


if __name__ == "__main__":
    date_start = '2015-01-01'
    date_end = '2021-12-31'
    date_s = datetime.strptime(date_start, "%Y-%m-%d")
    date_t = timedelta(days=1)
    date_e = datetime.strptime(date_end, "%Y-%m-%d")
    date_dl = date_s
    while date_dl <= date_e:
        date_dl_str = date_dl.strftime("%Y-%m-%d")
        data_range = date_dl_str + '/' + date_dl_str
        file_path = date_dl.strftime("%Y%m%d") + '.nc'
        CAMS_download(DATA_TYPE, data_range, TIME_RANGE, os.path.join(STORAGE_FOLDER, file_path))
        date_dl = date_dl + date_t
