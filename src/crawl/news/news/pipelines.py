# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from datetime import datetime
from src.crawl.database.operation import insert_document

TIME_FORMAT = '%b %d %Y %H:%M:%S TZ %z'

def get_timezone(time_str):
    return time_str.split(' ')[-2]


class NewsPipeline(object):
    def __init__(self, host, port, stats):
        self.host = host
        self.port = port
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings['DB_HOST']
        port = crawler.settings['DB_PORT']
        stats = crawler.stats
        return cls(host=host, port=port, stats=stats)

    def process_item(self, item, spider):
        self.stats.inc_value('processed_item')

        body = item.get('body', None)
        title = item.get('title', '').strip()
        timestamp = item.get('timestamp', None)
        source = item.get('source', None)
        url = item.get('url', None)
        if title and body and timestamp and source and url:
            # Remove queries
            url = url.split('?')[0]
            # Process text
            body_clean = BeautifulSoup(body, 'lxml').text
            sents = sent_tokenize(body_clean)
            sents = [sent.strip() for sent in sents]
            time_format = TIME_FORMAT.replace('TZ', get_timezone(timestamp))
            timestamp = datetime.strptime(timestamp, time_format)
            rst = insert_document({
                'title': title,
                'sentences': sents,
                'body': body,
                'timestamp': timestamp,
                'source': source,
                'url': url
            }, host=self.host, port=self.port)
            if rst:
                self.stats.inc_value('crawled_doc')
                if self.stats.get_value('crawled_doc') % 100 == 0:
                    print('Processed {} items, crawled {} documents'.format(
                        self.stats.get_value('processed_item'),
                        self.stats.get_value('crawled_doc')))
        return item
