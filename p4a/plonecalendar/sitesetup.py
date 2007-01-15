from p4a.calendar import interfaces
from p4a.plonecalendar import content
from p4a.common import site

from Products.CMFCore import utils as cmfutils 

def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)

    qi = cmfutils.getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['CMFonFive'])

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from p4a.calendar import interfaces
      >>> from p4a.common.testing import MockSite

      >>> site = MockSite()
      >>> site.queryUtility(interfaces.ICalendarSupport) is None
      True

      >>> setup_site(site)
      >>> site.getUtility(interfaces.ICalendarSupport)
      <CalendarSupport ...>

    """

    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.ICalendarSupport):
        sm.registerUtility(interfaces.ICalendarSupport,
                           content.CalendarSupport('calendar_support'))

def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')