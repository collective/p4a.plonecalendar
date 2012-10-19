import datetime
from zope import interface
from zope import component

from Products.ZCatalog import CatalogBrains
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.ATContentTypes.content import topic
from Products.CMFCore.utils import getToolByName
from p4a.common.dtutils import dt2DT, DT2dt
from dateable import kalends

try:
    # Plone 4.2 and later:
    from plone.app.querystring.queryparser import parseFormquery
except ImportError:
    pass

def _make_zcatalog_query(start, stop, kw):
    """Takes a IEventProvider query and makes it a ZCaralog query"""

    if 'title' in kw:
        # The catalog calls this property "Title" with a
        # capital T.
        kw['Title'] = kw['title']
        del kw['title']
    # Note how we assign the stop to the start and the start to the end
    # This is confusing, but correct. We want everything that that has a
    # start date before the stop time OR an end date after the start time.
    if stop is not None:
        kw['start']={'query': dt2DT(stop), 'range': 'max'}
    if start is not None:
        kw['end']={'query': dt2DT(start), 'range': 'min'}
    return kw


class EventProviderBase(object):

    def __init__(self, context):
        self.context = context

    def _getEvents(self, start=None, stop=None, **kw):
        kw = _make_zcatalog_query(start, stop, kw)
        tool = cmfutils.getToolByName(self.context, 'portal_calendar')
        portal_types = tool.getCalendarTypes()
        # Any first occurrences:
        event_brains = self._query(portal_type=portal_types, **kw)
        # And then the recurrences:
        if start is None:
            # XXX This is to handle the recurring events in the past events view.
            # This could also likely be improved.
            start = datetime.datetime(1970, 1, 1, 0, 0)
        if stop is None:
            # XXX This is to handle the recurring events in the list view.
            # It should possibly be done some other way, since it will recur to
            # the year 2020 as it is now.
            stop = start + datetime.timedelta(30)
        days = range(start.toordinal(),
                    (stop + datetime.timedelta(hours=23, minutes=59)).toordinal())
        # XXX How do we make the recurrence story pluggable?
        # This didn't work, because if RecurringEvent is not installed all fails:
        # This must work with standard Plone event and plone.app.event.
        if 'start' in kw:
            del kw['start']
        if 'end' in kw:
            del kw['end']
        recurrences = self._query(portal_type=portal_types,
                                  recurrence_days=days,
                                  **kw)
        return tuple((kalends.ITimezonedOccurrence(x) for x in event_brains)) + \
               tuple((kalends.ITimezonedRecurringEvent(x) for x in recurrences))

    def getOccurrences(self, start=None, stop=None, **kw):
        events = self.getEvents(start, stop, **kw)
        res = []
        for event in events:
            if kalends.IRecurringEvent.providedBy(event):
                res.extend(event.getOccurrences(start, stop))
            else:
                res.append(event)
        return res


class ATEventProvider(EventProviderBase):
    interface.implements(kalends.IEventProvider)
    component.adapts(atapi.BaseFolder)

    def getEvents(self, start=None, stop=None, **kw):
        path = '/'.join(self.context.getPhysicalPath())
        return self._getEvents(start=start, stop=stop, path=path, **kw)

    def _query(self, **kw):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        return catalog(**kw)


class ATEventCreator(object):
    interface.implements(kalends.IWebEventCreator)
    component.adapts(atapi.BaseFolder)

    def __init__(self, context):
        self.context = context

    def url(self, start=None, stop=None):
        """Returns a url to a page that can create an event.

        Optional start and stop times to pre-fill start and end of event.
        """
        if start:
            # if there is a start date, use it to initalize the new Event
            if not stop:
                stop = start
            id=self.context.generateUniqueId('Event')
            return self.context.absolute_url() +\
                '/portal_factory/Event/%s/edit?startDate=%s&endDate=%s' % \
                (id, start, stop)
        else:
            return self.context.absolute_url() +\
                '/createObject?type_name=Event'

    def typeTitle(self):
        """Returns the type name of the event type created"""
        return 'Event'

    def canCreate(self):
        """Test to know if the current user can create events"""
        mtool = cmfutils.getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('Add portal content', self.context)


