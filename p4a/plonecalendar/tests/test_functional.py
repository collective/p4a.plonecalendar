from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.Five.testbrowser import Browser        
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password

PloneTestCase.setupPloneSite(products=['p4a.plonecalendar'])


class TestFunctional(PloneTestCase.FunctionalTestCase):
    
    # XXX Many of these tests belong in dateable.chronos. However, we need
    # to make fake objects for that, so they are here, for the moment. /regebro
    
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
        # Create a blank topic:
        browser.open(portal_url)
        browser.getLink('Collection').click()
        form = browser.getForm('topic-base-edit')
        form.getControl(name='title').value = 'A Calendar Collection'
        form.getControl(name='form_submit').click()
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Changed subtype to Calendar" in browser.contents)
        
    def _save(self, browser):
        f = open("/tmp/browser.html", "w")
        f.write(browser.contents)
        f.close()
        
    def _isInCalendar(self, browser, text, calendar_start='class="ploneCalendar"'):
        contents = browser.contents[browser.contents.index(calendar_start):]
        contents = contents.replace('\n', ' ').replace('\t', ' ')
        contents = ' '.join([x.strip() for x in contents.split(' ') if x.strip()])
        return text in contents

    def test_disabling(self):
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        browser.handleErrors = False
        portal_url = self.portal.absolute_url()
        
        browser.open(portal_url + '/a-calendar')
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Removed Calendar subtype" in browser.contents)
        
        # Enable it again:        
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Changed subtype to Calendar" in browser.contents)
        
        # Set month as a default view:
        link = browser.getLink(id="list.html")
        link.click()
        self.failUnless("View changed." in browser.contents)
        
        # And disable it (this is a test for bug #65):
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Removed Calendar subtype" in browser.contents)
        
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

    def test_navigation(self):
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        browser.handleErrors = False
        portal_url = self.portal.absolute_url()
        browser.open(portal_url + '/a-calendar/month.html?date=2008-04-10')

        self.failUnless(self._isInCalendar(browser, 'April 2008'))
        browser.getLink(id="calendar-nav-previous").click()
        self.failUnless(self._isInCalendar(browser, 'March 2008'))
        browser.getLink(id="calendar-nav-next").click()
        self.failUnless(self._isInCalendar(browser, 'April 2008'))
        browser.getLink('Week').click()
        self.failUnless(self._isInCalendar(browser, '<span>Week</span> <span>15</span>'))
        browser.getLink(id="calendar-nav-previous").click()
        self.failUnless(self._isInCalendar(browser, '<span>Week</span> <span>14</span>'))
        browser.getLink(id="calendar-nav-next").click()
        self.failUnless(self._isInCalendar(browser, '<span>Week</span> <span>15</span>'))
        browser.getLink('Day').click()
        self.failUnless(self._isInCalendar(browser, 'Th 10/04'))
        browser.getLink(id="calendar-nav-previous").click()
        self.failUnless(self._isInCalendar(browser, 'We 09/04'))
        browser.getLink(id="calendar-nav-next").click()
        self.failUnless(self._isInCalendar(browser, 'Th 10/04'))
        
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
        # Make it recur.
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
