import geopandas


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
    
    ws = r'D:\Work_PhD\MISR_AHI_WS\220213\update6'
    geoj = ws + '/0.0/0_60_ll.json'
    # shp = ws + '/0.0/0_60_ll.shp'
    # shp_to_geojson(shp, geoj)
    shp = ws + '/0.0/0_60_roi.shp'
    geojson_to_shp(geoj, shp)