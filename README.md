# The Occasion Octopus - Import Bots

These bots import data from various sources and send it to the API of an Occasion Octopus server.

They are Open Source under the Apache license. See https://www.theoccasionoctopus.net/ for more.

## Setup

If you are on Ubuntu Focal 20.04 LTS, you'll need some libraries:

    apt-get install python3.8-dev python3-virtualenv gcc

Then set up a virtual environment and install the requirements. You may have other ways you like to do this, but you can run:
    
    virtualenv .ve -p python3
    source .ve/bin/activate
    pip3 install -r requirements.txt
    
    
## Running

To run, you must pass some config to every command:

    SERVER_INSTANCE_URL=http://localhost:8080 SERVER_ACCESS_TOKEN=b SERVER_ACCOUNT_ID=c  scrapy .....

Then use one of the commands below.

## Bots

### Coops UK, https://www.uk.coop/

    scrapy crawl coopsuk

### Open Tech Calendar, https://opentechcalendar.co.uk/

    scrapy crawl opentechcalendarlocations
    scrapy crawl opentechcalendargroups
    scrapy crawl opentechcalendarevents

### Schema.org data on a webpage

    scrapy crawl schemaorg -a starturl="http://example.com/"

### iCalendar files served from a URL

There is no need for a bot for this - this feature is available directly in the server itself.

### University of St. Andrews, https://events.st-andrews.ac.uk

This fetches online events only.

    scrapy crawl unistandrews

### Mobilizon servers

This gets all events on a server.

Note: This functionality will be build into the server later, by following the remote user "relay@instance.tld".

HTTPS is assumed.

    scrapy crawl mobillizon -a starthost="mobilizon.fr"

