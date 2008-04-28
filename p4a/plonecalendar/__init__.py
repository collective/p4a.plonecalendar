import pkg_resources
from p4a.calendar import interfaces
from Acquisition import aq_inner, aq_parent

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
