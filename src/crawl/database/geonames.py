from pymongo import MongoClient, DESCENDING, InsertOne
import src.crawl.news.news.settings as settings

def import_geonames(path):
    with open(path, 'r', encoding='utf-8') as r, \
            MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        geo_col = client['geonames']['all']
        # bulk = geo_col.initialize_unordered_bulk_op()
        bulk = []
        for i, line in enumerate(r):
            segs = line.rstrip().split('\t')
            name = segs[1]
            gid = segs[0]
            alternative_names = [n.strip() for n in segs[3].split(',') if n.strip()]
            latitude = float(segs[4])
            longitude = float(segs[5])
            bulk.append(InsertOne({
                'name': name,
                'gid': gid,
                'alternatives': [n.lower() for n in alternative_names],
                'coordinates': [latitude, longitude]
            }))
            if i and i % 10000 == 0:
                print(i)
                geo_col.bulk_write(bulk)
                bulk = []
        geo_col.bulk_write(bulk)

        geo_col.create_index('name')
        geo_col.create_index('alternatives')
        geo_col.create_index('gid')

import_geonames('/shared/nas/data/m1/yinglin8/projects/ir_final/geoname_all_countries.txt')
