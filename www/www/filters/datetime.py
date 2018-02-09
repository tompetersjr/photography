import datetime
import pytz


def formatDatetimeAt(value, formating='%m/%d/%Y at %I:%M %p (%Z)', timezone='US/Pacific'):
    if isinstance(value, datetime.datetime):
        local_tz = pytz.timezone(timezone)
        local_date = value.astimezone(local_tz)
        value = local_date.strftime(formating)
    return value

def formatDatetime(value, formating='%m/%d/%Y %-I:%-M %p (%Z)', timezone='US/Pacific'):
    if isinstance(value, datetime.datetime):
        local_tz = pytz.timezone(timezone)
        local_date = value.astimezone(local_tz)
        value = local_date.strftime(formating)
    return value

def formatDate(value, formating='%m/%d/%Y', timezone='US/Pacific'):
    if isinstance(value, datetime.datetime):
        local_tz = pytz.timezone(timezone)
        local_date = value.astimezone(local_tz)
        value = local_date.strftime(formating)
    return value

def formatTime(value, formating='%I:%M %p (%Z)', timezone='US/Pacific'):
    if isinstance(value, datetime.datetime):
        local_tz = pytz.timezone(timezone)
        local_date = value.astimezone(local_tz)
        value = local_date.strftime(formating)
    return value

def formatDateNoTZ(value, formating='%m/%d/%Y'):
    if isinstance(value, datetime.datetime):
        value = value.strftime(formating)
    return value