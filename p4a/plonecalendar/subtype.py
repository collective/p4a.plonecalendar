from zope import interface
from dateable.chronos import interfaces
from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor


class AbstractCalendarDescriptor(object):
    interface.implements(IPortalTypedFolderishDescriptor)

    title = u'Calendar'
    description = u'A folder that holds event objects'
    type_interface = interfaces.ICalendarEnhanced
    icon = '++resource++chronos_support/calendar_icon.gif'


class FolderCalendarDescriptor(AbstractCalendarDescriptor):
    for_portal_type = 'Folder'


class TopicCalendarDescriptor(AbstractCalendarDescriptor):
    for_portal_type = 'Topic'
