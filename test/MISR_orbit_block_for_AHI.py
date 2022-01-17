import pymongo
import re

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient["MISR_Blocks"]
mycol = mydb["blocks"]
ahicol = mydb['blocks4AHI']


def get_covered_blocks():
    clickQuery = {
        "geometry": {
            "$geoIntersects": {
                "$geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[85, 60], [150, 60], [150, -60], [85, -60], [85, 60]]], 
                        [[[150, 60], [180, 60], [180, -60], [150, -60], [150, 60]]], 
                        [[[-180, 60], [-155, 60], [-155, -60], [-180, -60], [-180, 60]]]
                        ]
                }
            }
        }
    }
    geoJsons = mycol.find(clickQuery)
    return geoJsons


if __name__ == "__main__":
    workspace_path = r'D:\Work_PhD\MISR_AHI_WS\220117'
    covered_blocks = get_covered_blocks()
    # ahicol.insert_many(covered_blocks)
    covered_path = []
    for c in covered_blocks:
        name = c['properties']['name']
        matchObj = re.search(r'MISR Path (\d+) Block', name)
        path = matchObj.group(1)
        if path not in covered_path:
            covered_path.append(path)
    print(covered_path)
