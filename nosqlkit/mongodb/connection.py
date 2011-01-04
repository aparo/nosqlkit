#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Flavio Percoco"
__docformat__ = "restructuredtext"

import pymongo
from django.core.exceptions import ImproperlyConfigured

class MongoConnection(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwarts = kwargs
        self._connected = False

    def _connect(self):
        from django.conf import settings
        if not self._connected:
            mongodb_name = getattr(settings, 'MONGO_DATABASE_KEY', "mongodb")
            self.settings_dict = getattr(settings, 'DATABASES').get(mongodb_name, {
                                                                        'NAME': settings.DATABASE_NAME,
                                                                        'ENGINE': 'django_mongodb_engine',
                                                                        'USER': '',
                                                                        'PASSWORD': '',
                                                                        'HOST': settings.DATABASE_HOST,
                                                                        'PORT': "27017",
                                                                        'SLAVE_OKAY' : True,
                                                                        'CURSOR_OPTS' : { 'timeout' : False}
                                                                        })
            host = self.settings_dict['HOST'] or None
            port = self.settings_dict['PORT'] or None
            user = self.settings_dict.get('USER', None)
            password = self.settings_dict.get('PASSWORD')
            self.db_name = self.settings_dict['NAME']
            self.safe_inserts = self.settings_dict.get('SAFE_INSERTS', False)
            self.wait_for_slaves = self.settings_dict.get('WAIT_FOR_SLAVES', 0)
            slave_okay = self.settings_dict.get('SLAVE_OKAY', False)

            try:
                if host is not None:
                    if pymongo.version >= '1.8':
                        assert isinstance(host, (basestring, list)), \
                        'If set, HOST must be a string or a list of strings'
                    else:
                        assert isinstance(host, basestring), \
                        'If set, HOST must be a string'

                if port:
                    if isinstance(host, basestring) and \
                            host.startswith('mongodb://'):
                        # If host starts with mongodb:// the port will be
                        # ignored so lets make sure it is None
                        port = None
                        import warnings
                        warnings.warn(
                        "If 'HOST' is a mongodb:// URL, the 'PORT' setting "
                        "will be ignored", ImproperlyConfigured
                        )
                    else:
                        try:
                            port = int(port)
                        except ValueError:
                            raise ImproperlyConfigured(
                            'If set, PORT must be an integer')

                assert isinstance(self.safe_inserts, bool), \
                'If set, SAFE_INSERTS must be True or False'
                assert isinstance(self.wait_for_slaves, int), \
                'If set, WAIT_FOR_SLAVES must be an integer'
            except AssertionError, e:
                raise ImproperlyConfigured(e)

            self._connection = pymongo.Connection(host=host,
                                                  port=port,
                                                  slave_okay=slave_okay)

            if user and password:
                auth = self._connection[self.db_name].authenticate(user,
                                                                   password)
                if not auth:
                    raise ImproperlyConfigured("Username and/or password for "
                                               "the MongoDB are not correct")

            self._db_connection = self._connection[self.db_name]

            from .serializer import TransformDjango
            self._db_connection.add_son_manipulator(TransformDjango())

            self._connected = True

    @property
    def db_connection(self):
        self._connect()
        return self._db_connection

    def __getattr__(self, name):
        self._connect()
        db = self._connection[name]
        from .serializer import TransformDjango
        db.add_son_manipulator(TransformDjango())
        return db

    def __getitem__(self, name):
        return self.__getattr__(name)


connection = MongoConnection()

def insert(collection, **kwargs):
    coll = getattr(connection.db_connection, collection)
    return coll.insert(kwargs)
