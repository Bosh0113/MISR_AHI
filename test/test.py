from datetime import *


ahi_localtime_start = '08:00:00Z'
ahi_localtime_end = '15:59:59Z'


if __name__ == "__main__":
    misr_time_str = '2016-06-20T04:18:26Z'
    time_offset = 6

    utc_date = datetime.strptime(misr_time_str, "%Y-%m-%dT%H:%M:%SZ")
    local_date2 = utc_date + timedelta(hours=time_offset)
    local_date1 = local_date2 + timedelta(days=-1)
    local_date3 = local_date2 + timedelta(days=1)

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