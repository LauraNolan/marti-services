import threading
from crits.services.handlers import get_config, update_config
import time
from . import handlers


class DaggerAgent(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print "Dagger thread started :)"
        while True:

            # Get config and grab some stuff we need.
            sc = get_config('dagger_service')

            if sc['active']:

                for crtfile in sc['dagger_settings']:
                    try:
                       (marti_name, dagger_name, decay) = crtfile.split(',')
                    except ValueError as e:
                        print e

                    handlers.decay_value(marti_name)
                    handlers.sendDagger(sc['hostname'], marti_name)

            time.sleep(int(sc['update_freq']))

polling_thread = DaggerAgent()

def start_dagger():
    global polling_thread

    # Get config and grab some stuff we need.
    sc = get_config('dagger_service')
    sc = sc.to_dict()

    if 'thread' in sc:
        if not sc['thread']:
            sc['thread'] = True
            update_config('dagger_service', sc, 'taxii')

            if not polling_thread.isAlive():
                polling_thread.start()
        else:
            sc['thread'] = False
            update_config('dagger_service', sc, 'taxii')