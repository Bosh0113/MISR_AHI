import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient["MISR_Blocks"]
mycol = mydb["blocks"]


def queryBlock(lon, lat):
    clickQuery = {
        "geometry": {
            "$geoIntersects": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        }
    }
    geoJsons = mycol.find(clickQuery)
    return geoJsons


if __name__ == "__main__":
    lon = 140.0981452753069
    lat = 35.62975746548003
    jsonObjs = queryBlock(lon, lat)
    print('location: (', lon, ', ', lat, ')')
    for json in jsonObjs:
        blockName = json['properties']['name']
        print(blockName)