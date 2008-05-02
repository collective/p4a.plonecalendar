from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.Five.testbrowser import Browser        
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password

PloneTestCase.setupPloneSite()


class TestFunctional(PloneTestCase.FunctionalTestCase):
    
    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
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
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Changed subtype to Calendar" in browser.contents)
        
    def _isInCalendar(self, browser, text, calendar_start='class="ploneCalendar"'):
        return text in browser.contents[browser.contents.index(calendar_start):]

    def test_basic_views(self):
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        browser.handleErrors = False
        portal_url = self.portal.absolute_url()
        
        # First check that they work empty:
        browser.open(portal_url + '/a-calendar')
        browser.getLink('Week').click()
        browser.getLink('Day').click()
        browser.getLink('List').click()
        browser.getLink('Past').click()
        
        # Create an event:
        browser.open(portal_url + '/a-calendar')
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

        # Check that it still works:
        browser.open(portal_url + '/a-calendar/day.html?date=2007-04-01')
        self.failUnless(self._isInCalendar(browser, "An Event"))
        browser.getLink('Week').click()
        self.failUnless(self._isInCalendar(browser, "An Event"))
        browser.getLink('Day').click()
        self.failUnless(self._isInCalendar(browser, "An Event"))
        # This event is in the past (unless you have borrowed Guidos time-machine)
        browser.getLink('Past').click()
        self.failUnless(self._isInCalendar(browser, "An Event", 'class="eventlist"'))
        browser.getLink('List').click()
        #import pdb;pdb.set_trace()
        self.failIf(self._isInCalendar(browser, "An Event", 'class="eventlist"'))
        
    def test_basic_recurrence(self):
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        browser.handleErrors = False
        portal_url = self.portal.absolute_url()
        browser.open(portal_url + '/a-calendar')

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
        
        # Make it recur.
        link = browser.getLink(id='IRecurringEvent')
        link.click()
        self.failUnless("Changed subtype to Recurring Event" in browser.contents)
        
        # Edit the recurrence info:
        link = browser.getLink('Edit')
        link.click()
        form = browser.getForm('event-base-edit')
        form.getControl(name='frequency').value = ['1']
        form.getControl(name='form_submit').click()
        
        browser.getLink("A Calendar").click()
        folder_url = browser.url
        browser.open(folder_url + '?date=2007-04-01')
        self.failUnless(self._isInCalendar(browser, "An Event"))
        browser.open(folder_url + '?date=2007-05-01')
        self.failUnless(self._isInCalendar(browser, "An Event"))
        

def test_suite():
    suite = TestSuite()
    suite.addTests(makeSuite(TestFunctional))
    suite.layer = layer.ZCMLLayer

    return suite
