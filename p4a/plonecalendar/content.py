from zope import interface
from dateable.chronos import interfaces
from OFS.SimpleItem import SimpleItem

class CalendarSupport(SimpleItem):
    """
    """

    interface.implements(interfaces.ICalendarSupport)

    @property
    def support_enabled(self):
        return True
