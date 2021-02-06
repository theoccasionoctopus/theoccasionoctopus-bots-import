import json
import scrapy
import xml.etree.ElementTree as ET
import re
import datetime

from theoccasionoctopusbotsimport.base_spider import BaseSpider

#
# TODO:
# This should not find existing events by URL but find by Event ID
# In 2021 I saw cases where the slug & URL changed but event ID stayed the same
#
class FOSDEM2021(BaseSpider):
    name = 'fosdem2021'
    download_delay = 5
    start_urls = ['https://fosdem.org/2021/schedule/xml']

    def start_requests(self):
        yield scrapy.Request(
            url='https://fosdem.org/2021/schedule/xml',
            callback=self.parse
        )

    def parse(self, response):
        root = ET.fromstring(response.text)

        ############# Make a tag for each room
        for elementRoom in root.findall("./day/room"):

            out = {
                'tag': {
                    'data': {
                        'title': elementRoom.get('name'),
                    },
                    'extra_fields': {
                        'room-name': elementRoom.get('name'),
                    },
                }
            }

            for guid, tag_data in self.tags.items():
                if tag_data['extra_fields'].get('room-name', 0) == elementRoom.get('name'):
                    out['tag']['guid'] = guid

            yield out

        ############# Events
        for elementDay in root.findall("./day"):
            year, month, day = elementDay.get('date').split('-')

            for elementRoom in elementDay.findall("./room"):
                for elementEvent in elementRoom.findall('./event'):

                    slug = ''.join(elementEvent.find('./slug').itertext())
                    title = ''.join(elementEvent.find('./title').itertext())
                    subtitle = ''.join(elementEvent.find('./subtitle').itertext())
                    track = ''.join(elementEvent.find('./track').itertext()) # Are room and track the same thing? TODO
                    type = ''.join(elementEvent.find('./type').itertext())
                    abstract = remove_html_tags(''.join(elementEvent.find('./abstract').itertext())) # Strip HTML tags TODO
                    description = remove_html_tags(''.join(elementEvent.find('./description').itertext())) # Strip HTML tags TODO
                    persons = '\n'.join(elementEvent.find('./persons').itertext())
                    url = 'https://fosdem.org/2021/schedule/event/' + slug + '/'

                    strptime_string = elementDay.get('date')+'T'+''.join(elementEvent.find('./start').itertext())+':00+01:00'
                    print(strptime_string)
                    start = datetime.datetime.strptime(strptime_string, '%Y-%m-%dT%H:%M:%S%z').astimezone(datetime.timezone.utc)

                    duration_hour, duration_minutes = ''.join(elementEvent.find('./duration').itertext()).split(':')
                    end = start + datetime.timedelta(hours=int(duration_hour), minutes=int(duration_minutes))

                    # TODO Links

                    combined_description = ''
                    if abstract:
                        combined_description += 'ABSTRACT:\n\n'+abstract.strip()+'\n\n'
                    if description:
                        combined_description += 'DESCRIPTION:\n\n'+description.strip()+'\n\n'
                    if persons:
                        combined_description += 'SPEAKERS:\n\n'+persons.strip()+'\n\n'


                    out = {
                        'event': {
                            'find_by_url': url,
                            'data': {
                                'title': title + ' ' + subtitle,
                                'url': url,
                                'description': combined_description,
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
                                'cancelled': False,
                            },
                            'extra_fields': {
                                'event-id': elementEvent.get('id'),
                                'event-slug': slug,
                            },
                            'add_tags': [],
                        }
                    }

                    for guid, tag_data in self.tags.items():
                        # Room
                        if tag_data['extra_fields'].get('room-name', 0) == elementRoom.get('name'):
                            out['event']['add_tags'].append(guid)

                    yield out


def remove_html_tags(data):
    data = data.replace('</p>','\n\n')
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', data)

