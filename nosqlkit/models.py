#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alberto Paro"
__docformat__ = "restructuredtext"

from django.conf import settings
from brainaetic.utils.dynloading import get_module_by_code

class BaseModel(object):
    collection = None

    @classmethod
    def insert(cls, **kwargs):
        for store in settings.NOSQL_STORES:
            func = get_module_by_code(store)
            func.insert(cls.collection, **kwargs)

class Log(BaseModel):
    collection = "actionlog"