class TopicEventProvider(EventProviderBase):
    interface.implements(kalends.IEventProvider)
    component.adapts(topic.ATTopic)

    def getEvents(self, start=None, stop=None, **kw):
        return self._getEvents(start=start, stop=stop, **kw)

    def _query(self, **kw):
        q = self.context.buildQuery()
        # if there are no criteria we'll get None
        if q is None:
            q = {}

        if kw.get('start') is not None and q.get('start') is not None:
            if q['start']['range'] == 'max':
                # There is a filter capping the maximum start time.
                # If the filter is earlier than the query, replace it.
                if q['start']['query'] < kw['start']['query']:
                    kw['start'] = q['start']
            elif q['start']['range'] == 'min':
                # There is a filter capping the minimum start time.
                # Remake the query into a minmax query.
                if q['start']['query'] > kw['start']['query']:
                    # If you give ZCatalog a minmax query, where min is
                    # larger than max it *should* reasonably return an
                    # empty result. Well. It doesn't... So we handle that
                    # case specially here:
                    return []
                kw['start'] = {'query': (q['start']['query'],
                                         kw['start']['query']),
                              'range': 'minmax'}

        if kw.get('end') is not None and q.get('end') is not None:
            if q['end']['range'] == 'min':
                # There is a filter capping the minimum start time.
                # If the filter is later than the query, replace it.
                if q['end']['query'] > kw['end']['query']:
                    kw['end'] = q['end']
            elif q['end']['range'] == 'max':
                # There is a filter capping the minimum start time.
                # Remake the query into a minmax query:
                if kw['end']['query'] > q['end']['query']:
                    # If you give ZCatalog a minmax query, where min is
                    # larger than max it *should* reasonably return an
                    # empty result. Well. It doesn't... So we handle that
                    # case specially here:
                    return []
                kw['end'] = {'query': (kw['end']['query'],
                                       q['end']['query']),
                              'range': 'minmax'}
        q.update(kw)
        #if kw['end'] < kw['start']:
            ## The end is before the start: The query should have an empty
            ## result, but unfortunately, portal_catalog isn't very smart
            ## about this, and will return stuff that has the end well after
            ## the end, for some reason. So we special case here:
            #return []
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        return catalog(**q)

class TopicEventCreator(object):
    interface.implements(kalends.IWebEventCreator)
    component.adapts(topic.ATTopic)

    def __init__(self, context):
        self.context = context

    def url(self, start=None, stop=None):
        """Returns a url to a page that can create an event.

        Optional start and stop times to pre-fill start and end of event.
        """
        raise AssertionError("If you had called canCreate first, you would" \
                             "know that you can't create events here")

    def typeTitle(self):
        """Returns the type name of the event type created"""
        raise AssertionError("If you had called canCreate first, you would" \
                             "know that you can't create events here")

    def canCreate(self):
        """Test to know if the current user can create events"""
        return False


