from pymongo import MongoClient
import src.crawl.news.news.settings as settings

with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
    data_col = client['data']['news']
    waitlist_col = client['data']['waitlist']

    for doc in data_col.find():
        if waitlist_col.find_one({'url': doc['url']}) is None:
            waitlist_col.insert_one({'url': doc['url']})
