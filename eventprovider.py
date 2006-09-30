import datetime
from zope import interface
from zope import component

from Products.ZCatalog import CatalogBrains
from p4a.calendar import interfaces
from DateTime import DateTime
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.ATContentTypes.content import topic

def dt2DT(dt):
    s = "%04i-%02i-%02i %02i:%02i" % (dt.year, dt.month, dt.day, dt.hour, dt.minute)
    return DateTime(s)

def DT2dt(dt):
    return datetime.datetime(dt.year(), dt.month(), dt.day(), dt.hour(), dt.minute())

class ATEventProvider(object):
    interface.implements(interfaces.IEventProvider)
    component.adapts(atapi.BaseObject)

    def __init__(self, context):
        self.context = context
        
    def gather_events(self, start, stop):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        event_brains = catalog(portal_type='Event',
                               path=path,
                               start={'query': dt2DT(start), 'range': 'min'},
                               end={'query': dt2DT(stop), 'range': 'max'})

        return (interfaces.IEvent(x) for x in event_brains)
    
    def all_events(self):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        event_brains = catalog(portal_type='Event',
                               path=path)
        return event_brains
        

class TopicEventProvider(object):
    interface.implements(interfaces.IEventProvider)
    component.adapts(topic.ATTopic)

    def __init__(self, context):
        self.context = context
        
    def acceptable_event(self, x, start, stop):
        start = dt2DT(start)
        stop = dt2DT(stop)
        
        return x.portal_type == 'Event' and x.start >= start and x.end <= stop
    
    def gather_events(self, start, stop):
        query = self.context.buildQuery()
        return (interfaces.IEvent(x) for x in self.context.queryCatalog() 
                if self.acceptable_event(x, start, stop))

    def all_events(self):
        query = self.context.buildQuery()
        return self.context.queryCatalog() 

class BrainEvent(object):
    interface.implements(interfaces.IEvent)
    component.adapts(CatalogBrains.AbstractCatalogBrain)

    def __init__(self, context):
        self.context = context
    
    @property
    def title(self):
        return self.context.Title

    @property
    def description(self):
        return self.context.Description
    
    @property
    def start(self):
        return DT2dt(self.context.start)

    @property
    def end(self):
        return DT2dt(self.context.end)

    @property
    def local_url(self):
        return self.context.absolute_url()
