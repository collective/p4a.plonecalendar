from unittest import TestSuite, makeSuite
from datetime import datetime, timedelta
from DateTime import DateTime
from Testing import ZopeTestCase

from zope.interface.verify import verifyObject

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.ZCatalog.Lazy import LazyCat

import dateable.kalends
import p4a.plonecalendar
from dateable.chronos.interfaces import ICalendarConfig
from dateable.kalends import IEventProvider, IWebEventCreator

PloneTestCase.setupPloneSite()


class EventProviderTestMixin(object):
    """Tests that the EventProvider API is correctly implemented
    Since IEventProvider has no implementation in this product
    these tests must be mixed in with a text that provides an
    event provider as self.provider in the setUp.
    """

    def test_interface(self):
        verifyObject(dateable.kalends.IEventProvider, self.provider)

    def test_gather_all(self):
        all_events = list(self.provider.getOccurrences())
        gathered_events = list(self.provider.getOccurrences())

        self.failUnlessEqual(len(all_events), len(gathered_events))

        for i in all_events:
            verifyObject(dateable.kalends.IOccurrence, i)
            exists = 0
            for j in gathered_events:
                if (i.title == j.title and
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnless(exists, "Event lists are not equal")


    def test_gather_future(self):
        all_events = list(self.provider.getOccurrences())
        if len(all_events) < 2:
            raise ValueError(
                "This test requires you to have at least two events "
                "with non overlapping start and end times.")

        # Pick out all the end datetimes for the events:
        end_times = [x.end for x in all_events]
        end_times.sort()
        # Pick an end date in the middle:
        dt = end_times[len(all_events)/2]

        # Get all dates starting at or after this middle date
        gathered_events = list(self.provider.getOccurrences(start=dt))

        for i in all_events:
            # The event should be returned if the end_date is above
            # the date given as a start date.
            should_exist = i.end >= dt

            # Now check if it exists:
            exists = False
            for j in gathered_events:
                if (i.title == j.title and
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnlessEqual(exists, should_exist,
                                 "Event lists are not as expected")

    def test_title_search(self):
        # This test assumes at least one event, but not all of them
        # has the text "event" in the title.
        all_events = list(self.provider.getOccurrences())
        gathered_events = list(self.provider.getOccurrences(title='event'))

        # Make sure something is returned
        self.failUnless(gathered_events)
        # But not everything
        self.failIfEqual(len(all_events), len(gathered_events))

        for i in gathered_events:
            self.failIf(i.title.lower().find('event') == -1)

class CalendarTestCase(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', dateable.chronos)
        zcml.load_config('configure.zcml', p4a.plonecalendar)

class ATEventProviderTest(CalendarTestCase, EventProviderTestMixin):

    def eventSetUp(self):
        # Create folder.
        self.folder.invokeFactory('Folder', id='calendar-folder')
        cal = self.folder['calendar-folder']
        cal.invokeFactory('Event', id='event1')
        cal['event1'].update(title='First Event',
                             startDate=DateTime('2006-09-28 08:30am GMT+0'),
                             endDate=DateTime('2006-09-28 09:30am GMT+0'))
        cal.invokeFactory('Event', id='event2')
        cal['event2'].update(title='Second Event',
                             startDate=DateTime('2006-09-29 08:30am GMT+0'),
                             endDate=DateTime('2006-09-29 09:30am GMT+0'))
        cal.invokeFactory('Event', id='meeting1')
        # Calling this event "Meeting" is just to have one event that does
        # not have the word "Event" in the title.
        cal['meeting1'].update(title='First Meeting',
                               startDate=DateTime('2006-09-30 08:30am GMT+0'),
                               endDate=DateTime('2006-09-30 09:30am GMT+0'))

    def afterSetUp(self):
        CalendarTestCase.afterSetUp(self)
        self.eventSetUp()
        self.provider = IEventProvider(self.folder['calendar-folder'])

    def test_createlink(self):
        cal = self.folder['calendar-folder']
        creator = IWebEventCreator(cal)
        link = creator.url()
        self.failUnlessEqual(link, "http://nohost/plone/Members/test_user_1_/calendar-folder/createObject?type_name=Event")


class TopicEventProviderTest(ATEventProviderTest):

    def afterSetUp(self):
        self.eventSetUp()
        self.loginAsPortalOwner()
        try:
            # Plone < 4.2
            self.folder.invokeFactory('Topic', id='calendar-topic')
            self.topic = self.folder['calendar-topic']
            criteria = self.topic.addCriterion(
                'portal_type', 'ATPortalTypeCriterion')
            criteria.value = (u'Event',)
        except ValueError:
            # Plone >= 4.2
            self.folder.invokeFactory('Collection', id='calendar-topic')
            self.topic = self.folder['calendar-topic']
            query = [{
                        'i': 'Type',
                        'o': 'plone.app.querystring.operation.string.is',
                        'v': 'Event',
                    }]
            self.topic.setQuery(query)
        self.provider = IEventProvider(self.topic)

    def test_createlink(self):
        cal = self.folder['calendar-topic']
        creator = IWebEventCreator(cal)
        self.failIf(creator.canCreate())

    def test_gather_events(self):
        # Make sure that restrictions made by the context topic and
        # our own query don't clash, see
        # http://plone4artists.org/products/plone4artistscalendar/issues/35

        # First off, we're going to set a date restriction so that
        # only events in the future are shown:
        try: 
            date_crit = self.topic.addCriterion('start', 'ATFriendlyDateCriteria')
            date_crit.setValue(0)
            date_crit.setDateRange('+')
            date_crit.setOperation('more')
    
            # Adding a criteria other than time
            subject_crit = self.topic.addCriterion('Subject', 'ATListCriterion')
            subject_crit.setValue(['foo', 'bar'])
        except AttributeError:
            # Plone 4.2 or later
            q = self.topic.getField('query').getRaw(self.topic)
            q.append({'i':'start', 'o': 'plone.app.querystring.operation.date.afterToday', 'v': None})
            # Adding a criteria other than time
            q.append({'i':'Subject', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['foo', 'bar']})
            self.topic.setQuery(q)

        calls = []
        class my_catalog:
            def __call__(self, **kwargs):
                calls.append(kwargs)
                return LazyCat([])
            searchResults = __call__
            def indexes(self):
                return ['Subject', 'start', 'end', 'Type']
            
        self.folder.portal_catalog = my_catalog()

        # Now let's make sure that a call to the catalog is done with
        # the correct set of arguments, and that the criteria defined
        # in the topic didn't interfere:
        start = datetime.now()
        stop = start + timedelta(seconds=3600)
        self.provider.getEvents(start=start, stop=stop)

        # XXX I don't like this test, it has too much internal knowledge.
        # Better to add more functional tests.
        self.assertEqual(len(calls), 2)
        # test to make sure that the recurrence search still has the extra
        # parameters in it
        self.failIf('Subject' not in calls[1].keys())

        # We don't mind the timezone at this point:
        self.assertEqual(calls[0]['end']['query'].strftime('%Y%m%d %H:%M'),
                         start.strftime('%Y%m%d %H:%M'))
        self.assertEqual(calls[0]['start']['query'][1].strftime('%Y%m%d %H:%M'),
                         stop.strftime('%Y%m%d %H:%M'))

class TestFunctional(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)

    def test_ui(self):
        from Products.Five.testbrowser import Browser
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        browser.handleErrors = False

        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        # Create a folder:
        browser.getLink('Folder').click()
        form = browser.getForm('folder-base-edit')
        form.getControl(name='title').value = 'A Calendar'
        form.getControl(name='form_submit').click()

        # Create an event:
        browser.getLink(id='event').click()
        form = browser.getForm('event-base-edit')
        form.getControl(name='title').value = 'An Event'
        form.getControl(name='startDate_year').value = ['2007']
        form.getControl(name='startDate_month').value = ['04']
        form.getControl(name='startDate_day').value = ['01']
        form.getControl(name='startDate_hour').value = ['11']
        form.getControl(name='startDate_minute').value = ['00']
        form.getControl(name='endDate_year').value = ['2007']
        form.getControl(name='endDate_month').value = ['04']
        form.getControl(name='endDate_day').value = ['01']
        form.getControl(name='endDate_hour').value = ['11']
        form.getControl(name='endDate_minute').value = ['00']
        form.getControl(name='form_submit').click()
        self.failUnless('an-event' in browser.url)

        browser.getLink("A Calendar").click()
        folder_url = browser.url
        browser.open(folder_url + '?date=2007-04-01')
        calendar = browser.contents[browser.contents.index('class="ploneCalendar"'):]
        self.failUnless("An Event" in calendar)
        browser.open(folder_url + '?date=2007-05-01')
        calendar = browser.contents[browser.contents.index('class="ploneCalendar"'):]
        self.failUnless("An Event" in calendar)

def test_suite():

    suite = TestSuite()
    suite.addTests(makeSuite(ATEventProviderTest))
    suite.addTests(makeSuite(TopicEventProviderTest))
    suite.layer = layer.ZCMLLayer

    return suite
