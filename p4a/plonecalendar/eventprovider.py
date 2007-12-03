import datetime
from zope import interface
from zope import component

import kalends
from Products.ZCatalog import CatalogBrains
from Products.chronos import interfaces
from DateTime import DateTime
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.ATContentTypes.content import topic
from Products.CMFCore.utils import getToolByName


def dt2DT(dt):
    s = "%04i-%02i-%02i %02i:%02i" % (dt.year, dt.month, dt.day,
                                      dt.hour, dt.minute)
    return DateTime(s)

def DT2dt(dt):
    return datetime.datetime(dt.year(), dt.month(), dt.day(),
                             dt.hour(), dt.minute())

def _make_zcatalog_query(start, stop, kw):
    """Takes a IEventProvider query and makes it a ZCaralog query"""
    if kw.has_key('title'):
        # The catalog calls this property "Title" with a 
        # capital T.
        kw['Title'] = kw['title']
        del kw['title']
    if stop is not None:
        kw['start']={'query': dt2DT(stop), 'range': 'max'} 
    if start is not None:
        kw['end']={'query': dt2DT(start), 'range': 'min'} 
    return kw

    
class ATEventProvider(object):
    interface.implements(kalends.IEventProvider)
    component.adapts(atapi.BaseObject)

    def __init__(self, context):
        self.context = context
        
    #def gather_events(self, start=None, stop=None, **kw):
        #catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        #path = '/'.join(self.context.getPhysicalPath())
        #kw = _make_zcatalog_query(start, stop, kw)
        #event_brains = catalog(portal_type='Event', path=path, **kw)
        #return (interfaces.IEvent(x) for x in event_brains)
    
    #def all_events(self):
        #catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        #path = '/'.join(self.context.getPhysicalPath())
        #event_brains = catalog(portal_type='Event', path=path)
        #return (interfaces.IEvent(x) for x in event_brains)
    
    #def event_creation_link(self, start=None, stop=None):
        #if self.context.portal_membership.checkPermission(
            #'Add portal content',self.context):
            #return self.context.absolute_url() + '/createObject?type_name=Event'
        #return ''

    def getEvents(self, start=None, stop=None, **kw):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        kw = _make_zcatalog_query(start, stop, kw)
        tool = cmfutils.getToolByName(self.context, 'portal_calendar')
        portal_types = tool.getCalendarTypes()
        # Any first occurrences:
        event_brains = catalog(portal_type=portal_types, path=path, **kw)
        # And then the recurrences:
        if stop is None:
            # XXX This is to handle the recurring events in the list view.
            # It should possibly be done some other way, since it will recur to
            # the year 2020 as it is now.
            stop = start + datetime.timedelta(30)
        if start is None:
            # XXX This is to handle the recurring events in the past events view.
            # This could also likely be improved.
            start = datetime.datetime(1970, 1, 1, 0, 0)
        days = range(start.toordinal(), 
                    (stop + datetime.timedelta(hours=23, minutes=59)).toordinal())
        # XXX How do we make the recurrence story pluggable?
        # This didn't work, because if RecurringEvent is not installed all fails:
        # Maybe we don't need pluggability, we could just require p4a.ploneevent,
        # But at least it should work without it....
        #recurrences = catalog(portal_type=portal_types, 
                              #path=path, 
                              #getRecueDays=days)
        recurrences = []
        return tuple((kalends.ITimezonedOccurrence(x) for x in event_brains)) + \
               tuple((kalends.ITimezonedRecurringEvent(x) for x in recurrences))

    def getOccurrences(self, start=None, stop=None, **kw):
        events = self.getEvents(start, stop, **kw)
        res = []
        for event in events:
            if kalends.IRecurring.providedBy(event):
                res.extend(event.getOcurrences(start, stop))
            else:
                res.append(event)
        return res    

class TopicEventProvider(object):
    interface.implements(kalends.IEventProvider)
    component.adapts(topic.ATTopic)

    def __init__(self, context):
        self.context = context
        
    def acceptable_event(self, x, start, stop):
        start = dt2DT(start)
        stop = dt2DT(stop)
        
        return x.portal_type == 'Event' and x.start >= start and x.end <= stop
    
    def gather_events(self, start=None, stop=None, **kw):
        kw = _make_zcatalog_query(start, stop, kw)

        # This sad hack allows us to overwrite whatever restriction
        # the topic makes to the date.  Providing the 'start' and
        # 'date' arguments to the 'queryCatalog' method would
        # otherwise just overwrite our own date criteria.
        # See http://plone4artists.org/products/plone4artistscalendar/issues/35
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        def my_catalog(request, **kwargs):
            kwargs.update(kw)
            return catalog(request, **kwargs)
        self.context.portal_catalog = my_catalog
        self.context.portal_catalog.searchResults = my_catalog
        value = (interfaces.IEvent(x) for x in self.context.queryCatalog())
        del self.context.portal_catalog
        return value

    def all_events(self):
        #query = self.context.buildQuery()
        event_brains = self.context.queryCatalog() 
        return (interfaces.IEvent(x) for x in event_brains)

    def event_creation_link(self, start=None, stop=None):
        return ""


class BrainEvent(object):
    interface.implements(kalends.ITimezonedOccurrence)
    component.adapts(CatalogBrains.AbstractCatalogBrain)

    def __init__(self, context):
        self.context = context
        self.event = None
        catalog = getToolByName(self.context, 'portal_catalog')
        putils = getToolByName(self.context, 'plone_utils')
        self.encoding = putils.getSiteEncoding()
        
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
        return DT2dt(self.context.start)

    @property
    def end(self):
        return DT2dt(self.context.end)
    
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

    def getOcurrences(self, start, stop):
        event = self._getEvent()
        res = []
        for each in event.calc_recueDays(start, stop):
            dt = datetime.date.fromordinal(each)
            res.append(Ocurrence(self.context, dt))
            
        return res
            
        
