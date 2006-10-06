import datetime
import calendar
from p4a.calendar import interfaces

class EventListingView(object):
    """View that lists events.
    """

    @property
    def allEvents(self):
        provider = interfaces.IEventProvider(self.context)
        return [x.context for x in provider.all_events()]
