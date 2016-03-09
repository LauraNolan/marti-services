import threading
from crits.services.handlers import get_config
import time
from . import handlers
from . import taxii
from dateutil.tz import tzutc
from dateutil.tz import tzlocal
from crits.core.mongo_tools import mongo_find
import pytz
from datetime import datetime
from dateutil.parser import parse
from datetime import timedelta
from pytz import timezone
from crits.core.class_mapper import class_from_id


class TaxiiAgentPolling(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print "Polling thread started :)"
        while True:

            # Get config and grab some stuff we need.
            sc = get_config('taxii_service')
            certfiles = sc['certfiles']

            if sc['auto_polling']:

               for crtfile in certfiles:
                   (source, feed, filepath, polling, inbox) = crtfile.split(',')
                   src = source.strip()
                   if polling in 'auto':
                       handlers.execute_taxii_agent(analyst="taxii", method="TAXII Agent Web",feed=src)

            time.sleep(int(sc['polling_time']))

polling_thread = TaxiiAgentPolling()

def start_polling():
    global polling_thread

    if not polling_thread.isAlive():
        polling_thread.start()



class TaxiiAgentInbox(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self, start=None, feed='inbox', end=None):
        print "Inbox thread started :)"

        while True:

            # Get config and grab some stuff we need.
            sc = get_config('taxii_service')
            certfiles = sc['certfiles']

            feeds = []

            for crtfile in certfiles:
                   (source, feed2, filepath, polling, inbox) = crtfile.split(',')
                   if inbox in 'auto':
                        feeds.append(source)

            if sc['auto_inbox']:

                # Last document's end time is our start time.
                last = taxii.Taxii.get_last(feed)
                if last:
                    start = pytz.utc.localize(last.end)

                # If start is a string, convert it to a datetime
                # YYYY-MM-DD HH:MM:SS
                if isinstance(start, str):
                    start = pytz.utc.localize(parse(start, fuzzy=True))

                # store the current time as the time of this request
                runtime = datetime.now(tzutc()) - timedelta(hours=5)

                end = runtime

                # If end is a string, convert it to a datetime
                # YYYY-MM-DD HH:MM:SS
                if isinstance(end, str):
                    end = pytz.utc.localize(parse(end, fuzzy=True))

                crits_taxii = taxii.Taxii()
                crits_taxii.runtime = runtime
                crits_taxii.end = end
                crits_taxii.feed = feed

                TLO = []
                TLO.append([{'items': mongo_find('domains', {'modified': {'$gt': start}}, sort=[('modified',-1)])}, {'collection' : 'Domain'}])
                TLO.append([{'items': mongo_find('email', {'modified': {'$gt': start}}, sort=[('modified',-1)])}, {'collection' : 'Email'}])
                TLO.append([{'items': mongo_find('ips', {'modified': {'$gt': start}}, sort=[('modified',-1)])}, {'collection' : 'IP'}])
                TLO.append([{'items': mongo_find('campaigns', {'modified': {'$gt': start}}, sort=[('modified',-1)])}, {'collection' : 'Campaign'}])
                TLO.append([{'items': mongo_find('sample', {'modified': {'$gt': start}}, sort=[('modified',-1)])},{'collection' : 'Sample'}])
                #Other TLOs that TAXII will send without error: pcaps/PCAP, raw_data/RawData, certificates/Certificate

                for samples in TLO:
                    for doc in samples[0]['items']:
                        release_list = []

                        obj_item = class_from_id(samples[1]['collection'], doc['_id'])

                        if 'releasability' in doc:
                            for release in doc['releasability']:
                                if release['name'] in feeds:
                                    if 'release' in release:
                                        if release['release']:
                                            release_list.append(release['name'])

                        if release_list != []:
                            data = handlers.run_taxii_service("taxii", obj_item, release_list, preview=False,confirmed=True)
                            print doc['_id'], " : ", data

                crits_taxii.save()

            time.sleep(int(sc['inbox_time']))

inbox_thread = TaxiiAgentInbox()

def start_inbox():
    global inbox_thread

    if not inbox_thread.isAlive():
        inbox_thread.start()