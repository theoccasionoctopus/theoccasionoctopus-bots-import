import scrapy
import extruct
from w3lib.html import get_base_url
from datetime import datetime

from theoccasionoctopusbotsimport.base_spider import BaseSpider


class UniStAndrews(BaseSpider):
    name = 'unistandrews'
    download_delay = 5

    def start_requests(self):
        yield scrapy.Request(
            url='https://events.st-andrews.ac.uk/event-location/online-via-ms-teams/',
            callback=self.parse
        )

    def parse(self, response):
        base_url = get_base_url(response.text, response.url)
        extructData = extruct.extract(response.text, base_url=base_url, syntaxes=['microdata'])

        for itemData in extructData['microdata']:
            if itemData.get('type') in ['http://schema.org/Event']:

                start = datetime.strptime(itemData.get('properties').get('startDate'), '%Y-%m-%dT%H:%M')
                end = datetime.strptime(itemData.get('properties').get('endDate'), '%Y-%m-%dT%H:%M')

                cancelled = itemData.get('properties').get('eventStatus') != 'on-schedule'

                out = {
                    'event': {
                        'find_by_url': itemData.get('properties').get('url'),
                        'data': {
                            'title': itemData.get('properties').get('name')[0],
                            'url': itemData.get('properties').get('url'),
                            'description': itemData.get('properties').get('description'),
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
                            'cancelled': cancelled,
                        },
                        'add_tags': [],
                    }
                }

                yield out
