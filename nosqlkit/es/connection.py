#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alberto Paro"
__docformat__ = "restructuredtext"

def get_connection(bulk_size=200):
    """
    Returns an ES connection
    """
    from pyes import ES
    from django.conf import settings
    return ES(settings.INDEXER_SERVER, bulk_size=bulk_size)

def insert(collection, **kwargs):
    from django.conf import settings
    iconn = get_connection()
    return iconn.index(kwargs, settings.APPLICATION_NAME, collection, bulk=False)
