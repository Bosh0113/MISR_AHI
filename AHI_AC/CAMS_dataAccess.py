import cdsapi
import os


def CAMS_download(v_type, d_range, t_range, nc_path):
    try:
        c = cdsapi.Client()

        c.retrieve(
            'cams-global-reanalysis-eac4', {
                'variable': v_type,
                'date': d_range,
                'time': t_range,
                'area': [60, 85, -60, -155],
                'format': 'netcdf',
            }, nc_path)
    except Exception as e:
        print('Error: ' + nc_path)
        print(e)


if __name__ == "__main__":
    # data_types = ['total_column_ozone', 'total_column_water_vapour']
    # date_start = '2016-01-01'
    # date_end = '2016-12-31'
    # date_range = date_start + '/' + date_end
    # time_range = [ '00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']

    ws = '/data/beichen/data/CAMS4AHI2016/Ozone'
    file_path = 'ozone_201601010000.nc'
    CAMS_download(['total_column_ozone'], '2016-01-01/2016-01-01', ['00:00'], os.path.join(ws, file_path))