import geopandas
import os


# shapefile转geojson: shapefile路径 geojson路径
def shp_to_geojson(shp_path, geoj_path):
    shp = geopandas.read_file(shp_path)
    shp.to_file(geoj_path, driver="GeoJSON", encoding="utf-8")


# geojson转shapefile: geojson路径 shapefile路径
def geojson_to_shp(geoj_path, shp_path):
    geoj = geopandas.read_file(geoj_path)
    geoj.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")


if __name__ == "__main__":
    # ws = r'D:\Work_PhD\MISR_AHI_WS\220210'
    # geoj = ws + '/AHI_view.json'
    # shp = ws + '/AHI_view.shp'
    # geojson_to_shp(geoj, shp)
    
    ws = r'D:\Work_PhD\MISR_AHI_WS\220630'
    geoj = ws + '/70_80.json'
    shp = ws + '/ROI_shp/70.5_80.shp'
    shp_to_geojson(shp, geoj)
    # shp = ws + '/0_50_roi.shp'
    # geojson_to_shp(geoj, shp)

    # ws_folder = r'D:\Work_PhD\MISR_AHI_WS\220331'
    # geoj_folder = os.path.join(ws_folder, 'ROI')
    # shp_folder = os.path.join(ws_folder, 'ROI_shp')
    # if not os.path.exists(shp_folder):
    #     os.makedirs(shp_folder)
    # geojs = os.listdir(geoj_folder)
    # for geoj_file in geojs:
    #     roi_name = geoj_file.split('.')[0] + '.' + geoj_file.split('.')[1]
    #     geoj_filename = os.path.join(geoj_folder, geoj_file)
    #     shp_filename = os.path.join(shp_folder, roi_name + '.shp')
    #     geojson_to_shp(geoj_filename, shp_filename)