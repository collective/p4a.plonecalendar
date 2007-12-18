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

Doublecheck conversions:

    >>> brt = pytz.timezone('Brazil/East')

    >>> dt = DateTime('2005/07/07 18:00:00 Brazil/East')
    >>> dt == dt2DT(DT2dt(dt))
    True

    >>> dt = datetime.datetime(2005, 07, 07, 18, 00, 00)
    >>> dt = brt.localize(dt)
    >>> dt == DT2dt(dt2DT(dt))
    True

"""

import os
import time
import datetime
from DateTime import DateTime
import pytz
try:
    from DateTime import pytz_support
except ImportError:
    import pytz_support

def _timezone_matches(tz, tzoffset, altoffset, tzname, altname):
    return (tz._tzinfos.has_key((tzoffset, datetime.timedelta(0), tzname)) and
            tz._tzinfos.has_key((altoffset, altoffset-tzoffset, altname)))

def _guess_local_time_zone(tzoffset, altoffset, tzname, altname):
    # This tries to guess local timezones based on what your local standard
    # and daylight offsets are, and what they are called. It *will* guess
    # incorrectly most of the time. For example, For the timezone Brazil/East,
    # all python knows is that you are in BTR/BRST and that this is GMT-3 and
    # GMT-2 respectively, and if DST is currently in effect or not. This
    # matches many different timezones, and this method will just return the
    # first one, which will be America/Sao_Paulo when DST is in effect and
    # America/Araguaina otherwise. This is problematic, because
    # America/Araguaina does not employ daylightsaving, so any time
    # localizations for DST-times WILL be incorrect.
    
    # Look through all timezones to find a match:
    now = datetime.datetime.now()
    for each in pytz.all_timezones:
        tz = pytz.timezone(each)
        if not hasattr(tz, '_tzinfos'):
            # This can't match
            continue
        if _timezone_matches(tz, tzoffset, altoffset, tzname, altname):
            # Check that DST is on or off:
            dst_should_be = time.daylight and altoffset-tzoffset or datetime.timedelta(0)
            if tz.localize(now).dst() == dst_should_be:
                return tz
        
    raise KeyError("Can't find a local timezone")

def local_time_zone():
    # XXX This is as of yet untested on windows. /regebro
    # First check if a TZ environment variable is set that points to a 
    # proper timezone:
    try:
        tzstr = os.environ['TZ']
        return pytz.timezone(tzstr)
    except KeyError:
        pass

    # That didn't work. Find the locale timezone info:
    tzoffset = datetime.timedelta(seconds=-time.timezone)
    altoffset = datetime.timedelta(seconds=-time.altzone)
    tzname = time.tzname[0]
    altname = time.tzname[1]

    # See if there is a timezone with the timezone name given.
    try:
        if time.daylight:
            tz = pytz.timezone(altname)
        else:
            tz = pytz.timezone(tzname)
        if not hasattr(tz, '_tzinfos'):
            # Some timezones have no tzinfos. If this returns one of them,
            # it can be assumed to be a correct match
            return tz
        elif _timezone_matches(tz, tzoffset, altoffset, tzname, altname):
            return tz
    except KeyError:
        pass
    
    # No, not that either. Then we need to use the local info to make a guess:
    return _guess_local_time_zone(tzoffset, altoffset, tzname, altname)

def gettz(name):
    try:
        return pytz.timezone(name)
    except KeyError:
        return pytz_support._numeric_timezones[name]

def dt2DT(dt, tzname=None):
    """Convert a python datetime to DateTime. 

    >>> import time, os
    >>> oldtz = os.environ['TZ']
    >>> os.environ['TZ'] = 'Brazil/East'
    >>> time.tzset()
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
    
    Change back:
    >>> os.environ['TZ'] = oldtz
    >>> time.tzset()    

    """
    if tzname is None and dt.tzinfo is None:
        # Assume local time
        # XXX turns out this method has a problem in some parts of Australia
        # As their timezone evidently is called EST, and this gets confused 
        # with the US EST.
        tz = local_time_zone()
    elif tzname is not None:
        # Convert to timezone
        tz = gettz(tzname)
    else:
        tz = None
    if tz is not None:
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
