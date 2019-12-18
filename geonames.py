from pymongo import MongoClient

def load(path, port):
    with open(path, 'r', encoding='utf-8') as r, \
        MongoClient(host='127.0.0.1', port=port) as client:
        col = client['geonames']['all']
        bulk_op = col.initialize_unordered_bulk_op()

        for i, line in enumerate(r):
            segs = line.rstrip('\n').split('\t')
            id, name, lon, lat, alt, latin = segs[0], segs[1], segs[4], segs[5], segs[3], segs[2]
            bulk_op.insert({
                'geo_id': id, 'name': name,
                'longitude': lon, 'latitude': lat,
                'alternatives': alt.split(','), 'latin': latin
            })

            if i % 100000 == 0:
                bulk_op.execute()
                bulk_op = col.initialize_unordered_bulk_op()
        bulk_op.execute()