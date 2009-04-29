from zope import interface
from dateable.chronos import interfaces
from p4a.plonecalendar import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from p4a.subtyper.sitesetup import setup_portal as subtyper_setup
from p4a.subtyper.interfaces import ISubtyped
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
    setup_profile(portal)
    
    subtyper_setup(portal)
    ploneevent_setup(portal)

def setup_profile(site):
    setup_tool = site.portal_setup
    for profile in ['dateable.chronos']:
        setup_tool.setImportContext('profile-%s:default' % profile)
        setup_tool.runAllImportSteps()
 
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

def unsetup_portal(portal, reinstall=False):
    sm = portal.getSiteManager()
    component = sm.queryUtility(interfaces.ICalendarSupport)
    
    # The adapter registry has an internal counter which get out of sync if you register
    # something multiple times, and the subscriber list can get out of sync. Resync all that.
    sm.utilities._subscribers[0][interfaces.ICalendarSupport][u''] = (component,)
    sm.utilities._provided[interfaces.ICalendarSupport] = 2
    # Now when the registry is sane again, unregister the components:
    sm.unregisterUtility(component, provided=interfaces.ICalendarSupport)
    
    # Make sure it got removed properly:
    assert(interfaces.ICalendarSupport not in sm.utilities._provided)
    assert(not sm.utilities._adapters[0][interfaces.ICalendarSupport])
    assert(not sm.utilities._subscribers[0][interfaces.ICalendarSupport][u''])
    
    # Remove the interface from the lists, or we'll get useless warning messages forever:
    # Verify that there is no trace of the utility:
    del sm.utilities._adapters[0][interfaces.ICalendarSupport]
    del sm.utilities._subscribers[0][interfaces.ICalendarSupport]
    
    if reinstall:
        # For reinstalls, this is all we need to do
        return
    # Now we need to remove all the marker interfaces.
    # First we need to make sure that object_provides is up to date.
    # Setting marker interfaces doesn't automatically update the catalog.
    portal.portal_catalog.manage_reindexIndex(('object_provides',))
    # Then we can use the removal utility to unregister all of them:
    count = 0
    for obj in utils.objs_with_iface(portal, interfaces.ICalendarEnhanced):
        provided = interface.directlyProvidedBy(obj)
        # Remove ICalendarEnhanced and ISubtyped:
        provided -= interfaces.ICalendarEnhanced
        provided -= ISubtyped
        interface.directlyProvides(obj, provided)
        count += 1
    logger.warn('Removed ICalendarEnhanced interface from %i objects for '
                'cleanup' % count)
    
    # Remove the chronos calendar tool and put the old one back:
    # (XXX should be done in Chronos, but this is a quick hack)
    from Products.CMFPlone.CalendarTool import CalendarTool
    portal._delObject('portal_calendar')
    portal._setObject('portal_calendar', CalendarTool())

 