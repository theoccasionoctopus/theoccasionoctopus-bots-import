import json
import scrapy
import datetime
from pytz import UTC

from theoccasionoctopusbotsimport.base_spider import BaseSpider


EXTRA_FIELD_ORIGINAL_TIME = 'orginal_start_time'
EXTRA_FIELD_ORIGINAL_TIME_FORMAT = '%Y-%m-%d %H-%M-%S'

class OpenTechCalendarEvents(BaseSpider):
    name = 'w3socialwebincubatorcommunitygroup'
    download_delay = 5

    def start_requests(self):
        yield scrapy.Request(
            # TODO when API supports it, should pass option to get all events (all over time + deleted + cancelled)
            url=self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/events.json',
            callback=self.parse_existing_events
        )

    def parse_existing_events(self, response):
        json_response = json.loads(response.text)


        # Make list of current events
        current_events = []
        for data in json_response.get('events'):
            if EXTRA_FIELD_ORIGINAL_TIME in data['extra_fields']:
                current_events.append(data['extra_fields'][EXTRA_FIELD_ORIGINAL_TIME])

        # Build list of dates we should be making
        event_starts = []
        pattern_start_dates = [
            datetime.datetime(2021,1,29,17,0,tzinfo=UTC),
            datetime.datetime(2021,1,23,15,0,tzinfo=UTC),
        ]
        create_up_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=60)
        for pattern_start_date in pattern_start_dates:
            while pattern_start_date < create_up_until:
                event_starts.append(pattern_start_date)
                pattern_start_date = pattern_start_date + datetime.timedelta(days=14)

        # Check if event already made; if not make it!
        for event_start in event_starts:
            extra_field_value = event_start.strftime(EXTRA_FIELD_ORIGINAL_TIME_FORMAT)
            if extra_field_value not in current_events:
                end = event_start + datetime.timedelta(hours=1)
                out = {
                    'event': {
                        'data': {
                            'title': 'Social Web Incubator CG meeting ',
                            'url': 'https://socialhub.activitypub.rocks/c/meeting/socialcg/15',
                            'description': '',
                            'start_year_utc': event_start.year,
                            'start_month_utc': event_start.month,
                            'start_day_utc': event_start.day,
                            'start_hour_utc': event_start.hour,
                            'start_minute_utc': event_start.minute,
                            'end_year_utc': end.year,
                            'end_month_utc': end.month,
                            'end_day_utc': end.day,
                            'end_hour_utc': end.hour,
                            'end_minute_utc': end.minute,
                            'deleted': False,
                            'cancelled': False,
                        },
                        'add_tags': [],
                        'extra_fields': {
                            EXTRA_FIELD_ORIGINAL_TIME: extra_field_value
                        }
                    }
                }
                yield out
