from mongoengine import Document

from crits.core.crits_mongoengine import CritsDocument
from mongoengine import StringField, DecimalField

class Dagger(CritsDocument, Document):
    """TAXII Document Object"""
    meta = {
        # mongoengine adds fields _cls and _types and uses them to filter database
        # responses unless you disallow inheritance. In other words, we
        # can't see any of our old data unless we add _cls and _types
        # attributes to them or turn off inheritance.
        #So we'll turn inheritance off.
        # (See http://mongoengine-odm.readthedocs.org/en/latest/guide/defining-documents.html#working-with-existing-data)
        "allow_inheritance": False,
        "collection": 'dagger',
        "crits_type": 'Dagger',
        "latest_schema_version": 1,
        #NOTE: minify_defaults fields should match the MongoEngine field names, NOT the database fields
        "minify_defaults": [
            'marti_name',
            'dagger_name'
            'dagger_value',
            'decay'
        ],
        "schema_doc": {
            'marti_name': 'The name of the marti item',
            'dagger_name': 'The name of the dagger item',
            'dagger_value': 'The current value 0-1',
            'decay': 'Rate of decay (in decimal)'
        },
    }

    marti_name = StringField()
    dagger_name = StringField()
    dagger_value = DecimalField()
    decay = DecimalField()

    def migrate(self):
        pass

    @classmethod
    def get_item(cls,name):
        return cls.objects(marti_name=name).first()

#import socket, math, time

# class Dagger():
#
#     def __init__(self, IP, PORT):
#
# def updateDagger(daggerIP, daggerPORT, daggerMSG):
#         try:
#                 client_socket = socket.socket()
#                 client_socket.connect((daggerIP, daggerPORT))
#                 client_socket.send(daggerMSG)
#                 client_socket.close()
#         except socket.error as e:
#                 print e
#
# def makeDaggerMSG(item, field, value, msg):
#         timeval = int(math.floor(time.time()*1000))
#         daggerMSG = "default,%s,%s,PROPERTY,STATUS,%s,%d,%s\n" % (item, field, value, timeval, msg)
#         return daggerMSG
#
# updateDagger(args.ip, int(args.port), makeDaggerMSG(ipList[args.item], args.field, args.value, args.msg))