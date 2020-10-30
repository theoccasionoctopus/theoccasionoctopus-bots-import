import scrapy
import requests

class BaseSpider(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.SERVER_INSTANCE_URL = crawler.settings['SERVER_INSTANCE_URL']
        spider.SERVER_ACCESS_TOKEN = crawler.settings['SERVER_ACCESS_TOKEN']
        spider.SERVER_ACCOUNT_ID = crawler.settings['SERVER_ACCOUNT_ID']

        r = requests.get(
            spider.SERVER_INSTANCE_URL + '/api/v1/account/' + spider.SERVER_ACCOUNT_ID + '/tags.json',
            headers={'Authorization': 'Bearer ' + spider.SERVER_ACCESS_TOKEN}
        )
        r.raise_for_status()
        spider.tags = {}
        for tag in r.json()['tags']:
            spider.tags[tag['id']] = tag

        return spider

