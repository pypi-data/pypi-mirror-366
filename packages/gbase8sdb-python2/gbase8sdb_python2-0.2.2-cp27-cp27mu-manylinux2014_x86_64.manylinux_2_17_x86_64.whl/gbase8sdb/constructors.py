# coding: utf-8

"""
Database API functions
"""
import datetime
from . import errors


def Date(year, month, day):
    return datetime.date(year, month, day)

def Time(hour, minute, second):
    errors.raise_error(errors.ERR_TIME_NOT_SUPPORTED)
    
def Timestamp(year, month, day, hour, minute, second):
    return datetime.datetime(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    return datetime.date.fromtimestamp(ticks)


def TimeFromTicks(ticks):
    errors.raise_error(errors.ERR_TIME_NOT_SUPPORTED)


def TimestampFromTicks(ticks):
    return datetime.datetime.fromtimestamp(ticks)


def Binary(value, encoding='utf-8'):
    if isinstance(value, unicode):
        return value.encode(encoding)
    return bytes(value)
