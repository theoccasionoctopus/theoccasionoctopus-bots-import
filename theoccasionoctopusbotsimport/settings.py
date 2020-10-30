import os

BOT_NAME = 'theoccasionoctopus_bots_import'

SPIDER_MODULES = ['theoccasionoctopusbotsimport.spiders']
NEWSPIDER_MODULE = 'theoccasionoctopusbotsimport.spiders'

# The URL should NOT have a slash at the end
SERVER_INSTANCE_URL = os.environ.get('SERVER_INSTANCE_URL', 'https://example.com')
SERVER_ACCESS_TOKEN = os.environ.get('SERVER_ACCESS_TOKEN', 'xxx')
SERVER_ACCOUNT_ID = os.environ.get('SERVER_ACCOUNT_ID', 'yyy')

USER_AGENT = 'Bots for ' + SERVER_INSTANCE_URL

ITEM_PIPELINES = {
    'theoccasionoctopusbotsimport.pipelines.SendToAPIPipeline': 300,
}
