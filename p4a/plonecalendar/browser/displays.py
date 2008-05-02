from zope.interface import implements
from zope.component import adapts
from dateable.chronos.interfaces import ICalendarEnhanced

from Products.CMFDynamicViewFTI.interfaces import IDynamicallyViewable

# What views exist should rather be defined in dateable.chronos...

class CalendarDynamicViews(object):
    
    implements(IDynamicallyViewable)
    adapts(ICalendarEnhanced)
    

    def __init__(self, context):
        self.context = context # Actually ignored...
        
    def getAvailableViewMethods(self):
        """Get a list of registered view method names
        """
        return [x[0] for x in self.getAvailableLayouts()]

    def getDefaultViewMethod(self):
        """Get the default view method name
        """
        return "month.html"

    def getAvailableLayouts(self):
        """Get the layouts registered for this object.
        """        
        return (("month.html", "Month view"),
                ("week.html", "Week view"),
                ("day.html", "Day view"),
                ("list.html", "Event list"),
                ("past.html", "Event archive"),
                )
