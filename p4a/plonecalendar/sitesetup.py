from dateable.chronos import interfaces
from p4a.plonecalendar import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from p4a.subtyper.sitesetup import setup_portal as subtyper_setup
from p4a.ploneevent.sitesetup import setup_portal as ploneevent_setup
from Products.CMFCore import utils as cmfutils

import logging
logger = logging.getLogger('p4a.plonecalendar.sitesetup')


def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    indexing.ensure_object_provides(portal)

    qi = cmfutils.getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['Marshall', 'Calendaring'])
    
    subtyper_setup(portal)
    ploneevent_setup(portal)


def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from dateable.chronos import interfaces
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
        sm.registerUtility(content.CalendarSupport('calendar_support'),
                           interfaces.ICalendarSupport)

def unsetup_portal(portal):
    # First we need to make sure that object_provides is up to date.
    # Setting marker interfaces doesn't automatically update the catalog.
    #portal.portal_catalog.reindexIndex('object_provides')
    #count = utils.remove_marker_ifaces(portal, interfaces.ICalendarEnhanced)
    #logger.warn('Removed ICalendarEnhanced interface from %i objects for '
                #'cleanup' % count)
    sm = portal.getSiteManager()
    component = sm.queryUtility(interfaces.ICalendarSupport)
    
    # The adapter registry has an internal counter which get out of sync if you register
    # something multiple times, and the subscriber list can get out of sync. Resync all that.
    sm.utilities._subscribers[0][interfaces.ICalendarSupport][u''] = (component,)
    sm.utilities._provided[interfaces.ICalendarSupport] = 2
    # Now when the registry is sane again, unregister the components:
    sm.unregisterUtility(component, provided=interfaces.ICalendarSupport)
    # Verify that there is no trace of the utility:
    assert(interfaces.IBasicCalendarSupport not in sm.utilities._provided)

    