from datetime import datetime
from DateTime import DateTime
from Testing import ZopeTestCase
import p4a.common
import p4a.calendar
import p4a.plonecalendar
from p4a.calendar.tests import EventProviderTestMixin
from p4a.calendar.interfaces import ICalendarConfig, IEventProvider
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer

PloneTestCase.setupPloneSite()

CalendarTestCase = PloneTestCase.PloneTestCase

class ATEventProviderTest(CalendarTestCase, EventProviderTestMixin):

    def eventSetUp(self):
        # Create folder.
        self.folder.invokeFactory('Folder', id='calendar-folder')
        cal = self.folder['calendar-folder']
        id = cal.invokeFactory('Event', id='event1')
        cal['event1'].update(title='First Event',
                             startDate=DateTime('2006-09-28 08:30am GMT+0'),
                             endDate=DateTime('2006-09-28 09:30am GMT+0'))
        id = cal.invokeFactory('Event', id='event2')
        cal['event2'].update(title='Second Event',
                             startDate=DateTime('2006-09-29 08:30am GMT+0'),
                             endDate=DateTime('2006-09-29 09:30am GMT+0'))
        id = cal.invokeFactory('Event', id='meeting1')
        # Calling this event "Meeting" is just to have one event that does
        # not have the word "Event" in the title.
        cal['meeting1'].update(title='First Meeting',
                               startDate=DateTime('2006-09-30 08:30am GMT+0'),
                               endDate=DateTime('2006-09-30 09:30am GMT+0'))

        # Activate calendaring capabilities on this folder
        config = ICalendarConfig(cal)
        config.calendar_activated = True
        
    def afterSetUp(self):
        self.eventSetUp()
        self.provider = IEventProvider(self.folder['calendar-folder'])

    def test_createlink(self):
        link = self.provider.event_creation_link()
        self.failUnlessEqual(link, "http://nohost/plone/Members/test_user_1_/calendar-folder/createObject?type_name=Event")


class TopicEventProviderTest(ATEventProviderTest):
    
    def afterSetUp(self):
        self.eventSetUp()
        self.loginAsPortalOwner()
        self.folder.invokeFactory('Topic', id='calendar-topic')
        topic = self.folder['calendar-topic']
        criteria = topic.addCriterion('portal_type', 'ATPortalTypeCriterion')
        criteria.value = (u'Event',)
        self.provider = IEventProvider(topic)

    def test_createlink(self):
        link = self.provider.event_creation_link()
        self.failUnlessEqual(link, "")

class LocationFilterTest(CalendarTestCase):

    def afterSetUp(self):
        # Create folder.
        self.folder.invokeFactory('Folder', id='calendarfolder')
        calendarfolder = self.folder['calendarfolder']
        # Activate calendaring capabilities on this folder
        config = ICalendarConfig(calendarfolder)
        config.calendar_activated = True
        
    def testLocationFilter(self):
        calendar = self.folder.calendarfolder
        view = calendar.unrestrictedTraverse('month.html')
        filter_html = view.render_filter()
        self.failUnlessEqual(filter_html, '')
        catalog = self.folder.portal_catalog.addIndex('location', 'FieldIndex')
        filter_html = view.render_filter()
        self.failUnless(filter_html.startswith('<span class="filter">'))
        
def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
    from zope.testing import doctest
    from zope.component import testing
    
    suite = TestSuite()
    suite.addTest(doctest.DocTestSuite('p4a.plonecalendar.sitesetup',
                                       optionflags=doctest.ELLIPSIS))
    suite.addTest(ZopeDocFileSuite(
        'calendar.txt',
        package='p4a.plonecalendar',
        test_class=CalendarTestCase,
        )
    )
    suite.addTests(makeSuite(ATEventProviderTest))
    suite.addTests(makeSuite(TopicEventProviderTest))
    suite.addTests(makeSuite(LocationFilterTest))
    suite.layer = layer.ZCMLLayer

    return suite
