from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase

from Products.Five.testbrowser import Browser
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.setup import portal_owner, default_password

@onsetup
def load_zcml():
    import p4a.plonecalendar
    zcml.load_config('configure.zcml', p4a.plonecalendar)

load_zcml()

PloneTestCase.setupPloneSite(products=['dateable.chronos', 'p4a.plonecalendar'])


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
        if 'form_submit' in browser.contents:
            self.submit_name = 'form_submit'
        else:
            self.submit_name = 'form.button.save'
        form.getControl(name=self.submit_name).click()

        # Create a blank topic:
        browser.open(portal_url)
        browser.getLink('Collection').click()
        form = browser.getForm(name='edit_form')
        form.getControl(name='title').value = 'A Calendar Collection'
        form.getControl(name=self.submit_name).click()
        
    def _save(self, browser):
        f = open("/tmp/browser.html", "w")
        f.write(browser.contents)
        f.close()
        
    def _isInCalendar(self, browser, text, calendar_start='id="calendar-view-tabs"', calendar_end=None):
        if calendar_end is None:
            calendar_end = 'id="viewlet-below-content"'
            if not calendar_end in browser.contents:
                # Plone 3:
                calendar_end = 'id="clear-space-before-footer"'
        contents = browser.contents[browser.contents.index(calendar_start):browser.contents.index(calendar_end)]
        contents = contents.replace('\n', ' ').replace('\t', ' ')
        contents = ' '.join([x.strip() for x in contents.split(' ') if x.strip()])
        return text in contents
                
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
        form.getControl(name=self.submit_name).click()
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
        self.failUnless(self._isInCalendar(browser, "An Event"))
        browser.getLink('List').click()
        
        self.failIf(self._isInCalendar(browser, "An Event"))

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
        
    # p4a.plonevent is now unsupported.
    #def test_basic_recurrence(self):
        #browser = Browser()
        #browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        #browser.handleErrors = False
        #portal_url = self.portal.absolute_url()
        #browser.open(portal_url + '/a-calendar')

        ## Create an event:
        #browser.getLink(id='event').click()
        #form = browser.getForm('event-base-edit')
        #form.getControl(name='title').value = 'An Event'
        #form.getControl(name='startDate_year').value = ['2007']
        #form.getControl(name='startDate_month').value = ['04']
        #form.getControl(name='startDate_day').value = ['01']
        #form.getControl(name='startDate_hour').value = ['11']
        #form.getControl(name='startDate_minute').value = ['00']
        #form.getControl(name='endDate_year').value = ['2007']
        #form.getControl(name='endDate_month').value = ['04']
        #form.getControl(name='endDate_day').value = ['01']
        #form.getControl(name='endDate_hour').value = ['11']
        #form.getControl(name='endDate_minute').value = ['00']
        ## Make it recur.
        #form.getControl(name='frequency').value = ['1']
        #form.getControl(name=self.submit_name).click()
        
        #browser.getLink("A Calendar").click()
        #folder_url = browser.url
        #browser.open(folder_url + '?date=2007-04-01')
        #self.failUnless(self._isInCalendar(browser, "An Event"))
        #browser.open(folder_url + '?date=2007-05-01')
        #self.failUnless(self._isInCalendar(browser, "An Event"))


def test_suite():
    suite = TestSuite()
    suite.addTests(makeSuite(TestFunctional))

    return suite
