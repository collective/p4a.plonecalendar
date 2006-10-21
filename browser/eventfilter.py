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
    
    def __init__(self, context=None, request=None, view=None):
        self.context = context
        self.request = request
        self.view = view

    def update(self):
        catalog = self.context.portal_catalog
        if not 'location' in  catalog.indexes():
            self.do_render = False
            return
        locations = filter(None, catalog.uniqueValuesFor('location'))
        self.locations = ('', ) + locations
        self.selected = self.request.form.get('location','')

        hidden_fields = []
        for key, value in self.request.form.items():
            # Keep form values that are likely to modify the view:
            if key in ('year', 'month', 'day', 'week'):
                hidden_fields.append({'name': key, 'value': value})
        self.hidden_fields = hidden_fields
        self.url = self.request.ACTUAL_URL
        self.do_render = True
    
    def render(self):
        if not self.do_render:
            return ''
        # Slight trickery needed. This could also be done by
        # letting the provider inherit from aq.implicit, and
        # wrapping it in self, but I haven't tested.
        return self.template.__of__(self.context)(provider=self)
         