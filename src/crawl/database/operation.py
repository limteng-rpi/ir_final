import traceback
from pymongo import MongoClient, DESCENDING
import src.crawl.news.news.settings as settings
from datetime import datetime, timedelta


def insert_document(item, host, port):
    try:
        with MongoClient(host=host, port=port) as client:
            data_col = client['data']['news']
            waitlist_col = client['data']['waitlist']
            # Check if the document exists
            doc = data_col.find_one({'url': item['url']})
            if doc is None:
                data_col.insert_one(item)
                waitlist_col.insert_one({'url': item['url']})
                return True
            else:
                # print('doc exists')
                return False
    except Exception:
        traceback.print_exc()
        return False


def get_top_entities(top_num=50):
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        count_col = client['analyze']['count']
        results = count_col.find().sort('timestamp', DESCENDING)
        last_result = next(results, None)
        if last_result:
            mention_count = last_result['mention_count'][:top_num]
            mention_count_ = []
            # process mention count
            for mention, counts in mention_count:
                total = sum([c for t, c in counts])
                type_list = [t for t, c in counts]
                mention_count_.append([mention, total, type_list])
            return {
                'timestamp': last_result['timestamp'].strftime('%b %d %Y %H:%M:%S'),
                'mentions': mention_count_
            }
        else:
            return {
                'timestamp': '',
                'mentions': []
            }


def get_trend_entities(top_num=50):

    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        trend_col = client['analyze']['trend_30']
        results = trend_col.find().sort('timestamp', DESCENDING)
        last_result = next(results, None)
        if last_result:
            mentions = last_result['mentions'][:top_num]
            mentions = [[m, p, sum(cs), cs] for m, p, cs in mentions]
            day_num = len(mentions[0][-1])
            dates = list(reversed([last_result['timestamp'] + timedelta(days=-i) for i in
                      range(day_num)]))
            dates = [datetime.strftime(d, '%m/%d') for d in dates]

            return {
                'timestamp': last_result['timestamp'].strftime(
                    '%b %d %Y %H:%M:%S'),
                'mentions': mentions,
                'dates': dates
            }
        else:
            return {
                'timestamp': '',
                'mentions': [],
                'dates': []
            }


def get_localization(top_num=5000):
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        local_col = client['analyze']['localization']
        results = local_col.find().sort('timestamp', DESCENDING)
        last_result = next(results, None)
        if last_result:
            mentions = [
                {
                    'type': 'Feature',
                    'properties': {
                        'name': m[0],
                        'count': m[1],
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [m[3], m[2]]
                    }
                }
                for m in last_result['mentions']
            ]
            return {
                'timestamp': last_result['timestamp'].strftime(
                    '%b %d %Y %H:%M:%S'),
                'data': {
                    'type': 'FeatureCollection',
                    'features': mentions
                }
                # 'mentions': mentions,
            }
        else:
            return {
                'timestamp': '',
                'data': {}
            }