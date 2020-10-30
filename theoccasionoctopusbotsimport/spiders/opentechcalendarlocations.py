import json
import scrapy

from theoccasionoctopusbotsimport.base_spider import BaseSpider


class OpenTechCalendarLocations(BaseSpider):
    name = 'opentechcalendarlocations'
    download_delay = 5
    start_urls = ['https://opentechcalendar.co.uk/api1/countries.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://opentechcalendar.co.uk/api1/countries.json',
            callback=self.parse_country
        )

    def parse_country(self, response):
        json_response = json.loads(response.text)

        for data in json_response.get('data'):

            # First Create a Tag for the actual country
            out = {
                'tag': {
                    'data': {
                        'title': data.get('title'),
                    },
                    'extra_fields': {
                        'opentechcalendar-country-id': data.get('twoCharCode'),
                    },
                }
            }

            for guid, tag_data in self.tags.items():
                if tag_data['extra_fields'].get('opentechcalendar-country-id', 0) == data.get('twoCharCode'):
                    out['tag']['guid'] = guid

            yield out

            # Next, parse areas
            #yield scrapy.Request(
            #    url='https://opentechcalendar.co.uk/api1/country/' + data.get('twoCharCode') + '/areas.json',
            #    callback=self.parse_root_area
            #)
            # There is a problem here - the data we get back does not show deleted areas. Leave for now.

