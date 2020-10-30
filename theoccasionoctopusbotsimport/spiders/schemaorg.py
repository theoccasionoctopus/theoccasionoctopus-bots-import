import scrapy
import extruct
from w3lib.html import get_base_url
from datetime import datetime

from theoccasionoctopusbotsimport.base_spider import BaseSpider


SCHEMA_ORG_EVENT_TYPES = [
    'Event',
    # TODO Copy from https://schema.org/Event#subtypes
    'EducationEvent'
]

SCHEMA_ORG_CANCELLED_EVENT_STATUS = [
    'https://schema.org/EventCancelled',
    'https://schema.org/EventPostponed',
    'http://schema.org/EventCancelled',
    'http://schema.org/EventPostponed'
]


class SchemaOrg(BaseSpider):
    name = 'schemaorg'
    download_delay = 5

    def start_requests(self):
        yield scrapy.Request(
            url=self.starturl,
            callback=self.parse
        )

    def parse(self, response):
        base_url = get_base_url(response.text, response.url)
        extructData = extruct.extract(response.text, base_url=base_url)

        for itemData in extructData['json-ld']:

            if itemData.get('@context') in ['http://schema.org','https://schema.org'] and itemData.get('@type') in SCHEMA_ORG_EVENT_TYPES:

                start = datetime.strptime(itemData.get('startDate'), '%Y-%m-%dT%H:%M:%S%z')
                end = datetime.strptime(itemData.get('endDate'), '%Y-%m-%dT%H:%M:%S%z')

                cancelled = itemData.get('eventStatus') in SCHEMA_ORG_CANCELLED_EVENT_STATUS

                out = {
                    'event': {
                        'find_by_url': itemData.get('url'),
                        'data': {
                            'title': itemData.get('name'),
                            'url': itemData.get('url'),
                            'description': itemData.get('description'),
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
