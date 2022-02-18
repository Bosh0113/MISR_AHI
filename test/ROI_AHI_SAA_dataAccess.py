# 使用python 3.6
from MisrToolkit import *
import math
from datetime import *
# from timezonefinder import TimezoneFinder
# from tzwhere import tzwhere
# from pytz import timezone

start_t = '2016-05-01T00:00:00Z'
end_t = '2016-05-31T23:59:59Z'

ahi_localtime_start = '08:00:00Z'
ahi_localtime_end = '15:59:59Z'

ahi_vza_bin = r'D:\Work_PhD\MISR_AHI_WS\220103\202201010000.sat.zth.fld.4km.bin'
misr_folder = r'D:\Work_PhD\MISR_AHI_WS\220213\MISR'


# get time offset to UTC, by lontitude not timezone
def ahi_lon_timeoffset(lon):
    lon_interval = 15
    UTC_e_lon = lon_interval / 2
    
    timeoffset = math.ceil((lon - UTC_e_lon) / lon_interval)

    return timeoffset


if __name__ == "__main__":
    roi_extent = [43.625, 90.772, 43.495, 90.952]
    center_pt = [(roi_extent[0] + roi_extent[2])/2, (roi_extent[1] + roi_extent[3])/2]
    # tz = tzwhere.tzwhere()
    # time_zone = tz.tzNameAt(center_pt[0], center_pt[1])
    # tf = TimezoneFinder(in_memory=True)
    # local_time_zone = tf.timezone_at(lat=center_pt[0], lng=center_pt[1])
    
    time_offset = ahi_lon_timeoffset(center_pt[1])
    # MISR mean time of scan
    misr_time = ('2016-06-20T04:18:26Z', '2016-06-20T05:57:19Z')
    misr_start_time_str = misr_time[0]
    misr_end_time_str = misr_time[1]
    misr_start_date = datetime.strptime(misr_start_time_str, "%Y-%m-%dT%H:%M:%SZ")
    misr_end_date = datetime.strptime(misr_end_time_str, "%Y-%m-%dT%H:%M:%SZ")
    diff_date = misr_end_date - misr_start_date
    misr_mean_date = misr_start_date + diff_date / 2
    misr_mean_date_str = misr_mean_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(misr_mean_date_str)
    # days of required AHI data (3 day)
    utc_date = datetime.strptime(misr_mean_date_str, "%Y-%m-%dT%H:%M:%SZ")
    local_date2 = utc_date + timedelta(hours=time_offset)
    local_date1 = local_date2 + timedelta(days=-1)
    local_date3 = local_date2 + timedelta(days=1)
    # UTC time range of required AHI data
    local_dates = [local_date1, local_date2, local_date3]
    for local_date in local_dates:
        local_day_str = local_date.strftime("%Y-%m-%dT")

        local_time_start_str = local_day_str + ahi_localtime_start
        local_date_start = datetime.strptime(local_time_start_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_date_start = local_date_start - timedelta(hours=time_offset)
        utc_date_start_str = utc_date_start.strftime("%Y-%m-%dT%H:%M:%SZ")

        local_time_end_str = local_day_str + ahi_localtime_end
        local_date_end = datetime.strptime(local_time_end_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_date_end = local_date_end - timedelta(hours=time_offset)
        utc_date_end_str = utc_date_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        utc_date_range = (utc_date_start_str, utc_date_end_str)

        print(utc_date_range)
    