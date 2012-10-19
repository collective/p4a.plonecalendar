from zope import interface
from dateable.chronos import interfaces
from p4a.plonecalendar import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from Products.CMFCore.utils import getToolByName
try:
    from p4a.subtyper.sitesetup import setup_portal as subtyper_setup
    from p4a.subtyper.interfaces import ISubtyped
    SUBTYPER_INSTALLED = True
except:
    SUBTYPER_INSTALLED = False
    
from Products.CMFCore import utils as cmfutils
import logging

def remove_all_old_crap(context, logger=None):
    if logger is None:
        logger = logging.getLogger('p4a.plonecalendar.sitesetup')
    portal = getToolByName(context, 'portal_url').getPortalObject()
    if not SUBTYPER_INSTALLED:
        raise SystemError("You can not run this without first installing p4a.subtyper")
    
    sm = portal.getSiteManager()
    component = sm.queryUtility(interfaces.ICalendarSupport)
    
    if component is not None:
        # The adapter registry has an internal counter which get out of sync if you register
        # something multiple times, and the subscriber list can get out of sync. Resync all that.
        sm.utilities._subscribers[0][interfaces.ICalendarSupport][u''] = (component,)
        sm.utilities._provided[interfaces.ICalendarSupport] = 2
        # Now when the registry is sane again, unregister the components:
        sm.unregisterUtility(component, provided=interfaces.ICalendarSupport)
        
        # Make sure it got removed properly:
        assert(interfaces.ICalendarSupport not in sm.utilities._provided)

        # Remove the interface from the lists, or we'll get useless warning messages forever:
        # Verify that there is no trace of the utility:
        try:
            del sm.utilities._adapters[0][interfaces.ICalendarSupport]
        except KeyError:
            pass
        try:
            del sm.utilities._subscribers[0][interfaces.ICalendarSupport]
        except KeyError:
            pass

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
    

def unsetup_portal(portal, reinstall=False):
    if reinstall:
        return
    # Remove the chronos calendar tool and put the old one back:
    # (XXX should be done in Chronos, but this is a quick hack)
    from Products.CMFPlone.CalendarTool import CalendarTool
    portal._delObject('portal_calendar')
    portal._setObject('portal_calendar', CalendarTool())

    # Reset all Calendar views
    allobjects = portal.portal_catalog(Type=('Folder', 'Topic', 'Collection'))
    for brain in allobjects:
        ob = brain.getObject()
        if getattr(ob, 'layout', None) in ('day.html', 'week.html', 'month.html', 'list.html', 'past.html'):
            del ob.layout
