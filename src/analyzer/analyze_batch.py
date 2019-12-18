import math
import os
import torch
import tqdm
import src.crawl.news.news.settings as settings
from pymongo import MongoClient
from collections import Counter, defaultdict
from datetime import datetime, timedelta


def count_entity_all_time(top_num=1000):
    mention_count = defaultdict(Counter)
    print('Counting entities')
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        result_col = client['result']['ner']
        count_col = client['analyze']['count']
        for doc in result_col.find():
            mentions = doc['mentions']
            for mention, tag in mentions:
                mention_count[mention][tag] += 1
        mention_count = [(k, v) for k, v in mention_count.items()]
        mention_count.sort(key=lambda x: sum([i for _, i in x[1].items()]),
                           reverse=True)
        mention_count = mention_count[:top_num]
        mention_count = [[k, [[i, j] for i, j in v.items()]]
                         for k, v in mention_count]
        print(mention_count)

        timestamp = datetime.utcnow()
        count_col.insert_one({
            'timestamp': timestamp,
            'mention_count': mention_count
        })
        count_col.create_index('timestamp')


def count_entity_one_month(top_num=1000):
    # Create time chunks
    start_datetime = datetime.utcnow() + timedelta(days=-30)
    mention_count = defaultdict(Counter)
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        data_col = client['data']['news']
        result_col = client['result']['ner']
        count_col = client['analyze']['count_30']
        for doc in result_col.find():
            url = doc['url']
            timestamp = data_col.find_one({'url': url})['timestamp']
            if timestamp > start_datetime:
                mentions = doc['mentions']
                for mention, tag in mentions:
                    mention_count[mention][tag] += 1
        mention_count = [(k, v) for k, v in mention_count.items()]
        mention_count.sort(key=lambda x: sum([i for _, i in x[1].items()]),
                           reverse=True)
        mention_count = mention_count[:top_num]
        mention_count = [[k, [[i, j] for i, j in v.items()]]
                         for k, v in mention_count]
        print(mention_count)

        timestamp = datetime.utcnow()
        count_col.insert_one({
            'timestamp': timestamp,
            'mention_count': mention_count
        })
        count_col.create_index('timestamp')

def find_chunk(chunks, timestamp):
    for i in range(len(chunks) - 1):
        if chunks[i] < timestamp <= chunks[i + 1]:
            return i
    return - 1


def trend_entity_one_month(top_num=1000, days=30):
    # Create time chunks
    end_datetime = datetime.utcnow()
    start_datetime = end_datetime + timedelta(days=-days)
    chunks = [start_datetime + timedelta(days=i) for i in range(days + 1)]

    mention_count = [Counter() for _ in range(days)]
    history_mention_count = Counter()
    recent_mention_count = Counter()
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        data_col = client['data']['news']
        result_col = client['result']['ner']
        count_col = client['analyze']['trend_30']
        print('Counting')
        for doc in result_col.find():
            url = doc['url']
            mentions = [m for m, _ in doc['mentions']]
            history_mention_count.update(mentions)

            timestamp = data_col.find_one({'url': url})['timestamp']
            if start_datetime < timestamp <= end_datetime:
                recent_mention_count.update(mentions)
                chunk = find_chunk(chunks, timestamp)
                if chunk > -1:
                    mention_count[chunk].update(mentions)
                else:
                    print('chunk error')
        # Find trending mentions
        print('Finding trending mentions')
        recent_total = sum([v for _, v in recent_mention_count.items()])
        # relative_pop = [(m, c/(1 + math.log(history_mention_count[m])))
        relative_pop = [(m, c/history_mention_count[m] * min(1000, history_mention_count[m]) ** .6)
                        for m, c in recent_mention_count.items()]
        relative_pop.sort(key=lambda x: x[1], reverse=True)
        relative_pop = relative_pop[:top_num]

        trending_entities = []
        for m, p in relative_pop:
            time_count = [mention_count[i][m] for i in range(days)]
            trending_entities.append([m, p, time_count])
        print(trending_entities)

        timestamp = datetime.utcnow()
        count_col.insert_one({
            'timestamp': timestamp,
            'mentions': trending_entities
        })
        count_col.create_index('timestamp')


def recent_localization(top_num=1000, days=30):
    # Create time chunks
    start_datetime = datetime.utcnow() + timedelta(days=-days)
    mention_count = Counter()
    with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
        data_col = client['data']['news']
        result_col = client['result']['ner']
        count_col = client['analyze']['localization']
        for doc in result_col.find():
            url = doc['url']
            timestamp = data_col.find_one({'url': url})['timestamp']
            if timestamp > start_datetime:
                mentions = doc['mentions']
                for mention, tag in mentions:
                    mention_count[mention] += 1
        mention_count = [(k, v) for k, v in mention_count.items()]
        mention_count.sort(key=lambda x: x[1], reverse=True)
        mention_count = mention_count[:top_num]

        # get location
        geo_col = client['geonames']['all']
        mention_count_ = []
        for m, c in mention_count:
            doc = geo_col.find_one({'alternatives': m.lower()})
            if doc:
                latitude, longitude = doc['coordinates']
                mention_count_.append([m, c, latitude, longitude])
        print(mention_count_)

        timestamp = datetime.utcnow()
        count_col.insert_one({
            'timestamp': timestamp,
            'mentions': mention_count_
        })
        count_col.create_index('timestamp')

count_entity_all_time(100)
count_entity_one_month(100)
trend_entity_one_month(100, 14)
recent_localization(5000, 30)