import kml2geojson
import pymongo


myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient["MISR_Blocks"]
mycol = mydb["blocks"]

# 存储block到MongoDB
if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220111'
    kml_file = 'misr_paths'
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

    mycol.insert_many(features)

    # creat index
    # db.blocks.insert(db.blocks_o.findOne())
    # db.blocks.createIndex({"features.geometry":"2dsphere"})
    # db.blocks.remove({})
    # db.blocks_o.find().forEach(function(x){db.blocks.insert(x);})
