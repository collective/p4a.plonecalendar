from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer

DEPENDENCIES = ['Archetypes']
PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

PRODUCTS = list()
PRODUCTS += DEPENDENCIES

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml
import p4a.calendar
import p4a.plonecalendar

class AudioTestCase(PloneTestCase.PloneTestCase):
    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        zcml.load_config('configure.zcml', p4a.calendar)
        zcml.load_config('configure.zcml', p4a.plonecalendar)

from DateTime import DateTime
from datetime import datetime
from p4a.calendar.tests import EventProviderTestMixin
from p4a.calendar.interfaces import ICalendarConfig, IEventProvider

class ATEventProviderTest(AudioTestCase, EventProviderTestMixin):

    def afterSetUp(self):
        # Create folder.
        self.folder.invokeFactory('Folder', id='calendar-folder')
        calendarfolder = self.folder['calendar-folder']
        id = calendarfolder.invokeFactory('Event', id='event1')
        calendarfolder['event1'].update(title='First Event',
                                        startDate=DateTime('2006-09-28 08:30am'),
                                        endDate=DateTime('2006-09-28 09:30am'))
        id = calendarfolder.invokeFactory('Event', id='event2')
        calendarfolder['event2'].update(title='Second Event',
                                        startDate=DateTime('2006-09-29 08:30am'),
                                        endDate=DateTime('2006-09-29 09:30am'))
        id = calendarfolder.invokeFactory('Event', id='meeting1')
        # Calling this event "Meeting" is just to have one event that does
        # not have the word "Event" in the title.
        calendarfolder['meeting1'].update(title='First Meeting',
                                        startDate=DateTime('2006-09-30 08:30am'),
                                        endDate=DateTime('2006-09-30 09:30am'))

        # Activate calendaring capabilities on this folder
        config = ICalendarConfig(calendarfolder)
        config.calendar_activated = True
        self.provider = IEventProvider(calendarfolder)
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
    
    suite = TestSuite()
    suite.addTest(ZopeDocFileSuite(
        'calendar.txt',
        package='p4a.plonecalendar',
        test_class=AudioTestCase,
        )
    )
    suite.addTests(makeSuite(ATEventProviderTest))
    suite.layer = layer.ZCMLLayer

    return suite
