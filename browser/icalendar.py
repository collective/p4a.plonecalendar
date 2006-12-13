import urllib2
from StringIO import StringIO
from zope import interface
from Products.CMFCore.utils import getToolByName
from p4a.calendar.interfaces import IEventProvider

class IiCalendarView(interface.Interface):
    def has_ical_support():
        """Whether or not the current object has ical support.
        """

    def exportCalendar(REQUEST=None):
        """Export the calendar
        """

    def PUT(REQUEST, RESPONSE):
        """This is a PUT method for iCalendar access.
        """
        
class iCalendarView(object):
    """ Export the contents of this Calendar as an iCalendar file """

    interface.implements(IiCalendarView)

    def has_ical_support(self):
        cached = getattr(self, '__cached_ical_support', None)
        if cached is not None:
            return cached
        
        ct = getToolByName(self, 'portal_calendar')
        try:
            ct.exportCalendar(events=[])
            cached = True
        except TypeError, e:
            cached = False
        
        self.__cached_ical_support = cached
        return cached

    def exportCalendar(self, REQUEST=None):
        """ Export the contents of this Calendar as an iCalendar file """
        if not self.has_ical_support():
            return ''

        ct = getToolByName(self, 'portal_calendar')
        eventprovider = IEventProvider(self.context)
        events = [x.context.getObject() for x in eventprovider.all_events()]
        self.request.RESPONSE.setHeader(
            'Content-Type', 'text/calendar;charset=utf-8')
        return ct.exportCalendar(events=events, REQUEST=REQUEST)

    def PUT(self, REQUEST, RESPONSE):
        """This is a PUT method for iCalendar access.
        
        The PUT method is found on the view "icalendar.ics". This
        can be slightly confusing, as it's there is no configure.zcml
        entry for it. 
        This is also the reason why the export view "icalendar.ics" has
        to be a template and not an attribute. As a template it is
        called by calling the view class, as an attribute, it is called
        by traversing to a default browser element, which is the attribute.
        That attribute doesn't have a PUT-method and WebDAV stops working.
        """
        ct = getToolByName(self.context, 'portal_calendar')
        ct.importCalendar(REQUEST['BODYFILE'], dest=self.context, do_action=True)
        RESPONSE.setStatus(204)
        return RESPONSE

    def import_from_url(self, url):
        if not self.has_ical_support():
            return "Calendaring product not installed."
        res = urllib2.urlopen(url)
        ical = StringIO('\n'.join(res.readlines()))
        ct = getToolByName(self.context, 'portal_calendar')
        ct.importCalendar(ical, dest=self.context, do_action=True)
        return "Import done!"

    def import_from_hcal(self, url):
        if not self.has_ical_support():
            return "Calendaring product not installed."

        import os
        import Globals

        # lxml.etree introduces a new class, lxml.etree.XSLT. 
        # The class can be given an ElementTree object to construct an XSLT transformer:

        from lxml import etree

        f = os.path.join(Globals.package_home(globals()), 'xhtml2vcal.xsl')
        xslt_doc = etree.parse(f)
        transform = etree.XSLT(xslt_doc)

        # You can then run the transformation on an ElementTree document by simply calling it, 
        # and this results in another ElementTree object:

        remote_page = urllib2.urlopen(url)
        parsed_page = etree.parse(remote_page)
        result = transform.apply(parsed_page)
        ical = StringIO(transform.tostring(result))
        ct = getToolByName(self.context, 'portal_calendar')
        ct.importCalendar(ical, dest=self.context, do_action=True)
        return "Import done!"
    
    def importFormHandler(self):
        if self.request.get('file') is not None:
            ct = getToolByName(self.context, 'portal_calendar')
            ct.importCalendar(self.request.get('file'), dest=self.context, do_action=True)
        if self.request.get('url') is not None:
            self.import_from_url(self.request.get('url'))
            
        
 