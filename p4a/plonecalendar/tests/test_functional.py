from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password

PloneTestCase.setupPloneSite()


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
        link = browser.getLink(id='ICalendarEnhanced')
        link.click()
        self.failUnless("Changed subtype to Calendar" in browser.contents)
        
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
        calendar = browser.contents[browser.contents.index('class="ploneCalendar"'):]
        self.failUnless("An Event" in calendar)
        browser.open(folder_url + '?date=2007-05-01')
        calendar = browser.contents[browser.contents.index('class="ploneCalendar"'):]
        self.failUnless("An Event" in calendar)
        

def test_suite():
    suite = TestSuite()
    suite.addTests(makeSuite(TestFunctional))
    suite.layer = layer.ZCMLLayer

    return suite
