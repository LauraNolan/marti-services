import threading
from crits.services.handlers import get_config
import time
from . import handlers

class TaxiiAgentPolling(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print "Thread started :)"
        while True:

            # Get config and grab some stuff we need.
            sc = get_config('taxii_service')
            certfiles = sc['certfiles']

            if sc['auto_polling']:

               for crtfile in certfiles:
                   (source, feed, filepath, sync) = crtfile.split(',')
                   src = source.strip()
                   if sync in 'auto':
                       handlers.execute_taxii_agent(analyst="taxii", method="TAXII Agent Web",feed=src)

            time.sleep(60)

polling_thread = TaxiiAgentPolling()

def start_polling():
    global polling_thread

    if not polling_thread.isAlive():
        polling_thread.start()