try:
    from plone.app.collection import collection

    class CollectionEventProvider(EventProviderBase):
        interface.implements(kalends.IEventProvider)
        component.adapts(collection.Collection)
    
        def getEvents(self, start=None, stop=None, **kw):
            return self._getEvents(start=start, stop=stop, **kw)
    
        def _getCriteria(self, query, i):
            for criteria in query:
                if criteria['i'] == i:
                    return criteria
            return None
        
        def _query(self, **kw):
            query = self.context.getField('query').getRaw(self.context)
            q = parseFormquery(self.context, query)
    
            if kw.get('start') is not None and q.get('start') is not None:
                if q['start']['range'] == 'max':
                    # There is a filter capping the maximum start time.
                    # If the filter is earlier than the query, replace it.
                    if q['start']['query'] < kw['start']['query']:
                        kw['start'] = q['start']
                elif q['start']['range'] == 'min':
                    # There is a filter capping the minimum start time.
                    # Remake the query into a minmax query.
                    if q['start']['query'] > kw['start']['query']:
                        # If you give ZCatalog a minmax query, where min is
                        # larger than max it *should* reasonably return an
                        # empty result. Well. It doesn't... So we handle that
                        # case specially here:
                        return []
                    kw['start'] = {'query': (q['start']['query'],
                                             kw['start']['query']),
                                  'range': 'minmax'}
    
            if kw.get('end') is not None and q.get('end') is not None:
                if q['end']['range'] == 'min':
                    # There is a filter capping the minimum start time.
                    # If the filter is later than the query, replace it.
                    if q['end']['query'] > kw['end']['query']:
                        kw['end'] = q['end']
                elif q['end']['range'] == 'max':
                    # There is a filter capping the minimum start time.
                    # Remake the query into a minmax query:
                    if kw['end']['query'] > q['end']['query']:
                        # If you give ZCatalog a minmax query, where min is
                        # larger than max it *should* reasonably return an
                        # empty result. Well. It doesn't... So we handle that
                        # case specially here:
                        return []
                    kw['end'] = {'query': (kw['end']['query'],
                                           q['end']['query']),
                                  'range': 'minmax'}
            q.update(kw)
            #if kw['end'] < kw['start']:
                ## The end is before the start: The query should have an empty
                ## result, but unfortunately, portal_catalog isn't very smart
                ## about this, and will return stuff that has the end well after
                ## the end, for some reason. So we special case here:
                #return []
            catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
            return catalog(**q)
    
    class CollectionEventCreator(object):
        interface.implements(kalends.IWebEventCreator)
        component.adapts(collection.Collection)
    
        def __init__(self, context):
            self.context = context
    
        def url(self, start=None, stop=None):
            """Returns a url to a page that can create an event.
    
            Optional start and stop times to pre-fill start and end of event.
            """
            raise AssertionError("If you had called canCreate first, you would" \
                                 "know that you can't create events here")
    
        def typeTitle(self):
            """Returns the type name of the event type created"""
            raise AssertionError("If you had called canCreate first, you would" \
                                 "know that you can't create events here")
    
        def canCreate(self):
            """Test to know if the current user can create events"""
            return False

except ImportError:
    pass

class BrainEvent(object):
    interface.implements(kalends.ITimezonedOccurrence)
    component.adapts(CatalogBrains.AbstractCatalogBrain)

    def __init__(self, context, date=None):
        self.context = context
        self.event = None
        putils = getToolByName(self.context, 'plone_utils')
        self.encoding = putils.getSiteEncoding()
        self.date = date

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def _getEvent(self):
        if self.event is None:
            self.event = self.context.getObject()
        return self.event

    @property
    def title(self):
        return unicode(self.context.Title,
                       self.encoding)

    @property
    def description(self):
        return unicode(self.context.Description,
                       self.encoding)

    @property
    def start(self):
        dt = DT2dt(self.context.start)
        if self.date is not None:
            dt = dt.replace(year=self.date.year,
                            month=self.date.month,
                            day=self.date.day)
        return dt

    @property
    def end(self):
        dt = DT2dt(self.context.end)
        if self.date is not None:
            dt = dt.replace(year=self.date.year,
                            month=self.date.month,
                            day=self.date.day)
        return dt

    @property
    def location(self):
        return self.context.location

    @property
    def url(self):
        return self.context.getURL()

    @property
    def type(self):
        type = self._getEvent().eventType
        # This is a list of unicode strings, typically.
        # We want just one string, so we take the first one.
        if type:
            return cmfutils.cookString(type[0])
        return ''

    @property
    def timezone(self):
        return self.context.start.timezone()


class RecurringBrainEvent(BrainEvent):

    interface.implements(kalends.ITimezonedRecurringEvent)
    component.adapts(CatalogBrains.AbstractCatalogBrain)

    def getOccurrences(self, start, stop):
        if start is not None:
            startdate = start.toordinal()
        if stop is not None:
            stopdate = stop.toordinal()
        event = self._getEvent()
        try:
            recurrence = kalends.IRecurrence(event)
        except TypeError:
            # Could not adapt to IRecurrence, which means no recurrence
            # support is installed.
            return []

        res = []

        for each in recurrence.getOccurrenceDays():
            if start is not None and each < startdate:
                continue
            if stop is not None and each > stopdate:
                break
            dt = datetime.date.fromordinal(each)
            res.append(BrainEvent(self.context, dt))

        return res

