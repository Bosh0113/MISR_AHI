#!/usr/bin/env python
# coding: utf-8

# ## Build parameter files to reproject MOD03|MYD03 by HEG command

# https://hdfeos.org/software/heg.php
# 
# HEG Tool HEG COMMAND LINE INTERFACE (CLI):
# 1. environment variables
# MRTDATADIR=/home/bob/HEG/data
# PGSHOME=/home/bob/HEG/TOOLKIT_MTD
# 2. command example
# ./subset_stitch_swath -p HegSwathStitch.prm_beichen

# In[ ]:


import os


# In[ ]:


BASE_PATH = '/disk1/workspace/20231225'
# MODIS_TYPE = 'MOD'
MODIS_TYPE = 'MYD'

DATA_PATH = '/disk1/Data'
MOD03_HDF_FOLDER = os.path.join(DATA_PATH, MODIS_TYPE+'03_AHI_HDF_2018')
MOD03_GEOTIFF_FOLDER = os.path.join(DATA_PATH, MODIS_TYPE+'03_AHI_GeoTiff_2018')
HEGCLI_CMD_FOLDER = os.path.join(BASE_PATH, MODIS_TYPE+'03_cmd')


# In[ ]:


cmd_file_template = '''
NUM_RUNS = 1

BEGIN
NUMBER_INPUTFILES = [input_hdf_file_number]
INPUT_FILENAMES = [input_hdf_files]
OBJECT_NAME = MODIS_Swath_Type_GEO|
FIELD_NAME = [parameter_key]|
BAND_NUMBER = 1
SPATIAL_SUBSET_UL_CORNER = ( 60.0 85.0 )
SPATIAL_SUBSET_LR_CORNER = ( -60.0 205.0 )
OUTPUT_OBJECT_NAME = MODIS_Swath_Type_GEO|
OUTGRID_X_PIXELSIZE = 0.01
OUTGRID_Y_PIXELSIZE = 0.01
RESAMPLING_TYPE = NN
OUTPUT_PROJECTION_TYPE = GEO
ELLIPSOID_CODE = WGS84
OUTPUT_PROJECTION_PARAMETERS = ( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0  )
OUTPUT_FILENAME = [output_tif_file]
SAVE_STITCHED_FILE = NO
OUTPUT_STITCHED_FILENAME = [output_hdf_file]
OUTPUT_TYPE = GEO
END

'''

cmd_template = '/home/beichen/software/opt/HEG_tool/bin/subset_stitch_swath -p [parameter_file];'


# In[ ]:


parameter_keys = ['SensorAzimuth', 'SensorZenith', 'SolarAzimuth', 'SolarZenith']

# cmd_list_str = ''
mod03_geo_folder = MOD03_GEOTIFF_FOLDER
if not os.path.exists(mod03_geo_folder):
    os.makedirs(mod03_geo_folder)
year_cmd_folder = HEGCLI_CMD_FOLDER
if not os.path.exists(year_cmd_folder):
    os.makedirs(year_cmd_folder)
    
mod03_filelist = os.listdir(MOD03_HDF_FOLDER)

for day_hdf_file in mod03_filelist:
    mod03_hdf_filename = os.path.join(MOD03_HDF_FOLDER, day_hdf_file)
    for parameter_key in parameter_keys:
    
        output_tif_filename = os.path.join(mod03_geo_folder, day_hdf_file[:-4] + '_' + parameter_key + '.tif')
        output_hdf_filename = os.path.join(mod03_geo_folder, day_hdf_file[:-4] + '_' + parameter_key + '.hdf')
        cmd_filename = os.path.join(year_cmd_folder, day_hdf_file[:-4] + '_' + parameter_key + '.prm_beichen')

        cmd_file_str = cmd_file_template.replace('[parameter_key]', parameter_key)
        cmd_file_str = cmd_file_str.replace('[input_hdf_file_number]', '1')
        cmd_file_str = cmd_file_str.replace('[input_hdf_files]', mod03_hdf_filename)
        cmd_file_str = cmd_file_str.replace('[output_tif_file]', output_tif_filename)
        cmd_file_str = cmd_file_str.replace('[output_hdf_file]', output_hdf_filename)

        with open(cmd_filename, 'w') as f:
            f.write(cmd_file_str)
            print(cmd_filename)

        cmd_c = cmd_template.replace('[parameter_file]', cmd_filename)
        os.system(cmd_c)
        # cmd_list_str = cmd_list_str + cmd_c

# with open(os.path.join(BASE_PATH, MODIS_TYPE+'03_HEGCLI_cmd.sh'), 'w') as f:
#     f.write(cmd_list_str)
#     print('over!')


# # Just run .sh file can be works!
