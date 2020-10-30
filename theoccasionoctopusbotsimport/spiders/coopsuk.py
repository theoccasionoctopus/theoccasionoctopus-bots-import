import scrapy
from datetime import datetime

from theoccasionoctopusbotsimport.base_spider import BaseSpider


class CoopsUK(BaseSpider):
    name = 'coopsuk'
    download_delay = 30
    start_urls = ['https://www.uk.coop/all-events']

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.uk.coop/all-events',
            callback=self.parse_list
        )

    def parse_list(self, response):
        for link in response.xpath("//article[contains(@class, 'node')]"):
            url = 'https://www.uk.coop' + link.xpath('a').xpath('@href').extract()[0]
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )
        next_page = response.xpath("//li[contains(@class, 'pager-next')]").xpath('a').xpath('@href').extract()
        if next_page:
            yield scrapy.Request(
                url='https://www.uk.coop' + next_page[0],
                callback=self.parse_list
            )

    def parse(self, response):

        if response.css("div.event-meta").css("span.date-display-start"):

            start_string = response.css("div.event-meta").css("span.date-display-start").xpath('@content').extract()[0]
            start = datetime.strptime(start_string, '%Y-%m-%dT%H:%M:%S%z')

            end_string = response.css("div.event-meta").css("span.date-display-end").xpath('@content').extract()[0]
            end = datetime.strptime(end_string, '%Y-%m-%dT%H:%M:%S%z')

        else:

            start_string = response.css("div.event-meta").css("span.date-display-single").xpath('@content').extract()[0]
            start = datetime.strptime(start_string, '%Y-%m-%dT%H:%M:%S%z')
            end = datetime.strptime(start_string, '%Y-%m-%dT%H:%M:%S%z')

        out = {
            'event': {
                'find_by_url': response.request.url,
                'data': {
                    'title': response.xpath("//h1").xpath('string(.)').extract()[0].strip(),
                    'url': response.request.url,
                    'description': response.xpath("//div[contains(@class, 'body')]").xpath('string(.)').extract()[0].strip(),
                    'start_year_timezone': start.year,
                    'start_month_timezone': start.month,
                    'start_day_timezone': start.day,
                    'start_hour_timezone': start.hour,
                    'start_minute_timezone': start.minute,
                    'end_year_timezone': end.year,
                    'end_month_timezone': end.month,
                    'end_day_timezone': end.day,
                    'end_hour_timezone': end.hour,
                    'end_minute_timezone': end.minute,
                    'deleted': False,
                    'cancelled': False,
                    },
                'add_tags': []
            }
        }
        for tag_id, tag in self.tags.items():
            if tag['title'] in out['event']['data']['title']:
                out['event']['add_tags'].append(tag_id)

        yield out
