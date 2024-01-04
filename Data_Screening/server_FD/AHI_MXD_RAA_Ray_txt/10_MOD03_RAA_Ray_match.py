#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import xarray
import numpy
from datetime import datetime, timedelta


# In[2]:


MXD = 'MOD'
START_TIME = '2018-01-01T00:00:00Z'

DATA_FOLDER = '/data01/people/beichen/data'
MXD_HDF_FOLDER = os.path.join(DATA_FOLDER, MXD + '03_AHI_HDF_2018')
MXD_GEOTIFF_FOLDER = os.path.join(DATA_FOLDER, MXD + '03_AHI_GeoTiff_2018')

ws = os.getcwd()
RAA_MATCHED_TXT = os.path.join(ws, MXD+'03_RAA-matched_infos.txt')
RAY_MATCHED_TXT = os.path.join(ws, MXD+'03_RAY-matched_infos.txt')


# In[3]:


# VZA diff
DIFF_VZA_THRESHOLD = 1 # degree
# RAA diff
DIFF_RAA_THRESHOLD = 10 # degree
# VAA diff
DIFF_VAA_THRESHOLD = 10 # degree


# In[4]:


AHI_VZA_NPY = DATA_FOLDER + '/AHI/AHI_VZA.npy'
AHI_VAA_NPY = DATA_FOLDER + '/AHI/AHI_VAA.npy'

ahi_vza_dn = numpy.load(AHI_VZA_NPY, allow_pickle=True)
ahi_vaa_dn = numpy.load(AHI_VAA_NPY, allow_pickle=True)

repeat_factor = 4
ahi_vza = numpy.repeat(numpy.repeat(ahi_vza_dn, repeat_factor, axis=0), repeat_factor, axis=1)
ahi_vaa = numpy.repeat(numpy.repeat(ahi_vaa_dn, repeat_factor, axis=0), repeat_factor, axis=1)

AHI_RESOLUTION = 0.01
ahi_lats = numpy.arange(60. - AHI_RESOLUTION / 2, -60, -AHI_RESOLUTION)
ahi_lons = numpy.arange(85. + AHI_RESOLUTION / 2, 205, AHI_RESOLUTION)


# In[5]:


def read_modis_angle(hdf_file_name):
    para_keys = ['SensorZenith', 'SolarZenith', 'SensorAzimuth', 'SolarAzimuth']
    # VZA SZA VAA SAA
    angle_list = []
    for para_key in para_keys:
        angle_tiff = os.path.join(MXD_GEOTIFF_FOLDER, hdf_file_name[:-4]+'_'+para_key+'.tif')
        angle_ds = xarray.open_rasterio(angle_tiff)
        angle_dn = numpy.array(angle_ds)[0]*1.
        angle_dn[angle_dn==-32767] = numpy.NaN
        angle_v = angle_dn/100
        angle_v = (angle_v+360)%360
        angle_list.append(angle_v)
    return angle_list[0], angle_list[1], angle_list[2], angle_list[3]


def get_raa(aa1, aa2):
    diff = numpy.abs(aa1 - aa2)
    raa = numpy.where(diff < 180, diff, 360 - diff)
    return raa

def is_raa_matched(modis_vza, modis_vaa, modis_saa, ahi_vza, ahi_vaa, ahi_saa):
    vza_condition = numpy.abs(modis_vza - ahi_vza) <= DIFF_VZA_THRESHOLD
    modis_raa = get_raa(modis_vaa, modis_saa)
    ahi_raa = get_raa(ahi_vaa, ahi_saa)
    raa_condition = numpy.abs(modis_raa - ahi_raa) <= DIFF_RAA_THRESHOLD
    return numpy.logical_and(vza_condition, raa_condition)

def is_vza_vaa_matched(modis_vza, modis_vaa, ahi_vza, ahi_vaa):
    vza_condition = numpy.abs(modis_vza - ahi_vza) <= DIFF_VZA_THRESHOLD
    diff_vaa = get_raa(modis_vaa, ahi_vaa)
    vaa_condition = diff_vaa <= DIFF_VAA_THRESHOLD
    return numpy.logical_and(vza_condition, vaa_condition)


# In[8]:


