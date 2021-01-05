import requests
from datetime import date
import urllib.parse
import copy


class SendToAPIPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.SERVER_INSTANCE_URL = crawler.settings['SERVER_INSTANCE_URL']
        self.SERVER_ACCESS_TOKEN = crawler.settings['SERVER_ACCESS_TOKEN']
        self.SERVER_ACCOUNT_ID = crawler.settings['SERVER_ACCOUNT_ID']

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):

        if item.get('event'):
            self._process_event(item['event'])
        if item.get('tag'):
            self._process_tag(item['tag'])

    def _process_event(self, event_data):

        # Process Data
        item_event_data_to_send = copy.deepcopy(event_data['data'])
        item_event_data_to_send['extra_field_0_name'] = 'Importer Last Saw'
        item_event_data_to_send['extra_field_0_value'] = date.today().strftime('%Y-%m')
        item_event_data_to_send['cancelled'] = 'Yes' if item_event_data_to_send.get('cancelled', False) else 'No'
        item_event_data_to_send['deleted'] = 'Yes' if item_event_data_to_send.get('deleted', False) else 'No'
        i = 1
        for k, v in event_data.get('extra_fields', {}).items():
            item_event_data_to_send['extra_field_'+str(i)+'_name'] = k
            item_event_data_to_send['extra_field_'+str(i)+'_value'] = v
            i += 1
        i = 0
        for tag_id in event_data.get('add_tags', []):
            item_event_data_to_send['add_tag_'+str(i)] = tag_id
            i += 1

        guid = event_data.get('guid')

        # Find GUID by URL?
        if 'find_by_url' in event_data:
            search_url = self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/events.json?' + \
                  'allDates=1&url=' + urllib.parse.quote(event_data['find_by_url'], safe='')
            r = requests.get(
                search_url,
                headers={'Authorization': 'Bearer ' + self.SERVER_ACCESS_TOKEN})
            for event in r.json()['events']:
                if event['url'] == event_data['find_by_url']:
                    guid = event['id']

        if guid:
            # Edit Existing Event
            r = requests.post(
                self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/event/' + guid + '.json',
                data=item_event_data_to_send,
                headers={'Authorization': 'Bearer ' + self.SERVER_ACCESS_TOKEN})
            return
        elif not event_data['data'].get('deleted', False) and not event_data['data'].get('cancelled', False):
            # New Event (But only if not deleted or cancelled)
            r = requests.post(
                self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/event.json',
                data=item_event_data_to_send,
                headers={'Authorization': 'Bearer '+ self.SERVER_ACCESS_TOKEN})

    def _process_tag(self, tag_data):
        # Process Data
        item_tag_data_to_send = copy.deepcopy(tag_data['data'])
        item_tag_data_to_send['extra_field_0_name'] = 'Importer Last Saw'
        item_tag_data_to_send['extra_field_0_value'] = date.today().strftime('%Y-%m')
        i = 1
        for k, v in tag_data.get('extra_fields', {}).items():
            item_tag_data_to_send['extra_field_'+str(i)+'_name'] = k
            item_tag_data_to_send['extra_field_'+str(i)+'_value'] = v
            i += 1

        guid = tag_data.get('guid')

        if guid:
            # Edit Existing tag
            r = requests.post(
                self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/tag/' + guid + '.json',
                data=item_tag_data_to_send,
                headers={'Authorization': 'Bearer ' + self.SERVER_ACCESS_TOKEN})
        else:
            # Send New tag
            r = requests.post(
                self.SERVER_INSTANCE_URL + '/api/v1/account/' + self.SERVER_ACCOUNT_ID + '/tag.json',
                data=item_tag_data_to_send,
                headers={'Authorization': 'Bearer ' + self.SERVER_ACCESS_TOKEN})

