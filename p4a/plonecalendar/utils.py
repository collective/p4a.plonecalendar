##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
Calendar utilities
"""

import os
import datetime, time
from DateTime import DateTime
import pytz
try:
    from DateTime import pytz_support
except ImportError:
    import pytz_support

def gettz(name):
    try:
        return pytz.timezone(name)
    except KeyError:
        return pytz_support._numeric_timezones[name]

def GMT4dt(date):
    if not isinstance(date, datetime.datetime):
        return 'UTC'
    offset = date.utcoffset()
    minutes = (offset.days*24*60)+(offset.seconds/60)
    if minutes == 0:
        return 'UTC'
    return 'GMT%+03i%02i' % divmod(minutes,60)

def dt2DT(dt, tzname=None):
    """Convert a python datetime to DateTime. 

    >>> import os
    >>> os.environ['TZ'] = 'Brazil/East'
    >>> brt = gettz('Brazil/East')

    No timezone information, assume local timezone at the time.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0))
    DateTime('2005/11/07 18:00:00 GMT-2')

    Provide a default TZID:

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0), tzname='EET')
    DateTime('2005/11/07 18:00:00 GMT+2')

    UTC timezone.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=pytz.utc))
    DateTime('2005/11/07 18:00:00 GMT+0')

    BRST timezone (GMT-2 on this day).

    >>> dt = datetime.datetime(2005, 11, 07, 18, 0, 0)
    >>> dt2DT(brt.localize(dt))
    DateTime('2005/11/07 18:00:00 GMT-2')

    BRT timezone (GMT-3 on this day).

    >>> dt = datetime.datetime(2005, 07, 07, 18, 0, 0)
    >>> dt2DT(brt.localize(dt))
    DateTime('2005/07/07 18:00:00 GMT-3')

    """
    if tzname is None and dt.tzinfo is None:
        # Assume local time
        tzname = os.environ['TZ']    
    if tzname is not None:
        # Convert to timezone
        tz = gettz(tzname)
        dt = tz.localize(dt)
    return DateTime(dt.isoformat())

def DT2dt(dt):
    """Convert a DateTime to python's datetime in UTC.

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 UTC'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=<StaticTzInfo 'Universal'>)
    >>> dt.astimezone(pytz.utc)
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=<UTC>)

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 Brazil/East'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=<DstTzInfo 'Brazil/East' BRST-1 day, 22:00:00 DST>)
    >>> dt.astimezone(pytz.utc)
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=<UTC>)

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 GMT-2'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=<StaticTzInfo 'GMT-2'>)
    >>> dt.astimezone(pytz.utc)
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=<UTC>)

    >>> dt = DT2dt(DateTime('2005/07/07 18:00:00 Brazil/East'))
    >>> dt
    datetime.datetime(2005, 7, 7, 18, 0, tzinfo=<DstTzInfo 'Brazil/East' BRT-1 day, 21:00:00 STD>)
    >>> dt.astimezone(pytz.utc)
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=<UTC>)

    >>> dt = DT2dt(DateTime('2005/07/07 18:00:00 GMT-3'))
    >>> dt
    datetime.datetime(2005, 7, 7, 18, 0, tzinfo=<StaticTzInfo 'GMT-3'>)
    >>> dt.astimezone(pytz.utc)
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=<UTC>)
    """
    tz = gettz(dt.timezone())
    value = datetime.datetime(dt.year(), dt.month(), dt.day(),
                              dt.hour(), dt.minute(), int(dt.second()),
                              int(dt.second()*1000000) % 1000000)
    value = tz.localize(value)
    return value

# Doublecheck conversions:
"""
    >>> dt = datetime.datetime('2005/07/07 18:00:00 Brazil/East')
    >>> dt ==Dt2dt(dt2DT(dt))

"""