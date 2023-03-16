import datetime as dt
import os

with open (r'E:\MISR_AHI_WS\230316\CloudMask_2019\time.txt','w') as f:
    date_start = '2019-01-01 00:00'
    date_end = '2019-12-31 09:00'
    date_t = dt.timedelta(minutes=10)
    date_s = dt.datetime.strptime(date_start, "%Y-%m-%d %H:%M")
    date_e = dt.datetime.strptime(date_end, "%Y-%m-%d %H:%M")
    date_time_now = date_s
    while date_time_now <= date_e:

        date = date_time_now.strftime("%Y%m%d%H%M")
        hour = int(date[8:10])
        
        if hour < 10:
            # print(date,hour)
            if not os.path.exists(r'E:\MISR_AHI_WS\230316\CloudMask_2019\cloudmask\{}\AHIcm.v0.{}.dat'.format(date[:6],date)):
                print(date)
                f.writelines(date + '\n')
        date_time_now = date_time_now + date_t