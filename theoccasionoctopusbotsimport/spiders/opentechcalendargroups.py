import json
import scrapy


from theoccasionoctopusbotsimport.base_spider import BaseSpider


class OpenTechCalendarGroups(BaseSpider):
    name = 'opentechcalendargroups'
    download_delay = 5
    start_urls = ['https://opentechcalendar.co.uk/api1/groups.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://opentechcalendar.co.uk/api1/groups.json',
            callback=self.parse
        )

    def parse(self, response):
        json_response = json.loads(response.text)

        for data in json_response.get('data'):

            out = {
                'tag': {
                    'data': {
                        'title': data.get('title'),
                        'description': data.get('description'),
                    },
                    'extra_fields': {
                        'opentechcalendar-group-id': data.get('slug'),
                    },
                }
            }

            for guid, tag_data in self.tags.items():
                if int(tag_data['extra_fields'].get('opentechcalendar-group-id',0)) == int(data.get('slug')):
                    out['tag']['guid'] = guid


            yield out