def get_raa_ray_matched(hdf_file):
    global RAA_MATCHED_TXT, RAY_MATCHED_TXT
    
    info_list = hdf_file.split('.')
    time_year = info_list[1][1:5]
    time_doy = info_list[1][-3:]
    time_HHMM = info_list[2]

    doy1_date = datetime.strptime(START_TIME, "%Y-%m-%dT%H:%M:%SZ")
    doyc_date = doy1_date + timedelta(days=(int(time_doy)-1))
    doyc_YYYYmmdd = doyc_date.strftime("%Y%m%d")
    doyc_time = doyc_YYYYmmdd + time_HHMM
    
    modis_vza, modis_sza, modis_vaa, modis_saa = read_modis_angle(hdf_file)
    ahi_sza = modis_sza
    ahi_saa = modis_saa
    
    # RAA-matching
    raa_match_2d = is_raa_matched(modis_vza, modis_vaa, modis_saa, ahi_vza, ahi_vaa, ahi_saa)
    raa_match_2d = raa_match_2d.astype(int)
    raa_indices = numpy.argwhere(raa_match_2d == 1)
    lon_values = ahi_lons[raa_indices[:, 1]]
    lat_values = ahi_lats[raa_indices[:, 0]]
    raa_matched_infos = []
    # lon lat modis_time modis_vza ahi_vza modis_vaa ahi_vaa modis_sza modis_saa
    for lon_val, lat_val in zip(lon_values, lat_values):
        lat_idx = int((60 - lat_val)/AHI_RESOLUTION)
        lon_idx = int((lon_val - 85)/AHI_RESOLUTION)
        modis_time = doyc_time
        modis_vza_v = round(modis_vza[lat_idx][lon_idx], 3)
        ahi_vza_v = round(ahi_vza[lat_idx][lon_idx], 3)
        modis_vaa_v = round(modis_vaa[lat_idx][lon_idx], 3)
        ahi_vaa_v = round(ahi_vaa[lat_idx][lon_idx], 3)
        modis_sza_v = round(modis_sza[lat_idx][lon_idx], 3)
        modis_saa_v = round(modis_saa[lat_idx][lon_idx], 3)
        matched_info = [round(lon_val,3), round(lat_val,3), modis_time, modis_vza_v, ahi_vza_v, modis_vaa_v, ahi_vaa_v, modis_sza_v, modis_saa_v]
    #     print(matched_info)
        raa_matched_infos.append(matched_info)
    # print(len(raa_matched_infos))
    
    # Ray-matching
    ray_match_2d = is_vza_vaa_matched(modis_vza, modis_vaa, ahi_vza, ahi_vaa)
    ray_match_2d = ray_match_2d.astype(int)
    ray_indices = numpy.argwhere(ray_match_2d == 1)
    lon_values = ahi_lons[ray_indices[:, 1]]
    lat_values = ahi_lats[ray_indices[:, 0]]
    # print(len(ray_indices))
    ray_matched_infos = []
    # lon lat modis_time modis_vza ahi_vza modis_vaa ahi_vaa modis_sza modis_saa
    for lon_val, lat_val in zip(lon_values, lat_values):
        lat_idx = int((60 - lat_val)/AHI_RESOLUTION)
        lon_idx = int((lon_val - 85)/AHI_RESOLUTION)
        modis_time = doyc_time
        modis_vza_v = round(modis_vza[lat_idx][lon_idx], 3)
        ahi_vza_v = round(ahi_vza[lat_idx][lon_idx], 3)
        modis_vaa_v = round(modis_vaa[lat_idx][lon_idx], 3)
        ahi_vaa_v = round(ahi_vaa[lat_idx][lon_idx], 3)
        modis_sza_v = round(modis_sza[lat_idx][lon_idx], 3)
        modis_saa_v = round(modis_saa[lat_idx][lon_idx], 3)
        matched_info = [round(lon_val,3), round(lat_val,3), modis_time, modis_vza_v, ahi_vza_v, modis_vaa_v, ahi_vaa_v, modis_sza_v, modis_saa_v]
    #     print(matched_info)
        ray_matched_infos.append(matched_info)
    # print(len(ray_matched_infos))
    
    raa_matched_infos = numpy.array(raa_matched_infos)
    ray_matched_infos = numpy.array(ray_matched_infos)
    
    with open(RAA_MATCHED_TXT, 'a') as file:
        for line in raa_matched_infos:
            line_str = ','.join(line)
            file.write(line_str + '\n')
        
    with open(RAY_MATCHED_TXT, 'a') as file:
        for line in ray_matched_infos:
            line_str = ','.join(line)
            file.write(line_str + '\n')
        
    print(time_year, time_doy, time_HHMM)
    return 1


# In[9]:


count = 0

hdf_filelist = os.listdir(MXD_HDF_FOLDER)
for hdf_file in hdf_filelist:
    try:
        s = get_raa_ray_matched(hdf_file)
        count = count + s
    except Exception as e:
        print(e)

    print(count)


# In[ ]:




