import kml2geojson


# 存储block到MongoDB
if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220111'
    kml_file = 'misr_paths_test'
    kml_path = ws + '/' + kml_file + '.kml'
    # kml2geojson中<LinearRing>必须在<Polygon>才可被识别
    geojson = kml2geojson.convert(kml_path)
    # print(type(geojson[0]))
    # geojson_path = ws + '/' + kml_file + '.txt'
    # f = open(geojson_path, 'w')
    # f.write(str(geojson[0]))
    # f.close()
    geojson_dict = geojson[0]
    features = geojson_dict['features']
    print(features[0])


