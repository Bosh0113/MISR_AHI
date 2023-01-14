import os
import numpy

ws = r'C:\Work\AHI_MISR\20230114'
ray_matched_record_npy = os.path.join(ws, 'AHI_MISR_Ray-matched.npy')
ray_matched_record_npy_50km = os.path.join(ws, 'AHI_MISR_Ray-matched_50km.npy')

ROI_DISTANCE = 0.5
if __name__ == "__main__":
    roi_lats = numpy.arange(60. - ROI_DISTANCE / 2, -60, -ROI_DISTANCE)
    roi_lons = numpy.arange(85. + ROI_DISTANCE / 2, 205, ROI_DISTANCE)
    ray_matched_record = numpy.load(ray_matched_record_npy, allow_pickle=True)
    # print(len(ray_matched_record))
    ray_matched_record_50km = []
    for ray_matched_record_item in ray_matched_record:
        loc = ray_matched_record_item['location']
        loc_lon = round(loc[0], 2)
        loc_lat = round(loc[1], 2)
        if loc_lon in roi_lons and loc_lat in roi_lats:
            ray_matched_record_50km.append(ray_matched_record_item)
    # print(len(ray_matched_record_50km))
    numpy.save(ray_matched_record_npy_50km, numpy.array(ray_matched_record_50km))