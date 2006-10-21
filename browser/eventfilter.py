from urllib import urlencode
from zope.interface import implements, Interface
from zope.component import adapts
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class LocationFilter(object):
    """A content provider for filtering events on location"""
    
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    
    template = ZopeTwoPageTemplateFile('location_filter.pt')
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def update(self):
        hidden_fields = []
        for key, value in self.request.form.items():
            # Keep form values that are likely to modify the view:
            if key in ('year', 'month', 'day', 'week'):
                hidden_fields.append({'name': key, 'value': value})
        self.hidden_fields = hidden_fields
        self.url = self.request.ACTUAL_URL
        catalog = self.context.portal_catalog
        locations = filter(None, catalog.uniqueValuesFor('location'))
        self.locations = ('', ) + locations
        self.selected = self.request.form.get('location','')
    
    def render(self):
        # Slight trickery needed. This could also be done by
        # letting the provider inherit from aq.implicit, and
        # wrapping it in self, but I haven't tested.
        return self.template.__of__(self.context)(provider=self)
         