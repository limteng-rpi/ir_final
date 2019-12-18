import os
import time
from src.crawl.util import load_seed_urls
from src.crawl.news.news.items import NewsItem
from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, MapCompose

TITLE_PATTERN = '//h1[@class="story-body__h1"][1]/text()'
BODY_PATTERN = ''

class BBCSpider(CrawlSpider):
    name = "bbc"
    allowed_domains = ['bbc.com', 'bbc.co.uk']
    start_urls = load_seed_urls(name)

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//a[starts-with(@href, "/news/") and contains(@href, "-")]',
            deny=('video_and_audio',)),
            callback='parse_item', follow=True),
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            'news.pipelines.NewsPipeline': 200
        }
    }

    def parse_item(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.default_output_processor = TakeFirst()
        loader.add_xpath('title', '//h1[@class="story-body__h1"][1]/text()')
        loader.add_xpath('body', '//div[contains(@class, "story-body__inner")]'
                                 '//p[not(contains(@class, "story-body__introduction"))]',
                         MapCompose(lambda x: x.strip()), Join())
        loader.add_xpath('timestamp', '//div[contains(@class, "story-body")]'
                                      '//div[contains(@class, "date")]/@data-seconds',
                         MapCompose(
                             lambda x: time.strftime('%b %d %Y %H:%M:%S %Z %z',
                                                     time.gmtime(int(x)))))
        loader.add_xpath('category', '//div[contains(@class, "story-body")]//'
                                     'a[@data-entityid="section-label"]/@href')
        loader.add_value('url', response.url)
        loader.add_value('source', 'bbc')
        return loader.load_item()