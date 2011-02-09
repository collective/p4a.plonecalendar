import pkg_resources
from dateable.chronos import interfaces
from Acquisition import aq_inner, aq_parent

# Import "MessageFactory" to create messages in the calendar domain
from zope.i18nmessageid import MessageFactory
P4ACalendarMF = MessageFactory('calendar')

VERSION = pkg_resources.get_distribution('p4a.plonecalendar').version


def update_catalog(obj, evt):
    """Reindex the object in the catalog.
    """

    obj.reindexObject()


def vevent_demarshalled(obj, evt):
    container = aq_parent(aq_inner(obj))
    config = interfaces.ICalendarConfig(container, None)
    if config is not None and not config.calendar_activated:
        config.calendar_activated = True
