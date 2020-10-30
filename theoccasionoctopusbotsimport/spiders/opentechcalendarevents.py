import json
import scrapy
from email.utils import parsedate_to_datetime

from theoccasionoctopusbotsimport.base_spider import BaseSpider


class OpenTechCalendarEvents(BaseSpider):
    name = 'opentechcalendarevents'
    download_delay = 5
    start_urls = ['https://opentechcalendar.co.uk/api1/events.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://opentechcalendar.co.uk/api1/events.json',
            callback=self.parse_list
        )

    def parse_list(self, response):
        json_response = json.loads(response.text)

        for data in json_response.get('data'):
            yield scrapy.Request(
                url='https://opentechcalendar.co.uk/api1/event/'+str(data['slug']) +'/info.json',
                callback=self.parse_event
            )

    def parse_event(self, response):
        json_response = json.loads(response.text)
        data = json_response['data'][0]

        start = parsedate_to_datetime(data.get('start').get('rfc2882utc'))
        end = parsedate_to_datetime(data.get('end').get('rfc2882utc'))

        out = {
            'event': {
                'find_by_url': data.get('siteurl'),
                'data': {
                    'title': data.get('summaryDisplay'),
                    'url': data.get('siteurl'),
                    'description': data.get('description'),
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
                    'deleted': data.get('deleted'),
                    'cancelled': data.get('cancelled'),
                },
                'add_tags': [],
            }
        }

        group_otc_slugs= [ int(d['slug']) for d in data.get('groups',[])]
        for guid, tag_data in self.tags.items():
            # Groups
            if int(tag_data['extra_fields'].get('opentechcalendar-group-id', 0)) in group_otc_slugs:
                out['event']['add_tags'].append(guid)
            # Country
            if tag_data['extra_fields'].get('opentechcalendar-country-id', None) and tag_data['title'] == data.get('country').get('title'):
                out['event']['add_tags'].append(guid)
        yield out

