import json
import os

roi_folder = r'D:\Work_PhD\MISR_AHI_WS\220309\ROI'


def get_extent(polygon_points):
    ullat = polygon_points[0][1]
    ullon = polygon_points[0][0]
    lrlat = polygon_points[0][1]
    lrlon = polygon_points[0][0]

    for pt in polygon_points:
        lat = pt[1]
        lon = pt[0]
        if ullat < lat:
            ullat = lat
        if lrlat > lat:
            lrlat = lat
        # all polygon in eastern Earth
        if ullon > lon:
            ullon = lon
        if lrlon < lon:
            lrlon = lon
    # upper left corner, lower right corner (ullat, ullon, lrlat, lrlon)
    return [ullat, ullon, lrlat, lrlon]


if __name__ == "__main__":
        
    roi_extent_record = {}

    # angles of MISR cameras
    MISR_vza = [0.0, 26.1, 45.6, 60.0, 70.5]

    for vza in MISR_vza:
        # read roi geoinfo
        folder = roi_folder + '/' + str(vza)
        file_list = os.listdir(folder)
        for file in file_list:
            if file.split('.')[1] == 'json':
                filename = folder + '/' + file
                with open(filename, 'r', encoding='utf-8') as f:
                    geoobj = json.load(f)
                    polygon_pts = geoobj['features'][0]['geometry']['coordinates'][0]
                    roi_extent = get_extent(polygon_pts)
                    lc_type = file.split('.')[0]
                    roi_name = str(vza) + '_' + lc_type
                    roi_extent_record[roi_name] = roi_extent
    
    print(roi_extent_record)
