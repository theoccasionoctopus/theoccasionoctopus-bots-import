import scrapy
from datetime import datetime
import json

from theoccasionoctopusbotsimport.base_spider import BaseSpider


class Mobillizon(BaseSpider):
    name = 'mobillizon'
    download_delay = 1

    def start_requests(self):
        yield scrapy.Request(
            url='https://' + self.starthost + '/.well-known/webfinger?resource=acct%3Arelay%40'+ self.starthost,
            callback=self.parse_webfinger
        )

    def parse_webfinger(self, response):
        json_response = json.loads(response.text)
        for link in json_response.get('links'):
            if link.get('type') == 'application/activity+json' and link.get('rel') == 'self':
                yield scrapy.Request(
                    url=link.get('href'),
                    callback=self.parse_profile
                )

    def parse_profile(self, response):
        json_response = json.loads(response.text)
        if json_response.get('outbox'):
            yield scrapy.Request(
                url=json_response.get('outbox') + '?page=1',
                callback=self.parse_outbox,
                meta ={'page':1, 'url':json_response.get('outbox')}
            )

    def parse_outbox(self, response):
        json_response = json.loads(response.text)
        if json_response.get('orderedItems',[]):
            for orderedItem in json_response.get('orderedItems',[]):
                if orderedItem.get('type') == 'Create' and orderedItem.get('object',{}).get('type') == 'Event':
                    data = orderedItem.get('object',{})
                    start = datetime.strptime(data.get('startTime'), '%Y-%m-%dT%H:%M:%S%z')
                    end = datetime.strptime(data.get('endTime'), '%Y-%m-%dT%H:%M:%S%z')
                    # TODO can we work out anything about timezone, country?
                    # eg https://mobilizon.fr/events/7f53ed99-e8ee-4c7b-81ef-0d9de1e0aed0 has a location
                    out = {
                        'event': {
                            'find_by_url': data.get('id'),
                            'data': {
                                'title': data.get('name'),
                                'url': data.get('id'),
                                'description': data.get('content'),
                                'start_year_utc': start.year,
                                'start_month_utc': start.month,
                                'start_day_utc': start.day,
                                'start_hour_utc': start.hour,
                                'start_minute_utc': start.minute,
                                'end_year_utc': end.year,
                                'end_month_utc': end.month,
                                'end_day_utc': end.day,
                                'end_hour_utc': end.hour,
                                'end_minute_utc': end.minute,
                                'deleted': False,
                                'cancelled': (data.get('ical:status') != 'CONFIRMED'),
                            },
                            'add_tags': [],
                        }
                    }
                    yield out
                elif orderedItem.get('object',{}).get('type') == 'Event':
                    # TODO Should do something with these
                    print(orderedItem)
            # go to the next page
            yield scrapy.Request(
                url=response.meta.get('url') + '?page='+ str(response.meta.get('page') +1) ,
                callback=self.parse_outbox,
                meta ={'page': response.meta.get('page') + 1, 'url': response.meta.get('url')}
            )
