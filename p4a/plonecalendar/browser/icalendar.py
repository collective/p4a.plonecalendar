import urllib2
from StringIO import StringIO
from zope import interface
from Products.CMFCore.utils import getToolByName
from dateable.kalends import IEventProvider, IWebEventCreator
from plone.memoize import view
from p4a.plonecalendar import P4ACalendarMF as _
from Products.Five.browser import BrowserView

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


class iCalendarView(BrowserView):
    """ Export the contents of this Calendar as an iCalendar file """

    interface.implements(IiCalendarView)

    @view.memoize
    def has_ical_support(self):
        if self.__name__ == 'import.html':
            # Check that we are not read only.
            provider = IWebEventCreator(self.context)
            if not provider.canCreate():
                return False

        # Now check that Calendaring is installed properly.
        ct = getToolByName(self, 'portal_calendar')
        try:
            ct.exportCalendar(events=[])
            return True
        except TypeError:
            return False

    def exportCalendar(self, REQUEST=None):
        """ Export the contents of this Calendar as an iCalendar file """
        if not self.has_ical_support():
            return ''

        ct = getToolByName(self, 'portal_calendar')
        eventprovider = IEventProvider(self.context)
        variables = self.context.REQUEST.form
        events = [x.context.getObject() for x in eventprovider.getEvents(**variables)]
        self.request.RESPONSE.setHeader(
            'Content-Type', 'text/calendar;charset=utf-8')
        return ct.exportCalendar(events=events, REQUEST=REQUEST)

    def PUT(self, REQUEST, RESPONSE):
        """This is a PUT method for iCalendar access.

        The PUT method is found on the view "icalendar.ics". This can be
        slightly confusing, as it's there is no configure.zcml entry for it.
        This is also the reason why the export view "icalendar.ics" has to use
        template and not just an attribute on the view. As a template it is
        called by calling the view class which can have a PUT-method. If it
        was an attribute, it would be called by traversing to a default
        browser element, which is the attribute. That attribute doesn't have a
        PUT-method and WebDAV wouldn't work.
        """
        ct = getToolByName(self.context, 'portal_calendar')
        ct.importCalendar(REQUEST['BODYFILE'], dest=self.context,
                          do_action=True)
        RESPONSE.setStatus(204)
        return RESPONSE

    def import_from_url(self, url):
        if not self.has_ical_support():
            return "Calendaring product not installed."
        res = urllib2.urlopen(url)
        text = '\n'.join(res.readlines())
        # Make sure it really is UTF8, to avoid failure later:
        try:
            text.decode('utf8')
        except UnicodeDecodeError:
            try:
                # Maybe it's Latin-1? That's a break of specs,
                # but a common one.
                text = text.decode('latin1')
                # Yup, sure is. Re-encode as utf8:
                text = text.encode('utf8', 'replace')
            except UnicodeDecodeError:
                # We have no idea, what this is, so lets just reencode it
                # as UTF8 and replace everything weird with <?>.
                text = text.encode('utf8', 'replace').encode('utf8', 'replace')

        ical = StringIO(text)
        ct = getToolByName(self.context, 'portal_calendar')
        items = ct.importCalendar(ical, dest=self.context, do_action=True)
        return _(u"%s items imported") % len(items)

    def import_from_hcal(self, url):
        if not self.has_ical_support():
            return "Calendaring product not installed."

        import os
        import Globals

        # lxml.etree introduces a new class, lxml.etree.XSLT.
        # The class can be given an ElementTree object to construct an
        # XSLT transformer:

        from lxml import etree

        f = os.path.join(Globals.package_home(globals()), 'xhtml2vcal.xsl')
        xslt_doc = etree.parse(f)
        transform = etree.XSLT(xslt_doc)

        # You can then run the transformation on an ElementTree
        # document by simply calling it, and this results in another
        # ElementTree object:

        remote_page = urllib2.urlopen(url)
        parsed_page = etree.parse(remote_page)
        result = transform.apply(parsed_page)
        ical = StringIO(transform.tostring(result))
        ct = getToolByName(self.context, 'portal_calendar')
        items = ct.importCalendar(ical, dest=self.context, do_action=True)
        return _(u"%s items imported") % len(items)

    def importFormHandler(self):
        if self.request.get('file') is not None:
            ct = getToolByName(self.context, 'portal_calendar')
            items = ct.importCalendar(self.request.get('file'),
                                      dest=self.context, do_action=True)
            self.request.portal_status_message = _(u"%s items imported") \
                                                 % len(items)
        if self.request.get('url') is not None:
            self.request.portal_status_message = \
                self.import_from_url(self.request.get('url'))
