from . import dagger
import socket
import math
import time

def init_values(marti_name,dagger_name,decay=None,dagger_value=None):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if item:
        dagger_item = item


    dagger_item.marti_name = marti_name
    dagger_item.dagger_name = dagger_name
    dagger_item.decay = decay

    if not item:
        dagger_item.dagger_value = 0
    if dagger_value is not None:
        dagger_item.dagger_value = dagger_value

    dagger_item.save()
    dagger_item.reload()

def set_value(marti_name,dagger_value):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if not item:
        print 'not here'
        return False

    if dagger_value < 0:
        dagger_value = 0

    item.dagger_value = dagger_value

    item.save()
    item.reload()

def decay_value(marti_name):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if not item:
        print 'item not here'
        return False

    set_value(marti_name,(item.dagger_value-item.decay))

def updateDagger(daggerIP, daggerPORT, daggerMSG): #44663
        try:
                client_socket = socket.socket()
                client_socket.connect((daggerIP, daggerPORT))
                client_socket.send(daggerMSG)
                client_socket.close()
        except socket.error as e:
                print e

def makeDaggerMSG(item, field, value, msg):
        timeval = int(math.floor(time.time()*1000))
        daggerMSG = "default,%s,%s,PROPERTY,STATUS,%s,%d,%s\n" % (item, field, value, timeval, msg)
        return daggerMSG

def sendDagger(daggerIP, marti_name):
    dagger_item = dagger.Dagger()
    item = dagger_item.get_item(marti_name)

    updateDagger(daggerIP, 44663, makeDaggerMSG(item.dagger_name, 'shield', str(item.dagger_value), 'init'))
