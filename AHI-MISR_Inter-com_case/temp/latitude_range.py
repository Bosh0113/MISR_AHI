import os

WORK_SPACE = os.getcwd()


if __name__ == "__main__":

    # folder_l1_list = ['0', '26', '45', '60', '70']
    folder_l1_list = ['26', '45']
    folder_l2_list = ['0', '1']
    
    for folder_l1 in folder_l1_list:
        south_low_latitude = -60
        south_high_latitude = 0
        north_low_latitude = 60
        north_high_latitude = 0
        folder_l1_path = os.path.join(WORK_SPACE, folder_l1)
        for folder_l2 in folder_l2_list:
            # each png
            misr_SR_band3_item_list = []
            ahi_SR_band3_item_list = []
            misr_SR_band4_item_list = []
            ahi_SR_band4_item_list = []
            folder_l2_path = os.path.join(folder_l1_path, folder_l2)
            roi_folder_list = os.listdir(folder_l2_path)
            for roi_folder in roi_folder_list:
                roi_infos = roi_folder.split('_')
                roi_lat = float(roi_infos[2])
                
                if roi_lat < 0:
                    # south
                    if roi_lat < south_high_latitude:
                        south_high_latitude = roi_lat
                    if roi_lat > south_low_latitude:
                        south_low_latitude = roi_lat
                else:
                    # north
                    if roi_lat < north_low_latitude:
                        north_low_latitude = roi_lat
                    if roi_lat > north_high_latitude:
                        north_high_latitude = roi_lat
        print(folder_l1)
        print('N:', str(north_high_latitude) + '-' + str(north_low_latitude))
        print('S:', str(south_high_latitude) + '-' + str(south_low_latitude))